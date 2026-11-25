"""
Tests exhaustivos para analítica por módulo.
Cada módulo tiene tests para: dataset normal, vacío, null, un registro, múltiples,
métricas, distribuciones, ranking, tendencias, alertas, insights.
"""
import pytest
from datetime import datetime

from app.helpers.reportes_analytics import AnalyticsResult, Severity
from app.helpers.reportes_module_analytics import (
    analytics_contratos, analytics_balance, analytics_patrocinadores,
    analytics_mantenimiento, analytics_tareas, analytics_premios,
    analytics_inventario, analytics_guiones, analytics_bitacora,
    analytics_usuarios, analytics_reels, run_analytics,
)


# ============================================================
# CONTRATOS
# ============================================================

class TestAnalyticsContratos:
    RECORDS = [
        {'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente', 'monto_total': 100000, 'fecha_inicio': '2026-01-01', 'fecha_fin': '2026-12-31', 'dias_restantes': 120},
        {'nombre_empresa': 'A', 'tipo': 'Plata', 'estatus': 'Vigente', 'monto_total': 50000, 'fecha_inicio': '2026-03-01', 'fecha_fin': '2026-09-15', 'dias_restantes': 11},
        {'nombre_empresa': 'B', 'tipo': 'Bronce', 'estatus': 'Vencido', 'monto_total': 30000, 'fecha_inicio': '2025-01-01', 'fecha_fin': '2025-12-31', 'dias_restantes': -90},
        {'nombre_empresa': 'B', 'tipo': 'Oro', 'estatus': 'Vigente', 'monto_total': 80000, 'fecha_inicio': '2026-02-01', 'fecha_fin': '2026-11-30', 'dias_restantes': 90},
        {'nombre_empresa': 'C', 'tipo': 'Plata', 'estatus': 'Borrador', 'monto_total': 20000, 'fecha_inicio': '2026-06-01', 'fecha_fin': '2027-06-01', 'dias_restantes': 270},
    ]

    def test_empty(self):
        r = analytics_contratos([])
        assert r.metrics == []
        assert r.alerts == []

    def test_total(self):
        r = analytics_contratos(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 5

    def test_vigentes(self):
        r = analytics_contratos(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'vigentes')
        assert m.value == 3

    def test_vencidos(self):
        r = analytics_contratos(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'vencidos')
        assert m.value == 1

    def test_borradores(self):
        r = analytics_contratos(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'borradores')
        assert m.value == 1

    def test_monto_total(self):
        r = analytics_contratos(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'monto_total')
        assert m.value == 280000

    def test_vigentes_pct(self):
        r = analytics_contratos(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'vigentes_pct')
        assert m.value == 60.0

    def test_distribuciones(self):
        r = analytics_contratos(self.RECORDS)
        assert len(r.distributions) == 3

    def test_rankings(self):
        r = analytics_contratos(self.RECORDS)
        assert len(r.rankings) == 1
        assert r.rankings[0].items[0].item == 'A'

    def test_tendencias(self):
        r = analytics_contratos(self.RECORDS)
        assert len(r.trends) == 1

    def test_alerta_vencido(self):
        r = analytics_contratos(self.RECORDS)
        alertas = [a for a in r.alerts if a.id == 'contratos_vencidos']
        assert len(alertas) == 1
        assert alertas[0].severity == Severity.CRITICAL

    def test_alerta_vencer_7d(self):
        records = [{'nombre_empresa': 'X', 'estatus': 'Vigente', 'monto_total': 10000,
                    'dias_restantes': 5}]
        r = analytics_contratos(records)
        alertas = [a for a in r.alerts if a.id == 'contratos_vencer_7d']
        assert len(alertas) == 1

    def test_insight_concentracion(self):
        records = [
            {'nombre_empresa': 'A', 'tipo': 'Oro', 'estatus': 'Vigente', 'monto_total': 100000, 'dias_restantes': 100},
            {'nombre_empresa': 'A', 'tipo': 'Plata', 'estatus': 'Vigente', 'monto_total': 80000, 'dias_restantes': 100},
            {'nombre_empresa': 'B', 'tipo': 'Bronce', 'estatus': 'Vigente', 'monto_total': 10000, 'dias_restantes': 100},
            {'nombre_empresa': 'C', 'tipo': 'Bronce', 'estatus': 'Vigente', 'monto_total': 5000, 'dias_restantes': 100},
        ]
        r = analytics_contratos(records)
        insights = [i for i in r.insights if i.key == 'conc_monto_top3']
        assert len(insights) == 1

    def test_single_record(self):
        r = analytics_contratos([self.RECORDS[0]])
        assert r.metrics[0].value == 1

    def test_native_types(self):
        r = analytics_contratos(self.RECORDS)
        for m in r.metrics:
            assert isinstance(m.value, (int, float))


# ============================================================
# BALANCE
# ============================================================

class TestAnalyticsBalance:
    RECORDS = [
        {'nombre_patrocinador': 'A', 'tipo_pago': 'Transferencia', 'monto': 50000, 'fecha_pago': '2026-01-15', 'id_contrato': 1},
        {'nombre_patrocinador': 'A', 'tipo_pago': 'Efectivo', 'monto': 20000, 'fecha_pago': '2026-02-10', 'id_contrato': 1},
        {'nombre_patrocinador': 'B', 'tipo_pago': 'Transferencia', 'monto': 80000, 'fecha_pago': '2026-03-05', 'id_contrato': 2},
        {'nombre_patrocinador': 'C', 'tipo_pago': 'Efectivo', 'monto': 15000, 'fecha_pago': '2026-04-20', 'id_contrato': 3},
    ]

    def test_empty(self):
        r = analytics_balance([])
        assert r.metrics == []

    def test_total_pagos(self):
        r = analytics_balance(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total_pagos')
        assert m.value == 4

    def test_monto_total(self):
        r = analytics_balance(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'monto_total')
        assert m.value == 165000

    def test_distribuciones(self):
        r = analytics_balance(self.RECORDS)
        assert len(r.distributions) == 2

    def test_rankings(self):
        r = analytics_balance(self.RECORDS)
        assert len(r.rankings) == 2

    def test_tendencias(self):
        r = analytics_balance(self.RECORDS)
        assert len(r.trends) == 2

    def test_insight_concentracion(self):
        records = [
            {'nombre_patrocinador': 'A', 'tipo_pago': 'Transferencia', 'monto': 100000, 'fecha_pago': '2026-01-01', 'id_contrato': 1},
            {'nombre_patrocinador': 'B', 'tipo_pago': 'Efectivo', 'monto': 20000, 'fecha_pago': '2026-01-01', 'id_contrato': 2},
        ]
        r = analytics_balance(records)
        insights = [i for i in r.insights if i.key == 'conc_pago_top1']
        assert len(insights) == 1

    def test_native_types(self):
        r = analytics_balance(self.RECORDS)
        for m in r.metrics:
            assert isinstance(m.value, (int, float))


# ============================================================
# PATROCINADORES
# ============================================================

class TestAnalyticsPatrocinadores:
    RECORDS = [
        {'nombre_empresa': 'A', 'tipo_contrato': 'Vigente', 'estado': 1},
        {'nombre_empresa': 'B', 'tipo_contrato': 'Vigente', 'estado': 1},
        {'nombre_empresa': 'C', 'tipo_contrato': 'Vencido', 'estado': 0},
    ]

    def test_empty(self):
        r = analytics_patrocinadores([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_patrocinadores(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 3

    def test_activos(self):
        r = analytics_patrocinadores(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'activos')
        assert m.value == 2

    def test_inactivos(self):
        r = analytics_patrocinadores(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'inactivos')
        assert m.value == 1

    def test_distribuciones(self):
        r = analytics_patrocinadores(self.RECORDS)
        assert len(r.distributions) == 1


# ============================================================
# MANTENIMIENTO
# ============================================================

class TestAnalyticsMantenimiento:
    RECORDS = [
        {'recurso_nombre': 'PC-01', 'estado': 'en_espera', 'fecha_ingreso': '2026-08-01', 'dias_en_taller': 5},
        {'recurso_nombre': 'PC-02', 'estado': 'en_reparacion', 'fecha_ingreso': '2026-07-15', 'dias_en_taller': 20},
        {'recurso_nombre': 'Video-01', 'estado': 'reparado', 'fecha_ingreso': '2026-06-01', 'dias_en_taller': 10},
        {'recurso_nombre': 'PC-01', 'estado': 'en_espera', 'fecha_ingreso': '2026-08-10', 'dias_en_taller': 2},
    ]

    def test_empty(self):
        r = analytics_mantenimiento([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_mantenimiento(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 4

    def test_en_espera(self):
        r = analytics_mantenimiento(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'en_espera')
        assert m.value == 2

    def test_promedio_dias(self):
        r = analytics_mantenimiento(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'promedio_dias')
        assert m.value == 9.2  # (5+20+10+2)/4 = 9.25, round(9.25,1) = 9.2 (banker's)

    def test_alerta_prolongado(self):
        records = [
            {'recurso_nombre': 'X', 'estado': 'en_espera', 'dias_en_taller': 20},
        ]
        r = analytics_mantenimiento(records)
        alertas = [a for a in r.alerts if a.id == 'mantenimiento_prolongado']
        assert len(alertas) == 1
        assert alertas[0].severity == Severity.WARNING

    def test_no_alerta_corto(self):
        records = [
            {'recurso_nombre': 'X', 'estado': 'en_espera', 'dias_en_taller': 5},
        ]
        r = analytics_mantenimiento(records)
        alertas = [a for a in r.alerts if a.id == 'mantenimiento_prolongado']
        assert len(alertas) == 0


# ============================================================
# TAREAS
# ============================================================

class TestAnalyticsTareas:
    RECORDS = [
        {'nombre_tarea': 'T1', 'estado': 'Pendiente', 'asignado_a': 'Juan', 'fecha_asignacion_tarea': '2026-08-01'},
        {'nombre_tarea': 'T2', 'estado': 'Pendiente', 'asignado_a': 'María', 'fecha_asignacion_tarea': '2026-08-15'},
        {'nombre_tarea': 'T3', 'estado': 'En Progreso', 'asignado_a': 'Juan', 'fecha_asignacion_tarea': '2026-08-10'},
        {'nombre_tarea': 'T4', 'estado': 'Completada', 'asignado_a': 'Pedro', 'fecha_asignacion_tarea': '2026-07-01'},
    ]

    def test_empty(self):
        r = analytics_tareas([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_tareas(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 4

    def test_pendientes(self):
        r = analytics_tareas(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'pendientes')
        assert m.value == 2

    def test_completadas_pct(self):
        r = analytics_tareas(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'completadas_pct')
        assert m.value == 25.0

    def test_alerta_antiguas(self):
        records = [
            {'nombre_tarea': 'T1', 'estado': 'Pendiente', 'asignado_a': 'Juan', 'fecha_asignacion_tarea': '2026-07-01'},
        ]
        r = analytics_tareas(records, today=datetime(2026, 9, 4))
        alertas = [a for a in r.alerts if a.id == 'tareas_antiguas']
        assert len(alertas) == 1


# ============================================================
# PREMIOS
# ============================================================

class TestAnalyticsPremios:
    RECORDS = [
        {'nombre': 'P1', 'patrocinador_nombre': 'A', 'estado': 'entregado', 'cantidad': 100, 'cantidad_entregada': 80, 'fecha_creacion': '2026-01-01'},
        {'nombre': 'P2', 'patrocinador_nombre': 'A', 'estado': 'pendiente', 'cantidad': 50, 'cantidad_entregada': 0, 'fecha_creacion': '2026-02-01'},
        {'nombre': 'P3', 'patrocinador_nombre': 'B', 'estado': 'entregado', 'cantidad': 200, 'cantidad_entregada': 200, 'fecha_creacion': '2026-03-01'},
    ]

    def test_empty(self):
        r = analytics_premios([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_premios(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 3

    def test_tasa_entrega(self):
        r = analytics_premios(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'tasa_entrega')
        # (80+0+200) / (100+50+200) = 280/350 = 80.0%
        assert m.value == 80.0

    def test_brecha(self):
        r = analytics_premios(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'brecha')
        assert m.value == 70

    def test_insight_baja_entrega(self):
        records = [
            {'nombre': 'P1', 'patrocinador_nombre': 'A', 'estado': 'pendiente', 'cantidad': 100, 'cantidad_entregada': 10, 'fecha_creacion': '2026-01-01'},
        ]
        r = analytics_premios(records)
        insights = [i for i in r.insights if i.key == 'baja_entrega']
        assert len(insights) == 1


# ============================================================
# INVENTARIO
# ============================================================

class TestAnalyticsInventario:
    RECORDS = [
        {'nombre': 'PC-01', 'tipo_nombre': 'Equipo de PC', 'estado_nombre': 'Disponible', 'costo': 1500, 'fecha_compra': '2026-01-01'},
        {'nombre': 'PC-02', 'tipo_nombre': 'Equipo de PC', 'estado_nombre': 'Asignado', 'costo': 2000, 'fecha_compra': '2026-02-01'},
        {'nombre': 'Video-01', 'tipo_nombre': 'Equipo de Video', 'estado_nombre': 'Disponible', 'costo': 5000, 'fecha_compra': '2026-03-01'},
    ]

    def test_empty(self):
        r = analytics_inventario([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_inventario(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 3

    def test_costo_total(self):
        r = analytics_inventario(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'costo_total')
        assert m.value == 8500

    def test_costo_promedio(self):
        r = analytics_inventario(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'costo_promedio')
        assert m.value == pytest.approx(2833.33, abs=0.1)

    def test_distribuciones(self):
        r = analytics_inventario(self.RECORDS)
        assert len(r.distributions) == 2


# ============================================================
# GUIONES
# ============================================================

class TestAnalyticsGuiones:
    RECORDS = [
        {'nombre': 'G1', 'estado': 'publicado', 'tiempo_segundos': 3600, 'game': 10, 'pregame': 5, 'creado_en': '2026-01-01'},
        {'nombre': 'G2', 'estado': 'borrador', 'tiempo_segundos': 1800, 'game': 5, 'pregame': 3, 'creado_en': '2026-02-01'},
        {'nombre': 'G3', 'estado': 'publicado', 'tiempo_segundos': 2400, 'game': 8, 'pregame': 4, 'creado_en': '2026-03-01'},
    ]

    def test_empty(self):
        r = analytics_guiones([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_guiones(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 3

    def test_tiempo_total(self):
        r = analytics_guiones(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'tiempo_total')
        assert m.value == 7800

    def test_total_game(self):
        r = analytics_guiones(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total_game')
        assert m.value == 23

    def test_distribuciones(self):
        r = analytics_guiones(self.RECORDS)
        assert len(r.distributions) == 1


# ============================================================
# BITÁCORA
# ============================================================

class TestAnalyticsBitacora:
    RECORDS = [
        {'usuario_nombre': 'Juan', 'tipo_accion': 'create', 'modulo': 'contratos', 'created_at': '2026-01-01'},
        {'usuario_nombre': 'Juan', 'tipo_accion': 'update', 'modulo': 'contratos', 'created_at': '2026-01-01'},
        {'usuario_nombre': 'María', 'tipo_accion': 'delete', 'modulo': 'inventario', 'created_at': '2026-02-01'},
        {'usuario_nombre': 'Pedro', 'tipo_accion': 'create', 'modulo': 'contratos', 'created_at': '2026-03-01'},
    ]

    def test_empty(self):
        r = analytics_bitacora([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_bitacora(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 4

    def test_creaciones(self):
        r = analytics_bitacora(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'creaciones')
        assert m.value == 2

    def test_distribuciones(self):
        r = analytics_bitacora(self.RECORDS)
        assert len(r.distributions) == 3

    def test_rankings(self):
        r = analytics_bitacora(self.RECORDS)
        assert len(r.rankings) == 2

    def test_insight_modulo_dominante(self):
        r = analytics_bitacora(self.RECORDS)
        insights = [i for i in r.insights if i.key == 'mod_dominante']
        assert len(insights) == 1


# ============================================================
# USUARIOS
# ============================================================

class TestAnalyticsUsuarios:
    RECORDS = [
        {'nombre': 'Juan', 'rol': 'Admin', 'departamento': 'Técnica', 'activo': 1},
        {'nombre': 'María', 'rol': 'Usuario', 'departamento': 'Comercial', 'activo': 1},
        {'nombre': 'Pedro', 'rol': 'Usuario', 'departamento': 'Técnica', 'activo': 0},
    ]

    def test_empty(self):
        r = analytics_usuarios([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_usuarios(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 3

    def test_activos(self):
        r = analytics_usuarios(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'activos')
        assert m.value == 2

    def test_distribuciones(self):
        r = analytics_usuarios(self.RECORDS)
        assert len(r.distributions) == 2


# ============================================================
# REELS
# ============================================================

class TestAnalyticsReels:
    RECORDS = [
        {'nombre': 'R1', 'patrocinado': 'A', 'duracion_total': 5.5, 'videos_count': 8, 'creado_en': '2026-01-01'},
        {'nombre': 'R2', 'patrocinado': 'B', 'duracion_total': 3.2, 'videos_count': 5, 'creado_en': '2026-02-01'},
    ]

    def test_empty(self):
        r = analytics_reels([])
        assert r.metrics == []

    def test_total(self):
        r = analytics_reels(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total')
        assert m.value == 2

    def test_total_videos(self):
        r = analytics_reels(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'total_videos')
        assert m.value == 13

    def test_duracion_total(self):
        r = analytics_reels(self.RECORDS)
        m = next(m for m in r.metrics if m.key == 'duracion_total')
        assert m.value == 522.0  # (5.5 + 3.2) * 60

    def test_distribuciones(self):
        r = analytics_reels(self.RECORDS)
        assert len(r.distributions) == 1


# ============================================================
# RUN_ANALYTICS (dispatcher)
# ============================================================

class TestRunAnalytics:
    def test_unknown_module(self):
        r = run_analytics('unknown', [{'x': 1}])
        assert r.module == 'unknown'
        assert r.metrics == []

    def test_contratos(self):
        r = run_analytics('contratos', [
            {'nombre_empresa': 'A', 'estatus': 'Vigente', 'monto_total': 10000, 'dias_restantes': 100}
        ])
        assert r.module == 'contratos'
        assert len(r.metrics) > 0

    def test_empty_records(self):
        r = run_analytics('balance', [])
        assert r.metrics == []
