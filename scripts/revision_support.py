"""Current revision adapters; historical source data remain unchanged."""
from collections import defaultdict
import csv
import importlib.util
import json
from pathlib import Path
import random

import numpy as np
import pandas as pd

import rebuild_rsv2_inputs as original

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'revisions/20261107'
DATA = BUNDLE / 'data'
EXPECTED = BUNDLE / 'expected'
OUT = ROOT / 'outputs/current'


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rebuild(root=ROOT):
    annotations = read(DATA / 'rsv2_independent_annotations.json')
    baseline = read(DATA / 'rsv2_reassessment_annotations.json')
    decisions = read(DATA / 'rsv2_alignment_decisions.json')
    mapping = read(DATA / 'case_id_mapping.json')
    old_responses, _ = original.validate(baseline, decisions, mapping)
    responses, factors = {}, {}
    added = 0
    for r in annotations['responses']:
        sid, reviewer, stage = key = r['source_id'], r['reviewer_code'], r['stage']
        assert key not in responses and key in old_responses
        old = old_responses[key]
        assert r['pair_id'] == old['pair_id'] and r['analyzability'] == old['analyzability']
        oldf = {f['factor_id']: f for f in old['factors']}
        newf = {f['factor_id']: f for f in r['factors']}
        assert len(newf) == len(r['factors']) and oldf.keys() <= newf.keys()
        for fid, f in oldf.items():
            assert newf[fid] == f, 'Retained factor codes/evidence must not change'
        for fid in newf.keys() - oldf.keys():
            assert stage == 'before' and newf[fid]['classifications'] == ['CoP']
            assert newf[fid]['layers'] == []
            added += 1
        responses[key] = r
        for f in r['factors']:
            assert f['classifications'] == sorted(set(f['classifications']))
            assert set(f['classifications']) <= original.ALLOWED_CODES
            assert f['layers'] == original.layers(f['classifications'])
            factors[(*key, f['factor_id'])] = f
    assert set(responses) == set(old_responses) and added == 4
    assert sum(len(r['factors']) for r in responses.values() if r['stage'] == 'before') == 248
    for d in decisions['decisions']:
        x, y = [factors[d['source_id'], reviewer, 'before', fid] for reviewer, fid in
                zip(d['pair_id'], [d['left_id'], d['right_id']])]
        assert d['strict_quote_match'] == bool(original.quote_keys(x) & original.quote_keys(y))
    context = read(DATA / 'rsv2_factor_case_context.json')
    by_case = defaultdict(list)
    for d in decisions['decisions']:
        by_case[d['source_id']].append(d)
    rows, units, graph_rows = [], {'before': [], 'after': []}, []
    rs = load(BUNDLE / 'code/rsv2_statistics.py', 'revision_graph')
    for mode in original.MODES:
        for matching in original.MATCHING:
            for c in context:
                sid, pair = c['source_id'], c['pair_id']
                aa = [responses[sid, reviewer, 'before'] for reviewer in pair]
                left, right = [{f['factor_id']: f for f in r['factors'] if original.eligible(f, mode)} for r in aa]
                selected = [d for d in by_case[sid] if d['left_id'] in left and d['right_id'] in right
                    and (d['relation'] == 'same' or matching == 'partial_sensitivity' and d['relation'] == 'partial')
                    and (matching != 'strict' or d['strict_quote_match'])]
                assert len({d['left_id'] for d in selected}) == len({d['right_id'] for d in selected}) == len(selected)
                n1, n2, matches = len(left), len(right), len(selected)
                row = dict(source_id=sid, pair_id=pair, actor_unclear_either=c['actor_unclear_either'],
                    time_mean_minutes=c['time_mean_minutes'], n_left=n1, n_right=n2, matches=matches,
                    f1=2*matches/(n1+n2) if n1+n2 else None, eligibility=mode, matching=matching)
                rows.append(row)
                if (mode, matching) != ('hfacs_or_indeterminate', 'same_proposition'):
                    continue
                assert row == c, 'Primary per-record counts differ from saved approved run'
                for d in selected:
                    for stage in units:
                        x, y = [factors[sid, reviewer, stage, fid] for reviewer, fid in
                                zip(pair, [d['left_id'], d['right_id']])]
                        lx, ly = set(x['layers']), set(y['layers'])
                        units[stage].append(dict(source_id=sid, pair_id=pair, left_id=d['left_id'], right_id=d['right_id'],
                            codes_left=x['classifications'], codes_right=y['classifications'],
                            layer_left=x['layers'], layer_right=y['layers'], codes_equal=x['classifications'] == y['classifications'],
                            layer_equal=lx == ly, layer_jaccard=len(lx & ly)/len(lx | ly) if lx | ly else None))
                maps = [{i: side+i for i in ff} for ff, side in [(left, 'L:'), (right, 'R:')]]
                for j, d in enumerate(selected):
                    maps[0][d['left_id']] = maps[1][d['right_id']] = f'U:{j}'
                ga, gb = [rs.graph(r, mp, list(ff.values())) for r, mp, ff in zip(aa, maps, [left, right])]
                adj_a, adj_b = [{tuple(sorted(e)) for e in g} for g in [ga, gb]]
                common = adj_a & adj_b
                graph_rows.append(dict(source_id=sid, pair_id=pair, left_edges=len(ga), right_edges=len(gb),
                    shared_directed=len(ga & gb), shared_adjacency=len(common),
                    direction_consistent=sum(any(e in ga and e in gb for e in [(x, y), (y, x)]) for x, y in common),
                    directed_f1=rs.f1(len(ga), len(gb), len(ga & gb)), adjacency_f1=rs.f1(len(adj_a), len(adj_b), len(common))))
    assert units == read(EXPECTED / 'rsv2_matched_units.json')
    assert graph_rows == read(EXPECTED / 'rsv2_graph_case_metrics.json')
    save(OUT / 'rebuilt_graph_cases.json', graph_rows)
    save(OUT / 'rebuilt_factor_cases.json', rows)
    save(OUT / 'rebuilt_matched_units.json', units)
    return rows, units, dict(independent_responses=120, independent_factors=248,
        reassessment_baseline_responses=120, reassessment_baseline_factors=244,
        restored_CoP_only_factors=added, saved_correspondences=55,
        scope='Independent evaluation uses pre-viewing versions; reassessment retains the actually presented baseline',
        case_covariates='Saved actor-difficulty flags and elapsed times; quotation checks preserved as fingerprints',
        new_model_calls=False, human_confirmation=False)


