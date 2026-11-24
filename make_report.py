"""Build Mini_Project_Report_PulseGrid.docx from the CSET312 template layout."""

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor

ROOT = Path(__file__).parent
ASSETS = ROOT / "report_assets"
OUT = ROOT / "_report_final.docx"

TITLE = "PULSEGRID: AI-POWERED INFRASTRUCTURE ANOMALY DETECTION AND FORECASTING"
STUDENTS = [
    ("Shikhar Verma", "S24CSEU2818"),
    ("Shushant Ranjan", "S24CSEU2802"),
    ("Akshara Singh", "S24CSEU2813"),
]
GITHUB = "https://github.com/<your-username>/pulsegrid"
MENTOR = "[Mentor Name] ([Designation])"

# ---------------------------------------------------------------- low level xml


def field(paragraph, instr, placeholder="1"):
    """Insert a Word field (TOC, PAGE, SEQ ...) with a cached placeholder result."""
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = placeholder
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for el in (begin, instr_el, sep, text, end):
        run._r.append(el)


def shade(paragraph_or_cell, hex_fill):
    pr = paragraph_or_cell._p.get_or_add_pPr() if hasattr(paragraph_or_cell, "_p") else paragraph_or_cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    pr.append(shd)


def page_numbers(section, fmt=None, start=None):
    sect_pr = section._sectPr
    el = sect_pr.find(qn("w:pgNumType"))
    if el is None:
        el = OxmlElement("w:pgNumType")
        sect_pr.append(el)
    if fmt:
        el.set(qn("w:fmt"), fmt)
    if start is not None:
        el.set(qn("w:start"), str(start))


def footer_page_number(section):
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    field(p, " PAGE ", "1")
    for run in p.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)


def keep_with_next(paragraph, on=True):
    paragraph.paragraph_format.keep_with_next = on


def cant_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    tr_pr.append(el)


# ---------------------------------------------------------------- setup


doc = Document()

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
pf = normal.paragraph_format
pf.line_spacing = 1.5
pf.space_after = Pt(6)
pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

for name, size, bold, italic, before, after in (
    ("Heading 1", 14, True, False, 14, 8),
    ("Heading 2", 12.5, True, False, 10, 6),
    ("Heading 3", 12, True, True, 8, 4),
):
    st = doc.styles[name]
    st.font.name = "Times New Roman"
    st.font.size = Pt(size)
    st.font.bold = bold
    st.font.italic = italic
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    st.paragraph_format.space_before = Pt(before)
    st.paragraph_format.space_after = Pt(after)
    st.paragraph_format.line_spacing = 1.15
    st.paragraph_format.keep_with_next = True
    st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

cap = doc.styles["Caption"]
cap.font.name = "Times New Roman"
cap.font.size = Pt(10)
cap.font.bold = False
cap.font.italic = False
cap.font.color.rgb = RGBColor(0, 0, 0)
cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.paragraph_format.space_before = Pt(4)
cap.paragraph_format.space_after = Pt(10)
cap.paragraph_format.line_spacing = 1.0

front = doc.styles.add_style("Front Heading", 1)  # 1 = paragraph
front.base_style = normal
front.font.name = "Times New Roman"
front.font.size = Pt(14)
front.font.bold = True
front.font.color.rgb = RGBColor(0, 0, 0)
front.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
front.paragraph_format.space_before = Pt(0)
front.paragraph_format.space_after = Pt(18)
front.paragraph_format.line_spacing = 1.5

code_style = doc.styles.add_style("Code Block", 1)
code_style.base_style = normal
code_style.font.name = "Consolas"
code_style.font.size = Pt(8.5)
code_style.element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
code_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
code_style.paragraph_format.line_spacing = 1.0
code_style.paragraph_format.space_before = Pt(0)
code_style.paragraph_format.space_after = Pt(0)
code_style.paragraph_format.left_indent = Inches(0.15)

for section in doc.sections:
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)


def para(text="", style=None, align=None, space_after=None, bold=False, italic=False, size=None):
    p = doc.add_paragraph(style=style)
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        if size:
            run.font.size = Pt(size)
    if align is not None:
        p.alignment = align
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    return p


def rich(parts, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=None):
    """parts: list of (text, bold, italic)."""
    p = doc.add_paragraph()
    p.alignment = align
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    for text, bold, italic in parts:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
    return p


def bullet(text, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.35)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_lead:
        p.add_run(bold_lead).bold = True
    p.add_run(text)
    return p


def numbered(text, bold_lead=None):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.left_indent = Inches(0.35)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_lead:
        p.add_run(bold_lead).bold = True
    p.add_run(text)
    return p


def caption(kind, text):
    p = doc.add_paragraph(style="Caption")
    p.add_run(f"{kind} ")
    field(p, f" SEQ {kind} \\* ARABIC ", "1")
    p.add_run(f": {text}")
    return p


def table_caption(text):
    p = caption("Table", text)
    keep_with_next(p)
    return p


def figure(path, width_in, cap_text=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    keep_with_next(p)
    p.add_run().add_picture(str(ASSETS / path), width=Inches(width_in))
    if cap_text:
        caption("Figure", cap_text)


def table(headers, rows, widths=None, font_size=9.5, align_center=True, header_fill="EDEDED"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0]
    cant_split(hdr)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(font_size)
        run.font.name = "Times New Roman"
        shade(cell, header_fill)
    for row_data in rows:
        row = t.add_row()
        cant_split(row)
        for i, text in enumerate(row_data):
            cell = row.cells[i]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (align_center and i > 0) else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            run = p.add_run(str(text))
            run.font.size = Pt(font_size)
            run.font.name = "Times New Roman"
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    return t


def code(lines, show_numbers=True):
    for i, line in enumerate(lines):
        p = doc.add_paragraph(style="Code Block")
        p.paragraph_format.keep_together = True
        shade(p, "F4F4F4")
        prefix = f"{i + 1:>3}  " if show_numbers else ""
        if prefix:
            run = p.add_run(prefix)
            run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
            run.font.name = "Consolas"
            run.font.size = Pt(8.5)
        run = p.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)


def algorithm(title, lines):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    keep_with_next(p)
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(10.5)
    code(lines)


def update_fields_on_open():
    settings = doc.settings.element
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    settings.append(el)


# ---------------------------------------------------------------- cover page

cover = doc.sections[0]
cover.footer.is_linked_to_previous = False

p = para(TITLE, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=26, bold=True, size=20)
p.paragraph_format.line_spacing = 1.3
p.paragraph_format.space_before = Pt(24)

para("A MINI-PROJECT REPORT (CSET312)", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10, bold=True, size=13)
para("BY", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14, bold=True, size=12)

for name, enrol in STUDENTS:
    p = para(name, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0, bold=True, size=12)
    p.paragraph_format.line_spacing = 1.2
    p = para(f"({enrol})", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8, size=12)
    p.paragraph_format.line_spacing = 1.2

logo = doc.add_paragraph()
logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
logo.paragraph_format.space_before = Pt(12)
logo.paragraph_format.space_after = Pt(12)
logo.add_run().add_picture(str(ASSETS / "university_logo.png"), width=Inches(3.3))

para("SUBMITTED TO", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8, bold=True, size=12)
p = para("SCHOOL OF COMPUTER SCIENCE ENGINEERING AND TECHNOLOGY, BENNETT UNIVERSITY",
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6, bold=True, size=12)
p.paragraph_format.line_spacing = 1.3
p = para("GREATER NOIDA, 201310, UTTAR PRADESH, INDIA", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=22, size=12)
p.paragraph_format.line_spacing = 1.3
para("Dec 2026", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12)

# ---------------------------------------------------------------- front matter

front_section = doc.add_section(WD_SECTION.NEW_PAGE)
page_numbers(front_section, fmt="lowerRoman", start=2)
footer_page_number(front_section)


def signature_block(heading):
    t = doc.add_table(rows=1, cols=3)
    t.autofit = False
    for i, (name, enrol) in enumerate(STUDENTS):
        cell = t.rows[0].cells[i]
        cell.width = Inches(2.08)
        cell.text = ""
        first = cell.paragraphs[0]
        first.paragraph_format.space_before = Pt(0)
        first.paragraph_format.space_after = Pt(28)
        first.paragraph_format.line_spacing = 1.0
        first.add_run(heading).italic = True
        second = cell.add_paragraph()
        second.paragraph_format.space_after = Pt(0)
        second.paragraph_format.line_spacing = 1.0
        second.add_run(name).bold = True
        third = cell.add_paragraph()
        third.paragraph_format.line_spacing = 1.0
        third.add_run(f"(Enroll. No. {enrol})")


