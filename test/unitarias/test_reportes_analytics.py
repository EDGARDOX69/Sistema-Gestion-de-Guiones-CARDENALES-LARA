"""
Tests exhaustivos para motores analíticos reutilizables.
Cubre: agregaciones, tendencias, comparativas, rankings, distribuciones, umbrales, alertas, AnalyticsResult.
"""
import pytest
from datetime import datetime, timedelta

from app.helpers.reportes_analytics import (
    safe_count, safe_sum, safe_average, safe_min, safe_max,
    safe_percentage, safe_ratio, count_by_field, sum_by_field, group_by,
    compute_trend, compare_periods, compare_dicts,
    compute_ranking, compute_distribution,
    Threshold, ThresholdGroup,
    parse_date, truncate_period,
    filter_by_date_range, filter_by_date_range_exclusive_end, shift_period,
    Direction, Severity,
    Metric, DistributionItem, Distribution, TrendPoint, Trend,
    RankingItem, Ranking, Comparison, Alert, Insight, AnalyticsResult,
    AlertEvidence, AlertRule,
    eval_field_threshold, eval_count_above, eval_percentage_above,
    eval_date_expired, eval_date_expiring, eval_age_above,
    eval_concentration, eval_range_outside,
    eval_and, eval_or,
    deduplicate_alerts, EnhancedAlert,
    register_alert_rules, get_alert_rules, evaluate_module_alerts,
)


# ============================================================
# AGREGACIONES
# ============================================================

class TestSafeCount:
    def test_normal(self):
        assert safe_count([{}, {}, {}]) == 3

    def test_empty(self):
        assert safe_count([]) == 0

    def test_none(self):
        assert safe_count(None) == 0


class TestSafeSum:
    def test_normal(self):
        assert safe_sum([{'v': 10}, {'v': 20}, {'v': 30}], 'v') == 60

    def test_empty(self):
        assert safe_sum([], 'v') == 0

    def test_none_values(self):
        assert safe_sum([{'v': 10}, {'v': None}, {'v': 20}], 'v') == 30

    def test_missing_field(self):
        assert safe_sum([{'x': 1}, {'x': 2}], 'v') == 0

    def test_string_numeric(self):
        assert safe_sum([{'v': '10'}, {'v': '20'}], 'v') == 30

    def test_invalid_strings(self):
        assert safe_sum([{'v': 'abc'}, {'v': 10}], 'v') == 10

    def test_decimal(self):
        from decimal import Decimal
        assert safe_sum([{'v': Decimal('10.5')}, {'v': Decimal('20.3')}], 'v') == pytest.approx(30.8)


class TestSafeAverage:
    def test_normal(self):
        assert safe_average([{'v': 10}, {'v': 20}, {'v': 30}], 'v') == 20

    def test_empty(self):
        assert safe_average([], 'v') == 0

    def test_single(self):
        assert safe_average([{'v': 42}], 'v') == 42

    def test_none_excluded(self):
        assert safe_average([{'v': 10}, {'v': None}, {'v': 20}], 'v') == 15

    def test_all_none(self):
        assert safe_average([{'v': None}, {'v': None}], 'v') == 0


class TestSafeMinMax:
    def test_min_normal(self):
        assert safe_min([{'v': 30}, {'v': 10}, {'v': 20}], 'v') == 10

    def test_max_normal(self):
        assert safe_max([{'v': 30}, {'v': 10}, {'v': 20}], 'v') == 30

    def test_min_empty(self):
        assert safe_min([], 'v') is None

    def test_max_empty(self):
        assert safe_max([], 'v') is None

    def test_min_none_values(self):
        assert safe_min([{'v': None}, {'v': 10}], 'v') == 10

    def test_max_none_values(self):
        assert safe_max([{'v': None}, {'v': 10}], 'v') == 10


class TestSafePercentage:
    def test_normal(self):
        assert safe_percentage(3, 10) == 30.0

    def test_zero_total(self):
        assert safe_percentage(3, 0) == 0.0

    def test_zero_part(self):
        assert safe_percentage(0, 10) == 0.0

    def test_full(self):
        assert safe_percentage(10, 10) == 100.0

    def test_negative(self):
        assert safe_percentage(-5, 10) == -50.0


class TestSafeRatio:
    def test_normal(self):
        assert safe_ratio(3, 10) == 0.3

    def test_zero_denominator(self):
        assert safe_ratio(3, 0) == 0.0

    def test_zero_numerator(self):
        assert safe_ratio(0, 10) == 0.0


