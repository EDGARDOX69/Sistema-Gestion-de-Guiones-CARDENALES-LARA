"""Tests para reportes_definition.py — registro central de reportes (FASE 3)."""
import pytest
from app.helpers.reportes_definition import (
    REPORT_DEFINITIONS, get_definition, get_fields, get_columns_tuple,
    get_default_columns, get_columns_preview, get_filters, get_filters_keys,
    get_kpi_cards, get_field_type, is_numeric, format_cell, get_all_modules,
)

MODULOS_ESPERADOS = {
    'guiones', 'inventario', 'premios', 'contratos', 'balance',
    'tareas', 'patrocinadores', 'usuarios', 'mantenimiento', 'reels', 'bitacora',
}


class TestExistencia:
    def test_todos_los_modulos_definidos(self):
        assert set(REPORT_DEFINITIONS.keys()) == MODULOS_ESPERADOS

    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_definicion_tiene_campos_requeridos(self, modulo):
        defn = get_definition(modulo)
        assert defn is not None
        assert defn['id'] == modulo
        assert 'titulo' in defn
        assert 'fields' in defn
        assert 'columns' in defn
        assert 'default_columns' in defn
        assert 'filters' in defn
        assert 'kpi_cards' in defn
        assert 'analytics' in defn

    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_fields_no_vacios(self, modulo):
        fields = get_fields(modulo)
        assert len(fields) > 0

    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_default_columns_existen_en_fields(self, modulo):
        defaults = get_default_columns(modulo)
        fields = get_fields(modulo)
        for key in defaults:
            assert key in fields, f"Default '{key}' no existe en fields[{modulo}]"


class TestCampos:
    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_fields_tienen_label_type(self, modulo):
        fields = get_fields(modulo)
        for key, campo in fields.items():
            assert 'label' in campo, f"{modulo}.{key} sin label"
            assert 'type' in campo, f"{modulo}.{key} sin type"
            assert campo['type'] in {'texto', 'texto_largo', 'entero', 'decimal',
                                      'moneda', 'fecha', 'fecha_hora', 'boolean',
                                      'porcentaje', 'duracion'}, \
                f"{modulo}.{key} type '{campo['type']}' no válido"

    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_fields_tienen_order(self, modulo):
        fields = get_fields(modulo)
        orders = [f.get('order', 0) for f in fields.values()]
        assert sorted(orders) == orders, f"Orders de {modulo} no están ordenados"

    def test_get_field_type(self):
        assert get_field_type('guiones', 'nombre') == 'texto'
        assert get_field_type('balance', 'monto') == 'moneda'
        assert get_field_type('inventario', 'costo') == 'moneda'

    def test_is_numeric(self):
        assert is_numeric('balance', 'monto') is True
        assert is_numeric('guiones', 'nombre') is False
        assert is_numeric('inventario', 'costo') is True

    def test_format_cell(self):
        assert format_cell('balance', 'monto', 50000) == '$50,000.00'
        assert format_cell('guiones', 'nombre', 'Test') == 'Test'
        assert format_cell('guiones', 'nombre', None) == '—'


class TestColumnas:
    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_columns_son_tuplas(self, modulo):
        columns = get_columns_tuple(modulo)
        for c in columns:
            assert isinstance(c, tuple)
            assert len(c) == 3
            assert isinstance(c[0], str)  # label
            assert isinstance(c[1], str)  # key
            assert isinstance(c[2], int)  # width

    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_columns_keys_existen_en_fields(self, modulo):
        columns = get_columns_tuple(modulo)
        fields = get_fields(modulo)
        for c in columns:
            assert c[1] in fields, f"Column key '{c[1]}' no existe en fields[{modulo}]"

    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_columns_preview_keys_match_fields(self, modulo):
        preview = get_columns_preview(modulo)
        fields = get_fields(modulo)
        for p in preview:
            assert p['key'] in fields, f"Preview key '{p['key']}' no existe en fields[{modulo}]"
            assert 'label' in p

    def test_reels_columns_vacio(self):
        """Reels tiene layout especial, columns vacío es válido."""
        assert get_columns_tuple('reels') == []


class TestFiltros:
    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_filtros_tienen_label_type(self, modulo):
        filters = get_filters(modulo)
        for key, f in filters.items():
            assert 'label' in f, f"{modulo}.{key} sin label"
            assert 'type' in f, f"{modulo}.{key} sin type"

    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_filtros_select_con_options_o_load_via(self, modulo):
        filters = get_filters(modulo)
        for key, f in filters.items():
            if f['type'] == 'select':
                assert 'options' in f or 'load_via' in f, \
                    f"{modulo}.{key} select sin options ni load_via"


class TestKPIs:
    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_kpi_cards_tienen_key_label_color(self, modulo):
        kpis = get_kpi_cards(modulo)
        assert len(kpis) > 0, f"{modulo} sin kpi_cards"
        for kpi in kpis:
            assert 'key' in kpi
            assert 'label' in kpi
            assert 'color' in kpi

    @pytest.mark.parametrize("modulo", MODULOS_ESPERADOS)
    def test_kpi_keys_no_duplicados(self, modulo):
        kpis = get_kpi_cards(modulo)
        keys = [k['key'] for k in kpis]
        assert len(keys) == len(set(keys)), f"KPI keys duplicados en {modulo}"


class TestConsistencia:
    """Test que cambiar una definición se refleja en todos los adaptadores."""

    def test_cambio_column_se_refleja_en_tuple_y_preview(self):
        defn = get_definition('guiones')
        original = defn['columns'][0]
        defn['columns'][0] = ('Test Label', 'nombre', 120)
        tuplas = get_columns_tuple('guiones')
        assert tuplas[0][0] == 'Test Label'
        preview = get_columns_preview('guiones')
        assert preview[0]['label'] == 'Test Label'
        # restaurar
        defn['columns'][0] = original

    def test_cambio_field_se_refleja_en_get_fields(self):
        defn = get_definition('guiones')
        original = defn['fields']['nombre']['label']
        defn['fields']['nombre']['label'] = 'Nombre Test'
        fields = get_fields('guiones')
        assert fields['nombre']['label'] == 'Nombre Test'
        # restaurar
        defn['fields']['nombre']['label'] = original


class TestGetAllModules:
    def test_returns_all_11(self):
        modules = get_all_modules()
        assert len(modules) == 11
        assert set(modules) == MODULOS_ESPERADOS