para("DECLARATION", style="Front Heading")
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(14)
p.add_run("I/We hereby declare that the work which is being presented in the report entitled ")
p.add_run("\u201cPulseGrid: AI-Powered Infrastructure Anomaly Detection and Forecasting\u201d").bold = True
p.add_run(
    ", is an authentic record of my/our own work carried out during the period from August 2026 to "
    "December 2026 at School of Computer Science and Engineering and Technology, Bennett University, "
    "Greater Noida."
)
p = doc.add_paragraph()
p.add_run("The matter and the results presented in this report have not been submitted by me/us for the award "
          "of any other degree elsewhere.")
p.paragraph_format.space_after = Pt(26)

signature_block("Signature of Candidate")
doc.add_page_break()

para("ACKNOWLEDGEMENT", style="Front Heading")
p = doc.add_paragraph()
p.add_run("I/We would like to take this opportunity to express my/our deepest gratitude to my/our mentor, ")
p.add_run(MENTOR).bold = True
p.add_run(
    ", for guiding, supporting and helping me/us in every possible way. I/we were extremely fortunate to have "
    "this mentorship, as it provided insightful solutions to the problems faced by us and contributed immensely "
    "towards the completion of this mini-project. I/We would also like to express my/our deepest gratitude to "
    "the Vice Chancellor, the Dean, the Head of the Department, the faculty members and our friends who helped "
    "us in the successful completion of this work."
)
p.paragraph_format.space_after = Pt(26)

signature_block("Signature of Candidate")
doc.add_page_break()

# --- table of contents
para("TABLE OF CONTENTS", style="Front Heading")
p = doc.add_paragraph()
p.paragraph_format.line_spacing = 1.0
field(p, ' TOC \\o "1-3" \\h \\z \\u ',
      "Right-click here and choose Update Field to build the table of contents.")
doc.add_page_break()

para("LIST OF TABLES", style="Front Heading")
p = doc.add_paragraph()
p.paragraph_format.line_spacing = 1.0
p.add_run("[[LIST_OF_TABLES]]")
doc.add_page_break()

para("LIST OF FIGURES", style="Front Heading")
p = doc.add_paragraph()
p.paragraph_format.line_spacing = 1.0
p.add_run("[[LIST_OF_FIGURES]]")
doc.add_page_break()

# --- abbreviations
para("LIST OF ABBREVIATIONS", style="Front Heading")
ABBREVIATIONS = [
    ("API", "Application Programming Interface"),
    ("CPU", "Central Processing Unit"),
    ("DFD", "Data Flow Diagram"),
    ("ER", "Entity\u2013Relationship"),
    ("FP", "False Positive"),
    ("IF", "Isolation Forest"),
    ("JSON", "JavaScript Object Notation"),
    ("KPI", "Key Performance Indicator"),
    ("MAE", "Mean Absolute Error"),
    ("ML", "Machine Learning"),
    ("OS", "Operating System"),
    ("RMSE", "Root Mean Squared Error"),
    ("SARIMA", "Seasonal Autoregressive Integrated Moving Average"),
    ("SRS", "Software Requirement Specification"),
    ("TOC", "Table of Contents"),
    ("UI", "User Interface"),
    ("UML", "Unified Modeling Language"),
    ("XGB", "Extreme Gradient Boosting"),
]
table(["Abbreviation", "Explanation of the Abbreviation"], ABBREVIATIONS, widths=[1.7, 4.5], align_center=False)
doc.add_page_break()

# --- abstract
para("ABSTRACT", style="Front Heading")
ABSTRACT = (
    "Modern application platforms run on fleets of machines whose health is described by a continuous stream of "
    "resource metrics. Operations teams are expected to notice a machine that is drifting towards failure long "
    "before a user does, yet threshold dashboards either stay silent or flood the on-call engineer with noise. "
    "This mini-project presents PulseGrid, a web-based monitoring dashboard that learns the normal behaviour of "
    "eight heterogeneous servers, scores every one-minute reading for abnormality, forecasts CPU utilisation and "
    "disk growth, and converts those signals into a single LOW, MEDIUM or HIGH risk verdict with a written reason. "
    "Telemetry is generated from a configurable workload model so that ground truth is known exactly: 518,400 "
    "minute-level rows cover 45 days, of which 11,642 minutes (2.25%) belong to 102 injected incidents of six "
    "kinds. A per-server Isolation Forest is trained on the first 60% of each timeline, calibrated on the next "
    "15% for a 0.5% false-positive budget, and evaluated on the held-out last 25%. The detector reaches a "
    "precision of 0.695, a recall of 0.459 and an F1 score of 0.553 on 126,728 test points, and it raises a "
    "signal for 24 of the 26 test incidents with a median delay of 3.5 minutes, against 2 of 26 for a static "
    "CPU-above-90 rule. An XGBoost regressor predicts CPU utilisation 30 minutes ahead with a mean absolute "
    "error of 2.53 percentage points against 3.58 for a persistence baseline, and a seven-day linear trend "
    "forecasts disk occupancy better than the naive value at one, three and seven day horizons. The risk engine "
    "classifies 96.36% of test minutes as LOW, 3.16% as MEDIUM and 0.48% as HIGH, so that a small number of "
    "urgent items can be read at a glance. All numbers reported here are reproduced by the evaluation script in "
    "the repository, and the conclusions discuss where the approach still fails, most visibly on slow memory "
    "leaks that hide inside the normal daytime distribution."
)
para(ABSTRACT)

_body_section = doc.add_section(WD_SECTION.NEW_PAGE)
page_numbers(_body_section, fmt="decimal", start=1)
footer_page_number(_body_section)

# ---------------------------------------------------------------- 1 introduction

doc.add_heading("1. INTRODUCTION", level=1)

para(
    "Every online service that people rely on is, underneath, a collection of machines reporting numbers about "
    "themselves. A single application server publishes its processor load, memory occupancy, disk usage, network "
    "throughput, request latency and error rate once a minute; a modest fleet of eight machines therefore produces "
    "more than eleven thousand measurements every hour. The numbers are easy to collect and surprisingly hard to "
    "act on. A static dashboard shows the same charts whether the system is healthy or five minutes away from an "
    "outage, and a threshold rule such as \u201cpage me when CPU is above 90%\u201d ignores the shape of the signal "
    "entirely: it stays quiet while memory creeps upwards for two days, and it fires repeatedly on a machine whose "
    "normal afternoon peak is already close to the limit."
)
para(
    "Cloud providers responded to this gap by turning monitoring into a machine-learning problem. Managed "
    "services now learn a baseline per metric, score deviations and forecast capacity, and the research behind "
    "them is well documented in the anomaly-detection and time-series literature that this report reviews. What "
    "is less available is a small, inspectable system that a student team can build end to end \u2014 one that "
    "generates its own labelled telemetry, trains a detector and a forecaster, fuses their outputs into an "
    "operational verdict and explains every verdict in words. PulseGrid is that system."
)
para(
    "PulseGrid simulates a fleet of eight servers with deliberately different personalities: one is a lightly "
    "loaded internal tool, another is a busy database host, and their normal CPU, memory and disk levels differ by "
    "a factor of three. Because the data is generated rather than borrowed, the exact minute at which every "
    "injected incident begins and ends is known, which allows the detector to be scored honestly on a held-out "
    "period instead of on anecdotes. The dashboard then answers three questions for the operator:"
)
bullet("is this machine behaving normally right now, and if not, how unusual is it?", "Detection: ")
bullet("where is CPU utilisation heading in the next half hour, and how many days of disk space remain?", "Forecast: ")
bullet("given both answers, how urgently should a human look at this machine, and why?", "Risk: ")
para(
    "The remainder of this report follows the CSET312 structure: the next chapter states the problem and reviews "
    "the research that shaped the design, Chapter 3 describes the methodology, diagrams, interface and "
    "implementation, and Chapter 4 reports the measured results and the work that remains."
)

doc.add_heading("1.1. Problem Statement", level=2)
para(
    "Operations teams that run a fleet of servers have no cheap way to tell a slow degradation from ordinary "
    "daily variation. Threshold alerting, which is what most small teams deploy, is simultaneously too late and "
    "too noisy: it reacts only after a resource has already crossed a fixed limit, it cannot see a trend that will "
    "cross that limit tomorrow, and on heterogeneous hardware a single limit produces false alarms on the busy "
    "machines while real incidents on the quiet ones stay invisible. The result is alert fatigue followed by "
    "missed incidents."
)
para(
    "The problem addressed by this project is therefore to build a monitoring system that (i) learns a separate "
    "notion of normal for every server from unlabelled history, (ii) reports an incident at the level of an "
    "episode rather than a single noisy minute, (iii) forecasts the two resources that cause most capacity "
    "incidents \u2014 CPU saturation and disk exhaustion \u2014 before they happen, and (iv) presents the outcome "
    "as a small number of ranked, explained risk items that an on-call engineer can trust."
)