class TestCountByField:
    def test_normal(self):
        recs = [{'estado': 'A'}, {'estado': 'B'}, {'estado': 'A'}]
        result = count_by_field(recs, 'estado')
        assert result == {'A': 2, 'B': 1}

    def test_empty(self):
        assert count_by_field([], 'x') == {}

    def test_missing_field(self):
        recs = [{'x': 1}, {}]
        result = count_by_field(recs, 'estado')
        assert result == {'—': 2}


class TestSumByField:
    def test_normal(self):
        recs = [{'tipo': 'A', 'monto': 100}, {'tipo': 'B', 'monto': 200}, {'tipo': 'A', 'monto': 50}]
        result = sum_by_field(recs, 'tipo', 'monto')
        assert result == {'A': 150, 'B': 200}

    def test_empty(self):
        assert sum_by_field([], 'x', 'v') == {}


class TestGroupBy:
    def test_normal(self):
        recs = [{'tipo': 'A'}, {'tipo': 'B'}, {'tipo': 'A'}]
        result = group_by(recs, 'tipo')
        assert len(result['A']) == 2
        assert len(result['B']) == 1

    def test_empty(self):
        assert group_by([], 'x') == {}


# ============================================================
# FECHAS
# ============================================================

class TestParseDate:
    def test_datetime(self):
        dt = datetime(2026, 1, 15, 10, 30)
        assert parse_date(dt) == dt

    def test_string_ymd(self):
        assert parse_date('2026-01-15') == datetime(2026, 1, 15, 0, 0)

    def test_string_ymd_hms(self):
        assert parse_date('2026-01-15 10:30:00') == datetime(2026, 1, 15, 10, 30)

    def test_string_dmy(self):
        assert parse_date('15/01/2026') == datetime(2026, 1, 15, 0, 0)

    def test_none(self):
        assert parse_date(None) is None

    def test_empty(self):
        assert parse_date('') is None

    def test_invalid(self):
        assert parse_date('not-a-date') is None


class TestTruncatePeriod:
    def test_day(self):
        dt = datetime(2026, 3, 15, 14, 30)
        assert truncate_period(dt, 'day') == '2026-03-15'

    def test_week(self):
        dt = datetime(2026, 3, 15)  # Sunday
        result = truncate_period(dt, 'week')
        assert '2026' in result
        assert 'W' in result

    def test_month(self):
        dt = datetime(2026, 3, 15)
        assert truncate_period(dt, 'month') == '2026-03'


class TestFilterByDateRange:
    def test_inclusive(self):
        recs = [
            {'f': '2026-01-10'},
            {'f': '2026-01-15'},
            {'f': '2026-01-20'},
        ]
        result = filter_by_date_range(recs, 'f', '2026-01-10', '2026-01-15')
        assert len(result) == 2

    def test_exclusive_end(self):
        recs = [
            {'f': '2026-01-10'},
            {'f': '2026-01-15'},
            {'f': '2026-01-20'},
        ]
        result = filter_by_date_range_exclusive_end(recs, 'f', '2026-01-10', '2026-01-15')
        assert len(result) == 2  # 10 and 15 included (15 < 16)

    def test_none_date_kept(self):
        recs = [{'f': None}, {'f': '2026-01-15'}]
        result = filter_by_date_range(recs, 'f', '2026-01-10', '2026-01-20')
        assert len(result) == 2


class TestShiftPeriod:
    def test_normal(self):
        s, e = shift_period('2026-01-01', '2026-01-31')
        assert s == datetime(2025, 12, 2)
        assert e == datetime(2025, 12, 31)

    def test_none(self):
        s, e = shift_period(None, '2026-01-31')
        assert s is None
        assert e is None


# ============================================================
# TENDENCIAS
# ============================================================

