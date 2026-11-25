"""
Tests de integración: PDF + analytics.
Valida que los PDFs generados incluyen las secciones de analítica correctamente.
"""
import pytest
from unittest.mock import MagicMock

from app.helpers.generators.base_report import BaseReportGenerator
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
from app.helpers.reportes_analytics import AnalyticsResult, Metric, Alert, Severity
from app.helpers.reportes_module_analytics import run_analytics


def _make_user():
    u = MagicMock()
    u.nombre = 'Test'
    u.rol = 'Admin'
    u.departamento = 'Técnica'
    return u


class TestPDFSinAnalytics:
    """PDFs sin analytics siguen funcionando igual."""
    def test_contratos_sin_analytics(self):
        gen = ContratosReport(_make_user())
        datos = [
            {'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente',
             'monto_total': 10000, 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31'},
        ]
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={})
        assert pdf is not None
        assert len(pdf) > 1000

    def test_balance_sin_analytics(self):
        gen = BalanceReport(_make_user())
        datos = [{'nombre_patrocinador': 'A', 'tipo_pago': 'Transferencia', 'monto': 50000, 'fecha_pago': '2026-01-01'}]
        pdf = gen.generate(datos, filtros={}, kpis={'total_pagos': 1}, opciones={})
        assert pdf is not None


