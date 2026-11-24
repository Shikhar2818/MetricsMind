import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

BASE = Path(__file__).resolve().parent
OUT = BASE / "PulseGrid_Project_Guide.docx"

NAVY = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2E, 0x5C, 0x9A)
GREY = RGBColor(0x59, 0x5F, 0x69)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
RED = RGBColor(0xA6, 0x1B, 0x1B)

TOKEN = re.compile(r"(\*\*.+?\*\*|\*[^*\n]+?\*|`[^`]+`)")


def rich(p, text, size=None, color=None, italic=False):
    for part in TOKEN.split(str(text)):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = p.add_run(part[1:-1])
            r.italic = True
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = "Consolas"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
            if size:
                r.font.size = Pt(size - 0.5)
        else:
            r = p.add_run(part)
        if size and not (part.startswith("`") and part.endswith("`")):
            r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color
        if italic:
            r.italic = True
    return p


def P(doc, text="", size=10.5, before=0, after=5, align=None, color=None, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.12
    if align:
        p.alignment = align
    if text:
        rich(p, text, size=size, color=color, italic=italic)
    return p


def B(doc, text, level=0, size=10.5):
    style = "List Bullet" if level == 0 else "List Bullet 2"
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.1
    rich(p, text, size=size)
    return p


def N(doc, text, size=10.5):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.1
    rich(p, text, size=size)
    return p


def H1(doc, text, page_break=True):
    if page_break:
        doc.add_page_break()
    h = doc.add_heading(level=1)
    h.paragraph_format.space_before = Pt(2)
    h.paragraph_format.space_after = Pt(8)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.size = Pt(19)
    r.font.color.rgb = NAVY
    r.bold = True
    # bottom rule
    pPr = h._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), "1F3864")
    pbdr.append(bottom)
    pPr.append(pbdr)
    return h


def H2(doc, text):
    h = doc.add_heading(level=2)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.size = Pt(13.5)
    r.font.color.rgb = BLUE
    r.bold = True
    return h


def H3(doc, text):
    h = doc.add_heading(level=3)
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(3)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.size = Pt(11.5)
    r.font.color.rgb = DARK
    r.bold = True
    return h


def set_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def cell_margins(table, top=40, bottom=40, left=80, right=80):
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for tag, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{tag}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblPr.append(mar)


def add_table(doc, headers, rows, widths, font=9, header_bg="1F3864", zebra="F2F5FA",
              bold_first=False, center_from=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.autofit = False
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_margins(t)
    hdr = t.rows[0]
    trPr = hdr._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    trPr.append(repeat)
    for i, h in enumerate(headers):
        c = hdr.cells[i]
        c.width = Inches(widths[i])
        set_bg(c, header_bg)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(font)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for ri, row in enumerate(rows):
        new_row = t.add_row()
        trPr2 = new_row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        trPr2.append(cant)
        cells = new_row.cells
        for i, val in enumerate(row):
            c = cells[i]
            c.width = Inches(widths[i])
            if zebra and ri % 2 == 1:
                set_bg(c, zebra)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.line_spacing = 1.05
            rich(p, str(val), size=font)
            if bold_first and i == 0:
                for r in p.runs:
                    r.bold = True
            if center_from is not None and i >= center_from:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    P(doc, "", after=2)
    return t


def callout(doc, title, body, bg="EAF1FB", bar="1F3864", title_color=NAVY):
    t = doc.add_table(rows=1, cols=1)
    t.autofit = False
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    c.width = Inches(6.7)
    set_bg(c, bg)
    tcPr = c._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "24" if edge == "left" else "4")
        el.set(qn("w:color"), bar)
        borders.append(el)
    tcPr.append(borders)
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = title_color
    p2 = c.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(4)
    p2.paragraph_format.line_spacing = 1.12
    rich(p2, body, size=9.5)
    P(doc, "", after=2)


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    rich(p, text, size=8.5, color=GREY, italic=True)


def add_field(paragraph, instr):
    run = paragraph.add_run()
    f1 = OxmlElement("w:fldChar")
    f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    f2 = OxmlElement("w:fldChar")
    f2.set(qn("w:fldCharType"), "end")
    run._r.append(f1)
    run._r.append(it)
    run._r.append(f2)


doc = Document()

# page setup
sec = doc.sections[0]
sec.page_width = Inches(8.5)
sec.page_height = Inches(11)
sec.left_margin = Inches(0.9)
sec.right_margin = Inches(0.9)
sec.top_margin = Inches(0.8)
sec.bottom_margin = Inches(0.8)
sec.different_first_page_header_footer = True

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(10.5)
normal.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
normal.paragraph_format.space_after = Pt(5)

doc.core_properties.title = "PulseGrid - Complete Project Guide"
doc.core_properties.subject = "AI-Powered Infrastructure Anomaly Detection & Forecasting"
doc.core_properties.author = "PulseGrid project"

# header + footer (not on cover)
hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = hp.add_run("PulseGrid  ·  AI Infrastructure Monitoring  ·  Project Guide")
hr.font.size = Pt(8)
hr.font.color.rgb = RGBColor(0x8A, 0x90, 0x9C)

fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r1 = fp.add_run("Page ")
r1.font.size = Pt(8.5)
r1.font.color.rgb = GREY
add_field(fp, "PAGE")
r2 = fp.add_run(" of ")
r2.font.size = Pt(8.5)
r2.font.color.rgb = GREY
add_field(fp, "NUMPAGES")
for r in fp.runs:
    r.font.size = Pt(8.5)
    r.font.color.rgb = GREY

# ============================ COVER ============================
P(doc, "", after=26)
band = doc.add_table(rows=1, cols=1)
band.autofit = False
band.alignment = WD_TABLE_ALIGNMENT.CENTER
bc = band.cell(0, 0)
bc.width = Inches(6.7)
set_bg(bc, "1F3864")
bp = bc.paragraphs[0]
bp.paragraph_format.space_before = Pt(28)
bp.paragraph_format.space_after = Pt(4)
br = bp.add_run("PulseGrid")
br.font.size = Pt(38)
br.bold = True
br.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
bp2 = bc.add_paragraph()
bp2.paragraph_format.space_before = Pt(0)
bp2.paragraph_format.space_after = Pt(26)
br2 = bp2.add_run("AI-Powered Infrastructure Anomaly Detection & Forecasting")
br2.font.size = Pt(13)
br2.font.color.rgb = RGBColor(0xC9, 0xD8, 0xEE)