class TestComputeTrend:
    def test_empty_records(self):
        trend = compute_trend([], 'fecha')
        assert trend.data == []

    def test_count_monthly(self):
        recs = [
            {'fecha': '2026-01-10'}, {'fecha': '2026-01-15'}, {'fecha': '2026-01-20'},
            {'fecha': '2026-02-05'}, {'fecha': '2026-02-15'},
        ]
        trend = compute_trend(recs, 'fecha', granularity='month')
        assert len(trend.data) == 2
        assert trend.data[0].period == '2026-01'
        assert trend.data[0].value == 3
        assert trend.data[0].previous_value is None
        assert trend.data[1].period == '2026-02'
        assert trend.data[1].value == 2
        assert trend.data[1].absolute_change == -1
        assert trend.data[1].percentage_change == pytest.approx(-33.33, abs=0.1)

    def test_sum_monthly(self):
        recs = [
            {'fecha': '2026-01-10', 'monto': 100},
            {'fecha': '2026-01-20', 'monto': 200},
            {'fecha': '2026-02-05', 'monto': 150},
        ]
        trend = compute_trend(recs, 'fecha', 'monto', aggregation='sum', granularity='month')
        assert trend.data[0].value == 300
        assert trend.data[1].value == 150
        assert trend.data[1].absolute_change == -150
        assert trend.data[1].percentage_change == pytest.approx(-50.0)

    def test_avg_monthly(self):
        recs = [
            {'fecha': '2026-01-10', 'v': 10},
            {'fecha': '2026-01-20', 'v': 20},
        ]
        trend = compute_trend(recs, 'fecha', 'v', aggregation='avg', granularity='month')
        assert trend.data[0].value == 15

    def test_daily(self):
        recs = [{'fecha': '2026-01-10'}, {'fecha': '2026-01-10'}, {'fecha': '2026-01-11'}]
        trend = compute_trend(recs, 'fecha', granularity='day')
        assert len(trend.data) == 2
        assert trend.data[0].value == 2
        assert trend.data[1].value == 1

    def test_weekly(self):
        recs = [{'fecha': '2026-01-05'}, {'fecha': '2026-01-06'}, {'fecha': '2026-01-12'}]
        trend = compute_trend(recs, 'fecha', granularity='week')
        assert len(trend.data) >= 2

    def test_invalid_dates_skipped(self):
        recs = [{'fecha': '2026-01-10'}, {'fecha': 'invalid'}, {'fecha': None}]
        trend = compute_trend(recs, 'fecha', granularity='month')
        assert len(trend.data) == 1
        assert trend.data[0].value == 1

    def test_percentage_change_zero_previous(self):
        recs = [
            {'fecha': '2026-01-10', 'v': 0},
            {'fecha': '2026-02-10', 'v': 10},
        ]
        trend = compute_trend(recs, 'fecha', 'v', aggregation='sum', granularity='month')
        assert trend.data[1].percentage_change is None

    def test_single_period(self):
        recs = [{'fecha': '2026-01-10'}]
        trend = compute_trend(recs, 'fecha', granularity='month')
        assert len(trend.data) == 1
        assert trend.data[0].absolute_change is None

    def test_datetime_objects(self):
        recs = [
            {'fecha': datetime(2026, 1, 10)},
            {'fecha': datetime(2026, 1, 20)},
        ]
        trend = compute_trend(recs, 'fecha', granularity='month')
        assert len(trend.data) == 1
        assert trend.data[0].value == 2


# ============================================================
# COMPARATIVAS
# ============================================================

class TestComparePeriods:
    def test_increase(self):
        c = compare_periods('total', 100, 80)
        assert c.current == 100
        assert c.previous == 80
        assert c.absolute_change == 20
        assert c.percentage_change == pytest.approx(25.0)
        assert c.direction == Direction.UP

    def test_decrease(self):
        c = compare_periods('total', 60, 100)
        assert c.absolute_change == -40
        assert c.percentage_change == pytest.approx(-40.0)
        assert c.direction == Direction.DOWN

    def test_unchanged(self):
        c = compare_periods('total', 50, 50)
        assert c.absolute_change == 0
        assert c.direction == Direction.UNCHANGED

    def test_zero_previous(self):
        c = compare_periods('total', 10, 0)
        assert c.absolute_change == 10
        assert c.percentage_change is None
        assert c.direction == Direction.UP

    def test_both_zero(self):
        c = compare_periods('total', 0, 0)
        assert c.direction == Direction.UNCHANGED

    def test_none_current(self):
        c = compare_periods('total', None, 50)
        assert c.direction == Direction.NOT_COMPARABLE

    def test_none_previous(self):
        c = compare_periods('total', 50, None)
        assert c.direction == Direction.NOT_COMPARABLE

    def test_string_numeric(self):
        c = compare_periods('total', '100', '80')
        assert c.current == 100
        assert c.previous == 80
        assert c.direction == Direction.UP


class TestCompareDicts:
    def test_normal(self):
        curr = {'a': 10, 'b': 20}
        prev = {'a': 8, 'b': 25}
        results = compare_dicts(curr, prev)
        assert len(results) == 2
        assert results[0].direction == Direction.UP
        assert results[1].direction == Direction.DOWN

    def test_skip_keys(self):
        curr = {'a': 10, 'b': 20, 'c': 30}
        prev = {'a': 8, 'b': 25, 'c': 30}
        results = compare_dicts(curr, prev, skip_keys={'b'})
        assert len(results) == 2

    def test_missing_in_prev(self):
        curr = {'a': 10, 'b': 20}
        prev = {'a': 8}
        results = compare_dicts(curr, prev)
        assert len(results) == 1