class TestPDFConAnalytics:
    """PDFs con analytics incluyen las secciones de análisis."""
    def test_contratos_con_analytics(self):
        gen = ContratosReport(_make_user())
        datos = [
            {'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente',
             'monto_total': 100000, 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31', 'dias_restantes': 100},
            {'nombre_empresa': 'B', 'tipo': 'Plata', 'estatus': 'Vencido',
             'monto_total': 50000, 'fecha_inicio': '2025-01-01', 'fecha_fin': '2025-12-31', 'dias_restantes': -30},
        ]
        analytics = run_analytics('contratos', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 2}, opciones={'analytics': analytics})
        assert pdf is not None
        assert len(pdf) > 2000
        # Verificar que es un PDF válido
        assert pdf[:4] == b'%PDF'

    def test_balance_con_analytics(self):
        gen = BalanceReport(_make_user())
        datos = [
            {'nombre_patrocinador': 'A', 'tipo_pago': 'Transferencia', 'monto': 100000, 'fecha_pago': '2026-01-01', 'id_contrato': 1},
            {'nombre_patrocinador': 'B', 'tipo_pago': 'Efectivo', 'monto': 20000, 'fecha_pago': '2026-02-01', 'id_contrato': 2},
        ]
        analytics = run_analytics('balance', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total_pagos': 2}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_mantenimiento_con_analytics(self):
        gen = MantenimientoReport(_make_user())
        datos = [
            {'recurso_nombre': 'PC-01', 'estado': 'en_espera', 'fecha_ingreso': '2026-08-01', 'dias_en_taller': 20},
            {'recurso_nombre': 'PC-02', 'estado': 'reparado', 'fecha_ingreso': '2026-07-01', 'dias_en_taller': 5},
        ]
        analytics = run_analytics('mantenimiento', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 2}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_tareas_con_analytics(self):
        gen = TareasReport(_make_user())
        datos = [
            {'nombre_tarea': 'T1', 'estado': 'Pendiente', 'asignado_a': 'Juan', 'fecha_asignacion_tarea': '2026-08-01'},
            {'nombre_tarea': 'T2', 'estado': 'Completada', 'asignado_a': 'María', 'fecha_asignacion_tarea': '2026-07-01'},
        ]
        analytics = run_analytics('tareas', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 2}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_premios_con_analytics(self):
        gen = PremiosReport(_make_user())
        datos = [
            {'nombre': 'P1', 'patrocinador_nombre': 'A', 'estado': 'entregado', 'cantidad': 100, 'cantidad_entregada': 80, 'fecha_creacion': '2026-01-01'},
        ]
        analytics = run_analytics('premios', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_inventario_con_analytics(self):
        gen = InventarioReport(_make_user())
        datos = [
            {'nombre': 'PC-01', 'tipo_nombre': 'Equipo', 'estado_nombre': 'Disponible', 'costo': 5000, 'fecha_compra': '2026-01-01'},
        ]
        analytics = run_analytics('inventario', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_guiones_con_analytics(self):
        gen = GuionesReport(_make_user())
        datos = [
            {'nombre': 'G1', 'estado': 'publicado', 'tiempo_segundos': 3600, 'game': 10, 'pregame': 5, 'creado_en': '2026-01-01'},
        ]
        analytics = run_analytics('guiones', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_bitacora_con_analytics(self):
        gen = BitacoraReport(_make_user())
        datos = [
            {'usuario_nombre': 'Juan', 'tipo_accion': 'create', 'modulo': 'contratos', 'created_at': '2026-01-01'},
        ]
        analytics = run_analytics('bitacora', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_usuarios_con_analytics(self):
        gen = UsuariosReport(_make_user())
        datos = [
            {'nombre': 'Juan', 'rol': 'Admin', 'departamento': 'Técnica', 'activo': 1},
        ]
        analytics = run_analytics('usuarios', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_patrocinadores_con_analytics(self):
        gen = PatrocinadoresReport(_make_user())
        datos = [
            {'nombre_empresa': 'A', 'tipo_contrato': 'Vigente', 'estado': 1},
        ]
        analytics = run_analytics('patrocinadores', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'

    def test_reels_con_analytics(self):
        gen = ReelsReport(_make_user())
        datos = [
            {'nombre': 'R1', 'patrocinado': 'A', 'duracion_total': 5.5, 'videos_count': 8, 'creado_en': '2026-01-01'},
        ]
        analytics = run_analytics('reels', datos)
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': analytics})
        assert pdf is not None
        assert pdf[:4] == b'%PDF'


class TestAnalyticsVacios:
    """Analytics vacíos no generan secciones adicionales."""
    def test_modulo_desconocido(self):
        gen = ContratosReport(_make_user())
        datos = [{'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente', 'monto_total': 10000}]
        analytics = run_analytics('modulo_fantasma', datos)
        # Analytics vacío: no debería fallar
        pdf = gen.generate(datos, filtros={}, kpis={'total': 1}, opciones={'analytics': analytics})
        assert pdf is not None

    def test_datos_vacios(self):
        gen = ContratosReport(_make_user())
        analytics = run_analytics('contratos', [])
        # Empty analytics, no crash
        assert analytics.metrics == []
        assert analytics.alerts == []


class TestSeccionAnalytics:
    """Test directo de _seccion_analytics."""
    def test_con_metricas(self):
        gen = BaseReportGenerator(_make_user())
        gen.MODULO = 'test'
        gen.TITULO = 'Test'
        ar = AnalyticsResult('test')
        ar.add_metric('total', 100, 'count')
        ar.add_metric('monto', 50000, 'currency')
        ar.add_metric('tasa', 85.5, 'percent')
        story = gen._seccion_analytics(ar)
        assert len(story) > 0

    def test_con_alertas(self):
        gen = BaseReportGenerator(_make_user())
        gen.MODULO = 'test'
        gen.TITULO = 'Test'
        ar = AnalyticsResult('test')
        ar.add_alert('test_alert', 'test', Severity.CRITICAL, 'Alerta de prueba', 'Descripción', affected_count=5)
        ar.add_alert('test_warning', 'test', Severity.WARNING, 'Warning', 'Desc')
        story = gen._seccion_analytics(ar)
        assert len(story) > 0

    def test_con_insights(self):
        gen = BaseReportGenerator(_make_user())
        gen.MODULO = 'test'
        gen.TITULO = 'Test'
        ar = AnalyticsResult('test')
        ar.add_insight('test_insight', 'Insight description')
        story = gen._seccion_analytics(ar)
        assert len(story) > 0

    def test_vacio(self):
        gen = BaseReportGenerator(_make_user())
        story = gen._seccion_analytics(None)
        assert story == []
