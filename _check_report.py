import sys
from pathlib import Path

import win32com.client as win32


def log(*a):
    print(*a, flush=True)


ROOT = Path(__file__).parent.resolve()
DOCX = ROOT / "_report_final.docx"
PDF = ROOT / "_report_preview.pdf"

log("start")
word = win32.DispatchEx("Word.Application")
word.Visible = True
word.DisplayAlerts = 0
log("word up")
doc = word.Documents.Open(str(DOCX), ConfirmConversions=False, ReadOnly=False, AddToRecentFiles=False)
log("opened", doc.Name)

n = 0
for field in doc.Fields:
    if "SEQ" in field.Code.Text:
        field.Update()
        n += 1
log("seq updated", n)

doc.Fields.Update()
log("all fields updated")

for toc in doc.TablesOfContents:
    toc.Update()
log("tocs updated")

for name in ("TOC 1", "TOC 2", "TOC 3", "Table of Figures", "Caption"):
    try:
        fmt = doc.Styles(name).ParagraphFormat
        fmt.SpaceBefore = 0
        fmt.SpaceAfter = 0
        fmt.LineSpacingRule = 0
    except Exception as exc:
        log("style skip", name, exc)
log("styles tightened")

doc.Repaginate()
log("pages:", doc.ComputeStatistics(2), "words:", doc.ComputeStatistics(0))

captions = [p.Range.Text.strip() for p in doc.Paragraphs
            if p.Range.Text.strip().startswith(("Table ", "Figure "))][:4]
log("first captions:", captions)

doc.Save()
log("saved")
doc.ExportAsFixedFormat(str(PDF), 17)
log("pdf exported")
doc.Close(SaveChanges=0)
word.Quit()
log("closed; pdf", PDF.exists(), PDF.stat().st_size // 1024, "KB")
