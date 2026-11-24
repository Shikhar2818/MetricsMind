from pathlib import Path
import win32com.client as w
ROOT = Path(__file__).parent.resolve()
app = w.DispatchEx("Word.Application"); app.Visible = True; app.DisplayAlerts = 0
d = app.Documents.Open(str(ROOT / "_report_final.docx"), ConfirmConversions=False, ReadOnly=False, AddToRecentFiles=False)
d.Repaginate()
print("pages:", d.ComputeStatistics(2), flush=True)
d.SaveAs(str(ROOT / "_report_final.docx"))
d.ExportAsFixedFormat(str(ROOT / "_report_preview.pdf"), 17)
d.Close(0); app.Quit()
print("exported", flush=True)
