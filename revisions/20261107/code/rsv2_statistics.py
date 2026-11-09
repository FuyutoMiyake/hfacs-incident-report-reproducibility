"""Reproducible case-clustered RSv2 analysis, retaining multilabel uncertainty.

Semantic decisions in alignment_decisions.csv are AI-assisted provisional coding.
No metric produced here upgrades that coding to human-confirmed reference data.
"""
import csv
import hashlib
import html
import json
import platform
import re
import unicodedata
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'analysis_npj/analysis_runs/rsv2_complete_20261001'
SEED = 20261001
NBOOT = 3000
HFACS = set('UA_DE UA_SE UA_PE UA_RV UA_EV PC_AM PC_AP PC_PL PC_TE PC_PE PC_CC PC_PR SI_IS SI_IO SI_FK SI_SV OI_RM OI_OC OI_OP'.split())
LEVELS = ['not_analyzable', 'uncertain', 'clear']

def read(name):
    return json.loads((RUN / name).read_text())

def save(name, value):
    (RUN / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

def norm(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value or ''))

def codes(f):
    return set(f.get('classifications', []))

def layers(f):
    return {dict(UA='L1', PC='L2', SI='L3', OI='L4')[c.split('_')[0]] for c in codes(f) & HFACS}

def eligible(f, mode):
    return mode == 'all' or bool(codes(f) & HFACS) or (mode == 'hfacs_or_indeterminate' and 'INDETERMINATE' in codes(f))

def quotekeys(f):
    return {(e.get('evidence_section'), norm(e.get('evidence_quote'))) for e in f.get('evidence_items', []) if norm(e.get('evidence_quote'))}

def f1(n1, n2, m):
    return 2 * m / (n1 + n2) if n1 + n2 else None

def agree(a, b, labels, weighted=False):
    n = len(a)
    if not n:
        return {'n': 0, 'raw': None, 'kappa': None, 'table': []}
    table = np.zeros((len(labels), len(labels)), dtype=int)
    for x, y in zip(a, b):
        table[labels.index(x), labels.index(y)] += 1
    distance = np.array([[abs(i-j)/(len(labels)-1) if weighted else float(i != j)
                          for j in range(len(labels))] for i in range(len(labels))])
    obs = (table * distance).sum() / n
    exp = (np.outer(table.sum(axis=1), table.sum(axis=0)) * distance).sum() / n ** 2
    return {'n': n, 'raw': float(np.trace(table)/n), 'kappa': float(1 - obs/exp) if exp else None,
            'table': table.tolist(), 'labels': labels}

def dist(values):
    values = [float(x) for x in values if x is not None and np.isfinite(x)]
    return {'n': len(values), 'median': float(np.median(values)) if values else None,
            'q1': float(np.quantile(values, .25)) if values else None,
            'q3': float(np.quantile(values, .75)) if values else None}

def bootstrap(rows, metric):
    if not rows:
        return {'low': None, 'high': None, 'valid': 0}
    rng = np.random.default_rng(SEED)
    groups = [[r for r in rows if r['pair_id'] == pair] for pair in sorted({r['pair_id'] for r in rows})]
    vals = []
    for _ in range(NBOOT):
        sample = [g[i] for g in groups for i in rng.integers(0, len(g), len(g))]
        x = metric(sample)
        if x is not None and np.isfinite(x):
            vals.append(float(x))
    return {'low': float(np.quantile(vals, .025)) if vals else None,
            'high': float(np.quantile(vals, .975)) if vals else None, 'valid': len(vals)}

def factor_summary(items):
    n1, n2, m = [sum(x[k] for x in items) for k in ['n_left', 'n_right', 'matches']]
    return {'cases': len(items), 'left_factors': n1, 'right_factors': n2, 'matched': m,
            'micro_f1': f1(n1, n2, m),
            'micro_f1_ci95': bootstrap(items, lambda xs: f1(sum(x['n_left'] for x in xs), sum(x['n_right'] for x in xs), sum(x['matches'] for x in xs))),
            'macro_f1': float(np.mean([x['f1'] for x in items if x['f1'] is not None])) if any(x['f1'] is not None for x in items) else None,
            'both_empty': sum(x['f1'] is None for x in items),
            'one_empty': sum(bool(x['n_left']) != bool(x['n_right']) for x in items)}

def class_summary(items):
    def layer_rate(xs):
        valid = [x for x in xs if x['layer_left'] and x['layer_right']]
        return sum(x['layer_equal'] for x in valid) / len(valid) if valid else None
    valid = [x for x in items if x['layer_left'] and x['layer_right']]
    single = [x for x in valid if len(x['layer_left']) == len(x['layer_right']) == 1]
    all_codes = sorted({v for x in items for k in ['codes_left', 'codes_right'] for v in x[k]})
    csingle = [x for x in items if len(x['codes_left']) == len(x['codes_right']) == 1]
    bylabel = {c: agree([int(c in x['codes_left']) for x in items], [int(c in x['codes_right']) for x in items], [0, 1]) for c in all_codes}
    return {'matched_factors': len(items), 'both_have_hfacs_layer': len(valid),
            'layer_set_exact': layer_rate(items),
            'layer_set_overlap_any': sum(bool(set(x['layer_left']) & set(x['layer_right'])) for x in valid)/len(valid) if valid else None,
            'fixed_unit_layer_exact_with_unclassified_not_agreement': sum(bool(x['layer_left'] and x['layer_right']) and x['layer_equal'] for x in items)/len(items) if items else None,
            'layer_set_jaccard': float(np.mean([x['layer_jaccard'] for x in valid])) if valid else None,
            'layer_singleton_kappa': agree([x['layer_left'][0] for x in single], [x['layer_right'][0] for x in single], ['L1', 'L2', 'L3', 'L4']),
            'detailed_set_exact': sum(x['codes_equal'] for x in items)/len(items) if items else None,
            'detailed_singleton_kappa': agree([x['codes_left'][0] for x in csingle], [x['codes_right'][0] for x in csingle], all_codes),
            'missing_layer_on_either': len(items) - len(valid), 'binary_by_code': bylabel}