# ============================================================
# RANKINGS
# ============================================================

class TestComputeRanking:
    def test_count_desc(self):
        recs = [{'p': 'A'}, {'p': 'A'}, {'p': 'B'}, {'p': 'C'}, {'p': 'C'}, {'p': 'C'}]
        r = compute_ranking(recs, 'p')
        assert len(r.items) == 3
        assert r.items[0].item == 'C'
        assert r.items[0].value == 3
        assert r.items[0].position == 1
        assert r.items[1].item == 'A'
        assert r.items[1].value == 2
        assert r.items[2].item == 'B'
        assert r.items[2].value == 1

    def test_sum_desc(self):
        recs = [
            {'p': 'A', 'v': 100}, {'p': 'B', 'v': 300}, {'p': 'A', 'v': 50},
        ]
        r = compute_ranking(recs, 'p', 'v', aggregation='sum')
        assert r.items[0].item == 'B'
        assert r.items[0].value == 300
        assert r.items[1].item == 'A'
        assert r.items[1].value == 150

    def test_top_n(self):
        recs = [{'p': 'A'}, {'p': 'B'}, {'p': 'C'}, {'p': 'D'}]
        r = compute_ranking(recs, 'p', top_n=2)
        assert len(r.items) == 2

    def test_bottom_n(self):
        recs = [{'p': 'A'}, {'p': 'B'}, {'p': 'C'}, {'p': 'D'}]
        r = compute_ranking(recs, 'p', bottom_n=2)
        assert len(r.items) == 2

    def test_asc(self):
        recs = [{'p': 'A'}, {'p': 'A'}, {'p': 'B'}]
        r = compute_ranking(recs, 'p', order='asc')
        assert r.items[0].item == 'B'
        assert r.items[1].item == 'A'

    def test_empty(self):
        r = compute_ranking([], 'p')
        assert r.items == []

    def test_top_n_exceeds(self):
        recs = [{'p': 'A'}]
        r = compute_ranking(recs, 'p', top_n=10)
        assert len(r.items) == 1

    def test_avg(self):
        recs = [
            {'p': 'A', 'v': 10}, {'p': 'A', 'v': 20},
            {'p': 'B', 'v': 100},
        ]
        r = compute_ranking(recs, 'p', 'v', aggregation='avg')
        assert r.items[0].item == 'B'
        assert r.items[0].value == 100
        assert r.items[1].item == 'A'
        assert r.items[1].value == pytest.approx(15)


# ============================================================
# DISTRIBUCIONES
# ============================================================

class TestComputeDistribution:
    def test_normal(self):
        recs = [{'e': 'A'}, {'e': 'A'}, {'e': 'B'}, {'e': 'C'}, {'e': 'C'}, {'e': 'C'}]
        d = compute_distribution(recs, 'e')
        assert d.total == 6
        assert len(d.items) == 3
        assert d.items[0].category == 'C'
        assert d.items[0].count == 3
        assert d.items[0].percentage == pytest.approx(50.0, abs=0.1)

    def test_empty(self):
        d = compute_distribution([], 'e')
        assert d.total == 0
        assert d.items == []

    def test_single_category(self):
        recs = [{'e': 'A'}, {'e': 'A'}]
        d = compute_distribution(recs, 'e')
        assert d.items[0].percentage == 100.0

    def test_missing_field(self):
        recs = [{'x': 1}, {}]
        d = compute_distribution(recs, 'e')
        assert d.items[0].category == '—'
        assert d.items[0].count == 2


# ============================================================
# UMBRALES
# ============================================================

class TestThreshold:
    def test_gt(self):
        t = Threshold('high', 'v', 'gt', 10)
        assert t.evaluate({'v': 15}) is True
        assert t.evaluate({'v': 5}) is False
        assert t.evaluate({'v': 10}) is False

    def test_lte(self):
        t = Threshold('low', 'v', 'lte', 5)
        assert t.evaluate({'v': 5}) is True
        assert t.evaluate({'v': 3}) is True
        assert t.evaluate({'v': 10}) is False

    def test_none_value(self):
        t = Threshold('x', 'v', 'gt', 10)
        assert t.evaluate({'v': None}) is False

    def test_missing_field(self):
        t = Threshold('x', 'v', 'gt', 10)
        assert t.evaluate({'x': 1}) is False

    def test_string_value(self):
        t = Threshold('x', 'v', 'gt', 10)
        assert t.evaluate({'v': '15'}) is True

    def test_eq(self):
        t = Threshold('x', 'v', 'eq', 10)
        assert t.evaluate({'v': 10}) is True
        assert t.evaluate({'v': 11}) is False

    def test_neq(self):
        t = Threshold('x', 'v', 'neq', 10)
        assert t.evaluate({'v': 11}) is True
        assert t.evaluate({'v': 10}) is False