def human_and_ai(report, compare):
    pooled = load(BUNDLE / 'code/pooled.py', 'pooled')
    rel = load(ROOT / 'analysis_npj/scripts/02_reliability_analysis.py', 'rel')
    units = read(DATA / 'human_pooled_units.json')
    result = {}
    for j, (name, cats, transform) in enumerate([
        ('detailed', rel.DETAILED_22, lambda x:x), ('layer', rel.TIER_5, rel.tier_merge_non_hfacs),
        ('binary', rel.BINARY_2, rel.binary)]):
        rows = [[(transform(a), transform(b)) for a, b in u['labels']] for u in units]
        result[name] = pooled.bootstrap(pooled.matrices(rows, cats), [u['pair'] for u in units], seed=20261014+j)
    compare(result, read(EXPECTED / 'human_pooled.json'), 'RSv1.pooled')
    report['rsv1_human_pooled'] = result
    final = load(ROOT / 'analysis_npj/scripts/79_evaluate_frozen_final_50.py', 'final')
    cases = pd.read_csv(DATA / 'canonical_cases.csv').fillna('')
    pairs = dict(zip(cases.source_id, cases.pair))
    report['rsv1_final'] = {}
    for model in ['gpt_5_6_sol', 'kimi_k26']:
        rows = read(DATA / f'rsv1_final_{model}_units.json')
        sources = sorted({r['source_id'] for r in rows})
        groups = [[s for s in sources if pairs[s] == p] for p in sorted({pairs[s] for s in sources})]
        by_source = {s: [r for r in rows if r['source_id'] == s] for s in sources}
        result = {}
        for name in ['detailed20', 'tier5', 'binary']:
            transform = getattr(final, name)
            point = final.agreement([transform(r['reference']) for r in rows], [transform(r['prediction']) for r in rows])
            rng = random.Random(final.BOOTSTRAP_SEED)
            values = {k: [] for k in ['accuracy', 'cohens_kappa', 'gwets_ac1']}
            for _ in range(10000):
                ids = [rng.choice(g) for g in groups for _ in g]
                sample = [r for s in ids for r in by_source[s]]
                v = final.agreement([transform(r['reference']) for r in sample], [transform(r['prediction']) for r in sample])
                for k in values: values[k].append(v[k])
            for k, v in values.items():
                point[k + '_ci95'] = [final.percentile(v, .025), final.percentile(v, .975)]
            point['valid_replicates'] = 10000
            result[name] = point
        expected = read(EXPECTED / f'rsv1_final_{model}.json')
        compare(result, {k:expected[k] for k in result}, 'RSv1.final.' + model)
        report['rsv1_final'][model] = result
        print(model, 'verified', flush=True)