def graph(a, mapping, factors):
    ids = {f['factor_id'] for f in factors}
    result = set()
    for e in a['relations']:
        left = e['source_factor_id']
        right = e.get('target_node_id', e.get('target_factor_id'))
        if left not in ids or (right not in ids and right != 'incident_outcome'):
            continue
        result.add((mapping[left], 'outcome' if right == 'incident_outcome' else mapping[right]))
    return result

def main():
    cases = read('canonical_cases.json')
    bases = read('canonical_independent.json')
    after = read('canonical_phase2.json')
    refs = read('canonical_consensus.json')
    bmap = {(b['source_id'], b['annotator_id']): b for b in bases}
    pmap = {(b['source_id'], b['annotator_id']): b for b in after}
    cmap = {(c['pair_id'], int(c['order'])): c for c in cases}
    decisions = list(csv.DictReader((RUN / 'alignment_decisions.csv').open()))
    match_rows = []
    for r in decisions:
        c = cmap[(r['pair'], int(r['main']))]
        sid = c['source_id']
        a = next(f for f in bmap[(sid, 'annotator_' + r['pair'][0])]['factors'] if f['factor_id'] == r['left'])
        b = next(f for f in bmap[(sid, 'annotator_' + r['pair'][1])]['factors'] if f['factor_id'] == r['right'])
        common_quotes = quotekeys(a) & quotekeys(b)
        match_rows.append({**r, 'source_id': sid, 'display_id': c['display_id'],
                           'left_text': a['factor_text'], 'right_text': b['factor_text'],
                           'left_evidence': a.get('evidence_items', []), 'right_evidence': b.get('evidence_items', []),
                           'strict_quote_match': bool(common_quotes), 'human_confirmed': False})
    for pair in ['AB', 'CD', 'EF']:
        for c in [c for c in cases if c['pair_id'] == pair]:
            selected = [m for m in match_rows if m['source_id'] == c['source_id'] and m['relation'] in ['same', 'partial']]
            assert len({m['left'] for m in selected}) == len(selected)
            assert len({m['right'] for m in selected}) == len(selected)
    save('alignment_review.json', match_rows)
    extraction = {}
    classification = {}
    graph_rows = []
    for mode in ['all', 'hfacs_only', 'hfacs_or_indeterminate']:
        all_rows = []
        for matching in ['strict', 'same_proposition', 'partial_sensitivity']:
            fr = []
            cr = {'before': [], 'after': []}
            for c in cases:
                sid, pair = c['source_id'], c['pair_id']
                a, b = [bmap[(sid, 'annotator_' + s)] for s in pair]
                af = {f['factor_id']: f for f in a['factors'] if eligible(f, mode)}
                bf = {f['factor_id']: f for f in b['factors'] if eligible(f, mode)}
                selected = [m for m in match_rows if m['source_id'] == sid and m['left'] in af and m['right'] in bf and
                            (m['relation'] == 'same' or (matching == 'partial_sensitivity' and m['relation'] == 'partial')) and
                            (matching != 'strict' or m['strict_quote_match'])]
                row = {'source_id': sid, 'display_id': c['display_id'], 'pair_id': pair,
                       'n_left': len(af), 'n_right': len(bf), 'matches': len(selected),
                       'f1': f1(len(af), len(bf), len(selected)), 'matching': matching, 'eligibility': mode,
                       'actor_unclear_either': any('actor_role_scope_unclear' in x['difficulty_reasons'] for x in [a, b]),
                       'time_mean_minutes': (a['elapsed_seconds'] + b['elapsed_seconds'])/120}
                fr.append(row)
                for m in selected:
                    for stage in ['before', 'after']:
                        if stage == 'before':
                            x, y = af[m['left']], bf[m['right']]
                        else:
                            x = next(f for f in pmap[(sid, a['annotator_id'])]['factors'] if f['factor_id'] == m['left'])
                            y = next(f for f in pmap[(sid, b['annotator_id'])]['factors'] if f['factor_id'] == m['right'])
                        lx, ly = layers(x), layers(y)
                        cx, cy = codes(x), codes(y)
                        cr[stage].append({'source_id': sid, 'pair_id': pair, 'left_id': m['left'], 'right_id': m['right'],
                            'codes_left': sorted(cx), 'codes_right': sorted(cy), 'layer_left': sorted(lx), 'layer_right': sorted(ly),
                            'codes_equal': cx == cy, 'layer_equal': lx == ly,
                            'layer_jaccard': len(lx & ly)/len(lx | ly) if lx | ly else None})
                if mode == 'hfacs_or_indeterminate' and matching == 'same_proposition':
                    amap = {id: 'L:' + id for id in af}
                    bmap_nodes = {id: 'R:' + id for id in bf}
                    for i, m in enumerate(selected):
                        amap[m['left']] = bmap_nodes[m['right']] = f'U:{i}'
                    ga, gb = graph(a, amap, list(af.values())), graph(b, bmap_nodes, list(bf.values()))
                    adj_a = {tuple(sorted(e)) for e in ga}
                    adj_b = {tuple(sorted(e)) for e in gb}
                    common = adj_a & adj_b
                    graph_rows.append({'source_id': sid, 'pair_id': pair, 'left_edges': len(ga), 'right_edges': len(gb),
                        'shared_directed': len(ga & gb), 'shared_adjacency': len(common),
                        'direction_consistent': sum(any(e in ga and e in gb for e in [(x, y), (y, x)]) for x, y in common),
                        'directed_f1': f1(len(ga), len(gb), len(ga & gb)),
                        'adjacency_f1': f1(len(adj_a), len(adj_b), len(common))})
            key = mode + ':' + matching
            extraction[key] = {p: factor_summary([x for x in fr if p == 'overall' or x['pair_id'] == p]) for p in ['overall', 'AB', 'CD', 'EF']}
            classification[key] = {s: {p: class_summary([x for x in xs if p == 'overall' or x['pair_id'] == p])
                                       for p in ['overall', 'AB', 'CD', 'EF']} for s, xs in cr.items()}
            if key == 'hfacs_or_indeterminate:same_proposition':
                save('factor_case_metrics.json', fr)
                save('matched_classification_units.json', cr)
                primary_rows = fr
    analyzer_agreement = {}
    paired_layer_units = read('matched_classification_units.json')
    classification_paired = {}
    for p in ['overall', 'AB', 'CD', 'EF']:
        before_units = {(x['source_id'], x['left_id'], x['right_id']): x for x in paired_layer_units['before'] if p == 'overall' or x['pair_id'] == p}
        joint = [(before_units[(y['source_id'], y['left_id'], y['right_id'])], y)
                 for y in paired_layer_units['after'] if (p == 'overall' or y['pair_id'] == p)]
        common = [(a, b) for a, b in joint if a['layer_left'] and a['layer_right'] and b['layer_left'] and b['layer_right']]
        singleton_both = [(a, b) for a, b in common if all(len(x[k]) == 1 for x in [a, b] for k in ['layer_left', 'layer_right'])]
        rate = lambda xs, stage, overlap: sum(bool(set(x[stage]['layer_left']) & set(x[stage]['layer_right'])) if overlap else x[stage]['layer_equal'] for x in xs)/len(xs) if xs else None
        classification_paired[p] = {'n_matched': len(joint), 'n_both_stage_classified': len(common),
            'exact_before_fixed_denominator': rate(common, 0, False), 'exact_after_fixed_denominator': rate(common, 1, False),
            'overlap_before_fixed_denominator': rate(common, 0, True), 'overlap_after_fixed_denominator': rate(common, 1, True),
            'n_singleton_in_both_stages': len(singleton_both),
            'singleton_before_same_units': agree([a['layer_left'][0] for a, b in singleton_both], [a['layer_right'][0] for a, b in singleton_both], ['L1', 'L2', 'L3', 'L4']),
            'singleton_after_same_units': agree([b['layer_left'][0] for a, b in singleton_both], [b['layer_right'][0] for a, b in singleton_both], ['L1', 'L2', 'L3', 'L4'])}
    transitions = Counter()
    pair_cases = []
    for c in cases:
        before_values, after_values = [], []
        for a in c['pair_id']:
            key = (c['source_id'], 'annotator_' + a)
            before_values.append(bmap[key]['analyzability'])
            after_values.append(pmap[key]['analyzability'])
            transitions[(before_values[-1], after_values[-1])] += 1
        pair_cases.append({**{k: c[k] for k in ['source_id', 'pair_id', 'display_id']}, 'before': before_values, 'after': after_values})
    for pair in ['AB', 'CD', 'EF']:
        rs = [x for x in pair_cases if x['pair_id'] == pair]
        analyzer_agreement[pair] = {}
        for stage in ['before', 'after']:
            value = agree([x[stage][0] for x in rs], [x[stage][1] for x in rs], LEVELS, True)
            value['kappa_ci95'] = bootstrap(rs, lambda xs: agree([x[stage][0] for x in xs], [x[stage][1] for x in xs], LEVELS, True)['kappa'])
            analyzer_agreement[pair][stage] = value
    trace_rows = []
    for type_name, items in [('independent', bases), ('consensus', refs)]:
        for b in items:
            source = next(c for c in cases if c['source_id'] == b['source_id'])
            for f in b['factors']:
                evidence = f.get('evidence_items', [])
                statuses = [bool(norm(e.get('evidence_quote'))) and norm(e.get('evidence_quote')) in norm(source.get('text_' + e.get('evidence_section', ''), '')) for e in evidence]
                trace_rows.append({'type': type_name, 'source_id': b['source_id'], 'factor_id': f['factor_id'],
                    'annotator_id': b.get('annotator_id'), 'quotes': len(evidence), 'quotes_found': sum(statuses),
                    'all_quotes_traceable': bool(evidence) and all(statuses),
                    'only_improvement_evidence': bool(evidence) and all(e.get('evidence_section') == 'improvement' for e in evidence)})
    save('evidence_traceability.json', trace_rows)
    consensus_stats = {p: {'cases': len([r for r in refs if p == 'overall' or r['pair_id'] == p]),
        'factors': sum(len(r['factors']) for r in refs if p == 'overall' or r['pair_id'] == p),
        'analyzability': dict(Counter(r['analyzability'] for r in refs if p == 'overall' or r['pair_id'] == p)),
        'case_resolution_stored': dict(Counter(r.get('case_resolution_status') or 'missing' for r in refs if p == 'overall' or r['pair_id'] == p)),
        'factor_resolution_stored': dict(Counter(f.get('resolution_status') or 'missing' for r in refs if p == 'overall' or r['pair_id'] == p for f in r['factors'])),
        'multilabel_factors': sum(len(codes(f)) > 1 for r in refs if p == 'overall' or r['pair_id'] == p for f in r['factors']),
        'multilayer_factors': sum(len(layers(f)) > 1 for r in refs if p == 'overall' or r['pair_id'] == p for f in r['factors']),
        'unclassified_factors': sum(not codes(f) for r in refs if p == 'overall' or r['pair_id'] == p for f in r['factors'])}
        for p in ['overall', 'AB', 'CD', 'EF']}
    reason_groups = {str(flag): factor_summary([x for x in primary_rows if x['actor_unclear_either'] == flag]) for flag in [True, False]}
    finite_rows = [x for x in primary_rows if x['f1'] is not None]
    rho = spearmanr([x['f1'] for x in finite_rows], [x['time_mean_minutes'] for x in finite_rows])
    graph_summary = {p: {'cases': len([g for g in graph_rows if p == 'overall' or g['pair_id'] == p]),
        'left_edges': sum(g['left_edges'] for g in graph_rows if p == 'overall' or g['pair_id'] == p),
        'right_edges': sum(g['right_edges'] for g in graph_rows if p == 'overall' or g['pair_id'] == p),
        'shared_directed': sum(g['shared_directed'] for g in graph_rows if p == 'overall' or g['pair_id'] == p),
        'shared_adjacency': sum(g['shared_adjacency'] for g in graph_rows if p == 'overall' or g['pair_id'] == p)} for p in ['overall', 'AB', 'CD', 'EF']}
    for v in graph_summary.values():
        v['directed_micro_f1'] = f1(v['left_edges'], v['right_edges'], v['shared_directed'])
    ai_summary = {'available': False}
    ai_file = RUN / 'ai/results.jsonl'
    ai_resolution = []
    ai_class_units = []
    if ai_file.exists():
        ai_results = {}
        for line in ai_file.read_text().splitlines():
            x = json.loads(line)
            if x['status'] == 'ok':
                ai_results[(x['mode'], x['source_id'])] = x
        for ref in refs:
            rr = ai_results.get(('resolution', ref['source_id']))
            if rr:
                ai_resolution += [{**f, 'source_id': ref['source_id'], 'pair_id': ref['pair_id'], 'human_verified': False} for f in rr['result']['factors']]
            pred = ai_results.get(('classification', ref['source_id']))
            if pred:
                for x in pred['result']['classifications']:
                    rf_id = pred['factor_map'][str(x['node_id'])]
                    f = next(f for f in ref['factors'] if f['factor_id'] == rf_id)
                    resolution = next((r['resolution'] for r in ai_resolution if r['source_id'] == ref['source_id'] and r['factor_id'] == rf_id), 'missing')
                    label = x['label']
                    single = len(codes(f)) == 1 and bool(codes(f) & HFACS)
                    ai_class_units.append({'source_id': ref['source_id'], 'pair_id': ref['pair_id'], 'factor_id': rf_id,
                        'human_codes': sorted(codes(f)), 'human_layers': sorted(layers(f)), 'ai_code': label,
                        'ai_layer': next(iter(layers({'classifications': [label]})), None),
                        'hit_any_human_code': label in codes(f), 'singleton_hfacs_reference': single,
                        'stored_resolution': f.get('resolution_status') or 'missing', 'llm_resolution': resolution})
        labeled_units = [x for x in ai_class_units if x['human_codes']]
        hfacs_units = [x for x in ai_class_units if x['human_layers']]
        ai_summary = {'available': True, 'successful_case_calls': dict(Counter(k[0] for k in ai_results)),
            'units': len(ai_class_units), 'labeled_units': len(labeled_units), 'unclassified_not_scored': len(ai_class_units)-len(labeled_units),
            'label_any_hit': sum(x['hit_any_human_code'] for x in labeled_units)/len(labeled_units) if labeled_units else None,
            'hfacs_labeled_units': len(hfacs_units),
            'hfacs_label_any_hit': sum(x['hit_any_human_code'] for x in hfacs_units)/len(hfacs_units) if hfacs_units else None,
            'multilabel_hit_is_permissive_not_exact_set_accuracy': True,
            'resolution_counts_llm_unverified': dict(Counter(x['resolution'] for x in ai_resolution)),
            'support_counts_llm_unverified': dict(Counter(x['support'] for x in ai_resolution)),
            'reason_origin_counts_llm_unverified': dict(Counter(x['reason_origin'] for x in ai_resolution))}
        single = [x for x in ai_class_units if x['singleton_hfacs_reference']]
        ai_summary['singleton_hfacs_detailed'] = agree([x['human_codes'][0] for x in single], [x['ai_code'] for x in single], sorted(HFACS | {'CoP', 'OTHER', 'INAPPROPRIATE'}))
        ai_summary['singleton_hfacs_layer'] = agree([x['human_layers'][0] for x in single], [x['ai_layer'] or 'nonHFACS' for x in single], ['L1', 'L2', 'L3', 'L4', 'nonHFACS'])
        cluster_rows = [{'source_id': c['source_id'], 'pair_id': c['pair_id'], 'units': [x for x in single if x['source_id'] == c['source_id']]} for c in cases]
        for metric in ['singleton_hfacs_detailed', 'singleton_hfacs_layer']:
            def score(xs):
                units = [u for x in xs for u in x['units']]
                if metric == 'singleton_hfacs_detailed':
                    return agree([u['human_codes'][0] for u in units], [u['ai_code'] for u in units], sorted(HFACS | {'CoP','OTHER','INAPPROPRIATE'}))['kappa']
                return agree([u['human_layers'][0] for u in units], [u['ai_layer'] or 'nonHFACS' for u in units], ['L1','L2','L3','L4','nonHFACS'])['kappa']
            ai_summary[metric]['case_bootstrap_ci95'] = bootstrap(cluster_rows, score)
        ai_summary['by_pair'] = {p: {'n': len([x for x in labeled_units if x['pair_id'] == p]),
            'hit_any': sum(x['hit_any_human_code'] for x in labeled_units if x['pair_id'] == p)/sum(x['pair_id'] == p for x in labeled_units) if any(x['pair_id'] == p for x in labeled_units) else None} for p in ['AB', 'CD', 'EF']}
        ai_summary['strata'] = {}
        for provenance in ['stored_resolution', 'llm_resolution']:
            ai_summary['strata'][provenance] = {s: {'n': len([x for x in labeled_units if x[provenance] == s]),
                'hit_any': sum(x['hit_any_human_code'] for x in labeled_units if x[provenance] == s)/sum(x[provenance] == s for x in labeled_units) if any(x[provenance] == s for x in labeled_units) else None}
                for s in ['source_confirmed', 'rule_adjudicated', 'unresolved', 'not_hfacs_target', 'missing']}
        save('ai/resolution_llm_unverified.json', ai_resolution)
        save('ai/classification_units.json', ai_class_units)
    phase2_summary = read('raw/prior_phase2_analysis.json')
    result = {'analysis_date': '2026-10-01', 'seed': SEED, 'bootstrap_replicates': NBOOT,
        'alignment_provenance': 'AI analyst provisional; no new human confirmation; not final primary endpoint',
        'extraction': extraction, 'classification': classification, 'classification_paired_same_units': classification_paired, 'analyzability_agreement': analyzer_agreement,
        'transitions': [[transitions[(a, b)] for b in LEVELS] for a in LEVELS],
        'before_analyzability': dict(Counter(b['analyzability'] for b in bases)),
        'after_analyzability': dict(Counter(b['analyzability'] for b in after)),
        'consensus': consensus_stats, 'graph_exploratory': graph_summary,
        'evidence_traceability': {p: {'factors': len([x for x in trace_rows if x['type'] == p]),
             'all_quotes_traceable': sum(x['all_quotes_traceable'] for x in trace_rows if x['type'] == p),
             'improvement_only': sum(x['only_improvement_evidence'] for x in trace_rows if x['type'] == p)} for p in ['independent', 'consensus']},
        'actor_unclear_association_exploratory': reason_groups,
        'factor_f1_time_spearman_exploratory': {'n': len(finite_rows), 'rho': float(rho.statistic), 'p': float(rho.pvalue)},
        'original_time_minutes': dist([b['elapsed_seconds']/60 for b in bases]),
        'phase2_active_time_minutes': dist([b['active_seconds']/60 for b in after]),
        'ai_conditional_exploratory': ai_summary,
        'limitations': ['No independently human-confirmed full60 semantic alignment', 'AB external approval; cloud remains draft',
            'Missing/uncertain provenance of stored resolution codes', 'Multicodes conflate alternatives and coexistence',
            'Phase2 reporter-cause fields confounded with factual metadata, rereading and prior consensus',
            'Different cases and raters between pairs; not rater effects', 'No prospectively frozen compatible end-to-end AI extraction arm',
            'LLM resolution/support unverified by humans; same model as classifier may bias strata',
            'Semantic alignment is post-hoc AI-assisted analyst coding, aware of study objectives; not independent blinded clinical adjudication',
            'No causal evidence that missing information caused disagreement',
            'Public JCQHC records, not original hospital reports']}
    save('analysis.json', result)
    save('graph_case_metrics.json', graph_rows)
    save('analyzability_case_metrics.json', pair_cases)
    for pair in ['AB', 'CD', 'EF']:
        for stage in ['before', 'after']:
            old = phase2_summary['agreement']['byPair'][pair][stage]
            assert np.isclose(analyzer_agreement[pair][stage]['raw'], old['raw'])
            assert np.isclose(analyzer_agreement[pair][stage]['kappa'], old['linearWeightedKappa'])
    assert result['transitions'] == [[phase2_summary['overall']['transitions'][a][b] for b in LEVELS] for a in LEVELS]
    figures(result)
    reports(result, cases, bases, after, refs, match_rows, ai_resolution)
    print(json.dumps({'factor_f1_provisional': extraction['hfacs_or_indeterminate:same_proposition'],
                      'analyzability': analyzer_agreement, 'ai': ai_summary}, ensure_ascii=False, indent=2))