# ---------------------------------------------------------------- 2 background

doc.add_heading("2. BACKGROUND RESEARCH", level=1)
para(
    "This chapter records the research that preceded the implementation. It first fixes the goals of the project "
    "in measurable terms, then reviews the published work on anomaly detection, industrial telemetry monitoring "
    "and time-series forecasting, and finally argues that the proposed system is feasible with the tools and time "
    "available to a three-member student team."
)

doc.add_heading("2.1. Goals and Objectives", level=2)
para(
    "The goals below were written before any code was produced and were used to judge the finished system. Each "
    "one is stated so that it can be checked against a number rather than an impression."
)
table_caption("Goals and objectives of the project")
table(
    ["#", "Goal or objective", "How it is verified"],
    [
        ["1", "Detect abnormal behaviour without hand-written thresholds for each metric",
         "One Isolation Forest per server; threshold calibrated on normal validation data only"],
        ["2", "Keep false alarms rare enough for a human to trust the alert list",
         "At most 0.5% of normal validation minutes may be flagged; measured precision reported"],
        ["3", "Report incidents as episodes, not isolated minutes",
         "Event-wise recall and median detection delay over 26 labelled test incidents"],
        ["4", "Forecast CPU 30 minutes ahead better than persistence",
         "MAE and RMSE against a naive last-value forecast on 103,544 test points"],
        ["5", "Estimate disk exhaustion in days instead of only reporting current usage",
         "Seven-day trend extrapolation scored at 1, 3 and 7 day horizons"],
        ["6", "Reduce the fleet to a short, explained list of risks",
         "LOW/MEDIUM/HIGH verdict with a textual reason for every scored minute"],
        ["7", "Ship a usable dashboard, not a notebook",
         "Fleet overview, per-server detail, alert list and model page served by a live API"],
    ],
    widths=[0.4, 3.1, 2.7],
    font_size=9,
)
para(
    "A deliberate non-goal was also recorded: the project does not attempt root-cause analysis across service "
    "dependencies. PulseGrid watches machines, not request traces, and a distributed-tracing backend would have "
    "doubled the scope without changing the detection problem being studied."
)

doc.add_heading("2.2. Literature Review and Project Feasibility", level=2)
para(
    "The literature relevant to this project falls into four groups: general anomaly-detection theory, classical "
    "unsupervised detectors that work on tabular measurements, deep sequence models built for telemetry, and "
    "forecasting methods. The review below follows those groups and ends with the gap that PulseGrid fills."
)
para(
    "Chandola, Banerjee and Kumar [3] provide the vocabulary that the rest of this literature uses. They separate "
    "point anomalies, in which one measurement is unusual on its own, from contextual anomalies, in which a value "
    "is unusual only given its context such as the hour of the day, and from collective anomalies, in which a "
    "sequence of individually plausible values is abnormal as a group. They also separate supervised, "
    "semi-supervised and unsupervised formulations, and observe that labels are usually unavailable in "
    "operational settings and expensive to obtain even when they exist. Both observations shaped PulseGrid: its "
    "detector is trained unsupervised, because a real operator has no labelled incident history, and its "
    "features include the hour of day and rolling baselines precisely so that a daily peak is not mistaken for a "
    "point anomaly."
)
para(
    "Isolation Forest, introduced by Liu, Ting and Zhou [1] and later analysed in depth by the same authors [2], "
    "is the detector chosen for this project. Instead of profiling what normal data looks like, it builds an "
    "ensemble of random binary trees that repeatedly split the data on a random feature at a random value; a "
    "point that is easy to isolate needs few splits and therefore has a short average path length, and that path "
    "length becomes the anomaly score. The method runs in linear time with a small memory footprint, makes no "
    "assumption about the distribution of the data, and requires no labels, which is exactly the operating "
    "condition of a monitoring agent. Its known weakness is equally relevant: because every split is aligned to a "
    "single axis, an anomaly that consists of an unusual combination of two individually normal values is harder "
    "to isolate, a limitation that reappears in this project as the multivariate anomaly type."
)
para(
    "Density-based and boundary-based alternatives were considered and rejected for this use case. Local Outlier "
    "Factor compares the local density around a point with the densities around its neighbours and is excellent "
    "for finding small clusters of unusual points, but it requires a nearest-neighbour search that becomes "
    "expensive as history grows and needs a sensible choice of neighbourhood size for every server. One-class "
    "support vector machines learn a boundary around normal data in a kernel space and are attractive in theory, "
    "but their cost scales poorly beyond a few thousand samples and their sensitivity parameter is difficult to "
    "set without labels. Since PulseGrid scores hundreds of thousands of rows per run on a laptop, the linear "
    "cost and the few hyperparameters of Isolation Forest were decisive."
)
para(
    "Industrial practice supplies the second group. Ahmad, Lavin, Purdy and Agha [6] describe an unsupervised "
    "real-time anomaly-detection pipeline deployed on Microsoft Azure telemetry. Their system maintains a model "
    "per metric, combines a simple extreme-value test with a seasonal model and a multivariate model, and reports "
    "roughly a twenty percent improvement over the previous production detector together with a large reduction "
    "in false positives. Two design decisions in PulseGrid are direct descendants of that paper: thresholds are "
    "calibrated per server rather than globally, and the detector emits a score that is later combined with other "
    "signals instead of a bare boolean. The same group produced the Numenta Anomaly Benchmark [5], which made "
    "explicit that point-wise precision and recall are poor measures for this problem. A detector that fires "
    "during the right incident but two minutes late is useful to an operator, yet point-wise recall punishes it "
    "for the minutes it missed before firing. NAB rewards early detection through an application-specific "
    "scoring function, and PulseGrid adopts the same philosophy by reporting event-wise recall and median delay "
    "alongside the conventional point metrics."
)
para(
    "The third group applies deep learning to telemetry. Hundman et al. [7] describe the system used at NASA's "
    "Jet Propulsion Laboratory for spacecraft telemetry: an LSTM predicts the next value of each channel, the "
    "residual between prediction and observation is thresholded with a dynamically computed limit, and a pruning "
    "step removes isolated spikes. Their paper is candid about the cost: the pipeline needs a labelled subset for "
    "tuning and a separate model per channel. Su et al. [8] go further with OmniAnomaly, which combines a "
    "recurrent network with a variational autoencoder and normalising flows to model the distribution of "
    "multivariate windows and scores a window by its reconstruction probability; it is the strongest published "
    "result on several server datasets, but it needs GPU training and produces a score whose scale is difficult "
    "to explain to an operator. DeepLog [10] attacks the adjacent problem of log-key sequences with an LSTM and a "
    "top-k ranking of predicted events, showing how sequence models can learn execution structure from raw logs "
    "without hand-crafted rules."
)
para(
    "A production-oriented middle ground is offered by Ren et al. [9], who describe the time-series anomaly "
    "detection service used inside Microsoft. Their method applies a spectral residual transform to the saliency "
    "of a series and then a small convolutional network to combine the resulting saliency map with the original "
    "signal, which is fast, needs no training labels and handles seasonality gracefully. It is deployed at scale "
    "and is the closest industrial analogue to what PulseGrid does, yet its per-series formulation and its "
    "emphasis on single-KPI signals leave room for a system that treats the six metrics of a machine jointly and "
    "then reasons about risk."
)
para(
    "Forecasting is the fourth group. Chen and Guestrin [4] introduced XGBoost, a regularised gradient-boosted "
    "tree implementation that has become the default for tabular regression: it handles heterogeneous features "
    "such as lagged values, rolling statistics and calendar fields, trains in seconds on a CPU, and exposes "
    "feature importance for interpretation. Classical seasonal models remain a fair baseline, and Hyndman and "
    "Athanasopoulos [11] argue that every forecast should be compared against a naive method before it is called "
    "useful, because persistence is hard to beat on strongly autocorrelated signals. That advice is followed "
    "literally in this project: a seasonal ARIMA model and an XGBoost model are both scored against persistence "
    "on the same forecast origins, and the seasonal model is reported even where it loses."
)
para(
    "Taken together, the reviewed work establishes that unsupervised, per-entity scoring is the right foundation "
    "for fleet monitoring, that point-wise accuracy is the wrong target, and that gradient-boosted trees are a "
    "credible forecaster for minute-level resource data. What it does not provide is a small, reproducible "
    "artefact that connects detection, calibration, forecasting and risk fusion on a heterogeneous fleet and "
    "measures each stage against a known ground truth. Building that artefact, and reporting honestly where it "
    "fails, is the contribution of this mini-project."
)