class TestThresholdGroup:
    def test_alerts_generated(self):
        tg = ThresholdGroup([
            Threshold('high', 'v', 'gt', 10, Severity.WARNING),
            Threshold('low', 'v', 'lt', 5, Severity.INFO),
        ])
        recs = [{'v': 15}, {'v': 3}, {'v': 8}]
        alerts = tg.evaluate(recs)
        assert len(alerts) == 2
        assert alerts[0].affected_count == 1
        assert alerts[1].affected_count == 1

    def test_no_alerts(self):
        tg = ThresholdGroup([Threshold('high', 'v', 'gt', 100)])
        alerts = tg.evaluate([{'v': 10}, {'v': 20}])
        assert alerts == []

    def test_empty_records(self):
        tg = ThresholdGroup([Threshold('high', 'v', 'gt', 10)])
        alerts = tg.evaluate([])
        assert alerts == []


# ============================================================
# ANALYTICSRESULT
# ============================================================

class TestAnalyticsResult:
    def test_add_metric(self):
        r = AnalyticsResult('test')
        r.add_metric('total', 'Total', 42)
        assert len(r.metrics) == 1
        assert r.metrics[0].key == 'total'
        assert r.metrics[0].value == 42

    def test_add_distribution(self):
        from app.helpers.reportes_analytics import DistributionItem
        r = AnalyticsResult('test')
        items = [DistributionItem('A', 5, 50.0)]
        r.add_distribution('dist', 'Dist', items, 10)
        assert len(r.distributions) == 1

    def test_add_trend(self):
        r = AnalyticsResult('test')
        points = [TrendPoint('2026-01', 10)]
        r.add_trend('t', 'Trend', points)
        assert len(r.trends) == 1

    def test_add_ranking(self):
        r = AnalyticsResult('test')
        items = [RankingItem('A', 100, 1)]
        r.add_ranking('r', 'Ranking', items)
        assert len(r.rankings) == 1

    def test_add_comparison(self):
        r = AnalyticsResult('test')
        r.add_comparison('total', 100, 80)
        assert len(r.comparisons) == 1
        assert r.comparisons[0].direction == Direction.UP

    def test_add_alert(self):
        r = AnalyticsResult('test')
        r.add_alert('a1', 'test', Severity.WARNING, 'Alert', 'Desc', 5)
        assert len(r.alerts) == 1

    def test_add_insight(self):
        r = AnalyticsResult('test')
        r.add_insight('i1', 'Some insight')
        assert len(r.insights) == 1

    def test_to_dict(self):
        r = AnalyticsResult('test')
        r.add_metric('m', 'M', 1)
        d = r.to_dict()
        assert d['module'] == 'test'
        assert len(d['metrics']) == 1
        assert d['metrics'][0]['value'] == 1

    def test_empty_result(self):
        r = AnalyticsResult('test')
        d = r.to_dict()
        assert d['metrics'] == []
        assert d['distributions'] == []
        assert d['trends'] == []
        assert d['rankings'] == []
        assert d['comparisons'] == []
        assert d['alerts'] == []
        assert d['insights'] == []


# ============================================================
# CONTRATOS DE DATOS (to_dict)
# ============================================================

class TestContracts:
    def test_metric_to_dict(self):
        m = Metric('k', 'Label', 42, 'count', 'f', ['f1'], 2)
        d = m.to_dict()
        assert d['key'] == 'k'
        assert d['precision'] == 2

    def test_distribution_to_dict(self):
        items = [DistributionItem('A', 5, 50.0)]
        dist = Distribution('d', 'Dist', items, 10)
        d = dist.to_dict()
        assert d['total'] == 10
        assert d['items'][0]['category'] == 'A'

    def test_trend_to_dict(self):
        points = [TrendPoint('2026-01', 10, 8, 2, 25.0)]
        t = Trend('t', 'Trend', points)
        d = t.to_dict()
        assert d['data'][0]['percentage_change'] == 25.0

    def test_ranking_to_dict(self):
        items = [RankingItem('A', 100, 1)]
        r = Ranking('r', 'Rank', items)
        d = r.to_dict()
        assert d['items'][0]['position'] == 1

    def test_comparison_to_dict(self):
        c = Comparison('ind', 100, 80, 20, 25.0, Direction.UP)
        d = c.to_dict()
        assert d['direction'] == 'up'

    def test_alert_to_dict(self):
        a = Alert('id', 'mod', Severity.CRITICAL, 'Title', 'Desc', count=5, data=[{'x': 1}])
        d = a.to_dict()
        assert d['severity'] == 'CRITICAL'
        assert d['affected_count'] == 5
        assert len(d['data']) == 1

    def test_insight_to_dict(self):
        i = Insight('k', 'text', Severity.WARNING)
        d = i.to_dict()
        assert d['severity'] == 'WARNING'