def figures(r):
    dest = RUN / 'figures'
    dest.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 180})
    colors = ['#127c76', '#bd6343', '#545a65']
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    vals = r['extraction']['hfacs_or_indeterminate:same_proposition']
    for i, p in enumerate(['AB', 'CD', 'EF']):
        v = vals[p]
        ci = v['micro_f1_ci95']
        axes[0].bar(i, v['micro_f1'], color=colors[i])
        axes[0].errorbar(i, v['micro_f1'], yerr=[[v['micro_f1']-ci['low']], [ci['high']-v['micro_f1']]], color='black', capsize=4)
        axes[0].text(i, ci['high']+.035, f"{v['micro_f1']:.3f}", ha='center')
    axes[0].set(xticks=range(3), xticklabels=['AB', 'CD', 'EF'], ylim=(0, 1), ylabel='Factor F1', title='Provisional semantic alignment')
    x = np.arange(3)
    for i, stage in enumerate(['before', 'after']):
        ys = [r['analyzability_agreement'][p][stage]['raw'] for p in ['AB', 'CD', 'EF']]
        axes[1].bar(x + (i-.5)*.32, ys, width=.32, label=stage, color=['#127c76', '#bd6343'][i])
    axes[1].set(xticks=x, xticklabels=['AB', 'CD', 'EF'], ylim=(0, 1), ylabel='Exact agreement', title='Analyzability (case level)')
    axes[1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(dest / 'factor_agreement.png')
    fig.savefig(dest / 'factor_agreement.pdf')
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.imshow(r['transitions'], cmap='Greys')
    for i in range(3):
        for j in range(3):
            n = r['transitions'][i][j]
            ax.text(j, i, str(n), ha='center', va='center', color='white' if n > 25 else 'black', fontsize=18)
    ax.set(xticks=range(3), yticks=range(3), xticklabels=['Not analyzable', 'Uncertain', 'Clear'],
           yticklabels=['Not analyzable', 'Uncertain', 'Clear'], xlabel='After public information', ylabel='Before', title='120 paired evaluations / 60 cases')
    fig.tight_layout()
    fig.savefig(dest / 'analyzability_transitions.png')
    fig.savefig(dest / 'analyzability_transitions.pdf')
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    v = r['classification_paired_same_units']['overall']
    x = np.arange(2)
    for i, stage in enumerate(['before', 'after']):
        ys = [v[f'exact_{stage}_fixed_denominator'], v[f'overlap_{stage}_fixed_denominator']]
        ax.bar(x+(i-.5)*.32, ys, width=.32, label=stage, color=['#127c76','#bd6343'][i])
    ax.set(xticks=x, xticklabels=['Identical layer sets', 'At least one shared layer'], ylim=(0,1),
           ylabel='Agreement', title=f'Fixed matched units: N={v["n_both_stage_classified"]} (provisional)')
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(dest / 'multilabel_agreement.png')
    fig.savefig(dest / 'multilabel_agreement.pdf')
    plt.close(fig)

def reports(r, cases, bases, after, refs, matches, resolution):
    primary = r['extraction']['hfacs_or_indeterminate:same_proposition']
    locked = (RUN / 'consensus_lock.json').exists()
    approval_text = ('ABの保存済み20症例が承認対象と三宅先生が確認した。最新DBとの再照合で全60保存版が変更されていないことを確認し、consensus_lock.jsonに版・hash・承認経路を記録して解析用RSを固定した。Main2・17・19のメモ提案は追加反映しない。DB上のdraft状態は変更していない。枝川先生の承認原文自体は独立取得していない。'
                     if locked else 'ABはユーザーから外部承認の報告があるが、DB上は20例ともdraft。DBを書き換えていない。承認原文との完全照合は未実施。')
    lines = ['# RSv2統合解析・監査結果', '', '作成日：2026-10-01', '',
        '略語：RS＝参照基準、HFACS＝人的要因の階層分類、F1＝抽出の一致指標、κ＝偶然一致を調整した一致係数。', '',
        '## 結論と確定度', '',
        '60症例・120独立回答・120追加情報確認の原本と、60合議保存版を固定コピーした。' + approval_text, '',
        '**分析可能性の前後比較は回答に基づく確定した記述集計。要因F1と対応要因分類一致はAI補助の意味対応に依存する暫定解析であり、人間確認前に主要評価の最終結果としない。**', '',
        '## 人間間の再現性', '',
        '|ペア|対象要因 左／右|同一中心命題の対応数|暫定micro F1（95% CI）|両側0症例|', '|---|---:|---:|---|---:|']
    for p in ['AB', 'CD', 'EF', 'overall']:
        v = primary[p]; ci = v['micro_f1_ci95']
        lines.append(f"|{p}|{v['left_factors']}／{v['right_factors']}|{v['matched']}|{v['micro_f1']:.3f}（{ci['low']:.3f}–{ci['high']:.3f}）|{v['both_empty']}|")
    lines += ['', 'HFACS又はINDETERMINATEを含む要因を対象とし、CoP/OTHER等だけの要因は除く。全抽出・HFACSだけ・strict引用一致・部分重なりの感度解析はanalysis.jsonへ全て保存。両側0をF1=1にしない。CIは症例単位・ペア内bootstrapで、対応表の誤り自体は反映しない。', '',
              '|ペア|分析可能性の一致 前→後|linear weighted κ 前→後|', '|---|---|---|']
    for p in ['AB', 'CD', 'EF']:
        x = r['analyzability_agreement'][p]
        lines.append(f"|{p}|{x['before']['raw']:.3f} → {x['after']['raw']:.3f}|{x['before']['kappa']:.3f} → {x['after']['kappa']:.3f}|")
    cl = r['classification']['hfacs_or_indeterminate:same_proposition']
    lines += ['', '|ペア|同じ対応要因の層集合一致 前→後|一意層部分 κ 前→後（N）|', '|---|---|---|']
    def fmt(x):
        return '未定義' if x is None else f'{x:.3f}'
    for p in ['AB', 'CD', 'EF', 'overall']:
        a, b = cl['before'][p], cl['after'][p]
        ka, kb = a['layer_singleton_kappa'], b['layer_singleton_kappa']
        lines.append(f"|{p}|{fmt(a['layer_set_exact'])} → {fmt(b['layer_set_exact'])}（双方にHFACS層あり {a['both_have_hfacs_layer']}→{b['both_have_hfacs_layer']}）|{fmt(ka['kappa'])} → {fmt(kb['kappa'])}（{ka['n']}→{kb['n']}）|")
    lines += ['', '全体κは異なる3ペアを束ねた参考値であり、6名の共通評価対象に対するκではない。前後で分類が空になる場合などは層一致の分母が変わるため、その件数と同じ対応IDの結果を併記。先頭ラベルへ強制的に単一化していない。', '',
        '同じ要因が前後の両時点で双方からHFACS分類されている部分だけに分母を固定すると、以下となる。「候補が一つでも重なる」と「候補集合が全く同じ」は区別する。', '',
        '|ペア|前後共通N|層集合完全一致 前→後|層候補の重なり 前→後|', '|---|---:|---|---|']
    for p, v in r['classification_paired_same_units'].items():
        lines.append(f"|{p}|{v['n_both_stage_classified']}|{fmt(v['exact_before_fixed_denominator'])} → {fmt(v['exact_after_fixed_denominator'])}|{fmt(v['overlap_before_fixed_denominator'])} → {fmt(v['overlap_after_fixed_denominator'])}|")
    lines += ['',
        '## 追加情報との統合', '',
        f"迷いなし：{r['before_analyzability'].get('clear',0)}/120 → {r['after_analyzability'].get('clear',0)}/120。情報追加は一律の一致改善を示していない。報告者の発生要因判断も提示しており、事実メタデータだけの効果、再読の効果、正確性の向上は分離できない。", '',
        '「追加しても迷いが残る」と「追加情報が無意味」は異なる。本文・報告者判断・構造化項目のどれがどの帰属を支持したかを、症例別一覧で確認する。情報不足が不一致を生んだという因果証明、報告書全体や院内原報告の品質評価とはしない。', '',
        f"主体等の不明をどちらかが報告した{r['actor_unclear_association_exploratory']['True']['cases']}症例の暫定factor F1は{fmt(r['actor_unclear_association_exploratory']['True']['micro_f1'])}、報告しなかった{r['actor_unclear_association_exploratory']['False']['cases']}症例では{fmt(r['actor_unclear_association_exploratory']['False']['micro_f1'])}であり、予想した『主体不明ならF1が低い』という方向はこの集計では示されなかった。CIは重なり、症例構成・ペア・抽出数にも左右される。要因F1と作業時間のSpearman相関は{fmt(r['factor_f1_time_spearman_exploratory']['rho'])}で、想定した時間延長による補強は得られていない。都合のよい結論に合わせて除外や指標変更をしない。", '',
        '## 合議結果の確定と未解決', '',
        f"保存合議要因：{r['consensus']['overall']['factors']}件。分類空欄 {r['consensus']['overall']['unclassified_factors']}件、複数層候補 {r['consensus']['overall']['multilayer_factors']}件。保存要因3区分：{r['consensus']['overall']['factor_resolution_stored']}。", '',
        '空欄を原文確定とみなさない。合議で分類が変わったことだけから人側のぶれ／原文不足を切り分けない。保存メモと不一致記録から分かる範囲を示す。LLMによる3区分は探索的判定であり、人間がその場で理由を確認したデータではない。', '',
        '## AI評価の範囲', '']
    ai = r['ai_conditional_exploratory']
    if ai['available']:
        lines += [f"既存7/22凍結r03と選択済みGPT-5.6 Solを変更せず、保存合議の要因文だけを固定ノードとして提示した。原文3欄のみを入力し、合議分類・主体・3区分は分類器に見せていない。{ai['units']}要因を分類し、分類のある{ai['labeled_units']}要因の任意候補hit率：{fmt(ai['label_any_hit'])}。HFACS候補あり{ai['hfacs_labeled_units']}要因に限定したhit率は{fmt(ai['hfacs_label_any_hit'])}。分類空欄{ai['unclassified_not_scored']}件を誤答分母へ入れていない。これは多ラベル集合の完全一致ではない。", '',
            f"一意HFACS参照要因 {ai['singleton_hfacs_detailed']['n']}件の詳細分類：一致 {fmt(ai['singleton_hfacs_detailed']['raw'])}、κ {fmt(ai['singleton_hfacs_detailed']['kappa'])}。層分類：一致 {fmt(ai['singleton_hfacs_layer']['raw'])}、κ {fmt(ai['singleton_hfacs_layer']['kappa'])}。", '',
            f"LLMのみの事後3区分等：{ai['resolution_counts_llm_unverified']}。支持判定：{ai['support_counts_llm_unverified']}。人間未確認であり、主要参照基準や原文不足の確証に用いない。判定LLMと分類器が同じモデルのため、層別にも独立性の限界がある。", '']
    lines += ['**事前固定されたRSv2互換の自由抽出・根拠spanプロンプトは確認できなかったため、end-to-end factor F1の主要AI評価は未実施。固定要因を渡した分類性能で代用しない。** 新たな自由抽出評価を行うなら、今回の結果を知った後の探索的評価として別計画・別runにする。RSv1とRSv2の差をLLM支援法の有用性・非劣性と解釈しない。', '',
        '## 根拠・時間・関係', '',
        f"引用追跡可能性：{r['evidence_traceability']}。引用が原文に見つかることは意味的な完全支持の証明ではない。独立した2名の支持判定はない。", '',
        f"独立評価の保存時間（分）：{r['original_time_minutes']}。Phase2活動時間（分）：{r['phase2_active_time_minutes']}。活動時間は全作業の実時間ではない。", '',
        '関係図は主検証に必須でなく、合議すり合わせも一律ではない。graph_case_metrics.jsonの方向付きedge F1は暫定意味対応を用いた探索的値。因果の正確性を検証済みとはしない。', '',
        '## 次に必要な確認', '',
        '1. ABの承認対象確認は完了。consensus_lock.jsonの60保存版を使用し、メモ提案の追加反映や3症例の再アノテーションは行わない。' if locked else '1. ABの承認対象が保存version一覧と一致するか、承認原文又は三宅先生の記録で最終確認。Main2・17・19には9/3メモの修正提案と保存版の差があるため、ab_saved_draft_vs_memo.csvを参照。メモ上の提案を承認済みと推定して自動反映しない。DBのcompleted化は今回していない。',
        '2. alignment_review.htmlとalignment_sources_blinded.htmlで意味対応（特に部分重なり／関連のみ）を研究者が確認。AI分類・LLM事後判定はこの確認時に見ない。この確認で初めてhuman-confirmed主要factor F1を固定できる。独立回答の再アノテーションは不要。',
        '3. AI全体評価を必須とする場合、事後探索的な自由抽出評価であることを片岡先生と合意。既存分類結果を抽出性能と読み替えない。', '',
        '## 再現の入口', '',
        'README.mdにコマンド、input_manifest.jsonに入力hash、reproducibility_manifest.jsonにコードと成果物hash。events.jsonlに経過を保存。クラウド原本へ書込みなし。']
    (RUN / 'summary.md').write_text('\n'.join(lines) + '\n')
    css = 'body{font-family:Arial,"Hiragino Sans",sans-serif;color:#253238;margin:32px auto;max-width:1350px;padding:0 20px;line-height:1.55}h1{font-size:24px}h2{font-size:19px;border-bottom:1px solid #bcc7ca;padding-bottom:6px}h3{font-size:16px}table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}th,td{border:1px solid #d4dde0;padding:8px;vertical-align:top;text-align:left}th{background:#edf2f3}pre{white-space:pre-wrap;font-family:inherit;font-size:13px;background:#f6f7f8;padding:12px}section{padding:18px 0;border-bottom:2px solid #899b9e}.cols{display:grid;grid-template-columns:1fr 1fr;gap:18px}.warn{border-left:4px solid #b15b39;padding:10px;background:#fff4ed}img{max-width:100%}@media(max-width:850px){.cols{grid-template-columns:1fr}}@media print{body{margin:0;font-size:11px}section{break-before:page}details{display:block}}'
    e = lambda x: html.escape(str(x))
    content = ['<!doctype html><html lang="ja"><meta charset="utf-8"><title>RSv2統合解析</title><style>' + css + '</style><body>',
               '<h1>RSv2統合解析・症例別監査一覧</h1><p>作成日：2026-10-01　RS＝参照基準／HFACS＝人的要因の階層分類／F1＝抽出一致指標</p>',
               '<p class="warn">要因の意味対応とLLM事後判定は人間確認前の探索的データです。' + ('ABの保存版承認をユーザー確認し、60例の解析用RSを固定しました。DBはdraftのままです。' if locked else 'ABは外部承認の報告がありますがDBはdraftのままです。') + '</p>',
               '<p><a href="summary.md">集計概要</a> | <a href="alignment_review.html">意味対応の確認表</a> | <a href="README.md">再現手順</a></p>',
               '<img src="figures/factor_agreement.png" alt="暫定要因F1と分析可能性一致"><img src="figures/analyzability_transitions.png" alt="分析可能性遷移"><img src="figures/multilabel_agreement.png" alt="同じ対応要因の層集合一致と候補重なり">']
    refmap = {x['source_id']: x for x in refs}
    bmap = {(x['source_id'], x['annotator_id']): x for x in bases}
    pmap = {(x['source_id'], x['annotator_id']): x for x in after}
    for c in cases:
        sid = c['source_id']; pair = c['pair_id']; ref = refmap[sid]
        content += [f'<section id="{e(sid)}"><h2>{e(pair)} {e(c["display_id"])} <small>{e(sid)}</small></h2>']
        for field, label in [('text_main', '事例'), ('text_background', '背景'), ('text_improvement', '改善策')]:
            content += [f'<h3>{label}（全文）</h3><pre>{e(c[field])}</pre>']
        content += ['<div class="cols">']
        for actor in pair:
            b = bmap[(sid, 'annotator_'+actor)]; p = pmap[(sid, 'annotator_'+actor)]
            content += [f'<div><h3>{e(b["annotator_name"])}：{e(b["analyzability"])} → {e(p["analyzability"])}</h3>', '<table><tr><th>ID／要因</th><th>分類 前→後／根拠</th></tr>']
            for f in b['factors']:
                pf = next(x for x in p['factors'] if x['factor_id'] == f['factor_id'])
                evidence = '\n'.join(ei.get('evidence_section','')+': '+ei.get('evidence_quote','') for ei in f.get('evidence_items',[]))
                content += [f'<tr><td>{e(f["factor_id"])} {e(f["factor_text"])}</td><td>{e(f["classifications"])} → {e(pf["classifications"])}<pre>{e(evidence)}</pre></td></tr>']
            content += ['</table>', '<p>追加後の変更理由：'+e(p.get('change_note',''))+'</p>', '<p>残る迷い：'+e(p.get('difficulty_note',''))+'</p>', '<p>困難理由：'+e(p.get('difficulty_reasons',[]))+'</p>', '<p>参照追加情報：'+e(p.get('change_sources',[]))+'</p>', '</div>']
        content += ['</div>', f'<h3>保存合議 v{e(ref["version"])}／DB {e(ref["status"])}／{e(ref["analyzability"])}</h3>', '<table><tr><th>要因</th><th>分類／保存区分</th><th>LLM判定（人間未確認）</th></tr>']
        for f in ref['factors']:
            rr = next((x for x in resolution if x['source_id'] == sid and x['factor_id'] == f['factor_id']), {})
            content += [f'<tr><td>{e(f["factor_id"])} {e(f["factor_text"])}<p>{e(f.get("notes",""))}</p></td><td>{e(f.get("classifications",[]))}<p>{e(f.get("resolution_status") or "未記入")}</p></td><td>{e(rr.get("resolution","未実行"))}<p>{e(rr.get("reason",""))}</p><p>不足情報：{e(rr.get("missing_information",""))}</p></td></tr>']
        content += ['</table>', '<h3>追加公開情報（提示された全項目）</h3><table><tr><th>項目</th><th>値</th></tr>']
        content += [f'<tr><td>{e(m["id"])} {e(m["name"])}</td><td>{e(m["value"])}</td></tr>' for m in c['metadata']]
        content += ['</table></section>']
    content += ['</body></html>']
    (RUN / 'case_review.html').write_text('\n'.join(content))
    blinded = ['<!doctype html><html lang="ja"><meta charset="utf-8"><title>意味対応用原文</title><style>'+css+'</style><body><h1>意味対応確認用の原文と独立抽出</h1><p>作成日：2026-10-01。RS＝参照基準。HFACS分類・AI予測・合議修正・LLM事後判定は非表示。対応漏れの確認にも用います。</p>']
    for c in cases:
        blinded += [f'<section id="{e(c["source_id"])}"><h2>{e(c["pair_id"])} {e(c["display_id"])}</h2>']
        for field, label in [('text_main','事例'),('text_background','背景'),('text_improvement','改善策')]:
            blinded += [f'<h3>{label}（全文）</h3><pre>{e(c[field])}</pre>']
        blinded += ['<div class="cols">']
        for a in c['pair_id']:
            b = bmap[(c['source_id'], 'annotator_' + a)]
            blinded += [f'<div><h3>{e(b["annotator_name"])}</h3><table><tr><th>ID／要因</th><th>保存された根拠</th></tr>']
            for f in b['factors']:
                evidence = '\n'.join(ei.get('evidence_section','')+': '+ei.get('evidence_quote','') for ei in f.get('evidence_items',[]))
                blinded += [f'<tr><td>{e(f["factor_id"])} {e(f["factor_text"])}</td><td><pre>{e(evidence)}</pre></td></tr>']
            blinded += ['</table></div>']
        blinded += ['</div></section>']
    (RUN / 'alignment_sources_blinded.html').write_text('\n'.join(blinded + ['</body></html>']))
    table = ['<!doctype html><html lang="ja"><meta charset="utf-8"><title>意味対応確認</title><style>'+css+'</style><body><h1>要因の意味対応：研究者確認用</h1><p>作成日：2026-10-01。F1＝抽出一致。AI補助の暫定対応であり人間未確認。sameのみ主案、partialは感度解析、causal_related／actor_diffは対応数に含めません。原文リンク先も分類・AI予測を隠しています。対応漏れは全独立要因一覧から確認できます。</p><table><tr><th>症例</th><th>左</th><th>右</th><th>判定と理由</th></tr>']
    for m in matches:
        table += [f'<tr><td><a href="alignment_sources_blinded.html#{e(m["source_id"])}">{e(m["pair"])} {e(m["display_id"])}</a></td><td>{e(m["left"])} {e(m["left_text"])}<pre>{e(json.dumps(m["left_evidence"],ensure_ascii=False))}</pre></td><td>{e(m["right"])} {e(m["right_text"])}<pre>{e(json.dumps(m["right_evidence"],ensure_ascii=False))}</pre></td><td>{e(m["relation"])}<p>{e(m["rationale"])}</p><p>同一引用：{e(m["strict_quote_match"])}</p></td></tr>']
    (RUN / 'alignment_review.html').write_text('\n'.join(table + ['</table></body></html>']))

if __name__ == '__main__':
    main()