doc.add_heading("2.2.1. Technical Feasibility", level=3)
para(
    "Every component of the proposed system exists as a mature open-source library. Data generation, feature "
    "engineering and evaluation require only NumPy and pandas; the detector uses scikit-learn's Isolation Forest; "
    "the forecaster uses XGBoost and statsmodels; the API uses FastAPI with Uvicorn; and the dashboard uses "
    "Next.js and React with Recharts. Storage is a single Parquet file of 518,400 rows, roughly forty megabytes, "
    "which fits comfortably in memory, so no database server is needed. Training the eight detectors and eight "
    "forecasters completes in a few minutes on a four-core laptop with no GPU, which means the whole pipeline can "
    "be re-run during a demonstration."
)

doc.add_heading("2.2.2. Economic and Operational Feasibility", level=3)
para(
    "The system runs entirely on free and open-source software, so the licence cost is zero and no cloud account "
    "is required. Operationally it is read-only: it observes a telemetry stream and never issues commands to the "
    "machines it watches, which removes the safety concerns that accompany automated remediation. Because the "
    "data source is a replay of generated telemetry, the dashboard can be demonstrated at sixty simulated seconds "
    "per real second and restarted deterministically, which makes the project suitable for evaluation in a "
    "classroom without live infrastructure. The same interface would accept a real metrics feed by replacing the "
    "data-access functions, which keeps the migration path short."
)

# ---------------------------------------------------------------- 3 methodology

doc.add_heading("3. METHODOLOGY", level=1)

doc.add_heading("3.1. Proposed System Overview", level=2)
para(
    "PulseGrid is a monitoring and decision-support system for a fleet of servers. Its purpose is to shorten the "
    "distance between a machine starting to misbehave and a human understanding that it needs attention. The "
    "system ingests minute-level telemetry, learns the normal behaviour of each machine independently, scores "
    "every reading, forecasts the two resources that cause capacity incidents, and fuses all of that into a risk "
    "verdict that is shown on a dashboard. The intended outcome is that an operator opens one page, sees eight "
    "machines ordered by urgency, and can justify every red item by reading the reason attached to it."
)
para(
    "Architecturally the system is a four-stage pipeline behind a thin web interface, shown in Figure 1. An "
    "offline stage generates and stores telemetry; a scoring stage builds features and applies the trained models; "
    "a serving stage exposes the scored data over HTTP; and a presentation stage renders it in the browser. The "
    "offline and scoring stages are pure Python and run as scripts, while the serving stage keeps the scored "
    "frame in memory and replays it against the wall clock so that the dashboard appears live."
)
figure("fig_architecture.png", 6.1, "System architecture: offline training, in-memory scoring and the browser dashboard")
para(
    "Separating the pipeline this way has three practical benefits. First, model training is decoupled from "
    "serving, so the dashboard never waits for a model to fit. Second, the scored frame contains both the raw "
    "measurement and the model's opinion of it, which makes the interface able to show a prediction next to the "
    "value that produced it. Third, the replay clock means the same code path serves a demonstration and a live "
    "feed, with only the data-access functions differing."
)

doc.add_heading("3.2. Users and Roles", level=2)
para(
    "Three kinds of user interact with PulseGrid. They differ in what they need from the same data rather than in "
    "what they are allowed to see, so the system implements one dashboard with role-appropriate entry points "
    "rather than a separate application per role."
)
table_caption("Users of the system and their roles")
table(
    ["User", "Primary need", "Main screens"],
    [
        ["Operations engineer",
         "Find the machine that needs attention now and understand why it was flagged",
         "Fleet overview, server detail, alert list"],
        ["Site reliability lead",
         "Judge whether the fleet is drifting over days and whether the detector is trustworthy",
         "Fleet overview trends, alert history, model page"],
        ["Evaluator or reviewer",
         "Check the claims of the project against measurable evidence",
         "Model page with precision, recall and forecast error"],
    ],
    widths=[1.4, 3.1, 1.7],
    font_size=9.5,
    align_center=False,
)
para(
    "Because this is a read-only monitoring tool, no role can change state; the only write operation in the whole "
    "system is the offline generation of telemetry. That property keeps the authorisation model trivial and means "
    "the interface can be shared without risk."
)

doc.add_heading("3.3. Detailed Workflow", level=2)
para(
    "The step-by-step operation of the system is described below, and the data-flow diagram in Section 3.4.4 "
    "shows the same sequence graphically."
)
numbered("Eight server profiles are declared in configuration, each with its own CPU level, daily amplitude, "
         "noise, memory baseline, network volume, latency and disk fill rate. A workload model combines a daily "
         "sinusoid, a weekly shape, correlated bursts and noise to produce one reading per minute for 45 days, "
         "yielding 518,400 rows across the six metrics.",
         "Generate the telemetry. ")
numbered("Six anomaly types are injected at known times with known durations: CPU spikes, memory leaks, disk "
         "fill, latency and error bursts, network bursts, and multivariate incidents in which no single metric is "
         "extreme. In total 102 incidents produce 11,642 abnormal minutes, 2.25% of the dataset.",
         "Inject labelled incidents. ")
numbered("Each server's timeline is ordered and cut into 60% training, 15% validation and 25% test. Features "
         "are built only from past values, so a reading never sees its own future.",
         "Split chronologically. ")
numbered("For every server and metric the pipeline adds rolling means and standard deviations over 5, 15 and "
         "60 minutes, first differences over 1 and 60 minutes, deviations from 6-hour and 24-hour baselines, and "
         "sinusoidal encodings of the hour of day. Slow baselines are what allow a leak to look unusual.",
         "Build features. ")
numbered("An Isolation Forest is fitted on the training slice of each server. Raw scores on the validation "
         "slice are rescaled to the unit interval, and the 99.5th percentile of the scores of known-normal "
         "validation minutes becomes that server's alerting threshold.",
         "Train and calibrate. ")
numbered("Every reading in every split receives a score and a flag. Consecutive flagged readings of the same "
         "incident are grouped into an event, and the delay from the true incident start to the first flag is "
         "recorded, because an operator cares about episodes and minutes of warning, not individual points.",
         "Score and group into events. ")
numbered("A separate XGBoost model per server predicts CPU utilisation 30 minutes ahead from lagged values, "
         "rolling statistics, calendar fields and the other five metrics. A seven-day linear fit on daily disk "
         "occupancy extrapolates the day on which the disk would reach 90%.",
         "Forecast. ")
numbered("The risk engine applies ordered rules to each scored minute: HIGH if the anomaly score is at least "
         "0.90 or CPU is at, or forecast to reach, 90%; MEDIUM if the reading is flagged or CPU is trending to "
         "80%; otherwise LOW. The rules also assemble a human-readable reason.",
         "Assess risk. ")
numbered("The API loads the scored frame, advances a replay cursor at sixty simulated seconds per real second, "
         "and answers requests for the fleet summary, per-server metric windows, the alert list and the model "
         "metrics. The dashboard polls it every few seconds.",
         "Serve and display. ")

para(
    "The server profiles and the injected anomaly types are the two inputs that determine everything downstream, "
    "so both are recorded in full. Table 3 lists the fleet, and Table 4 lists the incident vocabulary."
)
table_caption("Server profiles used by the telemetry generator")
table(
    ["Server", "Role", "CPU base / amplitude", "Memory base", "Disk fill (%/day)", "Network (Mbps)"],
    [
        ["server-01", "Internal tooling", "26 / 14", "36", "0.30", "150"],
        ["server-02", "Web front end", "38 / 20", "48", "0.15", "240"],
        ["server-03", "Application", "48 / 16", "55", "0.40", "320"],
        ["server-04", "Batch worker", "31 / 11", "42", "0.20", "180"],
        ["server-05", "Database primary", "57 / 22", "60", "0.10", "410"],
        ["server-06", "Cache", "22 / 9", "30", "0.05", "110"],
        ["server-07", "Analytics", "44 / 18", "52", "0.20", "290"],
        ["server-08", "API gateway", "63 / 24", "68", "0.05", "460"],
    ],
    widths=[0.85, 1.35, 1.3, 0.85, 1.05, 1.05],
    font_size=9,
    align_center=True,
)

figure("../backend/plots/server-01_week1.png", 6.0,
       "One week of generated telemetry for server-01, with the injected incidents highlighted")

table_caption("Injected anomaly types and their signature")
table(
    ["Type", "What it simulates", "Signature in the metrics", "Test points"],
    [
        ["cpu_spike", "A runaway process or a traffic surge", "CPU jumps 25\u201340 points for 5\u201320 minutes", "247"],
        ["memory_leak", "A process that never releases memory", "Memory rises slowly and does not fall back overnight", "924"],
        ["disk_fill", "Log rotation failing or a growing data directory", "Disk occupancy climbs at 3\u20138 times the normal rate", "727"],
        ["latency_error", "A downstream dependency degrading", "Latency and error rate rise together, CPU flat", "50"],
        ["network_burst", "Backup or replication traffic", "Network throughput doubles while other metrics stay calm", "126"],
        ["multivariate", "Interaction between resources", "No single metric is extreme, but the combination is unusual", "192"],
    ],
    widths=[1.0, 1.9, 2.6, 0.7],
    font_size=9,
    align_center=False,
)

