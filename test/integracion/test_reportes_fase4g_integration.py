"""
FASE 4G: Tests de integración completas.
Flujo completo: datos → analytics → PDF → validación.
"""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO

from app.helpers.generators.contratos_report import ContratosReport
from app.helpers.generators.balance_report import BalanceReport
from app.helpers.generators.mantenimiento_report import MantenimientoReport
from app.helpers.generators.tareas_report import TareasReport
from app.helpers.generators.premios_report import PremiosReport
from app.helpers.generators.inventario_report import InventarioReport
from app.helpers.generators.guiones_report import GuionesReport
from app.helpers.generators.bitacora_report import BitacoraReport
from app.helpers.generators.usuarios_report import UsuariosReport
from app.helpers.generators.patrocinadores_report import PatrocinadoresReport
from app.helpers.generators.reels_report import ReelsReport
from app.helpers.reportes_analytics import AnalyticsResult, Severity
from app.helpers.reportes_module_analytics import run_analytics


def _make_user():
    u = MagicMock()
    u.nombre = 'Test'
    u.rol = 'Admin'
    u.departamento = 'Técnica'
    u.id = 1
    return u


# ============================================================
# FLUJO COMPLETO POR MÓDULO
# ============================================================

class TestFlujoCompletoContratos:
    """Flujo completo: datos → analytics → PDF."""

    def test_datos_normales(self):
        datos = [
            {'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente',
             'monto_total': 100000, 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31', 'dias_restantes': 100},
            {'nombre_empresa': 'B', 'tipo': 'Plata', 'estatus': 'Vencido',
             'monto_total': 50000, 'fecha_inicio': '2025-01-01', 'fecha_fin': '2025-12-31', 'dias_restantes': -30},
            {'nombre_empresa': 'C', 'tipo': 'Bronce', 'estatus': 'Borrador',
             'monto_total': 20000, 'fecha_inicio': '2026-06-01', 'fecha_fin': '2027-06-01', 'dias_restantes': 270},
        ]
        analytics = run_analytics('contratos', datos)
        assert len(analytics.metrics) >= 8
        assert any(a.id == 'contratos_vencidos' for a in analytics.alerts)

        gen = ContratosReport(_make_user())
        pdf = gen.generate(datos, filtros={'estatus': 'Vigente'}, kpis={'total': 3},
                          opciones={'analytics': analytics, 'resumen': True})
        assert pdf[:4] == b'%PDF'
        assert len(pdf) > 3000

    def test_datos_vacios(self):
        analytics = run_analytics('contratos', [])
        assert len(analytics.metrics) == 0

    def test_un_registro(self):
        datos = [{'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente',
                  'monto_total': 100000, 'dias_restantes': 100}]
        analytics = run_analytics('contratos', datos)
        assert len(analytics.metrics) >= 5

        gen = ContratosReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'

    def test_muchosregistros(self):
        datos = [{'nombre_empresa': f'Empresa-{i}', 'tipo': 'Oro', 'estatus': 'Vigente',
                  'monto_total': 10000 * i, 'dias_restantes': 100} for i in range(50)]
        analytics = run_analytics('contratos', datos)
        assert len(analytics.metrics) >= 5

        gen = ContratosReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 50},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoBalance:
    def test_datos_normales(self):
        datos = [
            {'nombre_patrocinador': 'A', 'tipo_pago': 'Transferencia', 'monto': 100000, 'fecha_pago': '2026-01-01', 'id_contrato': 1},
            {'nombre_patrocinador': 'B', 'tipo_pago': 'Efectivo', 'monto': 20000, 'fecha_pago': '2026-02-01', 'id_contrato': 2},
        ]
        analytics = run_analytics('balance', datos)
        assert len(analytics.metrics) >= 3

        gen = BalanceReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total_pagos': 2},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoMantenimiento:
    def test_datos_normales(self):
        datos = [
            {'recurso_nombre': 'PC-01', 'estado': 'en_espera', 'fecha_ingreso': '2026-08-01', 'dias_en_taller': 20},
            {'recurso_nombre': 'PC-02', 'estado': 'reparado', 'fecha_ingreso': '2026-07-01', 'dias_en_taller': 5},
        ]
        analytics = run_analytics('mantenimiento', datos)
        assert len(analytics.metrics) >= 5
        assert any(a.id == 'mantenimiento_prolongado' for a in analytics.alerts)

        gen = MantenimientoReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 2},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoTareas:
    def test_datos_normales(self):
        datos = [
            {'nombre_tarea': 'T1', 'estado': 'Pendiente', 'asignado_a': 'Juan', 'fecha_asignacion_tarea': '2026-08-01'},
            {'nombre_tarea': 'T2', 'estado': 'Completada', 'asignado_a': 'María', 'fecha_asignacion_tarea': '2026-07-01'},
        ]
        analytics = run_analytics('tareas', datos)
        assert len(analytics.metrics) >= 4

        gen = TareasReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 2},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoPremios:
    def test_datos_normales(self):
        datos = [
            {'nombre': 'P1', 'patrocinador_nombre': 'A', 'estado': 'entregado', 'cantidad': 100, 'cantidad_entregada': 80, 'fecha_creacion': '2026-01-01'},
            {'nombre': 'P2', 'patrocinador_nombre': 'B', 'estado': 'pendiente', 'cantidad': 50, 'cantidad_entregada': 0, 'fecha_creacion': '2026-02-01'},
        ]
        analytics = run_analytics('premios', datos)
        assert len(analytics.metrics) >= 5

        gen = PremiosReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 2},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoInventario:
    def test_datos_normales(self):
        datos = [
            {'nombre': 'PC-01', 'tipo_nombre': 'Equipo', 'estado_nombre': 'Disponible', 'costo': 5000, 'fecha_compra': '2026-01-01'},
        ]
        analytics = run_analytics('inventario', datos)
        assert len(analytics.metrics) >= 3

        gen = InventarioReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoGuiones:
    def test_datos_normales(self):
        datos = [
            {'nombre': 'G1', 'estado': 'publicado', 'tiempo_segundos': 3600, 'game': 10, 'pregame': 5, 'creado_en': '2026-01-01'},
        ]
        analytics = run_analytics('guiones', datos)
        assert len(analytics.metrics) >= 5

        gen = GuionesReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoBitacora:
    def test_datos_normales(self):
        datos = [
            {'usuario_nombre': 'Juan', 'tipo_accion': 'create', 'modulo': 'contratos', 'created_at': '2026-01-01'},
        ]
        analytics = run_analytics('bitacora', datos)
        assert len(analytics.metrics) >= 3

        gen = BitacoraReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoUsuarios:
    def test_datos_normales(self):
        datos = [
            {'nombre': 'Juan', 'rol': 'Admin', 'departamento': 'Técnica', 'activo': 1},
        ]
        analytics = run_analytics('usuarios', datos)
        assert len(analytics.metrics) >= 3

        gen = UsuariosReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoPatrocinadores:
    def test_datos_normales(self):
        datos = [
            {'nombre_empresa': 'A', 'tipo_contrato': 'Vigente', 'estado': 1},
        ]
        analytics = run_analytics('patrocinadores', datos)
        assert len(analytics.metrics) >= 3

        gen = PatrocinadoresReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


