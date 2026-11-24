"""Fill [[LIST_OF_TABLES]] / [[LIST_OF_FIGURES]] with static entries and verified page numbers."""

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import Inches, Pt

sys.path.insert(0, str(Path("_tmp_pdf").resolve()))
import pymupdf  # noqa: E402

ROOT = Path(__file__).parent.resolve()
DOCX = ROOT / "_report_final.docx"
PDF = ROOT / "_report_preview.pdf"

doc = Document(DOCX)
pdf = pymupdf.open(PDF)

LABEL_RE = re.compile(r"^(?:[ivxlcdm]+|\d+)$")
labels = []
for page in pdf:
    found = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            if line["bbox"][1] < page.rect.height * 0.925:
                continue          # the footer sits below the text area
            text = "".join(span["text"].strip() for span in line["spans"]).strip()
            if LABEL_RE.match(text):
                found.append((line["bbox"][1], text))
    labels.append(max(found)[1] if found else "?")
assert all(lab != "?" for lab in labels[1:]), labels

body_start = labels.index("1")
captions = []
for p in doc.paragraphs:
    if p.style.name != "Caption":
        continue
    m = re.match(r"(Table|Figure) (\d+): (.+)", p.text.strip())
    if m:
        captions.append((m.group(1), int(m.group(2)), m.group(3).strip()))
print("pdf pages:", len(pdf), "| captions:", len(captions))

entry_style = doc.styles.add_style("List Entry", 1)
entry_style.base_style = doc.styles["Normal"]
entry_style.font.name = "Times New Roman"
entry_style.font.size = Pt(10.5)
entry_style.paragraph_format.line_spacing = 1.0
entry_style.paragraph_format.space_before = Pt(0)
entry_style.paragraph_format.space_after = Pt(4)


def page_of(kind, num, title):
    needle = f"{kind} {num}: {title[:25]}"
    hit = next((i for i in range(body_start, len(pdf)) if pdf[i].search_for(needle)), None)
    if hit is None:
        raise SystemExit(f"no page found for {needle}")
    return labels[hit]


def fill(marker, kind):
    anchor = marker._p
    for _, num, title in [c for c in captions if c[0] == kind]:
        p = doc.add_paragraph(style=entry_style)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.25), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        p.add_run(f"{kind} {num}: {title}\t{page_of(kind, num, title)}")
        anchor.addprevious(p._p)
    anchor.getparent().remove(anchor)
    print("filled", kind)


for p in list(doc.paragraphs):
    if "[[LIST_OF_TABLES]]" in p.text:
        fill(p, "Table")
    elif "[[LIST_OF_FIGURES]]" in p.text:
        fill(p, "Figure")

doc.save(DOCX)
print("saved", DOCX.name)