table_caption("Chronological data splits")
table(
    ["Split", "Share", "Rows", "Role in the pipeline"],
    [
        ["Train", "60%", "311,040", "Fits the Isolation Forest and the XGBoost regressor"],
        ["Validation", "15%", "77,760", "Calibrates the per-server threshold at a 0.5% false-positive budget"],
        ["Test", "25%", "129,600", "Held-out evaluation; 126,728 rows after warm-up rows are dropped"],
        ["Forecast test", "last 20%", "103,544", "Scored forecast origins after lag construction"],
        ["Risk test", "\u2014", "99,778", "Rows where a forecast and a score exist for the same minute"],
    ],
    widths=[1.1, 0.8, 1.0, 3.3],
    font_size=9.5,
    align_center=False,
)

# ---------------------------------------------------------------- 3.4 diagrams

doc.add_heading("3.4. Design Diagrams", level=2)
para(
    "Four diagrams document the design. The use-case diagram fixes what the system must let a user do, the class "
    "diagram fixes the responsibilities of the code, the entity\u2013relationship diagram fixes the data model, "
    "and the data-flow diagram fixes the order in which data is transformed. All four were drawn for this report "
    "and match the implementation exactly; the class names correspond one-to-one with the Python modules in "
    "backend/."
)

doc.add_heading("3.4.1. Use-case Diagram", level=3)
para(
    "Two actors interact with PulseGrid. The operations engineer is the primary actor and reaches all four use "
    "cases: viewing the fleet overview, inspecting a server with its forecast, filtering and sorting the alert "
    "list, and opening the model evaluation page. The evaluator is a secondary actor who only needs the model "
    "page. Opening a server directly from an alert is modelled as an extending use case, because it is an "
    "optional shortcut into \u201cinspect server metrics and forecast\u201d rather than a separate capability."
)
figure("fig_usecase.png", 6.2, "Use-case diagram for the operations engineer and the evaluator")

doc.add_heading("3.4.2. Class Diagram", level=3)
para(
    "The class diagram names six collaborators. AnomalyDetector owns the Isolation Forest, the feature list and "
    "the calibrated threshold, and produces ServerStatus objects, one per scored minute. Forecaster owns the "
    "per-server XGBoost models plus the disk trend window and raises predicted values. RiskEngine consumes a "
    "CPU value, a score, a forecast and a flag, and emits a severity together with a reason string; it is the "
    "only place where the LOW/MEDIUM/HIGH policy lives. Alert is the presentation-level projection of an "
    "interesting Status, and APIService is the thin layer that turns scored frames into JSON responses."
)
figure("fig_class.png", 6.2, "Class diagram of the scoring, forecasting and serving components")

doc.add_heading("3.4.3. Entity\u2013Relationship Diagram", level=3)
para(
    "The logical data model has five entities. A SERVER has many METRIC_READING rows, one per minute; a "
    "METRIC_READING belongs to exactly one server and carries the six measurements plus the ground-truth label. "
    "ANOMALY_EVENT groups a contiguous run of abnormal readings of one type and stores its start, end, peak "
    "score and severity. FORECAST rows are derived from readings and store an origin, a horizon and the "
    "predicted CPU, while ALERT rows record the moments at which the detector fired. The physical "
    "implementation stores readings in a single Parquet file and derives events, forecasts and alerts in "
    "memory, so the diagram is a logical rather than a schema-level model."
)
figure("fig_er.png", 6.2, "Entity\u2013relationship diagram of the logical data model")

doc.add_heading("3.4.4. Data-flow Diagram", level=3)
para(
    "The data-flow diagram numbers the five processes. Process 1.0 generates telemetry and writes it to the "
    "metrics store; 2.0 reads that store and builds feature vectors; 3.0 scores the vectors and fits the "
    "forecasters, writing the scored frame to an in-memory store; 4.0 reads the scores back, applies the risk "
    "rules and emits verdicts; and 5.0 serves JSON to the operator or evaluator. The two data stores are drawn "
    "separately to make clear that the model never writes back to the telemetry file."
)
figure("fig_dfd.png", 5.9, "Data-flow diagram of the five processing stages")

# ---------------------------------------------------------------- 3.5 interface

doc.add_heading("3.5. User Interface", level=2)

doc.add_heading("3.5.1. User Description and Mockup", level=3)
para(
    "The interface is a dark, dense dashboard designed for a person who glances at it many times a day. It has "
    "four screens, all reachable from a persistent left navigation rail: a fleet overview, a per-server detail "
    "page, an alert list and a model page. Colour carries meaning consistently across all four \u2014 green for "
    "LOW, amber for MEDIUM and red for HIGH \u2014 and every coloured element is accompanied by text so that the "
    "interface does not depend on colour alone."
)

para(
    "The fleet overview is the landing page. It opens with four summary tiles \u2014 machines monitored, active "
    "alerts, highest current risk and mean CPU \u2014 followed by a card per server showing its current CPU, "
    "memory and disk figures, a sparkline of the last hour, and a risk badge. The cards are ordered by "
    "severity, so the machine that needs attention is the first thing in the reading order. A compact trend "
    "chart against the top of the page shows fleet-wide CPU for the selected window."
)
figure("ui_overview.png", 6.2, "Fleet overview: summary tiles followed by one card per server, ordered by risk")

para(
    "The server detail page answers \u201cwhat is happening on this machine\u201d. A metric selector switches "
    "between CPU, memory, disk, network, latency and error rate; the chosen metric is drawn as a line with the "
    "detector's flags marked, so an operator can see exactly which minutes were considered abnormal. Below the "
    "chart, a forecast strip shows the predicted CPU value thirty minutes ahead with the time-to-threshold "
    "estimate, and a disk panel converts the current trend into days remaining before 90%. The right-hand "
    "column lists the most recent alerts for the server together with their reasons."
)
figure("ui_server.png", 6.2, "Server detail: metric chart with detector flags, 30-minute forecast and disk projection")

para(
    "The alert list is the working queue. Each row carries the timestamp, the server, the metric that triggered "
    "the alert, the anomaly score as a bar, the severity and the human-readable reason. The list can be filtered "
    "by severity and by server and sorted by time or by score, which is what the use-case diagram models as "
    "\u201cfilter and sort alerts\u201d. Selecting a row navigates to the corresponding server page at that moment, "
    "the extending use case described in Section 3.4.1."
)
figure("ui_alerts.png", 6.2, "Alert list with severity filter, anomaly score and a written reason for each alert")

para(
    "The model page is the evidence page. It reports the point-wise precision, recall and F1 of the detector "
    "against the static CPU rule, the event-wise recall and median delay, the per-server forecast error table, "
    "the disk-horizon table and the distribution of risk verdicts over the test period. It contains no controls "
    "and no live data, so it can be screenshotted for a report or shown to a reviewer without the replay clock "
    "running."
)
figure("ui_model.png", 6.2, "Model page: detection, forecast and risk metrics for the held-out test period")

# ---------------------------------------------------------------- 3.6 implementation

doc.add_heading("3.6. System Implementation", level=2)
para(
    "The system is implemented as two processes: a Python service that owns the data, the models and the API, "
    "and a Next.js application that owns the presentation. They communicate over HTTP only, which means either "
    "half can be restarted during development without disturbing the other. The backend is organised as eight "
    "small modules with a strict dependency direction: configuration is imported by everything, data generation "
    "and feature construction feed the models, and the API imports the models but nothing imports the API."
)
table_caption("Technology stack")
table(
    ["Layer", "Technology", "Reason for the choice"],
    [
        ["Language", "Python 3.11", "Best ecosystem for tabular machine learning"],
        ["Data handling", "pandas, NumPy, PyArrow", "Columnar Parquet storage and fast rolling windows"],
        ["Detection", "scikit-learn Isolation Forest", "Unsupervised, linear time, few hyperparameters"],
        ["Forecasting", "XGBoost, statsmodels SARIMAX", "Strong tabular regressor plus a classical baseline"],
        ["API", "FastAPI, Uvicorn", "Typed routes, automatic JSON serialisation, async serving"],
        ["Frontend", "Next.js 15, React 19, TypeScript", "Server components, typed props, fast refresh"],
        ["Charts", "Recharts", "Declarative charts that fit the dashboard layout"],
        ["Styling", "Tailwind CSS", "Consistent spacing and colour tokens without a design system"],
        ["Plots", "Matplotlib", "Static figures for the report and the evaluation page"],
    ],
    widths=[1.1, 2.1, 3.0],
    font_size=9.5,
    align_center=False,
)