# ============================================================
# ALERTAS - EVALUADORES GENÉRICOS
# ============================================================

class TestEvalFieldThreshold:
    def test_gt_triggered(self):
        ev = eval_field_threshold('v', 'gt', 10, Severity.WARNING)
        alerts = ev([{'v': 15}, {'v': 5}, {'v': 20}])
        assert len(alerts) == 1
        assert alerts[0].affected_count == 2

    def test_gt_not_triggered(self):
        ev = eval_field_threshold('v', 'gt', 10)
        alerts = ev([{'v': 5}, {'v': 8}])
        assert alerts == []

    def test_lte_triggered(self):
        ev = eval_field_threshold('v', 'lte', 7)
        alerts = ev([{'v': 5}, {'v': 7}, {'v': 8}])
        assert len(alerts) == 1
        assert alerts[0].affected_count == 2

    def test_lte_boundary(self):
        ev = eval_field_threshold('v', 'lte', 7)
        alerts = ev([{'v': 7}])
        assert len(alerts) == 1

    def test_none_values_skipped(self):
        ev = eval_field_threshold('v', 'gt', 10)
        alerts = ev([{'v': None}, {'x': 1}])
        assert alerts == []

    def test_empty_records(self):
        ev = eval_field_threshold('v', 'gt', 10)
        alerts = ev([])
        assert alerts == []

    def test_eq(self):
        ev = eval_field_threshold('v', 'eq', 10)
        alerts = ev([{'v': 10}, {'v': 11}])
        assert len(alerts) == 1
        assert alerts[0].affected_count == 1

    def test_neq(self):
        ev = eval_field_threshold('v', 'neq', 10)
        alerts = ev([{'v': 10}, {'v': 11}])
        assert len(alerts) == 1
        assert alerts[0].affected_count == 1

    def test_invalid_operator(self):
        ev = eval_field_threshold('v', 'invalid', 10)
        alerts = ev([{'v': 15}])
        assert alerts == []


class TestEvalCountAbove:
    def test_triggered(self):
        ev = eval_count_above(5)
        alerts = ev([{'x': 1}] * 8)
        assert len(alerts) == 1
        assert alerts[0].value == 8

    def test_not_triggered(self):
        ev = eval_count_above(10)
        alerts = ev([{'x': 1}] * 5)
        assert alerts == []

    def test_exact_threshold(self):
        ev = eval_count_above(5)
        alerts = ev([{'x': 1}] * 5)
        assert alerts == []

    def test_empty(self):
        ev = eval_count_above(5)
        alerts = ev([])
        assert alerts == []


class TestEvalPercentageAbove:
    def test_triggered(self):
        ev = eval_percentage_above('completadas', 'total', 80)
        alerts = ev([{'completadas': 85, 'total': 100}])
        assert len(alerts) == 1
        assert alerts[0].value == 85.0

    def test_not_triggered(self):
        ev = eval_percentage_above('completadas', 'total', 80)
        alerts = ev([{'completadas': 79, 'total': 100}])
        assert alerts == []

    def test_exact_threshold(self):
        ev = eval_percentage_above('completadas', 'total', 80)
        alerts = ev([{'completadas': 80, 'total': 100}])
        assert alerts == []

    def test_zero_denominator(self):
        ev = eval_percentage_above('completadas', 'total', 80)
        alerts = ev([{'completadas': 10, 'total': 0}])
        assert alerts == []


class TestEvalDateExpired:
    def test_triggered(self):
        today = datetime(2026, 9, 4)
        ev = eval_date_expired('fecha_fin')
        alerts = ev([{'fecha_fin': '2026-08-01'}, {'fecha_fin': '2026-10-01'}], today=today)
        assert len(alerts) == 1
        assert alerts[0].affected_count == 1

    def test_not_triggered(self):
        today = datetime(2026, 9, 4)
        ev = eval_date_expired('fecha_fin')
        alerts = ev([{'fecha_fin': '2026-12-01'}], today=today)
        assert alerts == []

    def test_invalid_date_skipped(self):
        today = datetime(2026, 9, 4)
        ev = eval_date_expired('fecha_fin')
        alerts = ev([{'fecha_fin': None}, {'fecha_fin': 'invalid'}], today=today)
        assert alerts == []