def additional(report, units, records, rs, compare):
    pooled = load(BUNDLE / 'code/pooled.py', 'pooled_intervals')
    responses = read(DATA / 'rsv2_independent_annotations.json')['responses']
    factors = {(r['source_id'], r['reviewer_code'], r['stage'], f['factor_id']): f
               for r in responses for f in r['factors']}
    decisions = read(DATA / 'rsv2_alignment_decisions.json')['decisions']
    classification = {}
    for mode in original.MODES:
        for matching in original.MATCHING:
            selected = []
            for d in decisions:
                x,y = [factors[d['source_id'], reviewer, 'before', fid] for reviewer,fid in zip(d['pair_id'], [d['left_id'],d['right_id']])]
                if not (original.eligible(x,mode) and original.eligible(y,mode)): continue
                if not (d['relation'] == 'same' or matching == 'partial_sensitivity' and d['relation'] == 'partial'): continue
                if matching == 'strict' and not d['strict_quote_match']: continue
                selected.append(d)
            stages = {}
            for stage in ['before','after']:
                us = []
                for d in selected:
                    x,y = [factors[d['source_id'], reviewer, stage, fid] for reviewer,fid in zip(d['pair_id'], [d['left_id'],d['right_id']])]
                    lx,ly = set(x['layers']),set(y['layers'])
                    us.append(dict(pair_id=d['pair_id'], codes_left=x['classifications'],codes_right=y['classifications'],
                        layer_left=x['layers'],layer_right=y['layers'],codes_equal=x['classifications']==y['classifications'],
                        layer_equal=lx==ly,layer_jaccard=len(lx&ly)/len(lx|ly) if lx|ly else None))
                stages[stage] = {p:rs.class_summary([u for u in us if p=='overall' or u['pair_id']==p]) for p in ['overall','AB','CD','EF']}
            classification[mode+':'+matching] = stages
    compare(classification, read(EXPECTED/'rsv2.json')['classification'], 'RSv2.all_classification_sensitivities')
    report['rsv2_all_classification_sensitivities_verified'] = True
    result = {}
    for j, stage in enumerate(['before', 'after']):
        rows = [[tuple(c[stage])] for c in records]
        result[stage] = pooled.bootstrap(pooled.matrices(rows, ['not_analyzable', 'uncertain', 'clear']),
            [c['pair_id'] for c in records], weighted=True, seed=20261024+j)
    compare(result, read(EXPECTED / 'pooled_reassessment.json'), 'RSv2.pooled_reassessment')
    report['pooled_reassessment'] = result
    changes = []
    baseline = read(DATA / 'rsv2_reassessment_annotations.json')['responses']
    after = {(r['source_id'], r['reviewer_code']):r for r in baseline if r['stage'] == 'after'}
    for r in baseline:
        if r['stage'] != 'before': continue
        a = {f['factor_id']: f for f in after[r['source_id'], r['reviewer_code']]['factors']}
        for f in r['factors']:
            changes.append((f['classifications'], a[f['factor_id']]['classifications']))
    changed = sum(x != y for x, y in changes)
    empty = sum(bool(x) and not y for x, y in changes)
    assert (len(changes), changed, empty) == (244, 26, 6)
    report['within_reviewer_classification_changes'] = dict(paired_factors=len(changes), changed_label_sets=changed, classification_to_empty=empty)
    fixed = [(a,b) for a,b in zip(units['before'], units['after']) if all(len(u[k]) == 1 for u in [a,b] for k in ['layer_left','layer_right'])]
    assert len(fixed) == 26
    intervals = {}
    for name, us, field in [('matched_detailed', units['before'], 'codes'), ('matched_layer', units['before'], 'layer'),
            ('fixed26_before', [a for a,b in fixed], 'layer'), ('fixed26_after', [b for a,b in fixed], 'layer')]:
        single = [u for u in us if len(u[field+'_left']) == len(u[field+'_right']) == 1]
        cats = sorted({v for u in us for side in ['left','right'] for v in u[field+'_'+side]})
        rows = [[(u[field+'_left'][0], u[field+'_right'][0]) for u in single if u['source_id'] == c['source_id']] for c in records]
        intervals[name] = pooled.bootstrap(pooled.matrices(rows, cats), [c['pair_id'] for c in records], seed=20261107)['kappa']
        intervals[name].update(units=len(single), records_with_units=sum(bool(r) for r in rows), cluster_records=len(records), seed=20261107)
    graph = read(OUT / 'rebuilt_graph_cases.json')
    seed = rs.SEED; rs.SEED = 20261107
    estimate = rs.f1(sum(r['left_edges'] for r in graph), sum(r['right_edges'] for r in graph), sum(r['shared_directed'] for r in graph))
    intervals['directed_relation_f1'] = dict(estimate=estimate,
        ci95=rs.bootstrap(graph, lambda rows: rs.f1(sum(r['left_edges'] for r in rows), sum(r['right_edges'] for r in rows), sum(r['shared_directed'] for r in rows))),
        cluster_records=60, seed=20261107)
    rs.SEED = seed
    compare(intervals, read(EXPECTED / 'rsv2_additional_ci.json'), 'RSv2.additional_CI')
    report['additional_intervals'] = intervals


def fta(compare):
    for stage, name in [('fta_gate', '06_fta_added_value.py'), ('fta_flat', '09_compare_flat_vs_fta.py')]:
        mod = load(BUNDLE / 'code' / name, 'current_' + stage)
        mod.OUT_DIR = OUT / stage
        mod.main()
        for p in (EXPECTED / stage).glob('*'):
            if p.suffix == '.json':
                compare(read(mod.OUT_DIR / p.name), read(p), stage + '.' + p.name)
            elif p.suffix == '.csv':
                a = list(csv.DictReader((mod.OUT_DIR / p.name).open(encoding='utf-8-sig')))
                b = list(csv.DictReader(p.open(encoding='utf-8-sig')))
                assert len(a) == len(b), p.name
                for i, (x,y) in enumerate(zip(a,b)):
                    assert x.keys() == y.keys()
                    for k, v in y.items():
                        try: expected = float(v)
                        except (ValueError, TypeError):
                            assert x[k] == v, (stage, p.name, i, k, x[k], v)
                        else:
                            if np.isnan(expected): assert x[k] in ['', 'nan']
                            else: compare(float(x[k]), expected, f'{stage}.{p.name}.{i}.{k}')
        print(stage, 'verified', flush=True)