table_caption("Backend modules and their responsibilities")
table(
    ["Module", "Lines", "Responsibility"],
    [
        ["config.py", "26", "Seed, dataset shape, metric list, thresholds and the eight server profiles"],
        ["data_gen.py", "143", "Workload model, event injection and Parquet output"],
        ["features.py", "34", "Window statistics, differences, long deviations and calendar encodings"],
        ["anomaly.py", "83", "Per-server Isolation Forest, threshold calibration, event grouping"],
        ["forecast.py", "137", "XGBoost CPU models, disk trend, SARIMA baseline, time-to-threshold"],
        ["risk.py", "49", "Rule fusion producing severity and reason"],
        ["api.py", "287", "Replay clock and the four read-only JSON endpoints"],
        ["evaluate.py", "171", "Reproduces every number in Chapter 4 and writes results.md"],
    ],
    widths=[1.2, 0.6, 4.4],
    font_size=9.5,
    align_center=False,
)

doc.add_heading("3.6.1. Algorithms and Pseudo Code", level=3)
para(
    "Four algorithms carry the intellectual weight of the system. They are written below in a language-neutral "
    "form so that the logic, rather than the Python syntax, is visible."
)

algorithm("Algorithm 1: Construction of a feature vector for one server-minute", [
    "input : telemetry T with one row per minute, metrics M = {cpu, memory, disk, network, latency, error}",
    "output: feature row x for the current minute t",
    "for each metric m in M do",
    "    for each window w in {5, 15, 60} do",
    "        x[m_mean_w]  <- mean(m[t-w+1 .. t])",
    "        x[m_std_w]   <- standard deviation(m[t-w+1 .. t])",
    "    x[m_diff]        <- m[t] - m[t-1]",
    "    x[m_diff60]      <- m[t] - m[t-60]",
    "    x[m_dev]         <- m[t] - mean(m[t-59 .. t])",
    "    for each long window L in {360, 1440} do",
    "        x[m_dev_L]   <- m[t] - mean(m[t-L+1 .. t])     // exposes slow drift",
    "    x[hour_sin] <- sin(2*pi*hour/24)",
    "    x[hour_cos] <- cos(2*pi*hour/24)",
    "return x",
])

para(
    "The long deviations are the feature that makes a memory leak visible. A leak adds only a few points per "
    "hour, which is invisible against the 60-minute window, but after a day it is large against the 24-hour "
    "baseline of the same server."
)

algorithm("Algorithm 2: Per-server training, calibration and scoring", [
    "input : server history H ordered by time, boundaries (b1, b2) = (0.60, 0.75)",
    "output: model f, threshold tau, scored rows S",
    "tr <- H[0 .. b1*|H|) ; va <- H[b1*|H| .. b2*|H|) ; te <- H[b2*|H| .. |H|)",
    "Xtr, Xva, Xte <- build_features(tr), build_features(va), build_features(te)",
    "f <- IsolationForest(n_estimators=200, seed=42) fitted on Xtr",
    "rva <- -f.decision_function(Xva)",
    "sva <- clip((rva - min(rva)) / (max(rva) - min(rva)), 0, 1)",
    "tau <- quantile(sva[va.is_anomaly == 0], 0.995)      // 0.5% false-positive budget",
    "for each split X in {Xtr, Xva, Xte} do",
    "    s <- clip((-f.decision_function(X) - min(rva)) / (max(rva) - min(rva)), 0, 1)",
    "    flag each row where s >= tau",
    "group consecutive flagged rows of one incident into an event",
    "return f, tau, S",
])

para(
    "Calibration on normal validation minutes only is the step that makes the detector usable. Without it, the "
    "Isolation Forest's arbitrary score scale would have to be thresholded by hand, and the operating point "
    "would differ between a quiet cache and a busy gateway."
)

algorithm("Algorithm 3: Thirty-minute-ahead CPU forecasting with XGBoost", [
    "input : per-server series with metrics M and calendar fields",
    "output: a model per server and a prediction for every test origin",
    "for each server s do",
    "    for each minute t do",
    "        v <- [cpu[t], cpu[t-1], cpu[t-5], cpu[t-15],",
    "              mean/std of cpu over 15 and 60 minutes,",
    "              hour[t], day_of_week[t], memory[t], disk[t], network[t], latency[t], error[t]]",
    "        target <- cpu[t+30]",
    "    split chronologically into 60% train, 20% validation, 20% test",
    "    model <- XGBRegressor(n_estimators=500, depth=6, lr=0.05, subsample=0.8)",
    "    fit model on train, early stopping on validation RMSE",
    "    predict on test and compare with the naive last-value forecast",
])

para(
    "Early stopping on a chronological validation slice matters here: the daily shape means a random split would "
    "place nearly identical minutes in training and test, and the reported error would be optimistic."
)

algorithm("Algorithm 4: Fusion of anomaly score, forecast and current load into a risk verdict", [
    "input : cpu now, anomaly score s, forecast f, detector flag b",
    "output: severity in {LOW, MEDIUM, HIGH} and a reason string",
    "reason <- empty",
    "if s >= 0.90 then append(\"high anomaly score\") else if b then append(\"flagged abnormal\")",
    "if f >= 90 then append(\"CPU forecast to cross 90% in ~n minutes\")",
    "else if f >= 80 then append(\"CPU trending to f%\") ",
    "if cpu >= 90 then append(\"CPU already at 90%\") ",
    "if reason is empty then return (LOW, \"metrics within learned normal range\")",
    "if s >= 0.90 or f >= 90 or cpu >= 90 then return (HIGH, reason)",
    "return (MEDIUM, reason)",
])

doc.add_heading("3.6.2. Source Code with Documentation", level=3)
para(
    "The repository is organised into backend/ for the Python service, frontend/ for the Next.js dashboard and "
    "report_assets/ for the figures in this report. The excerpts below are taken verbatim from the implementation "
    "and are the parts a reader needs in order to follow the algorithms above; the complete source, the "
    "generated dataset and the evaluation output are in the project repository at "
)
p = doc.paragraphs[-1]
p.add_run(GITHUB).bold = True
p.add_run(". The dataset can be regenerated deterministically from the fixed seed with ")
p.add_run("python backend/data_gen.py").font.name = "Consolas"
p.add_run(", and every number in Chapter 4 with ")
p.add_run("python backend/evaluate.py").font.name = "Consolas"
p.add_run(".")

para("Feature construction (backend/features.py).", bold=True, space_after=2)
code([
    "WINDOWS = (5, 15, 60)",
    "LONG = (360, 1440)  # 6 h and 24 h baselines expose slow drifts the 60 min window hides",
    "",
    "def add_features(df):",
    "    parts = []",
    "    for _, g in df.groupby(\"server\", sort=True):",
    "        g = g.sort_values(\"timestamp\")",
    "        f = {}",
    "        for m in METRICS:",
    "            s = g[m]",
    "            for w in WINDOWS:",
    "                f[f\"{m}_mean{w}\u201d] = s.rolling(w).mean()",
    "                f[f\"{m}_std{w}\u201d] = s.rolling(w).std()",
    "            f[f\"{m}_diff\"] = s.diff()",
    "            f[f\"{m}_diff60\"] = s.diff(60)",
    "            f[f\"{m}_dev\"] = s - s.rolling(60).mean()",
    "            for w in LONG:",
    "                f[f\"{m}_dev{w}\"] = s - s.rolling(w).mean()",
    "",
    "def feature_cols(df):",
    "    return [c for c in df.columns if c not in META]",
])

para("Detector training and calibrated scoring (backend/anomaly.py).", bold=True, space_after=2)
code([
    "for server, g in d.groupby(\"server\", sort=True):",
    "    g = g.sort_values(\"timestamp\")",
    "    n = len(g)",
    "    cut1, cut2 = int(n * BOUNDS[0]), int(n * BOUNDS[1])",
    "    tr, va = g.iloc[:cut1], g.iloc[cut1:cut2]",
    "    model = make_pipeline(StandardScaler(),",
    "        IsolationForest(n_estimators=200, random_state=SEED, n_jobs=-1))",
    "    model.fit(tr[cols])",
    "    raw_va = -model.decision_function(va[cols])",
    "    lo, hi = raw_va.min(), raw_va.max()",
    "    score_va = np.clip((raw_va - lo) / (hi - lo), 0, 1)",
    "    # 0.5% FP budget, calibrated on normal validation points",
    "    thr = float(np.quantile(score_va[va.is_anomaly == 0], 0.995))",
])