class TestFlujoCompletoReels:
    def test_datos_normales(self):
        datos = [
            {'nombre': 'R1', 'patrocinado': 'A', 'duracion_total': 5.5, 'videos_count': 8, 'creado_en': '2026-01-01'},
        ]
        analytics = run_analytics('reels', datos)
        assert len(analytics.metrics) >= 3

        gen = ReelsReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'


# ============================================================
# OPCIONES COMBINADAS
# ============================================================

class TestOpcionesCombinadas:
    def test_resumen_top_n_analytics(self):
        datos = [
            {'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente', 'monto_total': 100000, 'dias_restantes': 100},
            {'nombre_empresa': 'B', 'tipo': 'Plata', 'estatus': 'Vigente', 'monto_total': 50000, 'dias_restantes': 50},
        ]
        analytics = run_analytics('contratos', datos)
        gen = ContratosReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 2},
                          opciones={'analytics': analytics, 'resumen': True, 'top_n': 3})
        assert pdf[:4] == b'%PDF'
        assert len(pdf) > 2000

    def test_orientacion_horizontal_analytics(self):
        datos = [{'nombre_empresa': f'E-{i}', 'tipo': 'Oro', 'estatus': 'Vigente',
                  'monto_total': 10000 * i, 'dias_restantes': 100} for i in range(10)]
        analytics = run_analytics('contratos', datos)
        gen = ContratosReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 10},
                          opciones={'analytics': analytics, 'orientacion': 'horizontal'})
        assert pdf[:4] == b'%PDF'