P(doc, "", after=24)
p = P(doc, "The Complete Plain-English Guide", size=22, after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
for r in p.runs:
    r.bold = True
    r.font.color.rgb = NAVY
p = P(doc, "Every tab, every number, every term explained", size=13, after=3, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY)
P(doc, "plus a ready-to-use plan for presenting it to your teacher", size=11, after=30, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY, italic=True)

fact_rows = [
    ["What this is", "A monitoring dashboard that learns how each server normally behaves, flags unusual minutes, and forecasts CPU and disk."],
    ["The data", "8 synthetic servers × 45 days × 1 minute = 518,400 rows (3.1 million metric values)"],
    ["The models", "Isolation Forest (detection) + XGBoost (CPU forecast) + 7-day disk trend + a rule-based risk engine"],
    ["The app", "FastAPI backend + Next.js dashboard with 4 screens"],
    ["Written for", "Someone who knows about 10% of this project — no prior ML needed"],
]
t = doc.add_table(rows=0, cols=2)
t.autofit = False
t.alignment = WD_TABLE_ALIGNMENT.CENTER
cell_margins(t)
for k, v in fact_rows:
    cells = t.add_row().cells
    cells[0].width = Inches(1.55)
    cells[1].width = Inches(5.15)
    set_bg(cells[0], "EDF1F7")
    p0 = cells[0].paragraphs[0]
    r = p0.add_run(k)
    r.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = NAVY
    p1 = cells[1].paragraphs[0]
    rich(p1, v, size=9.5)
    for c in (cells[0], cells[1]):
        for para in c.paragraphs:
            para.paragraph_format.space_before = Pt(3)
            para.paragraph_format.space_after = Pt(3)

P(doc, "", after=26)
P(doc, "Prepared November 2026  ·  Read Section 1 first, then keep Section 12 (the presentation script) open on the day.",
  size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY, italic=True)

# ============================ CONTENTS ============================
H1(doc, "Contents")
P(doc, "This guide is written in the order you should learn it. You do not need to memorise it — you need to understand Sections 2, 3 and 12 really well, and be able to find any definition in Section 10.", after=8)

contents = [
    ["1", "Read this first", "How to use the guide, and the three sentences that explain the whole project"],
    ["2", "The project in one page", "The problem, the idea, what is real and what is synthetic"],
    ["3", "How the system fits together", "Every layer, every file, and how a raw number becomes a coloured badge"],
    ["4", "The data: what it is and how it is made", "Servers, metrics, daily rhythms, injected incidents, splits, replay"],
    ["5", "Screen 1 — Overview", "Every card, number and label on the fleet page"],
    ["6", "Screen 2 — Alerts", "What an alert actually is, and what each column means"],
    ["7", "Screen 3 — Server detail", "Metric tabs, the chart, and the three summary cards"],
    ["8", "Screen 4 — Model evaluation", "Precision, recall, F1, MAE, RMSE — with a worked example"],
    ["9", "How a minute flows through the system", "The end-to-end story, and what happens when you click"],
    ["10", "Glossary A–Z", "Every term in one table, in plain language"],
    ["11", "Honest limitations and future work", "The weaknesses a good teacher will ask about"],
    ["12", "Presentation plan for your teacher", "A 12-minute script with timings and exact clicks"],
    ["13", "Likely questions and ready answers", "20 questions, short answers you can say out loud"],
    ["14", "One-page cheat sheet", "The only numbers you need to memorise"],
    ["15", "Before you present: checklist", "Ten minutes of setup that prevents demo disasters"],
    ["16", "Appendix — files and commands", "Where everything lives and how to run it"],
]
add_table(doc, ["§", "Section", "What it gives you"], contents, [0.35, 2.05, 4.3], font=9, center_from=0)

callout(doc, "If you only have five minutes before class",
        "Read Section 14 (cheat sheet) and Section 12 (script). In the demo, open Overview → click server-07 → Alerts → Model evaluation. "
        "Say the four headline numbers: **24 of 26 incidents caught**, **3.5 minute median delay**, **F1 0.553 vs 0.023** for the simple CPU alarm, "
        "and **CPU forecast error 2.53 vs 3.58** for the naive guess.")

# ============================ 1. READ THIS FIRST ============================
H1(doc, "1. Read this first")
P(doc, "You said you know about 10% of what is happening on this site. That is completely normal for a project that combines data engineering, machine learning, an API and a dashboard. This document assumes you know **nothing** about machine learning and explains each idea twice: once in everyday language, then with the real number from your project.")

H2(doc, "1.1 The three sentences that explain everything")
callout(doc, "Memorise these three sentences",
        "**1.** I built a system that learns what “normal” looks like for each of 8 servers, instead of using one fixed alert limit for all of them.\n"
        "**2.** Every minute it gives the server an anomaly score from 0 to 1, forecasts CPU 30 minutes ahead and disk days ahead, and turns that into a LOW / MEDIUM / HIGH risk with a one-line reason.\n"
        "**3.** I tested it on the last 25% of the data it never saw: it caught 24 of 26 injected incidents about 3.5 minutes after they started, and its forecasts beat a naive guess on all 8 servers.",
        bg="F3F7EE", bar="4F7A28", title_color=RGBColor(0x3D, 0x5F, 0x1F))

H2(doc, "1.2 What each chapter is for")
B(doc, "**Sections 2–4** give you the story and the data. If a teacher asks “what did you build and where did the data come from?”, the answer is here.")
B(doc, "**Sections 5–8** are the four screens, one section each. Every label you can see on screen appears in a table with: what it says, what it means, and where the number comes from.")
B(doc, "**Section 9** connects the screens to the code. This is what makes you sound like you built it rather than copied it.")
B(doc, "**Section 10** is a dictionary. When a word surprises you, look it up there.")
B(doc, "**Section 11** lists the weaknesses honestly. Teachers reward this more than perfect numbers.")
B(doc, "**Sections 12–15** are the performance: a timed script, 20 questions with answers, a cheat sheet, and a setup checklist.")

H2(doc, "1.3 How to talk about it (and how not to)")
add_table(doc,
          ["Say this", "Not this", "Why"],
          [["“The system detects abnormal behaviour for that server’s own baseline.”",
            "“It detects attacks.”",
            "The data has no attacks. Overclaiming is the fastest way to lose marks."],
           ["“It flags and scores; the reason line is a rule-based hint.”",
            "“The AI explains the root cause.”",
            "The model does not diagnose causes; the risk engine writes the sentence."],
           ["“On synthetic data with injected incidents…”",
            "“In production it would…”",
            "Be explicit that the data is generated and the numbers are from that generator."],
           ["“Recall is 46%, precision is 70%.”",
            "“Accuracy is 99%.”",
            "99% of minutes are normal, so accuracy hides misses. Precision/recall are the honest pair."]],
          [2.55, 1.85, 2.3], font=9)

# ============================ 2. ONE PAGE ============================
H1(doc, "2. The project in one page")

H2(doc, "2.1 The problem, in everyday language")
P(doc, "Imagine eight machines, each reporting six numbers every single minute: CPU usage, memory usage, disk usage, network traffic, response latency and error rate. Over 45 days that is about **3.1 million individual values**. No human can watch that. Real monitoring tools usually solve it with fixed limits such as “alert if CPU is over 90%”.")
P(doc, "Fixed limits fail in two directions:")
B(doc, "**They are too late.** A server that normally sits at 25% CPU is in serious trouble at 70%, but a 90% rule says nothing.")
B(doc, "**They are too noisy.** server-08 normally runs at about 63% CPU and swings ±24 points. It crosses 90% while doing nothing unusual, so the alarm cries wolf.")
P(doc, "The project’s answer: **learn a separate idea of “normal” for every server**, including its daily rhythm, then ask “how unusual is this minute for this server, at this time of day?” That is what the anomaly score measures.")

H2(doc, "2.2 What the system outputs")
add_table(doc,
          ["Output", "Range", "Plain meaning", "Where you see it"],
          [["Anomaly score", "0 – 1", "How unlike this server’s own normal the current minute looks. Ordinary minutes are roughly 0.1–0.3; 0.9+ is extreme.", "Server cards, server detail, alerts"],
           ["Flag", "yes / no", "The score crossed that server’s calibrated threshold (99.5th percentile of normal validation scores).", "Red dots, shaded bands, “abnormal” label"],
           ["CPU forecast", "0 – 100 %", "Predicted CPU 30 minutes from now.", "“30m forecast”, CPU outlook card, dashed chart line"],
           ["Disk forecast", "% and days", "Current disk use, growth per day, and estimated days until 90%.", "Disk capacity card"],
           ["Risk level", "LOW / MEDIUM / HIGH", "A rule-based summary of score + current CPU + forecast, with a short reason.", "Badges, KPIs, alerts"],
           ["Event summary", "count + delay", "A contiguous incident counts as caught if at least one of its minutes is flagged; delay is time to the first flag.", "Model evaluation page"]],
          [1.25, 1.15, 2.9, 1.4], font=9)

H2(doc, "2.3 What is real and what is synthetic — say this clearly")
add_table(doc,
          ["Part", "Real or generated?", "What that means"],
          [["The 8 servers and their metrics", "**Generated** by `backend/data_gen.py` with a fixed random seed", "No real company data was available, so a realistic generator was written and the incidents were injected on purpose."],
           ["The incidents", "**Injected** at known times with known types", "This gives a correct answer key, so precision and recall can actually be computed."],
           ["The labels (`is_anomaly`)", "**Generated answer key**", "Used only for scoring and plots. Never given to the detector as an input."],
           ["The models", "**Trained on that data**", "Isolation Forest, XGBoost, and a least-squares line for disk."],
           ["The dashboard", "**Real software**", "It calls a real API and renders real model output. Only the underlying servers are simulated."],
           ["The “live” clock", "**A replay**, not the current time", "It loops over the last 20% of the data at 60× speed, so incidents appear during a demo."]],
          [1.5, 2.0, 3.2], font=9)

callout(doc, "Why synthetic data is a legitimate choice",
        "A supervised evaluation needs incidents with exact start and end times. Real logs rarely provide that, and privacy rules block sharing them. "
        "A seeded generator gives repeatable data, known ground truth, and controlled difficulty — which is exactly what you need to compare a learned detector against a fixed alarm. "
        "The trade-off is that the generator’s assumptions (daily shape, correlations, incident types) are simpler than reality; Section 11 says so explicitly.")

# ============================ 3. ARCHITECTURE ============================
H1(doc, "3. How the system fits together")
P(doc, "Think of it as a factory with eight stations. Raw numbers go in at the left, and a coloured badge with a sentence comes out at the right.")

callout(doc, "The pipeline in one line",
        "`data_gen.py` → `features.py` → `anomaly.py` + `forecast.py` → `risk.py` → `api.py` → Next.js dashboard\n"
        "…with `evaluate.py` running the same models offline to produce the scores shown on the Model evaluation page.")

H2(doc, "3.1 The eight layers")
add_table(doc,
          ["#", "Layer", "What it does (plain)", "File(s)", "Technology"],
          [["1", "Data generation", "Builds 8 servers × 45 days of minute-by-minute metrics, with realistic daily/weekly rhythms, correlated metrics, and 102 injected incidents with labels.", "`data_gen.py`, `config.py`", "NumPy, pandas, Parquet"],
           ["2", "Feature building", "Turns raw values into context: recent averages, variability, change since 1 and 60 minutes ago, deviation from 6-hour and 24-hour baselines, time of day.", "`features.py`", "pandas rolling windows"],
           ["3", "Detection", "Fits one Isolation Forest per server on the first 60% of its history, calibrates a threshold on the next 15%, and scores every minute 0–1.", "`anomaly.py`", "scikit-learn"],
           ["4", "Forecasting", "CPU: XGBoost predicts the value 30 minutes ahead. Disk: a 7-day straight-line trend gives %/day and days to 90%.", "`forecast.py`", "XGBoost, NumPy; SARIMA only for a comparison"],
           ["5", "Risk engine", "Combines score, current CPU and forecast into LOW / MEDIUM / HIGH and writes a short reason sentence.", "`risk.py`", "Plain Python rules"],
           ["6", "API", "Loads the data, fits all models once at startup, then serves JSON under a replay clock.", "`api.py`", "FastAPI, uvicorn, Pydantic"],
           ["7", "Dashboard", "Four screens that poll the API every 5 seconds and draw cards, charts and tables.", "`frontend/app`, `frontend/components`", "Next.js 15, React 19, TypeScript, Tailwind, Recharts, SWR"],
           ["8", "Evaluation", "Computes precision/recall/F1, event detection, MAE/RMSE, per-type recall and the risk mix; writes `results.md` and plots.", "`evaluate.py`", "scikit-learn metrics"]],
          [0.28, 1.0, 2.75, 1.35, 1.3], font=8.5, center_from=0)

H2(doc, "3.2 What belongs to what — traceability table")
P(doc, "This is the table to show if a teacher asks “how do you know that number is real?” Every visible element can be traced to an endpoint and a file.")
add_table(doc,
          ["What you see", "API endpoint", "Main fields", "Where it is computed"],
          [["Healthy / Warning / Critical counts", "`GET /summary`", "`healthy`, `warning`, `critical`", "`api.py` counts `severity` from `risk.py`"],
           ["Active anomalies, peak score", "`GET /summary`", "`active_anomalies`, `highest_forecast_risk`", "`anomaly.py` flags + max score"],
           ["Server cards and sparklines", "`GET /servers`", "6 metrics, `anomaly_score`, `severity`, `sparklines`", "`api.py` slices the last 2 h every 5 min"],
           ["Chart and red bands", "`GET /metrics`", "`points`, `anomalies`, `forecast`, `threshold`", "`anomaly.py` scored rows; runs grouped in `api.py`"],
           ["CPU outlook / Disk capacity", "`GET /forecast`", "`forecast_30min`, `minutes_to_90`, `disk_days_to_90`", "`forecast.py` + `api.py` 7-day slope"],
           ["Alert rows", "`GET /alerts`", "`severity`, `score`, `forecast_30min`, `reason`", "`risk.py` verdicts stored at startup"],
           ["Model evaluation charts", "none (static)", "Numbers in `frontend/lib/results.ts`", "`evaluate.py` wrote `results.md`; the page mirrors it"]],
          [1.75, 1.15, 2.1, 1.7], font=8.5)

H2(doc, "3.3 Why there are two “brains”")
P(doc, "Detection and forecasting answer different questions, so they use different models:")
B(doc, "**Detection** asks: *is this minute unusual compared with this server’s own history?* It is unsupervised — the model never sees the labels. Isolation Forest is good at this because it isolates rare points with a few random cuts.")
B(doc, "**Forecasting** asks: *what will CPU be in 30 minutes?* That is supervised regression: XGBoost learns from past (features → future value) pairs.")
B(doc, "**Risk** is deliberately not another model. It is a transparent rule set, so every badge can be explained in one sentence. Teachers and operators both prefer that to a black box.")

# ============================ 4. DATA ============================
H1(doc, "4. The data: what it is and how it is made")
P(doc, "Everything in the dashboard comes from one file: `backend/data/metrics.parquet`. It was produced once by `python data_gen.py` with **SEED = 42**, so it is reproducible: the same seed gives exactly the same 518,400 rows.")

H2(doc, "4.1 The fleet: 8 servers with 8 different personalities")
P(doc, "Each server has its own baseline level, daily swing and noise. This is the most important design decision in the whole project: it is why one fixed threshold cannot work.")
add_table(doc,
          ["Server", "Role in the story", "CPU base", "Memory base", "Network MB/s", "Latency ms", "Disk start → end", "Disk fill injected?"],
          [["server-01", "Quiet lightweight node", "26%", "36%", "150", "16", "21% → 72.5%", "Yes (2)"],
           ["server-02", "Medium app load", "38%", "48%", "240", "22", "34% → 50.7%", "No"],
           ["server-03", "Steady busy worker", "48%", "55%", "320", "26", "46% → 69.8%", "No"],
           ["server-04", "Low load, noisy readings", "31%", "42%", "180", "19", "28% → 75.9%", "Yes (2)"],
           ["server-05", "High-load app node", "57%", "60%", "410", "31", "52% → 67.2%", "No"],
           ["server-06", "Lightweight edge node", "22%", "30%", "110", "14", "18% → 32.1%", "No"],
           ["server-07", "Busy worker with disk pressure", "44%", "52%", "290", "24", "32% → 78.9%", "Yes (2)"],
           ["server-08", "Heaviest batch node", "63%", "68%", "460", "35", "57% → 71.3%", "No"]],
          [0.72, 1.62, 0.6, 0.68, 0.78, 0.66, 0.86, 0.78], font=8.5, center_from=2)
caption(doc, "Table 4.1 — Baselines from backend/config.py; disk end values are the last reading on day 45. Roles are the plain-language profiles shown in the app.")

H2(doc, "4.2 The six metrics and their units")
add_table(doc,
          ["Metric", "Unit", "What it measures", "What “normal” looks like here", "What a problem looks like"],
          [["CPU", "%", "How much of the processor is busy.", "A smooth daily wave: low at night, peak around 14:00, quieter on weekends.", "A sudden +30–42 point jump for 18–35 min, or a slow climb near 100%."],
           ["Memory", "% of RAM", "How much memory is in use.", "Follows CPU loosely, plus its own noise.", "A slow, almost-straight climb over 4–6 hours (a leak) that does not come back down."],
           ["Disk", "% used", "How full the disk is.", "Only ever goes up, a few tenths of a percent per day.", "A faster permanent climb; it never recovers on its own."],
           ["Network", "MB/s", "Traffic through the machine.", "Roughly proportional to CPU load.", "A 4–6× burst for 15–25 minutes."],
           ["Latency", "ms", "How long requests take to answer.", "16–35 ms depending on the server, rising with CPU.", "3.5–5× slower responses; usually the first visible symptom of stress."],
           ["Error rate", "% of requests", "Share of requests that failed.", "Well under 1%, rising with latency.", "A jump of 6–10 points while latency is also high."]],
          [0.62, 0.65, 1.55, 2.05, 1.83], font=8.5, center_from=1)

H2(doc, "4.3 How a normal day is generated")
P(doc, "For each server, `normal_series()` builds the CPU curve from four ingredients, then derives the other metrics from it:")
P(doc, "`cpu = base + amplitude × sin(2π(hour − 8) / 24) × (1 − 0.3 × weekend) + 4 × weekly_wave + random_noise`", size=9.5, italic=True)
B(doc, "**base** — the server’s typical level (22% for server-06, 63% for server-08).")
B(doc, "**amplitude × sine** — the daily rhythm. The sine peaks at 14:00 and bottoms out around 02:00. On weekends the swing is reduced by 30%, because offices are quieter.")
B(doc, "**4 × weekly_wave** — a slow ±4 point wave across the week so no two days are identical.")
B(doc, "**random noise** — per-server noise (2.0 to 3.8 points) so the curve looks measured, not drawn.")
P(doc, "The other five metrics are then **correlated on purpose**, which is what makes the data look like a real system rather than six unrelated lines:")
add_table(doc,
          ["Metric", "Formula used by the generator", "Why this is realistic"],
          [["Memory", "`mem_base + 0.32 × cpu + noise(2.0)`", "Busy servers usually also hold more in memory."],
           ["Network", "`net_base × (0.55 + cpu / 75) + noise(6% of base)`", "Traffic grows with work being done."],
           ["Latency", "`lat_base + 0.4 × cpu + 0.011 × cpu² + noise(2.5)`", "The squared term makes latency explode at high CPU — queueing behaviour."],
           ["Error rate", "`0.03 + 1.1 × (latency / 55)² + noise(0.22)`", "Failures follow slow responses."],
           ["Disk", "`disk_base + cumulative_sum(rate / 1440 + small positive jitter)`", "Disks fill slowly and never shrink; jitter is floored at zero, so the line is monotone."]],
          [0.85, 3.0, 2.85], font=8.5)
callout(doc, "One sentence to remember",
        "The six metrics are not six independent random lines. CPU drives memory, network and latency; latency drives errors; disk only grows. "
        "That is why a single injected CPU spike also makes latency and errors rise — and why the detector’s “combined” anomalies look believable.")

H2(doc, "4.4 The 102 injected incidents")
P(doc, "Once a server’s normal 45 days exist, incidents are pasted on top at random times. Each incident has a known start, end and type — that is the **answer key** used for evaluation. Incidents are prevented from overlapping by a boolean “used” mask, so every labelled minute has exactly one cause.")
add_table(doc,
          ["Anomaly type", "Events", "Duration", "What the generator changes", "Why it is easy or hard to catch"],
          [["CPU spike", "32 (4/server)", "18–35 min", "CPU +30–42 points; latency ×1.25–1.45; errors ×1.4–1.9.", "Easy for a 90% rule only if the base is low; hard when the spike starts from 25%."],
           ["Memory leak", "16 (2/server)", "240–360 min (4–6 h)", "Memory +16–26 points, ramping linearly; CPU +2–5.", "Hard: slow, small per-minute change, overlaps normal daytime memory."],
           ["Network burst", "16 (2/server)", "15–25 min", "Network ×4–6; latency ×1.2–1.4.", "Medium: obvious on a chart, but network varies a lot naturally."],
           ["Latency / error", "16 (2/server)", "12–20 min", "Latency ×3.5–5; error rate +6–10 points on a sine ramp.", "Easy: latency and errors move together, far from normal."],
           ["Multivariate", "16 (2/server)", "30–60 min", "Modest rise in five metrics at once (CPU +10–14, memory +8–12, network +45–70%, latency +50–80%, errors +1–2).", "Hard for single-metric thresholds; this is where a multi-feature model earns its place."],
           ["Disk fill", "6 (only 01, 04, 07)", "600–840 min", "Extra +0.02% per minute, kept permanently because disks do not shrink.", "Easy but slow: 12–17 points of permanent growth; the alert arrives minutes after the start."]],
          [1.05, 0.85, 0.95, 2.55, 1.3], font=8.5)
add_table(doc,
          ["Total incidents", "Labeled minutes", "Label rate", "Rows", "Timeline"],
          [["102", "11,642", "2.25%", "518,400", "2026-10-07 → 2026-11-20"]],
          [1.3, 1.3, 1.1, 1.3, 1.7], font=9, center_from=0)

H2(doc, "4.5 Chronological splits — and why shuffling would be cheating")
P(doc, "Time-series data must be split by time, never at random. If you shuffle minutes and train on the future, the model has effectively seen tomorrow while predicting today. That is called **leakage**, and it makes scores look wonderful and meaningless.")
add_table(doc,
          ["Split", "Share", "Used for", "Why"],
          [["Train", "first 60%", "Fitting the Isolation Forest and XGBoost", "Oldest history — the model learns normal from the past only."],
           ["Validation", "next 15%", "Choosing the anomaly threshold; early stopping for XGBoost", "A separate slice, still before the test period, for tuning decisions."],
           ["Test", "last 25%", "All reported detection numbers (126,728 minutes)", "Completely held out. Never used for fitting or thresholding."],
           ["Forecast test", "last 20%", "CPU and disk error numbers (103,544 minutes)", "XGBoost uses its own 60/20/20 split; reported errors come only from the final 20%."]],
          [0.85, 0.8, 2.5, 2.55], font=8.5)

H2(doc, "4.6 The replay clock — why the dashboard moves")
P(doc, "The API does not show real-time data; it replays the **test period** at 60× speed. One real second equals one simulated minute, so a 9-day window takes about **3.6 real hours** to loop.")
B(doc, "**Why replay?** A demo needs incidents to appear within minutes, and the models must only be scored on data they never saw. Replaying the held-out period does both.")
B(doc, "**What “LIVE” means:** it means “the replay feed is running”, not “connected to production servers”. The top bar shows both the simulated time and when the browser last synced.")
B(doc, "**Consequence for your demo:** right after startup the window may contain no incidents, so the Alerts page can be empty. Section 15 explains how to handle that.")

H2(doc, "4.7 Look at the generated data")
pic = BASE / "backend" / "plots" / "server-01_week1.png"
if pic.exists():
    doc.add_picture(str(pic), width=Inches(6.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(doc, "Figure 4.1 — server-01, first 7 days. Blue = CPU, purple = memory, red shaded = injected anomalies. "
                 "You can see the daily wave and how the incidents sit on top of it. This plot is produced by data_gen.py.")

P(doc, "What to notice in the figure:")
B(doc, "The normal curve is **smooth and repeating**, not random noise. That repeating shape is what the detector learns.")
B(doc, "Incidents are **short compared with 45 days**, which is why the labelled rate is only 2.25%.")
B(doc, "A disk-fill incident does not appear here because disk is not plotted; it shows in the Disk tab of server-01, climbing permanently.")

# ============================ 5. OVERVIEW ============================
H1(doc, "5. Screen 1 — Overview (the fleet page)")
P(doc, "URL `/` · sidebar name **Overview** · The question it answers: *“Is anything wrong across the whole fleet right now?”*")

H2(doc, "5.1 The page from top to bottom")
add_table(doc,
          ["Element", "What it literally says", "What it means", "Where the number comes from"],
          [["Sidebar logo", "PulseGrid / Infra intelligence", "The product name. “Infra” = infrastructure, the servers the app watches.", "Static UI"],
           ["Sidebar nav", "Overview · Alerts · Model evaluation", "Three sections. Server detail is not listed because you reach it by clicking a server card.", "`components/sidebar.tsx`"],
           ["Sidebar footer", "Replay feed · 60× / Synthetic fleet · 8 servers · 45 days", "The data is simulated and replayed 60 times faster than real time.", "`config.py` (`REPLAY_SPEED`) and UI copy"],
           ["Top bar title", "Fleet overview", "Changes with the page (Server detail, Alerts, Model evaluation).", "`topbar.tsx` uses the URL"],
           ["Green LIVE pill", "LIVE · replay 60×", "The replay is running. It is **not** a live production connection.", "`GET /health` → `status`, `replay_speed`"],
           ["Clock", "Nov 14, 09:32", "The simulated “now”. It advances one minute per real second.", "`GET /health` → `now`"],
           ["“synced 09:32:07”", "Last successful poll", "Proof the browser talked to the API in the last few seconds. If it freezes, the API is down.", "SWR refresh timestamp"],
           ["Page subtitle", "8 synthetic servers, each with its own learned idea of normal · sparklines show the last 2 hours", "The core idea in one line; sparklines are the tiny trend lines on each card.", "`summary.total_servers`"],
           ["“refreshing every 5s”", "Auto-refresh interval", "The page is not push-based; it asks the API again every 5 seconds.", "SWR `refreshInterval: 5000`"]],
          [1.3, 1.9, 2.35, 1.15], font=8.5)

H2(doc, "5.2 The five KPI cards")
P(doc, "KPI means “key performance indicator” — a headline number. They are all computed from the same snapshot: the latest minute per server at the replay time.")
add_table(doc,
          ["Card", "What it counts", "How to read it out loud", "Rule behind it"],
          [["Healthy (green)", "Servers whose risk is LOW.", "“How many servers have nothing worth looking at.”", "`severity == LOW`"],
           ["Warning (amber)", "Servers whose risk is MEDIUM.", "“Worth a look: the detector flagged something, or CPU is trending up.”", "`severity == MEDIUM`"],
           ["Critical (red)", "Servers whose risk is HIGH.", "“Act now: score ≥ 0.90, or CPU is at/forecast above 90%.”", "`severity == HIGH`"],
           ["Active anomalies (blue)", "Servers flagged by the detector at this exact minute.", "“How many servers are abnormal right now.” Usually 0 or 1; it is a snapshot, not a count over the day.", "`if_flag == 1`"],
           ["Peak anomaly score (blue)", "The highest anomaly score in the fleet, with the server name underneath.", "“The worst-looking server right now, and how extreme it is.” 0.10 = normal, 0.95 = very unusual.", "`max(anomaly_score)` and its server"]],
          [1.45, 1.95, 2.05, 1.25], font=8.5)

H2(doc, "5.3 The server cards")
P(doc, "Each card is a one-glance summary of one machine. Clicking anywhere on it opens that server’s detail page.")
add_table(doc,
          ["Part of the card", "Meaning", "Where it comes from"],
          [["Server name (mono font)", "The machine’s identifier, server-01 … server-08.", "`server` field"],
           ["Grey line under the name", "Its role: quiet lightweight node, heaviest batch node, and so on. This is a human-written profile, useful for interpreting the numbers.", "`frontend/lib/servers.ts`"],
           ["Badge (Healthy / Warning / Critical)", "The risk level for this server at the replay minute.", "`risk.py` → `severity`"],
           ["“anomaly score” + number", "0–1 unusualness score. Shown in red when the server is flagged.", "`anomaly.py`"],
           ["CPU / MEM / NET sparklines", "The last 2 hours of each metric as a tiny line. No axes — it shows *shape*, not exact values.", "`/servers` → `sparklines`, sampled every 5 minutes"],
           ["Number on the right of each sparkline", "The current value: CPU %, memory %, network MB/s (rounded to a whole number).", "Latest row"],
           ["“normal” / “abnormal”", "Whether the detector flagged this minute. It is a different question from the risk badge: a server can be “abnormal” but still MEDIUM, or HIGH because CPU is high.", "`if_flag`"],
           ["“30m forecast 24.6%”", "Predicted CPU half an hour from now.", "`forecast.py` → `pred`"]],
          [1.55, 3.2, 1.95], font=8.5)

callout(doc, "Why “Active anomalies” is often 0 while a server is orange",
        "The badge is a **risk level**, which also considers current CPU and the forecast. The anomaly count only counts the detector’s flag. "
        "A server can be MEDIUM because CPU is trending toward 80% without the anomaly score crossing its threshold. Both are shown so you can discuss the difference.")

H2(doc, "5.4 What to demonstrate here (20 seconds)")
P(doc, "Click nothing yet. Point at the top row and say: *“Eight servers, each with its own baseline. Green means nothing to look at, amber means worth a look, red means act now. The blue cards summarise the fleet: how many are abnormal this minute, and the worst score. This whole row refreshes every five seconds from the API.”*")
P(doc, "Then point at one card: *“Each card gives me the score, three two-hour sparklines, and the 30-minute CPU forecast. The role line tells me what kind of machine it is, because 60% CPU means different things on a quiet node and on the heaviest batch node.”*")

# ============================ 6. ALERTS ============================
H1(doc, "6. Screen 2 — Alerts")
P(doc, "URL `/alerts` · sidebar name **Alerts** · The question it answers: *“What has gone wrong recently, and how serious was it?”*")

H2(doc, "6.1 What an alert actually is")
P(doc, "An alert is **not** a separate model or a separate prediction. It is simply a stored minute whose risk level is MEDIUM or HIGH. The API takes all such minutes up to the replay time, sorts them newest first, and returns up to the requested limit (the page asks for 200).")
P(doc, "The page subtitle says it exactly: *“One row = a minute where a server behaved unlike its own normal.”* Consecutive abnormal minutes therefore produce several rows — that is intentional, because each row is a moment you could inspect.")

H2(doc, "6.2 The columns")
add_table(doc,
          ["Column", "Example", "What it means", "How it is produced"],
          [["Severity", "Critical / Warning", "HIGH is shown as Critical, MEDIUM as Warning. LOW never appears because those minutes are not alerts.", "`risk.py` verdict"],
           ["Server", "`server-07`", "Which machine. Clicking the row opens its detail page.", "`server` field"],
           ["Signal", "CPU / COMBINED", "A display label: **CPU** when the actual or forecast CPU is high (≥ 85% actual or ≥ 80% forecast); **combined** when several metrics contribute. It is a hint, not a diagnosis.", "`api.py` `/alerts` rule"],
           ["Score", "0.87", "The anomaly score for that minute, 0–1.", "`anomaly.py`"],
           ["CPU 30m", "91.4%", "The CPU forecast for 30 minutes later, at that same minute.", "`forecast.py`"],
           ["Reason", "high anomaly score 0.91; CPU already 92%", "A short sentence assembled from the rules that fired. It explains **why the level is what it is**, not the root cause.", "`risk.py` `assess()`"],
           ["Time", "Nov 14, 09:32", "The simulated timestamp of the minute.", "`timestamp`"]],
          [0.85, 1.5, 2.85, 1.5], font=8.5)

H2(doc, "6.3 The filters and sorting")
add_table(doc,
          ["Control", "Options", "What it does"],
          [["Severity dropdown", "All severities / Critical / Warning", "Filters by risk level. “Critical” = HIGH, “Warning” = MEDIUM."],
           ["Server dropdown", "All servers / each server present in the current alerts", "Shows only that machine. The list is built from the alerts currently loaded, not from all 8 servers."],
           ["Newest / Highest score", "Two sort buttons", "Newest sorts by time descending; Highest score puts the most extreme anomaly first."],
           ["Row click", "—", "Navigates to `/servers/<name>` so you can see the chart around that incident."],
           ["Footer", "“N alerts shown · auto-refresh every 5s”", "How many rows survived the filters, and the polling interval."]],
          [1.5, 2.1, 3.1], font=8.5)

H2(doc, "6.4 The empty state")
P(doc, "If no incident has occurred yet in the replay window, the page shows a bell icon and **“No alerts at this replay position”**. There are two different messages:")
B(doc, "**No alerts at all yet** → *“Alerts appear as the replay feed reaches periods of abnormal behavior.”* This is normal in the first minutes after the API starts.")
B(doc, "**Alerts exist but the filters exclude them** → *“No alerts match the current filters.”* Clear the filters.")
P(doc, "Do not “fix” this by lowering thresholds. It reflects where the replay currently is. Section 15 tells you how to make sure alerts are present before class.")

H2(doc, "6.5 What to say here (20 seconds)")
P(doc, "*“This is the triage list. Each row is one minute where a server behaved unlike its own normal. I can filter by severity or server, and sort by time or by how extreme the score is. The reason column is generated by transparent rules, so an operator gets a sentence, not just a colour. Clicking a row takes me to the chart around that minute.”*")

# ============================ 7. SERVER DETAIL ============================
H1(doc, "7. Screen 3 — Server detail")
P(doc, "URL `/servers/server-01` … `/servers/server-08` · reached by clicking any server card or alert row · The question it answers: *“What exactly happened on this machine, and what is likely next?”*")

H2(doc, "7.1 The header")
add_table(doc,
          ["Element", "Meaning"],
          [["“← Fleet”", "Back to the overview."],
           ["Server name", "The machine you are inspecting."],
           ["Badge", "Current risk level for this server."],
           ["Role pill (e.g. “BUSY WORKER WITH DISK PRESSURE”)", "The human-written profile, so you know whether 70% CPU is normal for this machine."],
           ["Grey sentence after the badge", "The current reason, e.g. “metrics within learned normal range” or “abnormal behavior flagged, score 0.71”."]],
          [2.3, 4.4], font=9)

H2(doc, "7.2 The six metric tabs")
add_table(doc,
          ["Tab", "Unit", "What it tells you", "Typical healthy look", "What to point out during the demo"],
          [["CPU", "%", "Processor busy share.", "Smooth daily wave, server-specific base.", "The dashed line is the +30 min forecast; red dots are flagged minutes; the dashed horizontal line is 90%."],
           ["Memory", "%", "RAM in use.", "Follows CPU loosely.", "A leak looks like a ramp that does not come back down. This is the model’s weak spot."],
           ["Disk", "%", "Disk used.", "Slow monotone climb.", "Disk never decreases. server-01/04/07 received fills, so their lines jump upward permanently."],
           ["Network", "MB/s", "Traffic volume.", "Proportional to CPU.", "Bursts are 4–6× normal and easy to see by eye."],
           ["Latency", "ms", "Response time.", "16–35 ms depending on server.", "Rises before errors; the squared term in the generator makes it explode at high CPU."],
           ["Error rate", "%", "Failed request share.", "Below ~1%.", "Follows latency upward; a latency incident usually drags errors with it."]],
          [0.85, 0.6, 1.5, 1.45, 2.3], font=8.5)

H2(doc, "7.3 The time-range buttons")
P(doc, "`1h · 6h · 24h · 3d · 7d` change how much history is drawn. The API downsamples to at most about 400 points so the chart stays fast; the shape is preserved, individual minutes may be skipped. On 3d and 7d the axis labels include the date, otherwise you would see the same clock times repeated.")
callout(doc, "Why the chart can look flat on “24h”",
        "The replay window is only about nine days, and each range looks **backwards from the simulated now**. Early in the loop, “7d” may contain less than seven days. "
        "Also, 400 points spread over 7 days is about one point every 25 minutes, so short 20-minute spikes can be thinned out. Use 1h or 6h to show a spike clearly.")

H2(doc, "7.4 Anatomy of the chart — every visual element")
add_table(doc,
          ["Visual", "What it is", "How to explain it"],
          [["Solid blue line", "The actual metric value for each minute.", "“This is the measurement.”"],
           ["Red dots", "Minutes where the detector’s flag is 1, drawn on top of the line at the metric’s value.", "“These are the model’s accusations.”"],
           ["Red shaded bands", "A continuous run of flagged minutes (gaps of 2 minutes or less are merged).", "“The band shows how long the abnormal period lasted.”"],
           ["Grey dashed line (CPU only)", "The predicted value for 30 minutes ahead, shifted forward so it overlays the future.", "“The model’s guess, drawn where it belongs in time.”"],
           ["Grey dashed horizontal line (CPU only)", "The fixed 90% threshold, for comparison with the learned detector.", "“This is what a traditional alarm would watch.”"],
           ["Current value (top right)", "The latest value at the replay minute, with its unit.", "“The number right now.”"],
           ["Tooltip on hover", "Timestamp, value or forecast, and the anomaly score for that minute.", "“Hovering gives the exact minute and its score.”"],
           ["Y-axis", "0–100 for percentages, automatic range for MB/s and ms.", "Percentages are fixed so you can compare shapes honestly."]],
          [1.7, 2.55, 2.45], font=8.5)

H2(doc, "7.5 The three summary cards under the chart")
add_table(doc,
          ["Card", "Big number", "Small line", "How it is computed"],
          [["CPU outlook", "Forecast CPU in 30 min (e.g. 27.4%)", "“No 90% threshold crossing in the next 30 min”, or “Threshold crossing in ~N min”.", "If the forecast is above 90, `time_to_cross` linearly interpolates between current and forecast CPU. If not, no crossing. During the test window no forecast crossed 90%, so this branch is rarely seen."],
           ["Disk capacity", "Current disk use (e.g. 72.5%)", "“Reaches 90% in ~N days at X pct/day”, or “No growth trend detected”.", "Fit a straight line to the last 7 daily disk readings; slope = %/day; days = (90 − current) / slope. A negative or zero slope means no estimate."],
           ["Detection", "Current anomaly score", "“abnormal behavior at current time” or “no abnormal behavior now”.", "Latest score from the Isolation Forest and whether it crossed that server’s threshold."]],
          [1.1, 1.75, 2.1, 1.75], font=8.5)

H2(doc, "7.6 The “About this server” card")
P(doc, "This card is written by a human (in `frontend/lib/servers.ts`), not by the model. It has three columns:")
B(doc, "**What it is** — the server’s role and personality, including how many disk fills it received.")
B(doc, "**Normal day (before incidents)** — the baseline numbers from `config.py`: CPU, memory, network, latency and starting disk.")
B(doc, "**What the data shows** — the 45-day outcome: where disk ended, whether CPU spikes reach 100%, and what to watch.")
P(doc, "It exists because a score without context is meaningless. 70% CPU is alarming on server-06 and completely ordinary on server-08. Saying that out loud is a strong point in a presentation.")

# ============================ 8. MODEL EVALUATION ============================
H1(doc, "8. Screen 4 — Model evaluation")
P(doc, "URL `/model` · sidebar name **Model evaluation** · The question it answers: *“How do you know the models are any good?”*")
P(doc, "This is the page a teacher will spend the most time on. It is also the page with the most jargon, so this section explains each number twice: what it means, and what it is in your project.")

H2(doc, "8.1 What is being scored, and on what")
B(doc, "**Detection** is scored on the **last 25%** of each server’s timeline: **126,728 minutes** the model never saw while fitting or tuning.")
B(doc, "**Forecasting** is scored on the **last 20%** of the forecasting dataset: **103,544 minutes** (30-minute-ahead targets).")
B(doc, "**Risk** is scored on the minutes where a forecast exists: **99,778 minutes**.")
B(doc, "The answer key (`is_anomaly`) is used **only** for scoring. It is not a feature, so the model cannot cheat.")

H2(doc, "8.2 The short version box")
P(doc, "*“The learned detector catches 24 of 26 incidents, typically 3.5 minutes after they start, and about 7 in 10 of its flags are real. Forecasts beat the naive baseline on all eight servers; the slow memory leak remains the blind spot.”*")
P(doc, "If you memorise one paragraph for the whole project, memorise that one.")

H2(doc, "8.3 The four KPI cards at the top")
add_table(doc,
          ["Card", "Value", "What it means in plain words", "What to compare it with"],
          [["Detector F1", "0.553", "One number balancing “how many flags were right” and “how many incidents were caught”. 0 is useless, 1 is perfect.", "The fixed CPU>90 rule: 0.023. The learned model is about 24× better on this balanced score."],
           ["XGBoost MAE", "2.53", "On average the 30-minute CPU forecast is wrong by about 2.5 CPU percentage points.", "Naive “CPU will be the same as now”: 3.58. The model is ~29% better."],
           ["Events detected", "24 / 26", "Of the 26 incidents that fall in the test window, 24 had at least one minute flagged. Median delay: 3.5 minutes.", "CPU>90 catches 2 of 26."],
           ["Slow leak recall", "0.01", "Only about 1% of memory-leak minutes were flagged; 2 of 3 leak events were touched at some point.", "This is the honest failure. Say it before the teacher finds it."]],
          [1.25, 0.9, 2.65, 1.9], font=8.5)

H2(doc, "8.4 “How to read these numbers” — the eight terms, expanded")
H3(doc, "Anomaly score (0–1)")
P(doc, "Every minute gets one number for how unlike that server’s own normal it looks. Think of it as a “weirdness meter”. The Isolation Forest builds many random trees that cut the data into small groups; points that get isolated after very few cuts are unusual. That isolation depth is converted to a 0–1 score per server. Ordinary minutes sit around 0.1–0.3; 0.9+ is extreme. The score is **relative to that server**, so 0.8 on server-06 and 0.8 on server-08 mean the same thing statistically, even though the raw CPU values differ.")
H3(doc, "Precision 0.70")
P(doc, "Of all the minutes the model flagged, about **70% were genuinely abnormal**. The other 30% were false alarms. The fixed CPU>90 rule scores 0.074 — only 7 in 100 of its alarms are real — because several busy servers sit near 90% while behaving normally.")
H3(doc, "Recall 0.46")
P(doc, "Of all the truly abnormal minutes, the model caught about **46%**. That sounds low, but anomalies are uneven: it catches 96% of latency/error minutes and 91% of disk-fill minutes, but only 1% of memory-leak minutes. Recall is a **point-wise** measure; event-wise it does much better (24/26), because one flagged minute is enough to raise an incident.")
H3(doc, "F1 0.55")
P(doc, "The harmonic mean of precision and recall: `F1 = 2 × (precision × recall) / (precision + recall)`. It stops you from cheating by flagging everything (high recall, terrible precision) or nothing (high precision by never raising an alarm). The CPU>90 rule scores 0.023.")
H3(doc, "Events caught / delay")
P(doc, "An incident is **caught** if at least one of its minutes is flagged. **Delay** is the time from the incident’s first minute to the first flag. The model caught 24 of 26 with a median delay of 3.5 minutes. The two misses: one slow memory leak (a leak event was “touched” only after 82.5 minutes) and one network burst.")
H3(doc, "MAE / RMSE")
P(doc, "Both measure forecast error in CPU percentage points, 30 minutes ahead.")
B(doc, "**MAE (mean absolute error)** = the average size of the miss, ignoring direction. MAE 2.53 means a typical miss of ~2.5 points.")
B(doc, "**RMSE (root mean squared error)** = square the misses, average, square-root. It punishes large misses much more. RMSE 3.54 means there are some bigger misses hiding behind the average.")
B(doc, "If MAE is small but RMSE is much larger, most predictions are good but a few are very wrong. Always report both; reporting only the prettier one is a red flag.")
H3(doc, "Risk levels")
P(doc, "LOW = nothing to look at. MEDIUM = worth a look. HIGH = act now. The rules are: HIGH if anomaly score ≥ 0.90, or current CPU ≥ 90%, or forecast CPU ≥ 90%; MEDIUM if the detector flagged the minute or CPU is trending to ≥ 80%; otherwise LOW. Over the test minutes: **96.36% LOW, 3.16% MEDIUM, 0.48% HIGH**.")
H3(doc, "Why the memory leak is missed")
P(doc, "The leak adds 16–26 memory points over 4–6 hours — roughly 0.07–0.1 points per minute. Normal daytime memory already varies by more than that, so at a threshold calibrated to allow only 0.5% false alarms, the leak hides under the noise. It is a **signal-to-noise** problem, not a bug. Section 11 lists fixes: longer trend features, a dedicated slope detector, or smoothing the score over hours.")

H2(doc, "8.5 Worked example: turn precision and recall into actual counts")
P(doc, "Numbers like 0.695 feel abstract. Here is the arithmetic that makes them concrete, using the test set.")
P(doc, "126,728 test minutes × 1.788% truly abnormal ≈ **2,266 abnormal minutes** (and 124,462 normal).")
add_table(doc,
          ["", "Model says abnormal", "Model says normal", "Row total"],
          [["**Reality: abnormal**", "True positives ≈ 1,040", "False negatives ≈ 1,226", "2,266"],
           ["**Reality: normal**", "False positives ≈ 456", "True negatives ≈ 124,006", "124,462"],
           ["**Column total**", "≈ 1,496 flags", "≈ 125,232", "126,728"]],
          [1.7, 1.8, 1.8, 1.2], font=9, center_from=1)
B(doc, "Precision = 1,040 / 1,496 ≈ **0.695** → about 7 in 10 flags are real.")
B(doc, "Recall = 1,040 / 2,266 ≈ **0.459** → about 46% of abnormal minutes are caught.")
B(doc, "F1 = 2 × 0.695 × 0.459 / (0.695 + 0.459) ≈ **0.553**.")
P(doc, "This 2×2 table is called a **confusion matrix**. If a teacher asks “what does precision mean?”, drawing this table on the board is the clearest possible answer.")

H2(doc, "8.6 Chart: learned detector vs fixed CPU alarm")
add_table(doc,
          ["Bar", "Isolation Forest", "CPU > 90", "Interpretation"],
          [["Precision", "0.695", "0.074", "The learned model’s alarms are ~9× more often real."],
           ["Recall", "0.459", "0.014", "The learned model catches ~33× more abnormal minutes."],
           ["F1", "0.553", "0.023", "Overall, the fixed rule is close to useless on this fleet."],
           ["Events detected", "24 / 26", "2 / 26", "Event-wise, the gap is just as large."],
           ["Median delay", "3.5 min", "—", "The two events the rule caught had no useful lead."]],
          [1.35, 1.45, 1.15, 2.75], font=8.5, center_from=1)
P(doc, "Why the fixed rule fails so badly: with eight different baselines, 90% is not “high” in a comparable way. server-08’s normal wave reaches the high 80s, so the rule fires on ordinary afternoons; meanwhile a spike from 22% to 60% on server-06 never reaches 90 at all. A single threshold cannot represent eight different machines.")

H2(doc, "8.7 Chart: catch rate by failure type")
P(doc, "This is **recall per anomaly type**, computed one type against everything else. It shows *where* the model is strong and weak.")
add_table(doc,
          ["Type", "Abnormal minutes", "Events caught", "Recall", "Precision", "Median delay", "One-line reading"],
          [["CPU spike", "247", "9 / 9", "0.62", "0.10", "0.0 min", "Always caught, immediately; many flags land outside the labelled window, so precision looks low."],
           ["Memory leak", "924", "2 / 3", "0.01", "0.00", "82.5 min", "The blind spot: minutes overlap normal memory, so almost nothing is flagged."],
           ["Network burst", "126", "5 / 6", "0.44", "0.04", "3.0 min", "Usually caught quickly; one burst missed entirely."],
           ["Latency / error", "50", "3 / 3", "0.96", "0.03", "1.0 min", "Easiest signal: latency and errors move together and far from normal."],
           ["Multivariate", "192", "4 / 4", "0.60", "0.08", "9.5 min", "The multi-feature model proves its worth: no single metric is extreme, yet it finds them."],
           ["Disk fill", "727", "1 / 1", "0.91", "0.44", "33.0 min", "Caught almost every minute, but slowly: disk moves only ~0.02 points/min."]],
          [0.9, 0.9, 0.82, 0.62, 0.68, 0.82, 1.96], font=8)
callout(doc, "Why per-type precision is low even though overall precision is 0.70",
        "The detector does **not** output a type. It only says “this minute is unusual”. Per-type precision is computed one type against everything else, so a flag during a CPU spike that overlaps a disk-fill minute counts as a false positive for the CPU row. "
        "This table is for understanding behaviour, not for judging the detector; the headline precision (0.695) is the fair overall number. Saying this before the teacher asks shows maturity.")

H2(doc, "8.8 Chart: forecast accuracy, CPU 30 minutes ahead")
P(doc, "**Naive baseline:** “CPU in 30 minutes will equal CPU now.” It is the honest minimum any forecaster must beat. XGBoost uses the last 1, 5 and 15 minutes, 15- and 60-minute means and standard deviations, time of day, day of week, and the other five metrics.")
add_table(doc,
          ["Metric", "Naive", "XGBoost", "Improvement", "Meaning"],
          [["MAE (all servers)", "3.58", "2.53", "−29%", "A typical miss drops by about one CPU point."],
           ["RMSE (all servers)", "4.84", "3.54", "−27%", "Large misses also shrink, so the gain is not just an average effect."]],
          [1.55, 0.9, 1.0, 1.0, 2.25], font=8.5, center_from=1)
add_table(doc,
          ["Server", "Naive MAE", "XGBoost MAE", "Delta", "Reading"],
          [["server-01", "3.11", "2.15", "−31%", "Clear gain"],
           ["server-02", "4.00", "2.72", "−32%", "Clear gain"],
           ["server-03", "2.86", "1.92", "−33%", "Clear gain"],
           ["server-04", "4.55", "3.19", "−30%", "Noisiest server; still a clear gain"],
           ["server-05", "3.49", "2.30", "−34%", "Largest relative gain"],
           ["server-06", "2.62", "1.86", "−29%", "Quietest server; lowest absolute error"],
           ["server-07", "3.65", "3.13", "−14%", "Weakest gain — spikey workload"],
           ["server-08", "4.35", "2.98", "−31%", "Busiest server; big gain"],
           ["ALL", "3.58", "2.53", "−29%", "Model wins on every server"]],
          [1.1, 1.2, 1.3, 0.9, 2.2], font=8.5, center_from=1)

H2(doc, "8.9 The SARIMA comparison — and why reporting a loss is good")
P(doc, "SARIMA is a classical time-series model that describes a series using its own past values and seasonal patterns. It was tried on server-01 on a 30-minute grid, predicting the **average of the next 30 minutes**, with a seasonal period of 48 (24 hours at 30-minute steps).")
add_table(doc,
          ["Model", "Target", "MAE", "RMSE"],
          [["Naive (30-min grid)", "next 30-min mean", "1.20", "1.40"],
           ["SARIMA(1,0,0)(1,0,1,48)", "next 30-min mean", "2.77", "3.33"],
           ["XGBoost (same origins)", "point at +30 min", "2.08", "2.60"]],
          [2.3, 2.0, 1.0, 1.0], font=9, center_from=2)
P(doc, "Two honest observations: SARIMA **lost to the naive baseline** here, and XGBoost beat SARIMA even though SARIMA was predicting an easier, smoothed target. The reason is that the daily pattern is already captured by the clock features, while a single seasonal ARIMA structure struggles with 1-minute noise and a short fitting window. The project keeps the comparison in the report instead of hiding it — a negative result reported accurately is still a result.")
P(doc, "Also note the targets differ: SARIMA predicts the next 30-minute **mean**, XGBoost predicts the **point** at +30 minutes. They are scored at the same origins, but the comparison is indicative, not perfectly like-for-like. The report says this explicitly.")

H2(doc, "8.10 Chart: disk forecast error")
P(doc, "Disk is forecast with a 7-day straight-line trend. The baseline is “disk will not change”.")
add_table(doc,
          ["Horizon", "Trend MAE", "Naive MAE", "Trend RMSE", "Naive RMSE", "What it means"],
          [["1 day", "0.58", "0.69", "2.03", "2.02", "Trend wins on average error; large misses are similar."],
           ["3 days", "1.64", "2.05", "4.25", "4.03", "Trend wins on average, but a few big misses are slightly worse."],
           ["7 days", "4.15", "4.98", "8.95", "7.79", "Average error still better; RMSE clearly worse — fills and rate changes hurt."]],
          [0.8, 0.9, 0.9, 1.0, 1.0, 2.1], font=8.5, center_from=1)
P(doc, "The page itself states the caveat: the trend has lower **average** error at every horizon but slightly worse **RMSE** at 3–7 days. That means a handful of large misses remain, usually when an injected disk fill changes the growth rate. Reporting only MAE would make the model look better than it is — this is exactly the kind of honesty that earns marks.")

H2(doc, "8.11 Chart: risk level distribution")
add_table(doc,
          ["Level", "Test minutes", "Share", "What it means for an operator"],
          [["LOW", "99,778", "96.36%", "The vast majority of time is quiet. Good: the dashboard is not crying wolf all day."],
           ["MEDIUM", "3,271", "3.16%", "Roughly 45 minutes per simulated day per fleet are “worth a look”."],
           ["HIGH", "495", "0.48%", "About 7 minutes per simulated day are “act now”. Rare enough to be credible."]],
          [0.9, 1.2, 0.9, 3.7], font=8.5, center_from=1)
P(doc, "Because 96% of minutes are LOW, **accuracy would be a misleading metric** (a model that always says “normal” would score 96%). Precision and recall focus on the rare abnormal minutes, which is why they are the headline numbers.")

H2(doc, "8.12 The evaluation plot")
pic = BASE / "backend" / "plots" / "server-02_test.png"
if pic.exists():
    doc.add_picture(str(pic), width=Inches(6.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(doc, "Figure 8.1 — server-02, first 3 days of the test period. Top: CPU, the +30 min forecast (dashed orange), red flags, red labelled windows, 90% line. "
                 "Bottom: anomaly score with that server’s threshold (dotted). This is the visual proof that flags follow incidents.")
P(doc, "How to read the figure: the forecast tracks the daily wave closely; flags cluster inside the shaded incident windows; the score panel shows the threshold line and how far the score rises during incidents. Outside incidents the score mostly stays below the threshold — that is the 0.5% false-alarm budget working.")

# ============================ 9. FLOW ============================
H1(doc, "9. How a minute flows through the system")
P(doc, "This is the section that turns “I used a dashboard” into “I built a pipeline”. Read it until you can tell it as a story without notes.")

H2(doc, "9.1 The life of one minute, in nine steps")
N(doc, "**A timestamp arrives.** The generator has already created 64,800 minutes per server. At replay time the API computes the current simulated minute from elapsed real time × 60, modulo the window length.")
N(doc, "**Six raw values are read.** CPU, memory, disk, network, latency and error rate for that server and minute come from the scored dataframe in memory.")
N(doc, "**Features are computed.** `features.py` has already added 68 columns per row: rolling means and standard deviations over 5/15/60 minutes, 1- and 60-minute changes, deviation from the 60-minute, 6-hour and 24-hour averages, and sine/cosine of the hour. The detector sees this context, not the raw six numbers alone.")
N(doc, "**The Isolation Forest scores it.** One model per server. It was fitted only on the first 60% of that server’s history. The score is min–max scaled to 0–1 using the validation range.")
N(doc, "**The threshold decides the flag.** Each server’s threshold is the 99.5th percentile of scores on **normal validation minutes**, so about 0.5% of normal minutes are allowed to flag. Below → normal; above → flagged.")
N(doc, "**XGBoost forecasts CPU.** The model was fitted on the first 60% and early-stopped on the next 20%; it outputs the CPU value 30 minutes later. The disk slope is computed separately from the last 7 daily readings.")
N(doc, "**The risk engine combines them.** `assess(cpu, score, forecast, flagged)` returns LOW/MEDIUM/HIGH plus a reason built from the rules that fired.")
N(doc, "**The API serves JSON.** `/servers`, `/summary`, `/metrics`, `/forecast`, `/alerts` read from the same in-memory snapshot, so every screen agrees on the same minute.")
N(doc, "**The dashboard renders and polls again.** SWR re-fetches every 5 seconds; Recharts redraws the line, dots and shaded bands.")

H2(doc, "9.2 What happens when you click")
add_table(doc,
          ["Your action", "Request", "What the API does", "What you see"],
          [["Open the site", "`GET /summary`, `GET /servers`", "Reads the latest row per server at the replay minute; counts severities; samples sparklines every 5 min for 2 h.", "Five KPIs and eight cards"],
           ["Wait 5 seconds", "Same two requests", "The replay clock has moved; new rows may be latest.", "Numbers and sparklines shift"],
           ["Click a server card", "`GET /metrics?server=…&metric=cpu&range=24h`, `GET /forecast?server=…`, `GET /servers`", "Slices the last 24 h, groups flagged runs, builds the forecast points, computes the disk slope.", "Server page with chart, three cards, About card"],
           ["Switch to Memory", "`GET /metrics?…&metric=memory…`", "Same slice for another column; no forecast is returned for non-CPU metrics.", "New line, red dots and bands; dashed forecast disappears"],
           ["Choose 7d", "`GET /metrics?…&range=7d`", "Uses a 10,080-minute window and downsamples to ~400 points.", "Wider, denser chart with date labels"],
           ["Open Alerts", "`GET /alerts?limit=200`", "Takes all MEDIUM/HIGH minutes up to now, newest first, labels each signal, returns the rows.", "Table, filters, sorting"],
           ["Click an alert row", "Navigation only", "No extra API call; the server page fetches its own data.", "The same server page, ready to inspect"],
           ["API stops", "Fetch fails", "No response.", "Red error card with a Retry button on every page"]],
          [1.15, 2.0, 2.15, 1.4], font=8)

H2(doc, "9.3 Where the models are actually trained")
P(doc, "There is no training while you browse. When `uvicorn api:app` starts, `load()` runs once: it reads the Parquet file, calls `detect()` (which fits 8 Isolation Forests), calls `predict_cpu()` (which fits 8 XGBoost models), merges the scores and predictions, and computes a risk verdict for every forecastable minute. That is why startup takes about **25–30 seconds**. After that, every request is just slicing and formatting. This is worth saying: it explains the startup delay and shows you understand the difference between training and serving.")

H2(doc, "9.4 Why the dashboard has no database")
P(doc, "The project is an MVP for one fixed dataset, so the Parquet file **is** the store and the API keeps the scored rows in memory. There is nothing to write: no user accounts, no feedback loop, no persistence of alerts. That keeps the system small enough to run on a laptop. Section 11 lists what a production version would need instead.")

# ============================ 10. GLOSSARY ============================
H1(doc, "10. Glossary A–Z")
P(doc, "Every term that appears in the app, the report or this guide. If a word in a table above is unclear, find it here.")

gloss = [
    ["Anomaly", "A moment that does not fit the usual pattern for that server.", "Everywhere"],
    ["Anomaly score", "A 0–1 weirdness number for one minute, relative to that server’s own history.", "Cards, chart tooltips, model page"],
    ["API", "Application Programming Interface — the backend’s menu of URLs the dashboard can ask for data.", "Architecture"],
    ["Baseline", "The typical level or the reference model you compare against. Here: the naive forecast and the CPU>90 rule.", "Model page"],
    ["Causal features", "Features that only use the past (and present), never the future, so the model cannot peek ahead.", "features.py"],
    ["Chronological split", "Splitting data by time: first 60% train, next 15% validation, last 25% test.", "anomaly.py"],
    ["Cold start", "What happens before enough history exists to know what “normal” is. This project avoids it by always having 60% history first.", "Design choice"],
    ["Confusion matrix", "The 2×2 table of true/false positives and negatives. Precision and recall are computed from it.", "Section 8.5"],
    ["CORS", "Cross-Origin Resource Sharing — the browser rule that lets `localhost:3000` call `127.0.0.1:8000`.", "api.py"],
    ["Data leakage", "Accidentally letting the model see information from the future or from the answer key. It inflates scores and invalidates them.", "Why splits are chronological"],
    ["Disk fill (injected)", "An incident that adds permanent disk growth, mimicking logs or data piling up.", "server-01/04/07"],
    ["Downsampling", "Keeping every Nth point so a 7-day chart stays fast. Shape is preserved; individual minutes may be skipped.", "/metrics"],
    ["Endpoint", "One URL the API exposes, e.g. `/forecast?server=server-03`.", "api.py"],
    ["Event-wise detection", "Counting an incident as caught if any one of its minutes is flagged.", "24/26"],
    ["F1", "A single score balancing precision and recall. 1 is perfect; 0 is useless.", "Model page"],
    ["False negative", "A real anomaly the model did not flag. A miss.", "Confusion matrix"],
    ["False positive", "A normal minute the model flagged. A false alarm.", "Confusion matrix"],
    ["Feature", "An input column the model uses. Raw CPU is a feature; so is “CPU minus its 60-minute average”.", "features.py"],
    ["Feature engineering", "The work of turning raw measurements into useful context columns.", "features.py"],
    ["Flag", "A yes/no decision that a minute crossed the threshold.", "Red dots"],
    ["Forecast horizon", "How far ahead you predict. Here 30 minutes for CPU, 1–7 days for disk.", "forecast.py"],
    ["Ground truth / label", "The known correct answer. Here, the injected `is_anomaly` column. Never used as input.", "Evaluation"],
    ["Isolation Forest", "An unsupervised model that finds unusual points by seeing how quickly random cuts isolate them.", "anomaly.py"],
    ["JSON", "A text format for structured data; what the API returns and the browser parses.", "All endpoints"],
    ["KPI", "Key Performance Indicator — a headline number on a dashboard.", "Overview"],
    ["Lag feature", "A past value used as an input, e.g. CPU 15 minutes ago.", "forecast.py"],
    ["Latency", "How long a request takes to get a response, in milliseconds.", "Metric tab"],
    ["MAE", "Mean Absolute Error — the average size of a forecast miss, in the metric’s units.", "Model page"],
    ["Median delay", "The middle value of detection delays across incidents. Less distorted by one slow catch than the mean.", "3.5 min"],
    ["Monotonic", "Only moves in one direction. Disk usage never decreases here.", "data_gen.py"],
    ["Multivariate anomaly", "An anomaly visible only when several metrics move together, not in any single one.", "Injected type"],
    ["Naive forecast", "The simplest baseline: “the future equals the present” (or the last value).", "Compared on model page"],
    ["Outlier", "A value far from the rest. Related to anomaly, but not identical: an outlier may be harmless.", "General"],
    ["Parquet", "A compact columnar file format for dataframes. `metrics.parquet` is the whole dataset.", "backend/data"],
    ["Percentile", "The value below which a given share of observations fall. The 99.5th percentile leaves 0.5% above it.", "Threshold"],
    ["Polling", "Asking the server again on a timer instead of the server pushing updates. Here, every 5 s.", "SWR"],
    ["Precision", "Of everything flagged, the share that was truly abnormal. “How often am I right when I alarm?”", "0.695"],
    ["Recall", "Of all truly abnormal minutes, the share that was flagged. “How much of the problem do I catch?”", "0.459"],
    ["Replay clock", "A simulated clock that moves through historical data at 60× speed.", "Top bar"],
    ["Risk engine", "The transparent rule set that turns score + CPU + forecast into LOW/MEDIUM/HIGH and a reason.", "risk.py"],
    ["RMSE", "Root Mean Squared Error — like MAE but punishes large misses much more.", "3.54"],
    ["Rolling window", "A moving calculation over the last N minutes, e.g. a 60-minute average.", "features.py"],
    ["SARIMA", "A classical seasonal time-series model, tried here as a comparison and beaten by XGBoost.", "Model page"],
    ["Seed", "A fixed number that makes random generation repeatable. This project uses 42.", "data_gen.py"],
    ["Severity", "LOW / MEDIUM / HIGH risk, shown as Healthy / Warning / Critical.", "Badges"],
    ["Sparkline", "A tiny line chart with no axes, used to show shape at a glance.", "Server cards"],
    ["Supervised vs unsupervised", "Supervised learns from labelled answers; unsupervised finds structure without labels. Detection here is unsupervised; forecasting is supervised.", "Concept"],
    ["SWR", "The React data-fetching library used for polling and caching. The name comes from “stale-while-revalidate”.", "frontend"],
    ["Synthetic data", "Data generated by a program rather than measured from real machines.", "Whole dataset"],
    ["Threshold", "The cut-off score above which a minute is flagged. Calibrated per server at the 99.5th percentile of normal validation scores.", "anomaly.py"],
    ["Time-to-threshold", "Estimated minutes until CPU reaches 90%, or days until disk does.", "Forecast cards"],
    ["Train / validation / test", "Three chronological slices: fit, tune, and honestly evaluate.", "Splits"],
    ["True negative", "A normal minute correctly not flagged.", "Confusion matrix"],
    ["True positive", "An abnormal minute correctly flagged.", "Confusion matrix"],
    ["Unsupervised", "Learning patterns without being given the right answers.", "Isolation Forest"],
    ["XGBoost", "A gradient-boosted tree model; here it predicts CPU 30 minutes ahead from lagged and contextual features.", "forecast.py"],
]
add_table(doc, ["Term", "Plain meaning", "Where you meet it"], gloss, [1.45, 4.15, 1.1], font=8.5)

# ============================ 11. LIMITATIONS ============================
H1(doc, "11. Honest limitations and future work")
P(doc, "Read this section twice. Being able to name your own weaknesses is the difference between “a student who ran a script” and “an engineer who understands the system”. Say these before the teacher finds them.")

H2(doc, "11.1 Limitations you should state")
add_table(doc,
          ["Limitation", "Why it exists", "What it means for the results", "How you would fix it"],
          [["The data is synthetic", "No real, labelled, shareable telemetry was available.", "Absolute numbers are only valid for this generator; the method is what generalises.", "Validate on a public dataset (NAB, SMD, KPI) or a real anonymised fleet."],
           ["Slow memory leaks are missed", "The leak’s per-minute change is smaller than normal daytime variation; the 0.5% false-alarm budget hides it.", "Leak recall 0.01 point-wise, 2/3 events touched. This is the main quality gap.", "Add long-horizon slope features, a dedicated trend detector, or smooth scores over hours."],
           ["The detector does not name the type", "Isolation Forest is unsupervised and outputs one score, not a class.", "The alert’s “Signal” label is a heuristic, and per-type precision is low.", "Add a supervised classifier on top, or per-type detectors."],
           ["The dashboard shows a replay", "It loops the test period at 60× so incidents appear in a demo.", "The clock is simulated; “LIVE” means the feed is running.", "Stream real metrics and score them as they arrive."],
           ["Risk rules are hand-written", "Deliberate: transparent and explainable.", "Thresholds (0.90, 80%, 90%) were chosen by judgement, not optimised.", "Tune on validation data or learn a small decision model."],
           ["One forecast horizon", "30 minutes for CPU; 1–7 days for disk.", "It cannot warn about a spike two hours away.", "Add multi-horizon forecasts and show a cone of uncertainty."],
           ["Disk RMSE is worse at 3–7 days", "A straight line cannot anticipate a change in growth rate.", "Average error improves, but a few large misses remain.", "Robust regression, change-point detection, or a learned disk model."],
           ["The CPU-crossing HIGH branch is untested on the test slice", "No 30-minute forecast crossed 90% during the test window.", "That rule exists but was not exercised by the evaluation.", "Evaluate on a period containing a sustained high-CPU incident."],
           ["Startup is slow and memory-hungry", "Eight Isolation Forests and eight XGBoost models are fitted at boot; the machine has ~16 GB RAM.", "~25–30 s startup and ~2.6 GB free during runs.", "Persist trained models, load lazily, or use fewer trees for a demo build."]],
          [1.25, 1.75, 1.85, 1.85], font=8)

H2(doc, "11.2 What you would do with two more weeks")
B(doc, "**Add a leakage-safe drift check:** compare the score distribution month over month to detect when “normal” itself changes.")
B(doc, "**Type the anomalies:** train a small supervised classifier on labelled windows to turn “something is wrong” into “this looks like a memory leak”.")
B(doc, "**Improve leak detection:** a dedicated slope/trend feature over 4–8 hours, evaluated event-wise rather than point-wise.")
B(doc, "**Add uncertainty:** quantile forecasts for CPU, so the dashboard can show a range instead of one number.")
B(doc, "**Persist models and stream data:** replace boot-time training with saved artefacts and a real ingestion path; add a database for alert history.")
B(doc, "**Test on real or public data:** the strongest possible follow-up is showing the same pipeline on a dataset you did not generate.")

# ============================ 12. PRESENTATION ============================
H1(doc, "12. Presentation plan for your teacher")
P(doc, "This is a 12-minute plan: about 5 minutes of talking, 5 minutes of demo, 2 minutes of limitations and questions. If you have only 7 minutes, use the shortened version at the end of this section.")

H2(doc, "12.1 Before you start: what should be on screen")
B(doc, "The Overview page, already loaded, with the LIVE clock moving.")
B(doc, "A second tab on the Model evaluation page, already scrolled to the top.")
B(doc, "`results.md` open in an editor in the background (fallback if the API dies).")
B(doc, "This document open at Section 13 (questions), on a second monitor or printed.")
B(doc, "Do **not** start with the code. Start with the problem.")

H2(doc, "12.2 The script, with timings and exact clicks")
add_table(doc,
          ["Time", "On screen", "Say this (in your own words, but keep the numbers)"],
          [["0:00 – 1:00", "Overview",
            "“Eight servers report six metrics every minute for 45 days. That is about 3.1 million values. A traditional monitor uses one limit for everyone — alert if CPU is over 90%. That fails twice: a quiet server at 70% is in trouble but never triggers, and a busy server at 88% triggers while doing nothing wrong. So I built a system that learns a separate normal for each server.”"],
           ["1:00 – 2:00", "Overview",
            "“This is the fleet view. Green, amber, red are LOW, MEDIUM and HIGH risk. The blue cards tell me how many servers are abnormal this minute and the worst score. Each card has a two-hour sparkline and a 30-minute CPU forecast. The role line matters: 60% CPU is normal on the heaviest batch node and alarming on the quiet edge node.”"],
           ["2:00 – 4:00", "Switch to Model page, point at KPI row",
            "“I tested on the last 25% of the data — 126,728 minutes the models never saw. The learned detector caught 24 of 26 incidents, typically 3.5 minutes after they started. About 7 in 10 of its alarms were real: precision 0.695, recall 0.459, F1 0.553. The fixed CPU>90 rule scored F1 0.023 on the same data. That comparison is the core result.”"],
           ["4:00 – 5:30", "Model page, scroll to charts",
            "“Catch rate depends on the failure type: 96% of latency/error minutes, 91% of disk-fill minutes, but only 1% of memory-leak minutes. The leak is the honest blind spot: it rises slowly and hides inside normal daytime memory. On forecasting, XGBoost beats the naive guess on all eight servers — CPU MAE 2.53 vs 3.58, about 29% better. A SARIMA comparison actually lost, and I reported that instead of removing it.”"],
           ["5:30 – 7:00", "Server detail: click server-07, then Disk",
            "“This is server-07, which received two disk fills. Disk only goes up. The shaded bands are flagged periods, the red dots are individual flags, and the card estimates days to 90% from a seven-day trend. You can see why a fixed CPU threshold would miss this entirely: the problem is not CPU at all.”"],
           ["7:00 – 8:30", "Switch to CPU on server-05 or server-08",
            "“On CPU, the dashed line is the 30-minute forecast and the horizontal line is 90%. On server-08 the normal wave already reaches the high 80s, so the old rule fires on ordinary afternoons. The learned score stays low because that shape is normal for this machine. That is the whole idea in one picture.”"],
           ["8:30 – 9:30", "Alerts page",
            "“Alerts are just minutes whose risk is MEDIUM or HIGH. Each row has a score, the CPU forecast, and a reason generated by transparent rules. I can filter by severity or server, sort by how extreme the score is, and click through to the chart. The reason is a hint, not a root-cause diagnosis.”"],
           ["9:30 – 11:00", "Back to Model page, risk distribution",
            "“Overall, 96.4% of minutes are LOW, 3.2% MEDIUM and 0.48% HIGH. That is a usable alert volume: rare enough to trust, frequent enough to matter. The main limitations are synthetic data, the missed slow leaks, and the fact that the detector does not name the anomaly type. My next step would be a dedicated trend detector for leaks and a typed classifier on top.”"],
           ["11:00 – 12:00", "Overview or chart",
            "“To summarise: per-server learning beats a global threshold, forecasts beat the naive baseline on every server, and I can explain exactly where the system still fails. Thank you — I’m happy to go deeper on any number.”"]],
          [0.75, 1.65, 4.3], font=8.5)

H2(doc, "12.3 The 7-minute version")
N(doc, "**1 min:** problem + one fixed threshold cannot fit eight servers (use the server-06 vs server-08 example).")
N(doc, "**2 min:** Overview demo — KPIs, one card, role line, 30-minute forecast.")
N(doc, "**2 min:** Model page — 24/26, 3.5 min, F1 0.553 vs 0.023, MAE 2.53 vs 3.58.")
N(doc, "**1 min:** server-07 Disk chart — an incident a CPU threshold would never see.")
N(doc, "**1 min:** limitations — synthetic data, memory leak, no typing. Close with the one-line summary.")

H2(doc, "12.4 Demo choreography (do it in this order)")
B(doc, "**Overview first, always.** It answers “what is this?” without any jargon.")
B(doc, "**Then the Model page**, because the numbers justify the product. Do not leave it for the end; if time runs out, this is the page that matters.")
B(doc, "**Then one server detail** that matches your story: server-07 for disk, server-05/08 for CPU and false alarms.")
B(doc, "**Then Alerts**, briefly. It is the most familiar screen to a teacher and needs the least explanation.")
B(doc, "**Never open code during the demo** unless asked. If asked, open `risk.py` (short, readable rules) or `features.py`, not the whole repo.")

H2(doc, "12.5 If the demo breaks")
P(doc, "The API takes ~25–30 seconds to start and the frontend needs it for every page. If a page shows a red error card:")
B(doc, "Say: *“The backend fits eight models at startup, so it takes about half a minute. Let me show you the saved results while it comes up.”*")
B(doc, "Open `results.md`: it contains the same tables the Model page displays.")
B(doc, "Open `backend/plots/server-02_test.png`: it shows flags, forecast and labels on real generated data.")
B(doc, "Do not restart random processes in front of the class. Section 16 has the exact commands if you must.")

# ============================ 13. Q&A ============================
H1(doc, "13. Likely questions and ready answers")
P(doc, "Short answers you can say out loud. The parenthetical note is the deeper point if they push further.")

qa = [
    ["Is this real data?", "No — it is synthetic, generated with a fixed seed so it is reproducible. That gave me exact incident start and end times, which real logs rarely provide, so I could compute precision and recall honestly. (The pipeline itself is real; only the servers are simulated.)"],
    ["Why synthetic instead of a real dataset?", "I needed labelled incidents to evaluate detection. Public datasets exist, but they do not match this metric schema or give me controlled incident types. Synthetic data also avoids privacy problems. The trade-off is that the generator is simpler than reality, which I state as a limitation."],
    ["What is an Isolation Forest, in one sentence?", "It finds unusual points by repeatedly cutting the data at random; a point that gets isolated after very few cuts is unusual. (It is unsupervised, so it never sees the labels.)"],
    ["Why not use an LSTM or a deep model?", "The dataset is tabular, the patterns are daily cycles plus noise, and a tree model with lag features is strong, fast and explainable. A deep model would add complexity without evidence of better results at a 30-minute horizon."],
    ["Recall is only 46% — is that bad?", "Point-wise recall is 46%, but event-wise it caught 24 of 26 incidents within 3.5 minutes. An incident lasts many minutes, so one flag is enough to raise it. The low point-wise number is driven almost entirely by slow memory leaks."],
    ["Why is precision only 0.70?", "Because I deliberately capped false alarms at 0.5% of normal validation minutes. Lowering the threshold would raise recall and lower precision. It is a tunable trade-off, not a fixed property. (Show the confusion matrix.)"],
    ["Why does the CPU>90 rule do so badly?", "Eight servers have different baselines. server-08 normally reaches the high 80s, so the rule fires on normal afternoons; server-06 spiking from 22% to 60% never reaches 90. One global limit cannot represent eight machines."],
    ["How do I know the model isn't cheating with the labels?", "The label column is excluded from the feature list, and the split is chronological: train on the first 60%, test on the last 25%. The threshold is calibrated only on normal validation minutes. (`features.py` defines the feature list; `anomaly.py` drops labels.)"],
    ["Why 99.5th percentile for the threshold?", "It sets a false-alarm budget: about 0.5% of normal minutes may flag. I chose it because alert fatigue is the main failure mode of monitoring tools. It is a design choice, not a law."],
    ["Why is the memory leak missed?", "It adds about 0.07–0.1 memory points per minute over 4–6 hours, which is smaller than normal daytime variation. At a 0.5% false-alarm budget it hides under the noise. A dedicated long-window slope detector is the fix."],
    ["Why did SARIMA lose to the naive forecast?", "The daily shape is already captured by hour features in XGBoost, while SARIMA had to fit 1-minute noise and seasonality from a short window. Reporting the loss is more honest than deleting the comparison."],
    ["What is the dashboard actually showing live?", "A replay of the held-out test period at 60× speed, not production servers. One real second is one simulated minute; the nine-day window loops in about 3.6 hours."],
    ["Do incidents ever overlap?", "No. A boolean mask prevents reuse of minutes, so every labelled minute has exactly one cause. That keeps the evaluation clean."],
    ["How would this scale to 500 servers?", "Training is per server and embarrassingly parallel; scoring is a row-wise transform. The bottlenecks are memory and retraining cadence, so I would persist models, train in batch, and score streaming data."],
    ["How long does the pipeline take?", "Data generation and training take a few minutes; the API fits all 16 models at startup in about 25–30 seconds; evaluation writes the full report in about two minutes."],
    ["Why 30 minutes ahead for CPU?", "It is long enough to act — drain a node, add capacity — and short enough that the daily pattern still dominates, so accuracy stays useful. Longer horizons need uncertainty bands."],
    ["Is this detecting attacks?", "No. It detects abnormal behaviour relative to a server’s own baseline. An attack is one possible cause, but so is a bad deployment or a disk filling up. The wording throughout is deliberately “abnormal behaviour”."],
    ["What is the business value?", "Fewer missed incidents than a fixed threshold, far fewer false alarms than a noisy static rule, and a forecast that buys time before a limit is hit. It is decision support, not automatic remediation."],
    ["What would you do differently with more time?", "Add a leak-specific trend detector, type the anomalies with a supervised model, validate on a real/public dataset, and add uncertainty to forecasts."],
    ["Why does the site have no login or database?", "It is an MVP for one fixed dataset. The Parquet file is the store and the API scores in memory. A production version would need ingestion, persistence and access control."],
]
add_table(doc, ["Question", "Answer"], qa, [2.05, 4.65], font=8.5)

# ============================ 14. CHEAT SHEET ============================
H1(doc, "14. One-page cheat sheet")
P(doc, "The only numbers worth memorising. If you remember nothing else, remember the bold ones.")

H2(doc, "14.1 Data")
add_table(doc,
          ["Fact", "Value"],
          [["Fleet", "8 servers × 45 days × 1 minute"],
           ["Rows / metric values", "518,400 rows / about 3.1 million values"],
           ["Timeline", "2026-10-07 → 2026-11-20"],
           ["Injected incidents", "**102** (32 CPU spikes, 16 leaks, 16 network bursts, 16 latency/error, 16 multivariate, 6 disk fills)"],
           ["Labeled abnormal minutes", "11,642 = **2.25%** of all minutes"],
           ["Disk fills injected on", "server-01, server-04, server-07 (two each)"],
           ["Split", "60% train / 15% validation / 25% test, chronological"]],
          [2.25, 4.45], font=9)

H2(doc, "14.2 Detection (test set, 126,728 minutes)")
add_table(doc,
          ["Number", "Value", "Meaning"],
          [["Precision", "**0.695**", "7 in 10 flags are real"],
           ["Recall", "**0.459**", "46% of abnormal minutes caught"],
           ["F1", "**0.553**", "Balanced score"],
           ["CPU>90 rule F1", "0.023", "The baseline it beats"],
           ["Events caught", "**24 / 26**", "Median delay **3.5 min**"],
           ["CPU>90 events", "2 / 26", "Almost blind"],
           ["Strongest type", "latency/error 0.96 recall", "Also disk fill 0.91"],
           ["Weakest type", "memory leak 0.01 recall", "2 of 3 events touched, 82.5 min delay"]],
          [1.7, 2.05, 2.95], font=9)

H2(doc, "14.3 Forecasting")
add_table(doc,
          ["Number", "Value", "Meaning"],
          [["CPU MAE", "**2.53** vs naive 3.58", "~29% better, 30 min ahead"],
           ["CPU RMSE", "3.54 vs naive 4.84", "Large misses also reduced"],
           ["Best server gain", "server-05: 3.49 → 2.30 (−34%)", "Worst: server-07 −14%"],
           ["SARIMA check", "naive 1.20 · SARIMA 2.77 · XGB 2.08", "SARIMA lost; reported honestly"],
           ["Disk MAE", "1d 0.58 · 3d 1.64 · 7d 4.15", "Naive: 0.69 / 2.05 / 4.98"],
           ["Disk RMSE caveat", "worse at 3–7 days", "A few large misses remain"]],
          [1.6, 2.65, 2.45], font=9)

H2(doc, "14.4 Risk and runtime")
add_table(doc,
          ["Number", "Value", "Meaning"],
          [["Risk mix", "96.36% LOW · 3.16% MEDIUM · 0.48% HIGH", "Over 99,778 test minutes"],
           ["HIGH rule", "score ≥ 0.90 or CPU at/forecast ≥ 90%", "MEDIUM if flagged or trending ≥ 80%"],
           ["Replay", "60×, 9-day window, loops ~3.6 h", "1 real second = 1 simulated minute"],
           ["API startup", "~25–30 s", "Fits 8 Isolation Forests + 8 XGBoost models"],
           ["Polling", "every 5 s", "SWR on every screen"],
           ["Test points", "126,728 detection · 103,544 forecast · 99,778 risk", "All from the held-out tail"]],
          [1.35, 3.05, 2.3], font=9)

# ============================ 15. CHECKLIST ============================
H1(doc, "15. Before you present: checklist")
P(doc, "Ten minutes of setup prevents the two demo failures that actually happen: the API is not running, and the replay window has no alerts yet.")

H2(doc, "15.1 Ten minutes before")
add_table(doc,
          ["✓", "Task", "How to check"],
          [["☐", "Close heavy apps (browser tabs, games, Docker) to free RAM", "The pipeline needs roughly 2.5–3 GB free; the machine has ~16 GB total."],
           ["☐", "Start the API", "`cd backend` then `uvicorn api:app --host 127.0.0.1 --port 8000`; wait ~30 s."],
           ["☐", "Confirm the API is healthy", "Open `http://127.0.0.1:8000/health`; you should see `status: ok`, `servers: 8`, and a moving `now`."],
           ["☐", "Start the frontend", "`cd frontend` then `npm run dev`; open `http://localhost:3000`."],
           ["☐", "Check the LIVE pill and clock", "If the clock is frozen, the API is down or CORS failed — check the browser console."],
           ["☐", "Visit all four screens once", "Overview, a server detail, Alerts, Model evaluation. Confirm no red error cards."],
           ["☐", "Check Alerts has rows", "If it is empty, the replay is early. Leave the app running; incidents appear as the clock advances. As a fallback, use `/servers/server-07` and the Disk tab, which always has an incident history."],
           ["☐", "Open the fallback files", "`results.md` and `backend/plots/server-02_test.png` in separate windows."],
           ["☐", "Open this guide at Section 13", "For question time."],
           ["☐", "Silence notifications", "And set the browser to 100% zoom so the tables are readable on the projector."]],
          [0.35, 2.6, 3.75], font=8.5)

H2(doc, "15.2 During the demo")
B(doc, "Move slowly. One click, then talk. Do not scroll while speaking.")
B(doc, "Point at the exact element you are describing: the badge, the dashed line, the red band.")
B(doc, "If a number surprises you, read it from the screen instead of guessing.")
B(doc, "If something fails, switch to `results.md` and keep the same script. Never debug live.")

H2(doc, "15.3 The three sentences to end on")
P(doc, "*“Per-server learning beats one global threshold: 24 of 26 incidents versus 2 of 26. Forecasts beat the naive baseline on all eight servers. And I can tell you exactly where it still fails — slow memory leaks — and how I would fix that.”*")

# ============================ 16. APPENDIX ============================
H1(doc, "16. Appendix — files and commands")

H2(doc, "16.1 Where everything lives")
add_table(doc,
          ["Path", "What it contains"],
          [["`backend/config.py`", "Seed 42, 45 days, 8 server profiles, thresholds, replay speed, paths"],
           ["`backend/data_gen.py`", "Generates normal series, injects 102 incidents, writes `data/metrics.parquet` and the week-1 plot"],
           ["`backend/features.py`", "68 causal features per row: rolling stats, changes, deviations, time of day"],
           ["`backend/anomaly.py`", "Per-server Isolation Forest, validation threshold, scoring, event table"],
           ["`backend/forecast.py`", "XGBoost CPU +30 min, SARIMA comparison, disk trend, time-to-threshold"],
           ["`backend/risk.py`", "LOW/MEDIUM/HIGH rules and reason sentences"],
           ["`backend/api.py`", "FastAPI app, replay clock, all seven endpoints, startup training"],
           ["`backend/evaluate.py`", "Computes every reported metric and writes `results.md` + the test plot"],
           ["`results.md`", "The full evaluation report with all tables"],
           ["`backend/plots/`", "`server-01_week1.png` (data), `server-02_test.png` (detection vs forecast)"],
           ["`frontend/app/`", "Four screens: `/`, `/servers/[server]`, `/alerts`, `/model`"],
           ["`frontend/lib/results.ts`", "The evaluation numbers rendered on the Model page"],
           ["`frontend/lib/servers.ts`", "Eight human-written server profiles and metric explanations"],
           ["`backend/data/metrics.parquet`", "The entire 518,400-row dataset"]],
          [2.35, 4.35], font=8.5)

H2(doc, "16.2 Commands")
P(doc, "**Regenerate the dataset** (a few minutes):", size=9.5)
P(doc, "`cd backend`  →  `python data_gen.py`", size=9.5)
P(doc, "**Retrain and check the detector:**", size=9.5)
P(doc, "`python anomaly.py`", size=9.5)
P(doc, "**Rebuild the full report** (~2 minutes):", size=9.5)
P(doc, "`python evaluate.py`", size=9.5)
P(doc, "**Run the API:**", size=9.5)
P(doc, "`uvicorn api:app --host 127.0.0.1 --port 8000`", size=9.5)
P(doc, "**Run the dashboard:**", size=9.5)
P(doc, "`cd frontend`  →  `npm run dev`  →  open `http://localhost:3000`", size=9.5)

H2(doc, "16.3 The seven API endpoints")
add_table(doc,
          ["Endpoint", "Returns", "Used by"],
          [["`GET /health`", "status, simulated now, replay speed, data range, server count", "Top bar; setup check"],
           ["`GET /servers`", "Latest 6 metrics, score, forecast, severity, reason, sparklines for all 8", "Overview cards"],
           ["`GET /summary`", "Healthy/warning/critical counts, active anomalies, peak score", "Overview KPIs"],
           ["`GET /metrics?server=&metric=&range=`", "Downsampled series, anomaly windows, CPU forecast, 90% threshold", "Server chart"],
           ["`GET /anomalies`", "Flagged runs in the last 24 h with max score and severity", "Not used by the current UI (available for API demos)"],
           ["`GET /forecast?server=`", "CPU now / +30 min, minutes to 90%, disk now, %/day, days to 90%", "Server summary cards"],
           ["`GET /alerts?limit=`", "Recent MEDIUM/HIGH minutes with score, forecast, signal, reason", "Alerts table"]],
          [2.25, 3.15, 1.3], font=8.5)

P(doc, "", after=14)
callout(doc, "Final note",
        "You do not need to sound like an ML researcher. You need to sound like someone who built a system and knows where it is strong. "
        "Say the problem, show the four screens, quote 24/26, 3.5 minutes, F1 0.553 vs 0.023, MAE 2.53 vs 3.58 — then name the memory-leak blind spot before anyone asks. "
        "That combination is far more convincing than perfect numbers.",
        bg="F3F7EE", bar="4F7A28", title_color=RGBColor(0x3D, 0x5F, 0x1F))

doc.save(OUT)
print("saved", OUT, OUT.stat().st_size)
print("paragraphs", len(doc.paragraphs), "tables", len(doc.tables))