para("Risk fusion (backend/risk.py).", bold=True, space_after=2)
code([
    "def assess(cpu, score, forecast, flagged):",
    "    reasons = []",
    "    if score >= 0.9:",
    "        reasons.append(f\"high anomaly score {score:.2f}\")",
    "    elif flagged:",
    "        reasons.append(f\"abnormal behavior flagged, score {score:.2f}\")",
    "    if forecast >= CPU_THRESHOLD:",
    "        reasons.append(f\"CPU forecast {forecast:.0f}% in ~{time_to_cross(...)} min\")",
    "    elif forecast >= 80:",
    "        reasons.append(f\"CPU trending to {forecast:.0f}%\")",
    "    if not reasons:",
    "        return \"LOW\", \"metrics within learned normal range\"",
    "    high = score >= 0.9 or forecast >= CPU_THRESHOLD or cpu >= CPU_THRESHOLD",
    "    return (\"HIGH\" if high else \"MEDIUM\"), \"; \".join(reasons)",
])

para("Forecast horizon and time-to-threshold (backend/forecast.py).", bold=True, space_after=2)
code([
    "H = 30  # forecast horizon in minutes",
    "FEATS = [\"cpu\", \"cpu_lag1\", \"cpu_lag5\", \"cpu_lag15\", \"cpu_mean15\", \"cpu_std15\",",
    "         \"cpu_mean60\", \"cpu_std60\", \"hour\", \"dow\", \"memory\", \"disk\",",
    "         \"network\", \"latency\", \"error_rate\"]",
    "",
    "def time_to_cross(now, pred, threshold, horizon=H):",
    "    if pred <= threshold:",
    "        return None",
    "    if now >= threshold:",
    "        return 0",
    "    return round(horizon * (threshold - now) / (pred - now))",
])

para(
    "Two implementation details are worth documenting because they are easy to get wrong. The replay clock in "
    "api.py does not sleep between requests; it computes the visible timestamp from the process start time and "
    "the replay speed, so a page reload always shows a consistent moment and the server never blocks. And the "
    "evaluation script writes its output to results.md, which the model page imports at build time, so the "
    "numbers shown in the dashboard and the numbers printed in this report cannot drift apart."
)

# ---------------------------------------------------------------- 4 conclusion

doc.add_heading("4. CONCLUSION", level=1)

doc.add_heading("4.1. Goals and Vision", level=2)
para(
    "The vision behind PulseGrid was a monitoring page that behaves like an experienced colleague: it knows what "
    "each machine normally looks like, it notices the change before the outage, and it says why it is worried in "
    "one sentence. The concrete goal was narrower and measurable \u2014 learn normal behaviour per server without "
    "labels, keep false alarms rare, report incidents rather than minutes, forecast CPU and disk before they "
    "saturate, and reduce the fleet to a short explained risk list."
)
para(
    "Judged against the seven objectives fixed in Table 1, six are met and one is only partly met. Detection "
    "without hand-written per-metric thresholds is achieved: a single feature pipeline and a single model class "
    "serve all six metrics on all eight machines. The false-alarm budget is met by construction, because the "
    "threshold is placed at the 99.5th percentile of normal validation scores, and the measured precision of "
    "0.695 confirms that the budget holds on unseen data. Episodes are reported with a median delay of 3.5 "
    "minutes and 24 of 26 incidents detected. The CPU forecaster beats persistence by 29% in mean absolute "
    "error, and the disk trend beats the naive value at all three horizons. The risk engine does reduce the "
    "fleet to a small set of explained items. The objective that is only partly met is the detection of slow "
    "memory leaks, which the 0.5% operating point misses; this is analysed honestly below rather than hidden."
)

doc.add_heading("4.2. Delivered Solution", level=2)
para(
    "The delivered product is a working two-process application: a FastAPI service that replays 45 days of "
    "scored telemetry and a Next.js dashboard that visualises it. All of the numbers in this section are "
    "reproduced by running backend/evaluate.py, and the same numbers are displayed on the model page of the "
    "dashboard."
)
para(
    "Table 8 compares the detector with the static rule it replaces, evaluated on the held-out last 25% of "
    "every server's timeline. The static rule fires when CPU exceeds 90%, which is the most common alert in "
    "small deployments. It achieves a precision of 0.074, meaning thirteen of every fourteen pages it generates "
    "are spurious, and it catches two of the twenty-six test incidents. The Isolation Forest raises an order of "
    "magnitude fewer false alarms and detects twenty-four of the twenty-six incidents."
)
table_caption("Detection performance on the held-out test period (126,728 points)")
table(
    ["Detector", "Precision", "Recall", "F1", "Incidents detected", "Median delay"],
    [
        ["Isolation Forest (per server)", "0.695", "0.459", "0.553", "24 / 26", "3.5 min"],
        ["Static rule: CPU > 90%", "0.074", "0.014", "0.023", "2 / 26", "not meaningful"],
    ],
    widths=[2.0, 0.85, 0.7, 0.6, 1.15, 0.95],
    font_size=9.5,
)
para(
    "The point-wise recall of 0.459 looks modest until it is read next to the event-wise result. A memory leak "
    "that lasts four hours is one incident and 240 abnormal minutes; a detector that fires for the last ninety "
    "minutes of it has a point recall of 0.37 but caught the incident, and the operator had ninety minutes of "
    "warning. This is precisely the argument made by the Numenta Anomaly Benchmark [5], and it is why both "
    "measures are reported. Figure 11 shows the behaviour on a test window in which a disk-fill incident is "
    "detected early and tracked to the end."
)
figure("../backend/plots/server-02_test.png", 6.1,
       "Detection and forecast behaviour on the server-02 test window; shaded regions are labelled incidents")

para(
    "Table 9 breaks the same result down by anomaly type. Disk fill and latency incidents are detected almost "
    "completely, because both produce a sustained departure from a stable baseline. CPU spikes are detected in "
    "all nine incidents but with poor point precision, since the detector also fires on the surrounding ramp. "
    "Network bursts are found in five of six incidents. The multivariate incidents are caught as events even "
    "though no single metric is extreme, which suggests the combination of six metrics in one feature space is "
    "doing useful work. Memory leaks are the clear failure: one of three incidents detected, and a point recall "
    "of 0.01."
)
table_caption("Detection by anomaly type on the test period (one-vs-rest precision; flags are not typed)")
table(
    ["Type", "Points", "Precision", "Recall", "F1", "Incidents", "Median delay"],
    [
        ["cpu_spike", "247", "0.10", "0.62", "0.18", "9 / 9", "0.0 min"],
        ["disk_fill", "727", "0.44", "0.91", "0.60", "1 / 1", "33.0 min"],
        ["latency_error", "50", "0.03", "0.96", "0.06", "3 / 3", "1.0 min"],
        ["memory_leak", "924", "0.00", "0.01", "0.00", "2 / 3", "82.5 min"],
        ["multivariate", "192", "0.08", "0.60", "0.14", "4 / 4", "9.5 min"],
        ["network_burst", "126", "0.04", "0.44", "0.07", "5 / 6", "3.0 min"],
    ],
    widths=[1.3, 0.75, 0.95, 0.8, 0.6, 0.9, 1.1],
    font_size=9.5,
)
para(
    "The memory-leak failure has a specific cause and is worth stating plainly. The injected leak raises memory "
    "by roughly one percentage point per hour, while normal daytime memory on a busy server swings by fifteen "
    "points. At the 0.5% false-positive operating point the leak's level is still inside the normal band, so no "
    "threshold that respects the budget can flag it. The 24-hour deviation feature reduces the problem but does "
    "not remove it. A dedicated slope test \u2014 regressing the last six hours of memory and alerting on a "
    "consistently positive slope \u2014 is the obvious remedy and is listed as remaining work rather than claimed "
    "as done."
)

para(
    "Table 10 reports the CPU forecaster per server. Every one of the eight machines improves on persistence, "
    "with mean absolute error falling from 3.58 to 2.53 percentage points overall, a reduction of 29%. The "
    "improvement is largest on the busiest machines, which is where capacity decisions matter: server-02 and "
    "server-08 improve by more than a full point of absolute error."
)
table_caption("CPU forecast 30 minutes ahead, per server (percentage points)")
table(
    ["Server", "Naive MAE", "XGBoost MAE", "Naive RMSE", "XGBoost RMSE"],
    [
        ["server-01", "3.11", "2.15", "3.89", "2.69"],
        ["server-02", "4.00", "2.72", "5.22", "3.61"],
        ["server-03", "2.86", "1.92", "4.07", "2.82"],
        ["server-04", "4.55", "3.19", "5.98", "4.28"],
        ["server-05", "3.49", "2.30", "4.36", "2.88"],
        ["server-06", "2.62", "1.86", "4.48", "3.35"],
        ["server-07", "3.65", "3.13", "4.55", "4.13"],
        ["server-08", "4.35", "2.98", "5.70", "4.13"],
        ["All servers", "3.58", "2.53", "4.84", "3.54"],
    ],
    widths=[1.5, 1.2, 1.3, 1.2, 1.3],
    font_size=9.5,
)