# ============================================================
# EDGE CASES
# ============================================================

class TestEdgeCases:
    def test_valores_nulos_en_datos(self):
        datos = [
            {'nombre_empresa': 'A', 'tipo': None, 'estatus': 'Vigente',
             'monto_total': None, 'dias_restantes': None},
        ]
        analytics = run_analytics('contratos', datos)
        assert len(analytics.metrics) >= 3

        gen = ContratosReport(_make_user())
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1},
                          opciones={'analytics': analytics})
        assert pdf[:4] == b'%PDF'

    def test_campos_faltantes(self):
        datos = [{'nombre_empresa': 'A'}]
        analytics = run_analytics('contratos', datos)
        assert len(analytics.metrics) >= 1

    def test_analytics_none(self):
        gen = ContratosReport(_make_user())
        datos = [{'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente', 'monto_total': 10000}]
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': None})
        assert pdf[:4] == b'%PDF'

    def test_analytics_vacio(self):
        gen = ContratosReport(_make_user())
        datos = [{'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente', 'monto_total': 10000}]
        ar = AnalyticsResult('contratos')
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': ar})
        assert pdf[:4] == b'%PDF'


# ============================================================
# DISPATCHER RUN_ANALYTICS
# ============================================================

class TestRunAnalyticsCompleto:
    TODOS_LOS_MODULOS = [
        ('contratos', {'nombre_empresa': 'A', 'estatus': 'Vigente', 'monto_total': 10000, 'dias_restantes': 100}),
        ('balance', {'nombre_patrocinador': 'A', 'tipo_pago': 'Transferencia', 'monto': 50000, 'fecha_pago': '2026-01-01'}),
        ('patrocinadores', {'nombre_empresa': 'A', 'tipo_contrato': 'Vigente', 'estado': 1}),
        ('mantenimiento', {'recurso_nombre': 'PC', 'estado': 'en_espera', 'dias_en_taller': 5}),
        ('tareas', {'nombre_tarea': 'T', 'estado': 'Pendiente', 'asignado_a': 'J', 'fecha_asignacion_tarea': '2026-08-01'}),
        ('premios', {'nombre': 'P', 'patrocinador_nombre': 'A', 'estado': 'entregado', 'cantidad': 100, 'cantidad_entregada': 80, 'fecha_creacion': '2026-01-01'}),
        ('inventario', {'nombre': 'PC', 'tipo_nombre': 'Equipo', 'estado_nombre': 'Disponible', 'costo': 5000, 'fecha_compra': '2026-01-01'}),
        ('guiones', {'nombre': 'G', 'estado': 'publicado', 'tiempo_segundos': 3600, 'game': 10, 'pregame': 5, 'creado_en': '2026-01-01'}),
        ('bitacora', {'usuario_nombre': 'J', 'tipo_accion': 'create', 'modulo': 'contratos', 'created_at': '2026-01-01'}),
        ('usuarios', {'nombre': 'J', 'rol': 'Admin', 'departamento': 'Técnica', 'activo': 1}),
        ('reels', {'nombre': 'R', 'patrocinado': 'A', 'duracion_total': 5.5, 'videos_count': 8, 'creado_en': '2026-01-01'}),
    ]

    @pytest.mark.parametrize("modulo,record", TODOS_LOS_MODULOS)
    def test_un_registro_por_modulo(self, modulo, record):
        ar = run_analytics(modulo, [record])
        assert ar.module == modulo
        assert len(ar.metrics) >= 1

    def test_desconocido(self):
        ar = run_analytics('modulo_fantasma', [{'x': 1}])
        assert ar.module == 'modulo_fantasma'
        assert ar.metrics == []

    def test_vacio(self):
        ar = run_analytics('contratos', [])
        assert ar.metrics == []
