"""Export helpers: PDF and Excel reporting utilities.

Simple, robust helpers used by the GUI to produce PDF and Excel reports.
They save any provided matplotlib Figures to temporary PNGs, embed those
images into the outputs, and clean up temporary files afterwards.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image as RLImage
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
import os
import subprocess
import tempfile
from typing import List, Optional
from datetime import datetime


def _save_figs_to_temp_png(figs: Optional[List]):
    """Save matplotlib Figure objects to temp PNG files and return paths.

    figs: list of matplotlib.figure.Figure or objects exposing ``savefig(path)``.
    Returns list of filesystem paths. Caller should remove files after use.
    """
    if not figs:
        return []
    paths: List[str] = []
    for i, fig in enumerate(figs):
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_dashboard_{i}.png")
            tmp.close()
            # fig may be a matplotlib Figure or similar object with savefig
            try:
                fig.savefig(tmp.name, bbox_inches='tight')
            except Exception:
                # if it's already a path-like object, try copying
                try:
                    if isinstance(fig, str) and os.path.exists(fig):
                        os.replace(fig, tmp.name)
                    else:
                        raise
                except Exception:
                    os.unlink(tmp.name)
                    continue
            paths.append(tmp.name)
        except Exception:
            continue
    return paths


def _cleanup_temp_files(paths: List[str]):
    for p in paths:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass


def export_report_pdf(results: Optional[dict], path: str, figs: Optional[List] = None):
    """Create a simple PDF report including `results` summary and dashboard images.

    - `results` is expected to be a mapping-like object with printable keys/values.
    - `figs` is an optional list of matplotlib Figures (or objects with savefig).
    """
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("TaxFlow - Tax Report", styles['Title']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Results table
    data = [["Key", "Value"]]
    if results:
        for k, v in results.items():
            data.append([str(k), str(v)])
    tbl = Table(data, colWidths=[150, 350])
    tbl.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, (0, 0, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    # Embed dashboard images
    img_paths = _save_figs_to_temp_png(figs)
    try:
        for p in img_paths:
            try:
                img = RLImage(p, width=450, height=300)
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception:
                continue
        doc.build(story)
    finally:
        _cleanup_temp_files(img_paths)


def export_report_excel(results: Optional[dict], path: str, figs: Optional[List] = None):
    """Create a simple Excel workbook with a summary sheet and optional image sheets.

    The function writes `results` into the first sheet and places each image
    into its own sheet named `Dashboard_1`, `Dashboard_2`, ...
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Generated", datetime.now().strftime('%Y-%m-%d %H:%M')])
    ws.append([])
    if results:
        for k, v in results.items():
            # If the value is a mapping (e.g., 'steps' or 'slab'), write a header
            # row and then write each inner key/value on its own row. This avoids
            # trying to write complex objects (like dicts) directly to cells.
            if isinstance(v, dict):
                ws.append([str(k), ''])
                for ik, iv in v.items():
                    try:
                        ws.append([f"  {ik}", iv])
                    except Exception:
                        ws.append([f"  {ik}", str(iv)])
            else:
                try:
                    ws.append([str(k), v])
                except Exception:
                    ws.append([str(k), str(v)])

    img_paths = _save_figs_to_temp_png(figs)
    try:
        for i, p in enumerate(img_paths):
            try:
                ws_img = wb.create_sheet(title=f"Dashboard_{i+1}")
                img = XLImage(p)
                ws_img.add_image(img, 'A1')
            except Exception:
                continue
        wb.save(path)
    finally:
        _cleanup_temp_files(img_paths)


def print_pdf(path: str):
    """Send a PDF file to the default printer on Windows using `os.startfile`.

    Falls back to opening the PDF if printing is not supported.
    Returns True on a successful attempt, False otherwise.
    """
    if os.name == 'nt':
        try:
            os.startfile(path, 'print')
            return True
        except Exception:
            try:
                os.startfile(path)
                return True
            except Exception:
                return False
    else:
        try:
            subprocess.run(['lp', path], check=True)
            return True
        except Exception:
            return False