para(
    "A seasonal ARIMA model with a 48-step daily seasonality was fitted to server-01 on a thirty-minute grid "
    "for comparison. It scored a mean absolute error of 2.77 against 1.20 for the naive forecast on the same "
    "origins, so it loses clearly and is reported rather than omitted, following the advice of Hyndman and "
    "Athanasopoulos [11] that a naive benchmark must always be shown. The likely reason is that the series has "
    "a strong weekly component that a 48-step daily seasonality cannot represent, while the trees learn the "
    "hour and day-of-week fields directly."
)

table_caption("Disk occupancy forecast error by horizon (percentage points)")
table(
    ["Horizon", "Trend MAE", "Naive MAE", "Trend RMSE", "Naive RMSE"],
    [
        ["1 day", "0.58", "0.69", "2.03", "2.02"],
        ["3 days", "1.64", "2.05", "4.25", "4.03"],
        ["7 days", "4.15", "4.98", "8.95", "7.79"],
    ],
    widths=[1.3, 1.2, 1.2, 1.3, 1.2],
    font_size=9.5,
)
para(
    "The disk trend beats the naive value at all three horizons in mean absolute error, which is the measure "
    "that matters for a capacity decision, while its root mean squared error is slightly worse at one and three "
    "days because a single sharp fill contributes a large squared error. In practice the dashboard shows the "
    "days-to-90% estimate derived from the same seven-day fit, so an operator sees \u201ceighteen days left\u201d "
    "rather than a percentage."
)

para(
    "Finally, Table 12 shows how the three signals combine. Over 99,778 scored test minutes, 96.36% are LOW, "
    "3.16% are MEDIUM and 0.48% are HIGH. That distribution is the practical justification for the risk layer: "
    "an operator who only looks at the HIGH band reviews about four hundred and ninety-five minutes of "
    "evidence during a test window that spans more than eleven days, instead of scanning a hundred thousand "
    "rows."
)
table_caption("Risk verdict distribution over the test period (99,778 scored minutes)")
table(
    ["Severity", "Minutes", "Share", "Meaning"],
    [
        ["LOW", "99,778", "96.36%", "Metrics inside the learned normal range"],
        ["MEDIUM", "3,271", "3.16%", "Flagged by the detector, or CPU trending towards 80%"],
        ["HIGH", "495", "0.48%", "Score at least 0.90, or CPU at or forecast to reach 90%"],
    ],
    widths=[1.1, 1.1, 0.9, 3.2],
    font_size=9.5,
    align_center=False,
)
para(
    "Two honest caveats belong with these results. No CPU forecast crossed 90% during the test window, so the "
    "forecast-crossing branch of the HIGH rule was exercised only by current load and by anomaly score; the "
    "rule is tested for correctness in unit terms but not by a real crossing in this dataset. And because the "
    "data is synthetic, the absolute numbers describe this generator rather than any production fleet. What "
    "does transfer is the relative result, that unsupervised per-server scoring with calibrated thresholds "
    "beats a static rule by a wide margin on both false alarms and detected incidents."
)

doc.add_heading("4.3. Remaining Work", level=2)
para(
    "Four pieces of work would turn this prototype into something an operations team could run."
)
bullet("The memory-leak failure needs a dedicated slope detector: a regression over the last six hours of "
       "memory, alerting when the slope is positive and consistent across sub-windows, and reporting the "
       "projected day on which memory would reach 90%. This is a small, well-understood addition and is the "
       "single highest-value improvement.",
       "Leak detection by trend, not level. ")
bullet("The current score is a scalar with no notion of which metric caused it. Per-metric contributions, "
       "computed by scoring each metric family separately and comparing, would let the dashboard say \"disk is "
       "the problem\" rather than \"this minute is unusual\".",
       "Attribution of a score to a metric. ")
bullet("The replay clock is a demonstration device. A production version would consume Prometheus or an "
       "OpenTelemetry collector, keep a rolling training window, and retrain per server nightly so that a "
       "machine whose workload changes does not slowly become permanently anomalous.",
       "A live collector and periodic retraining. ")
bullet("Thresholds are calibrated once, offline. A feedback loop in which an operator marks an alert as "
       "\"expected\" would allow the false-positive budget to be spent where it is least costly, which is the "
       "approach taken by the production systems reviewed in Chapter 2.",
       "Operator feedback on alerts. ")
para(
    "None of these requires a redesign. The pipeline was built with a clear seam between data access, scoring "
    "and presentation, and each of the four items fits behind one of those seams."
)

# ---------------------------------------------------------------- references

doc.add_heading("5. REFERENCES", level=1)

REFERENCES = [
    "F. T. Liu, K. M. Ting and Z.-H. Zhou, \u201cIsolation Forest,\u201d in Proceedings of the 8th IEEE International "
    "Conference on Data Mining (ICDM), Pisa, Italy, 2008, pp. 413\u2013422.",
    "F. T. Liu, K. M. Ting and Z.-H. Zhou, \u201cIsolation-Based Anomaly Detection,\u201d ACM Transactions on Knowledge "
    "Discovery from Data, vol. 6, no. 1, Article 3, pp. 1\u201339, 2012.",
    "V. Chandola, A. Banerjee and V. Kumar, \u201cAnomaly Detection: A Survey,\u201d ACM Computing Surveys, vol. 41, "
    "no. 3, Article 15, pp. 1\u201358, 2009.",
    "T. Chen and C. Guestrin, \u201cXGBoost: A Scalable Tree Boosting System,\u201d in Proceedings of the 22nd ACM "
    "SIGKDD International Conference on Knowledge Discovery and Data Mining, San Francisco, CA, USA, 2016, "
    "pp. 785\u2013794.",
    "A. Lavin and S. Ahmad, \u201cEvaluating Real-time Anomaly Detection Algorithms \u2013 the Numenta Anomaly "
    "Benchmark,\u201d in Proceedings of the IEEE 14th International Conference on Machine Learning and Applications "
    "(ICMLA), Miami, FL, USA, 2015, pp. 38\u201344.",
    "S. Ahmad, A. Lavin, S. Purdy and Z. Agha, \u201cUnsupervised Real-time Anomaly Detection for Streaming Data,\u201d "
    "Neurocomputing, vol. 262, pp. 134\u2013147, 2017.",
    "K. Hundman, V. Constantinou, C. Laporte, I. Colwell and T. Soderstrom, \u201cDetecting Spacecraft Anomalies "
    "Using LSTMs and Nonparametric Dynamic Thresholding,\u201d in Proceedings of the 24th ACM SIGKDD International "
    "Conference on Knowledge Discovery and Data Mining, London, UK, 2018, pp. 387\u2013395.",
    "Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun and D. Pei, \u201cRobust Anomaly Detection for Multivariate Time Series "
    "through Stochastic Recurrent Neural Network,\u201d in Proceedings of the 25th ACM SIGKDD International "
    "Conference on Knowledge Discovery and Data Mining, Anchorage, AK, USA, 2019, pp. 2828\u20132837.",
    "H. Ren, Q. Xu, Y. Wang, Y. Yi, C. Zhu, Y. Ma, J. Wang, X. Yang and T. Guo, \u201cTime-Series Anomaly Detection "
    "Service at Microsoft,\u201d in Proceedings of the 25th ACM SIGKDD International Conference on Knowledge "
    "Discovery and Data Mining, Anchorage, AK, USA, 2019, pp. 3009\u20133017.",
    "M. Du, F. Li, G. Zheng and V. Srikumar, \u201cDeepLog: Anomaly Detection and Diagnosis from System Logs through "
    "Deep Learning,\u201d in Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security, "
    "Dallas, TX, USA, 2017, pp. 1285\u20131298.",
    "R. J. Hyndman and G. Athanasopoulos, Forecasting: Principles and Practice, 3rd ed. Melbourne, Australia: "
    "OTexts, 2021.",
]
for i, ref in enumerate(REFERENCES, start=1):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.first_line_indent = Inches(-0.4)
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(8)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run(f"[{i}]\t")
    p.add_run(ref)

update_fields_on_open()
doc.core_properties.title = TITLE.title()
doc.core_properties.author = ", ".join(n for n, _ in STUDENTS)
doc.core_properties.subject = "CSET312 Mini-Project Report"
doc.save(OUT)
print(f"wrote {OUT.name} ({OUT.stat().st_size / 1024:.0f} KB)")
