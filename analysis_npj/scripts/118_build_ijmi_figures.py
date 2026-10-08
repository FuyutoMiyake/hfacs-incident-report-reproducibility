#!/usr/bin/env python3
"""Build four vector figures from saved results without recomputing inference."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import ContentStream
from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, Rect, String
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis_npj/manuscript/figures/ijmi_20261004"
FINAL = ROOT / "analysis_npj/prompt_adaptation/split50x3_20260722"
RUN = ROOT / "analysis_npj/analysis_runs/consultation_data_audit_20261002"
FLAT = ROOT / "analysis_npj/results/flat_vs_fta"
INPUTS = [
    RUN / "analysis.json",
    FINAL / "final_results/final_results.json",
    FINAL / "final_results_kimi_k26/kimi_k26_final_results.json",
    FINAL / "split_manifest.json",
    ROOT / "analysis_npj/derived/rsv2_main60_sampling_manifest.json",
    ROOT / "analysis_npj/derived/canonical_cases.csv",
    ROOT / "analysis_npj/derived/canonical_nodes.csv",
    FLAT / "aggregate_metrics.csv",
    FLAT / "micro_category_metrics.csv",
    FLAT / "paired_differences.csv",
]
INK, GRAY, GRID = "#202124", "#62666B", "#DADDE0"
TEAL, ROSE = "#16736B", "#A44363"
PROVENANCE = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def unique(rows, **criteria):
    found = [r for r in rows if all(r[k] == v for k, v in criteria.items())]
    if len(found) != 1:
        raise ValueError((criteria, len(found)))
    return found[0]


def text(d, x, y, value, size=12, bold=False, color=INK, anchor="start"):
    font = "Arial-Bold" if bold else "Arial"
    width = pdfmetrics.stringWidth(str(value), font, size)
    left = x - width if anchor == "end" else x - width / 2 if anchor == "middle" else x
    if left < -0.5 or left + width > d.width + 0.5 or y < 0 or y + size > d.height + 2:
        raise ValueError(f"Text outside figure: {value!r} {(left, y, width)}")
    d.add(String(x, y, str(value), fontName=font, fontSize=size,
                 fillColor=HexColor(color), textAnchor=anchor))


def lines(d, x, y, values, size=12, leading=17, **kwargs):
    for i, value in enumerate(values):
        text(d, x, y - i * leading, value, size=size, **kwargs)


def line(d, x1, y1, x2, y2, color=GRID, width=1, dash=None):
    d.add(Line(x1, y1, x2, y2, strokeColor=HexColor(color), strokeWidth=width,
               strokeDashArray=dash))


def arrow(d, points, color=GRAY, dash=None):
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        line(d, x1, y1, x2, y2, color, 1.25, dash)
    (x1, y1), (x2, y2) = points[-2:]
    angle = math.atan2(y2-y1, x2-x1)
    bx, by = x2 - 7*math.cos(angle), y2 - 7*math.sin(angle)
    nx, ny = 3*math.sin(angle), -3*math.cos(angle)
    d.add(Polygon([x2, y2, bx+nx, by+ny, bx-nx, by-ny],
                  fillColor=HexColor(color), strokeColor=None))


def box(d, x, y, w, h, heading, body, color=TEAL):
    d.add(Rect(x, y, w, h, fillColor=white, strokeColor=HexColor(GRID), strokeWidth=1))
    line(d, x, y+h, x+w, y+h, color, 2)
    text(d, x+14, y+h-25, heading, 14, True)
    lines(d, x+14, y+h-47, body, 11.5, 17)


def interval(d, xmap, y, point, low, high, color, secondary=False):
    x, lo, hi = xmap(point), xmap(low), xmap(high)
    line(d, lo, y, hi, y, color, 1.8)
    line(d, lo, y-4, lo, y+4, color, 1.2)
    line(d, hi, y-4, hi, y+4, color, 1.2)
    if secondary:
        d.add(Rect(x-3.5, y-3.5, 7, 7, fillColor=white,
                   strokeColor=HexColor(color), strokeWidth=1.6))
    else:
        d.add(Circle(x, y, 3.8, fillColor=HexColor(color), strokeColor=None))


def figure1(a, primary, sampling, split, cases, nodes):
    d = Drawing(780, 650)
    n1 = len(cases)
    n1ok = sum(r["canonical_analyzability"] == "分析可能" for r in cases)
    n2 = sampling["sampling"]["main_n"]
    c = a["consensus"]["overall"]
    total_responses = sum(sum(row) for row in a["transitions"])
    box(d, 181, 566, 418, 65, "JCQHC public records, 2010-2024",
        [f"{sampling['universe']['total_unique_cases']:,} records; three narrative fields"], GRAY)
    arrow(d, [(390, 566), (390, 536), (193, 536), (193, 507)])
    arrow(d, [(390, 536), (588, 536), (588, 507)])
    box(d, 24, 369, 338, 138, f"RSv1: AI-assisted review ({n1} records)",
        [f"Sampling seed 150; {2*n1} independent responses",
         f"AI-generated FTA: {len(nodes):,} original nodes",
         "Six reviewers in three pairs; 50 records/pair",
         "Agreement between independent reviewers",
         "on jointly retained leaf nodes"])
    box(d, 418, 393, 338, 114, f"RSv2: direct extraction ({n2} new records)",
        [f"Sampling seed {sampling['sampling']['seed']}; {2*n2} responses",
         "No AI candidate tree; 20 records/pair",
         "Five separate pilot records excluded from evaluation"], ROSE)
    arrow(d, [(193, 369), (193, 346)])
    arrow(d, [(588, 393), (588, 347)])
    box(d, 24, 273, 338, 73, "Pair-adjudicated RSv1",
        [f"{n1ok} analysable; {n1-n1ok} not analysable"])
    counts = c["analyzability"]
    box(d, 418, 224, 338, 123, "Pair-adjudicated RSv2",
        [f"{c['factors']} saved consensus factors in {c['cases']} records",
         f"Case analysability: without uncertainty, {counts['clear']};",
         f"with uncertainty, {counts['uncertain']}; not analysable, {counts['not_analyzable']}",
         "Exploratory AI classification of fixed human factors"], ROSE)
    # Both analyses branch from the same reference; neither is a further cohort filter.
    arrow(d, [(193, 273), (193, 265), (193, 257)])
    arrow(d, [(193, 265), (12, 265), (12, 190), (193, 190), (193, 178)])
    box(d, 24, 196, 338, 61, "FTA added-value analyses",
        ["Structural rankings and direct-classification baseline"])
    pop = primary["population"]
    box(d, 24, 64, 338, 114, "RSv1 frozen classification reanalysis",
        [f"Development {split['development']['n_cases']} / selection {split['selection']['n_cases']} / final {split['final']['n_cases']}",
         f"Final evaluation set: {split['final']['n_cases']} records;",
         f"{pop['analyzable_cases']} analysable, comprising {pop['hfacs_leaves']} leaf nodes",
         "Selected primary model and secondary Kimi evaluation"])
    box(d, 418, 64, 338, 114, "RSv2 public-information reassessment",
        [f"Same {n2} records and {total_responses} saved individual responses",
         "Public fields include reporter-assigned causes",
         "Independent reassessment; no second consensus"], ROSE)
    arrow(d, [(756, 439), (769, 439), (769, 121), (756, 121)], ROSE, [4, 3])
    text(d, 24, 26, "RSv1 and RSv2 are different cohorts and tasks, not a before-after performance comparison.", 11)
    PROVENANCE["figure1"] = {
        "source_records": sampling["universe"]["total_unique_cases"],
        "rsv1_records": n1, "rsv1_independent_responses": 2*n1,
        "rsv1_original_nodes": len(nodes), "rsv1_analysable": n1ok,
        "rsv2_records": n2, "rsv2_consensus_factors": c["factors"],
        "rsv2_reassessment_responses": total_responses,
        "role": "Study flow; dashed arrow reuses individual responses, not consensus answers.",
    }
    return d


def figure2(a, primary, secondary):
    d = Drawing(780, 610)
    xmap = lambda v: 210 + 337*v
    for value in [0, .2, .4, .6, .8, 1]:
        x = xmap(value)
        line(d, x, 300, x, 505, GRID, .7)
        line(d, x, 107, x, 211, GRID, .7)
        text(d, x, 87, f"{value:.1f}", 10, anchor="middle")
    text(d, 24, 577, "A. RSv1: AI classification agreement with the adjudicated reference", 14, True)
    text(d, 24, 555, "37 analysable records; 306 leaves from the frozen final set of 50 records", 11)
    d.add(Circle(30, 531, 3.8, fillColor=HexColor(TEAL), strokeColor=None))
    text(d, 41, 527, "GPT-5.6 Sol: selected primary model", 10.5)
    d.add(Rect(328, 527, 7, 7, fillColor=white, strokeColor=HexColor(ROSE), strokeWidth=1.6))
    text(d, 341, 527, "Kimi K2.6: secondary evaluation", 10.5)
    text(d, 587, 508, "Kappa [95% CI]", 11, True)
    all_rows = []
    for y, key, label in [(477, "detailed20", "Detailed categories"),
                          (409, "tier5", "Layers + non-HFACS"),
                          (341, "binary", "HFACS / non-HFACS")]:
        text(d, 24, y-10, label, 11.5)
        for offset, model, data, color, second in [(0, "GPT-5.6 Sol", primary, TEAL, False),
                                                  (-23, "Kimi K2.6", secondary, ROSE, True)]:
            value = data[key]
            point = value["cohens_kappa"]
            low, high = value["cohens_kappa_ci95"]
            interval(d, xmap, y+offset, point, low, high, color, second)
            text(d, 587, y+offset-4, f"{point:.3f} [{low:.3f}, {high:.3f}]", 10.5, color=color)
            all_rows.append(dict(cohort="RSv1", model=model, metric=key,
                                 estimate=point, ci_low=low, ci_high=high, n=value["n"]))
    line(d, 24, 283, 752, 283, INK, .8)
    text(d, 24, 257, "B. RSv2: classification of human-adjudicated factors (exploratory)", 14, True)
    text(d, 24, 235, "75 singleton-HFACS reference factors; GPT-5.6 Sol; not end-to-end extraction", 11)
    for y, key, label in [(195, "singleton_hfacs_detailed", "Detailed HFACS reference"),
                          (142, "singleton_hfacs_layer", "L1-L4 reference")]:
        value = a["ai_conditional_exploratory"][key]
        point = value["kappa"]
        low, high = value["case_bootstrap_ci95"]["low"], value["case_bootstrap_ci95"]["high"]
        interval(d, xmap, y, point, low, high, TEAL)
        text(d, 24, y-4, label, 11.5)
        text(d, 587, y-4, f"{point:.3f} [{low:.3f}, {high:.3f}]", 10.5, color=TEAL)
        all_rows.append(dict(cohort="RSv2", model="GPT-5.6 Sol", metric=key,
                             estimate=point, ci_low=low, ci_high=high, n=value["n"]))
    text(d, 378, 59, "Cohen's kappa with record-cluster bootstrap 95% confidence intervals", 11, anchor="middle")
    text(d, 24, 25, "Different units and label spaces: these estimates do not measure improvement from RSv1 to RSv2.", 10.5)
    PROVENANCE["figure2"] = all_rows
    return d


def figure3(diffs, aggregates, micro):
    d = Drawing(780, 480)
    xmap = lambda v: 300 + (v+.30)/.50*265
    text(d, 24, 450, "FTA prompting versus direct HFACS category prediction (exploratory)", 14, True)
    text(d, 24, 427, "87 analysable RSv1 records; Main 11-50 within each pair; improvement narrative withheld", 11)
    text(d, 588, 389, "Difference [95% CI]", 11, True)
    for v in [-.3, -.2, -.1, 0, .1, .2]:
        x = xmap(v)
        line(d, x, 105, x, 372, INK if v == 0 else GRID, 1.1 if v == 0 else .7)
        text(d, x, 84, f"{v:+.1f}" if v else "0", 10, anchor="middle")
    records = []
    definitions = [
        ("augmented_reference", "precision", "Mean precision"),
        ("augmented_reference", "recall", "Mean recall"),
        ("all_hfacs", "micro_f1", "Micro-F1, all HFACS"),
        ("l3_l4", "micro_f1", "Micro-F1, L3/L4"),
    ]
    for y, (target, metric, label) in zip([352, 280, 208, 136], definitions):
        row = unique(diffs, analysis_set="primary_main11_50", target=target,
                     comparison="fta_minus_flat", metric=metric)
        point, low, high = map(float, [row["estimate"], row["ci_low"], row["ci_high"]])
        values = {}
        for method in ["fta", "flat"]:
            if metric == "micro_f1":
                item = unique(micro, analysis_set="primary_main11_50", scope=target, method=method)
                values[method] = float(item["f1"])
            else:
                item = unique(aggregates, analysis_set="primary_main11_50", target=target,
                              method=method, metric=metric)
                values[method] = float(item["estimate"])
        if not math.isclose(values["fta"]-values["flat"], point, abs_tol=1e-12):
            raise ValueError("FTA paired point difference does not match its plotted estimates")
        color = TEAL if point >= 0 else ROSE
        text(d, 24, y+2, label, 12, True)
        text(d, 24, y-17, f"FTA {values['fta']:.3f}; direct {values['flat']:.3f}", 10.5, color=GRAY)
        interval(d, xmap, y, point, low, high, color)
        text(d, 588, y-4, f"{point:+.3f} [{low:+.3f}, {high:+.3f}]", 10.5, color=color)
        records.append(dict(target=target, metric=metric, estimate=point, ci_low=low,
                            ci_high=high, n_records=int(row["n_cases"]), **values))
    text(d, 432, 59, "Paired difference (FTA minus direct classification)", 11, anchor="middle")
    text(d, 24, 26, "Precision/recall are case-level means; micro-F1 pools category counts. CIs use 2,000 record resamples.", 10.5)
    PROVENANCE["figure3"] = records
    return d


def figure4(a):
    d = Drawing(780, 575)
    matrix = a["transitions"]
    totals = [sum(row) for row in matrix]
    after = [sum(matrix[r][c] for r in range(3)) for c in range(3)]
    total = sum(totals)
    improved = sum(matrix[r][c] for r in range(3) for c in range(3) if c > r)
    worse = sum(matrix[r][c] for r in range(3) for c in range(3) if c < r)
    same = sum(matrix[r][r] for r in range(3))
    text(d, 24, 541, "Public-information addition: within-reviewer analysability transitions", 14, True)
    text(d, 24, 518, f"60 records x 2 reviewers = {total} paired reviewer assessments", 11)
    text(d, 408, 474, "AFTER additional public information", 11.5, True, anchor="middle")
    labels = [["Not analysable"], ["Analysable with", "uncertainty"],
              ["Analysable without", "uncertainty"]]
    for col in range(3):
        lines(d, 277.5+135*col, 445, labels[col], size=11.5, leading=15, anchor="middle")
    lines(d, 192, 445, ["BEFORE additional", "public information"], size=11, leading=15,
          bold=True, anchor="end")
    for row in range(3):
        y = 302 - 95*row
        lines(d, 192, y+53, labels[row], size=11.5, leading=15, anchor="end")
        text(d, 192, y+13, f"n = {totals[row]}", 10.5, anchor="end", color=GRAY)
        for col in range(3):
            fill = "#EEF0F2" if row == col else "#DDEEE9" if col > row else "#F3E1E6"
            x = 210 + col*135
            d.add(Rect(x, y, 135, 95, fillColor=HexColor(fill), strokeColor=white, strokeWidth=2))
            count = matrix[row][col]
            text(d, x+67.5, y+47, str(count), 26, True, anchor="middle")
            text(d, x+67.5, y+23, f"{100*count/totals[row]:.1f}% of row", 10.5, anchor="middle", color=GRAY)
    for col, n in enumerate(after):
        text(d, 277.5+135*col, 91, f"After n = {n}", 10.5, anchor="middle")
    for x, count, label, color in [(24, improved, "More analysable", TEAL),
                                 (287, same, "Same rating", INK),
                                 (532, worse, "Less analysable", ROSE)]:
        text(d, x, 55, f"{label}: {count}/{total} ({100*count/total:.1f}%)", 11.5, True, color=color)
    text(d, 24, 24, "Sequential, non-blinded reassessment includes reporter-assigned causes; not a causal metadata effect.", 10.5)
    PROVENANCE["figure4"] = dict(matrix=matrix, row_totals=totals, column_totals=after,
                                 responses=total, records=total//2, more_analysable=improved,
                                 less_analysable=worse, unchanged=same,
                                 unit="paired reviewer response", percentage_denominator="row total")
    return d


def wrap(value, width, font="Arial", size=10.5):
    result, current = [], ""
    for word in value.split():
        trial = current + (" " if current else "") + word
        if pdfmetrics.stringWidth(trial, font, size) > width and current:
            result.append(current)
            current = word
        else:
            current = trial
    return result + ([current] if current else [])


def captions():
    return [
        ("Figure1_study_flow", "Study flow and distinct evaluation cohorts",
         "RSv1 used AI-generated fault tree analysis (FTA) candidates and 150 public records. RSv2 involved independent human factor extraction without AI-generated candidates in 60 new records, following a separate five-record pilot. The dashed path carries independent responses into public-information reassessment, not consensus answers. RSv1 and RSv2 involved different records and tasks; differences between their scores should not be interpreted as performance improvement. The 50/50/50 classification split was a later reanalysis, not an untouched external cohort. AI, artificial intelligence; JCQHC, Japan Council for Quality Health Care; RS, reference standard.",
         "RSv1とRSv2は別症例・別課題です。破線は独立回答を追加情報確認へ再利用する経路です。"),
        ("Figure2_ai_classification_agreement", "AI classification agreement with human reference standards",
         "Points show Cohen's kappa and record-cluster bootstrap 95% confidence intervals. A: 306 leaves from 37 analysable RSv1 records (5,000 resamples); detailed and layer scoring included non-HFACS categories. GPT-5.6 Sol was primary and Kimi K2.6 secondary. B: fixed consensus factors, scored against 75 singleton-HFACS RSv2 references (3,000 resamples); non-HFACS predictions were retained. Panel B is exploratory conditional classification, not end-to-end extraction. Cohorts, units and label spaces differ between panels. AI, artificial intelligence; HFACS, Human Factors Analysis and Classification System; RS, reference standard.",
         "RSv2は人間が抽出した固定要因の分類で、原文からのAI自由抽出ではありません。RSv1との数値差を改善・悪化とは扱いません。"),
        ("Figure3_fta_added_value", "FTA versus direct HFACS category prediction under matched input conditions",
         "Points show paired differences (fault tree analysis [FTA] minus direct classification) and 95% record-bootstrap confidence intervals in 87 analysable first-reference-standard (RSv1) records from Main 11-50 within each reviewer pair. Both methods used Kimi K2.5 with the event description and background as inputs; improvement measures were excluded. The reference comprised report-level HFACS category sets derived from RSv1 consensus labels and categories from reviewer-added factors. Precision and recall are record-level means; micro-F1 pools category counts. Intervals came from the saved 2,000-resample analysis, not rounded values. This exploratory comparison followed the FTA scale-up gate and does not measure clinical benefit. L3, unsafe supervision; L4, organisational influences.",
         "FTAではPrecisionが上がる一方、Recallは下がっています。全分類のF1差の区間は0をまたぎ、L3/L4のF1は直接分類の方が高い結果です。"),
        ("Figure4_public_information_transitions", "Analysability before and after additional public information",
         "Cells show counts and row percentages of paired reviewer assessments. The matrix compares each reviewer's rating before and after reassessment, comprising 120 paired assessments of 60 records by two reviewers per record. Green cells denote movement to a more analysable rating, gray cells an unchanged rating and rose cells a less analysable rating. Additional information included factual public fields and reporter-assigned cause judgements. Reassessment was sequential and non-blinded and could not isolate effects of metadata, rereading, prior consensus exposure or reporter judgements. Rating changes do not establish correctness or improved inter-rater agreement.",
         "追加後により分析可能な評価へ動いた回答は19件、同じ評価は94件、より困難な評価へ動いた回答は7件です。一致度や正確性の改善を直接示す図ではありません。"),
    ]


def drawn_fonts_embedded(path):
    reader = PdfReader(path)
    for page in reader.pages:
        current, used = None, set()
        for operands, operator in ContentStream(page.get_contents(), reader).operations:
            if operator == b"Tf":
                current = operands[0]
            elif operator in [b"Tj", b"TJ", b"'", b'"']:
                used.add(current)
        fonts = page["/Resources"]["/Font"].get_object()
        for name in used:
            font = fonts[name].get_object()
            descriptor = font.get("/FontDescriptor")
            if not descriptor or not descriptor.get_object().get("/FontFile2"):
                return False
    return True


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before_hashes = {str(p.relative_to(ROOT)): sha(p) for p in INPUTS}
    fonts = [("Arial", Path("/System/Library/Fonts/Supplemental/Arial.ttf")),
             ("Arial-Bold", Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"))]
    resolved_fonts = []
    for name, path in fonts:
        if not path.exists():
            import reportlab
            path = Path(reportlab.__file__).parent / "fonts" / ("VeraBd.ttf" if name.endswith("Bold") else "Vera.ttf")
        resolved_fonts.append((name, path))
        pdfmetrics.registerFont(TTFont(name, str(path)))
    a, primary, secondary, split, sampling = [read_json(p) for p in INPUTS[:5]]
    cases, nodes = read_csv(INPUTS[5]), read_csv(INPUTS[6])
    aggregate, micro, diffs = [read_csv(p) for p in INPUTS[7:]]
    figures = [figure1(a, primary, sampling, split, cases, nodes),
               figure2(a, primary, secondary), figure3(diffs, aggregate, micro), figure4(a)]
    descriptions = captions()
    for d, (stem, title, caption, _) in zip(figures, descriptions):
        renderSVG.drawToFile(d, str(OUT / (stem+".svg")))
        c = canvas.Canvas(str(OUT / (stem+".pdf")), pagesize=(d.width, d.height), invariant=1)
        c.setTitle(title)
        c.setAuthor("Fuyuto Miyake")
        renderPDF.draw(d, c, 0, 0)
        c.save()
        subprocess.run(["pdftoppm", "-singlefile", "-r", "160", "-png",
                        str(OUT / (stem+".pdf")), str(OUT / stem)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    combined = OUT / "IJMI_figures_review_20261004.pdf"
    c = canvas.Canvas(str(combined), invariant=1)
    c.setTitle("IJMI figure review 4 October 2026")
    c.setAuthor("Fuyuto Miyake")
    for index, (d, (_, title, caption, _)) in enumerate(zip(figures, descriptions), 1):
        caption_lines = wrap(caption, d.width, size=10.5)
        footer_height = 30+15*len(caption_lines)
        abbreviations = wrap("AI: artificial intelligence; RS: reference standard; FTA: fault tree analysis; HFACS: Human Factors Analysis and Classification System; JCQHC: Japan Council for Quality Health Care; CI: confidence interval.", d.width, size=8.5)
        header_height = 80+11*(len(abbreviations)-1)
        title_y = d.height+footer_height+header_height-31
        c.setPageSize((d.width+40, d.height+footer_height+header_height))
        c.setFont("Arial-Bold", 15)
        c.drawString(20, title_y, f"Figure {index}  {title}")
        c.setFont("Arial", 9)
        c.drawString(20, title_y-15, "Created: 4 October 2026")
        c.setFont("Arial", 8.5)
        for i, value in enumerate(abbreviations):
            c.drawString(20, title_y-29-11*i, value)
        renderPDF.draw(d, c, 20, footer_height+10)
        c.setFont("Arial", 10.5)
        for i, value in enumerate(caption_lines):
            c.drawString(20, footer_height-10-15*i, value)
        c.showPage()
    c.save()
    (OUT / "figure_data.json").write_text(json.dumps(PROVENANCE, indent=2)+"\n")
    title = "# IJMI Figure Captions\n\nCreated: 4 October 2026\n\nAbbreviations: AI, artificial intelligence; FTA, fault tree analysis; HFACS, Human Factors Analysis and Classification System; JCQHC, Japan Council for Quality Health Care; RS, reference standard; CI, confidence interval.\n\n"
    (OUT / "captions.md").write_text(title + "\n\n".join(
        f"## Figure {i} {title}\n\n{caption}" for i, (_, title, caption, _) in enumerate(descriptions, 1))+"\n")
    sections = []
    for i, (stem, title, caption, japanese) in enumerate(descriptions, 1):
        sections.append(f'<section id="figure{i}"><h2>Figure {i} {html.escape(title)}</h2>'
                        f'<p>{html.escape(japanese)}</p><img src="{stem}.svg" alt="{html.escape(title)}">'
                        f'<p class="files"><a href="{stem}.svg">SVG</a> / <a href="{stem}.pdf">PDF</a> / <a href="{stem}.png">PNG</a></p>'
                        f'<p class="caption">{html.escape(caption)}</p></section>')
    (OUT / "index.html").write_text('<!doctype html><html lang="ja"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>IJMI 図案 2026-10-04</title>'
        '<style>body{margin:0;color:#202124;background:#fff;font:16px/1.7 Arial,sans-serif;letter-spacing:0}'
        'main{max-width:1040px;margin:auto;padding:28px 24px}h1{font-size:26px}h2{font-size:20px}'
        'a{color:#16736b}nav{display:flex;flex-wrap:wrap;gap:18px;border-bottom:1px solid #dadde0;padding:14px 0}'
        'section{padding:30px 0;border-bottom:1px solid #dadde0}img{display:block;width:100%;height:auto;margin:18px 0}'
        '.caption{font-size:14px;color:#62666b}.files{margin:8px 0}@media(max-width:600px){main{padding:16px}h1{font-size:22px}}</style>'
        '<main><h1>IJMI 論文用図案</h1><p>作成日：2026-10-04。固定済み解析から生成したレビュー用4図です。'
        'RSv1とRSv2は別症例・別課題であり、情報追加は非盲検の再評価です。</p>'
        '<p>RS＝参照基準、FTA＝故障の木解析、HFACS＝人的要因分類体系、CI＝信頼区間。</p>'
        '<p><a href="IJMI_figures_review_20261004.pdf">4図と英文キャプションのPDF</a> / '
        '<a href="figure_data.json">図の数値</a> / <a href="captions.md">英文キャプション</a></p>'
        '<nav>'+''.join(f'<a href="#figure{i}">Figure {i}</a>' for i in range(1,5))+'</nav>'
        +''.join(sections)+'</main></html>')
    after_hashes = {str(p.relative_to(ROOT)): sha(p) for p in INPUTS}
    checks = {"source_inputs_unchanged": before_hashes == after_hashes,
              "four_figure_pdf_pages": len(PdfReader(combined).pages) == 4,
              "120_reassessment_responses": PROVENANCE["figure4"]["responses"] == 120,
              "transition_counts_19_94_7": [PROVENANCE["figure4"][k] for k in ["more_analysable","unchanged","less_analysable"]] == [19,94,7],
              "row_margins_match_saved_before": PROVENANCE["figure4"]["row_totals"] == [a["before_analyzability"][k] for k in ["not_analyzable","uncertain","clear"]],
              "column_margins_match_saved_after": PROVENANCE["figure4"]["column_totals"] == [a["after_analyzability"][k] for k in ["not_analyzable","uncertain","clear"]],
              "rsv1_final_population_matches_secondary": all(primary["population"][k] == secondary["population"][k] for k in ["all_cases","analyzable_cases","hfacs_leaves"]),
              "rsv2_analysis_population_matches_sampling": a["consensus"]["overall"]["cases"] == sampling["sampling"]["main_n"],
              "svg_editable_text": all("<text" in (OUT/(stem+".svg")).read_text() for stem, *_ in descriptions),
              "individual_pdf_single_page": all(len(PdfReader(OUT/(stem+".pdf")).pages) == 1 for stem, *_ in descriptions),
              "drawn_pdf_text_fonts_embedded": all(drawn_fonts_embedded(p) for p in [combined]+[OUT/(stem+".pdf") for stem, *_ in descriptions])}
    if not all(checks.values()):
        raise ValueError(checks)
    manifest = dict(date="2026-10-04", build_command=f"{sys.executable} analysis_npj/scripts/118_build_ijmi_figures.py",
                    generator_sha256=sha(Path(__file__)), source_inputs_sha256=before_hashes,
                    font_inputs_sha256={str(p):sha(p) for _, p in resolved_fonts}, checks=checks,
                    underlying_analysis_recomputed=False, new_ai_calls=False,
                    scientific_qc="Semantic matches remain unconfirmed; visual review is not scientific validation.",
                    visual_review={"status":"pending"},
                    output_sha256={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.suffix in [".svg",".pdf",".png",".html"] or p.name in ["figure_data.json", "captions.md"]})
    (OUT / "figure_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"output_directory":str(OUT),"figures":4,"checks_passed":len(checks)}))


if __name__ == "__main__":
    main()