class TestEvalDateExpiring:
    def test_triggered_within_days(self):
        today = datetime(2026, 9, 4)
        ev = eval_date_expiring('fecha_fin', 30)
        alerts = ev([{'fecha_fin': '2026-09-20'}], today=today)
        assert len(alerts) == 1
        assert alerts[0].affected_count == 1

    def test_not_triggered_beyond_days(self):
        today = datetime(2026, 9, 4)
        ev = eval_date_expiring('fecha_fin', 7)
        alerts = ev([{'fecha_fin': '2026-09-20'}], today=today)
        assert alerts == []

    def test_boundary_exactly_today(self):
        today = datetime(2026, 9, 4)
        ev = eval_date_expiring('fecha_fin', 30)
        alerts = ev([{'fecha_fin': '2026-09-04'}], today=today)
        assert len(alerts) == 1

    def test_boundary_exactly_at_limit(self):
        today = datetime(2026, 9, 4)
        ev = eval_date_expiring('fecha_fin', 7)
        alerts = ev([{'fecha_fin': '2026-09-11'}], today=today)
        assert len(alerts) == 1


class TestEvalAgeAbove:
    def test_triggered(self):
        today = datetime(2026, 9, 4)
        ev = eval_age_above('fecha_asignacion', 14)
        alerts = ev([{'fecha_asignacion': '2026-08-01'}], today=today)
        assert len(alerts) == 1
        assert alerts[0].affected_count == 1

    def test_not_triggered(self):
        today = datetime(2026, 9, 4)
        ev = eval_age_above('fecha_asignacion', 30)
        alerts = ev([{'fecha_asignacion': '2026-08-20'}], today=today)
        assert alerts == []

    def test_adds_age_days(self):
        today = datetime(2026, 9, 4)
        ev = eval_age_above('fecha', 10)
        alerts = ev([{'fecha': '2026-08-01'}], today=today)
        assert alerts[0].evidence.sample_records[0]['_age_days'] == 34


class TestEvalConcentration:
    def test_triggered(self):
        ev = eval_concentration('patrocinador', 'monto', 2, 60)
        alerts = ev([
            {'patrocinador': 'A', 'monto': 100},
            {'patrocinador': 'A', 'monto': 50},
            {'patrocinador': 'B', 'monto': 80},
            {'patrocinador': 'C', 'monto': 10},
        ])
        assert len(alerts) == 1
        # A=150, B=80, total=240; top2=230/240=95.8%
        assert alerts[0].value == 95.8

    def test_not_triggered(self):
        ev = eval_concentration('patrocinador', 'monto', 2, 80)
        alerts = ev([
            {'patrocinador': 'A', 'monto': 100},
            {'patrocinador': 'B', 'monto': 100},
            {'patrocinador': 'C', 'monto': 100},
        ])
        assert alerts == []

    def test_empty(self):
        ev = eval_concentration('p', 'v', 2, 60)
        alerts = ev([])
        assert alerts == []


class TestEvalRangeOutside:
    def test_triggered_below(self):
        ev = eval_range_outside('v', min_val=10, max_val=100)
        alerts = ev([{'v': 5}, {'v': 50}])
        assert len(alerts) == 1
        assert alerts[0].affected_count == 1

    def test_triggered_above(self):
        ev = eval_range_outside('v', min_val=10, max_val=100)
        alerts = ev([{'v': 150}])
        assert len(alerts) == 1

    def test_not_triggered(self):
        ev = eval_range_outside('v', min_val=10, max_val=100)
        alerts = ev([{'v': 50}, {'v': 100}])
        assert alerts == []

    def test_only_min(self):
        ev = eval_range_outside('v', min_val=10)
        alerts = ev([{'v': 5}])
        assert len(alerts) == 1

    def test_only_max(self):
        ev = eval_range_outside('v', max_val=100)
        alerts = ev([{'v': 150}])
        assert len(alerts) == 1


# ============================================================
# ALERTAS COMPUESTAS
# ============================================================

class TestEvalAnd:
    def test_all_triggered(self):
        ev1 = eval_field_threshold('a', 'gt', 5)
        ev2 = eval_field_threshold('b', 'gt', 5)
        ev = eval_and(ev1, ev2)
        alerts = ev([{'a': 10, 'b': 10}])
        assert len(alerts) == 2

    def test_partial_triggered(self):
        ev1 = eval_field_threshold('a', 'gt', 5)
        ev2 = eval_field_threshold('b', 'gt', 5)
        ev = eval_and(ev1, ev2)
        alerts = ev([{'a': 10, 'b': 3}])
        assert alerts == []


class TestEvalOr:
    def test_one_triggered(self):
        ev1 = eval_field_threshold('a', 'gt', 5)
        ev2 = eval_field_threshold('b', 'gt', 5)
        ev = eval_or(ev1, ev2)
        alerts = ev([{'a': 10, 'b': 3}])
        assert len(alerts) == 1

    def test_both_triggered(self):
        ev1 = eval_field_threshold('a', 'gt', 5)
        ev2 = eval_field_threshold('b', 'gt', 5)
        ev = eval_or(ev1, ev2)
        alerts = ev([{'a': 10, 'b': 10}])
        assert len(alerts) == 2

    def test_none_triggered(self):
        ev1 = eval_field_threshold('a', 'gt', 5)
        ev2 = eval_field_threshold('b', 'gt', 5)
        ev = eval_or(ev1, ev2)
        alerts = ev([{'a': 3, 'b': 3}])
        assert alerts == []


# ============================================================
# DEDUPLICACIÓN
# ============================================================

class TestDeduplicateAlerts:
    def test_no_duplicates(self):
        alerts = [
            Alert('a1', '', Severity.WARNING, 'A', 'desc', count=1),
            Alert('a2', '', Severity.WARNING, 'B', 'desc', count=2),
        ]
        result = deduplicate_alerts(alerts)
        assert len(result) == 2

    def test_duplicates(self):
        alerts = [
            Alert('a1', '', Severity.WARNING, 'A', 'desc', count=1),
            Alert('a1', '', Severity.WARNING, 'A', 'desc2', count=5),
        ]
        result = deduplicate_alerts(alerts)
        assert len(result) == 1
        assert result[0].affected_count == 5

    def test_different_modules(self):
        alerts = [
            Alert('a1', 'mod1', Severity.WARNING, 'A', 'desc', count=1),
            Alert('a1', 'mod2', Severity.WARNING, 'A', 'desc', count=2),
        ]
        result = deduplicate_alerts(alerts)
        assert len(result) == 2


# ============================================================
# EVIDENCIA
# ============================================================

class TestAlertEvidence:
    def test_basic(self):
        e = AlertEvidence(5, [{'id': 1}, {'id': 2}])
        d = e.to_dict()
        assert d['affected_count'] == 5
        assert len(d['sample_records']) == 2

    def test_with_aggregate(self):
        e = AlertEvidence(10, aggregate_value=75.5, aggregate_field='pct')
        d = e.to_dict()
        assert d['aggregate_value'] == 75.5
        assert d['aggregate_field'] == 'pct'


# ============================================================
# REGISTRO DE REGLAS
# ============================================================

class TestAlertRulesRegistry:
    def test_register_and_get(self):
        rule = AlertRule('test', 'test_module', 'Test', 'desc', Severity.INFO, lambda r, today=None: [])
        register_alert_rules('test_module', [rule])
        rules = get_alert_rules('test_module')
        assert len(rules) == 1
        assert rules[0].id == 'test'

    def test_unknown_module(self):
        rules = get_alert_rules('nonexistent')
        assert rules == []


class TestEvaluateModuleAlerts:
    def test_with_rules(self):
        rule = AlertRule('r1', 'm', 'R1', 'desc', Severity.WARNING,
                        eval_field_threshold('v', 'gt', 10))
        register_alert_rules('test_eval', [rule])
        alerts = evaluate_module_alerts('test_eval', [{'v': 15}, {'v': 5}])
        assert len(alerts) == 1
        assert alerts[0].module == 'test_eval'

    def test_no_rules(self):
        alerts = evaluate_module_alerts('nonexistent', [{'v': 15}])
        assert alerts == []


# ============================================================
# ALERT CON NUEVOS CAMPOS
# ============================================================

class TestAlertEnhanced:
    def test_backward_compatible(self):
        a = Alert('id', 'mod', Severity.WARNING, 'Title', 'Desc', count=5)
        assert a.value == 5
        assert a.affected_count == 5

    def test_new_fields(self):
        e = AlertEvidence(3)
        a = Alert('id', 'mod', Severity.CRITICAL, 'Title', 'Desc',
                  value=10, threshold=7, unit='days', affected_count=10, evidence=e)
        d = a.to_dict()
        assert d['value'] == 10
        assert d['threshold'] == 7
        assert d['unit'] == 'days'
        assert d['affected_count'] == 10
        assert d['evidence']['affected_count'] == 3

    def test_rule_field(self):
        a = Alert('id', 'mod', Severity.WARNING, 'T', 'D', rule='expiration')
        d = a.to_dict()
        assert d['rule'] == 'expiration'
