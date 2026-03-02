"""
PDF summary generation using reportlab.

Produces a single-page A4 portrait PDF with a professional
production order layout: header banner, metrics bar, parameter
tables, lane breakdown, and footer.
"""
from datetime import date, datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

# ── Colour palette ────────────────────────────────────────────
_NAVY = colors.HexColor("#1B2A4A")
_BLUE = colors.HexColor("#4472C4")
_LIGHT_BLUE = colors.HexColor("#D9E2F3")
_LIGHT_GREY = colors.HexColor("#F2F2F2")
_MED_GREY = colors.HexColor("#E0E0E0")
_YELLOW = colors.HexColor("#FFF9DB")
_WHITE = colors.white
_PAGE_W, _PAGE_H = A4
_MARGIN = 20 * mm
_CONTENT_W = _PAGE_W - 2 * _MARGIN


# ── Reusable styles ──────────────────────────────────────────
def _style(name, **kw):
    defaults = dict(fontName="Helvetica", fontSize=9, leading=11, textColor=colors.black)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)


_S_HEADER_TITLE = _style("hdr_title", fontName="Helvetica-Bold", fontSize=18,
                          textColor=_WHITE, leading=22)
_S_HEADER_SUB = _style("hdr_sub", fontSize=9, textColor=colors.HexColor("#B0C4DE"),
                        leading=11)
_S_HEADER_RIGHT = _style("hdr_right", fontSize=9, textColor=_WHITE,
                          alignment=TA_RIGHT, leading=11)
_S_METRIC_NUM = _style("metric_num", fontName="Helvetica-Bold", fontSize=16,
                        alignment=TA_CENTER, leading=20)
_S_METRIC_LBL = _style("metric_lbl", fontSize=7, alignment=TA_CENTER,
                        textColor=colors.HexColor("#666666"), leading=9)
_S_FOOTER_NOTE = _style("footer_note", fontSize=8, textColor=colors.HexColor("#333333"))
_S_FOOTER_TS = _style("footer_ts", fontSize=7, textColor=colors.HexColor("#999999"))
_S_TABLE_HDR = _style("tbl_hdr", fontName="Helvetica-Bold", fontSize=8,
                       textColor=_WHITE, leading=10)
_S_TABLE_CELL = _style("tbl_cell", fontSize=8, leading=10)
_S_TABLE_CELL_BOLD = _style("tbl_cell_b", fontName="Helvetica-Bold", fontSize=8, leading=10)
_S_TABLE_CELL_ITALIC = _style("tbl_cell_i", fontName="Helvetica-Oblique", fontSize=8,
                               leading=10, textColor=colors.HexColor("#555555"))


# ── Zone 1: Header Banner ────────────────────────────────────
def _build_header_banner(ordernummer, vdp_aantal, date_str):
    left_top = Paragraph("ORDER SAMENVATTING", _S_HEADER_SUB)
    left_bot = Paragraph(str(ordernummer), _S_HEADER_TITLE)
    right_top = Paragraph(f"Datum: {date_str}", _S_HEADER_RIGHT)
    right_bot = Paragraph(f"VDP aantal: {vdp_aantal}", _S_HEADER_RIGHT)

    # Account for banner padding (5mm each side) so inner columns fit
    inner_w = _CONTENT_W - 10 * mm
    inner = Table(
        [[left_top, right_top],
         [left_bot, right_bot]],
        colWidths=[inner_w * 0.6, inner_w * 0.4],
    )
    inner.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    banner = Table([[inner]], colWidths=[_CONTENT_W])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 4 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("ROUNDEDCORNERS", [2 * mm, 2 * mm, 2 * mm, 2 * mm]),
    ]))
    return banner


# ── Zone 2: Key Metrics Bar ──────────────────────────────────
def _build_metrics_bar(totaal_etiketten, mes, meters_per_baan,
                       formaat_hoogte, formaat_breedte):
    total_meters = sum(meters_per_baan) if meters_per_baan else 0.0
    items = [
        (str(totaal_etiketten), "Totaal etiketten"),
        (str(mes), "Banen"),
        (f"{total_meters:.1f}", "Totaal meters"),
        (f"{formaat_hoogte} x {formaat_breedte}", "Formaat (mm)"),
    ]

    box_w = _CONTENT_W / len(items)
    cells_top = []
    cells_bot = []
    for val, label in items:
        cells_top.append(Paragraph(val, _S_METRIC_NUM))
        cells_bot.append(Paragraph(label, _S_METRIC_LBL))

    bar = Table([cells_top, cells_bot], colWidths=[box_w] * len(items))
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _LIGHT_GREY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 3 * mm),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 3 * mm),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
        ("LINEAFTER", (0, 0), (-2, -1), 0.5, _MED_GREY),
        ("ROUNDEDCORNERS", [2 * mm, 2 * mm, 2 * mm, 2 * mm]),
    ]))
    return bar


# ── Zone 3: Order Parameters (two mini-tables side by side) ──
def _mini_param_table(rows, col_widths):
    """Build a small two-column parameter table with blue header."""
    data = [[Paragraph("Parameter", _S_TABLE_HDR),
             Paragraph("Waarde", _S_TABLE_HDR)]]
    for label, value in rows:
        data.append([Paragraph(label, _S_TABLE_CELL),
                     Paragraph(str(value), _S_TABLE_CELL)])

    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), _BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), _WHITE),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
    ]
    # alternating rows
    for i in range(1, len(data)):
        bg = _WHITE if i % 2 == 1 else _LIGHT_BLUE
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(style_cmds))
    return t


def _build_params_table(wikkel, kern, extra_etiketten, afwijking_waarde,
                        formaat_hoogte, formaat_breedte, vdp_aantal,
                        totaal_etiketten):
    half = (_CONTENT_W - 4 * mm) / 2
    col_w = [half * 0.5, half * 0.5]

    left_rows = [
        ("Kern", f"{kern} mm"),
        ("Wikkel", str(wikkel)),
        ("Extra etiketten", str(extra_etiketten)),
        ("Afwijking", str(afwijking_waarde)),
    ]
    right_rows = [
        ("Formaat hoogte", f"{formaat_hoogte} mm"),
        ("Formaat breedte", f"{formaat_breedte} mm"),
        ("VDP aantal", str(vdp_aantal)),
        ("Totaal etiketten", str(totaal_etiketten)),
    ]

    left_t = _mini_param_table(left_rows, col_w)
    right_t = _mini_param_table(right_rows, col_w)

    wrapper = Table([[left_t, right_t]], colWidths=[half, half],
                    spaceBefore=0, spaceAfter=0)
    wrapper.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 4 * mm),
    ]))
    return wrapper


# ── Zone 4: Banen Overzicht ──────────────────────────────────
def _build_lanes_table(banen_summary, meters_per_baan, totaal_etiketten, mes,
                       vdp_aantal=1):
    col_widths = [12 * mm, 48 * mm, 62 * mm, 16 * mm, 16 * mm, 16 * mm]
    ncols = len(col_widths)

    _S_VDP_HDR = _style("vdp_hdr", fontName="Helvetica-Bold", fontSize=9,
                         textColor=_WHITE, leading=12)

    def _col_header_row():
        return [
            Paragraph("Baan", _S_TABLE_HDR),
            Paragraph("Beeld", _S_TABLE_HDR),
            Paragraph("Omschrijving", _S_TABLE_HDR),
            Paragraph("Aantal", _S_TABLE_HDR),
            Paragraph("Subtotaal", _S_TABLE_HDR),
            Paragraph("Meters", _S_TABLE_HDR),
        ]

    data = []
    style_cmds = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
    ]

    vdp_aantal = max(vdp_aantal, 1)

    for vdp_idx in range(vdp_aantal):
        # ── VDP header row (navy, spans all columns) ──
        vdp_row_idx = len(data)
        vdp_label = Paragraph(f"VDP {vdp_idx + 1}", _S_VDP_HDR)
        data.append([vdp_label] + [""] * (ncols - 1))
        style_cmds.extend([
            ("SPAN", (0, vdp_row_idx), (-1, vdp_row_idx)),
            ("BACKGROUND", (0, vdp_row_idx), (-1, vdp_row_idx), _NAVY),
            ("TEXTCOLOR", (0, vdp_row_idx), (-1, vdp_row_idx), _WHITE),
            ("TOPPADDING", (0, vdp_row_idx), (-1, vdp_row_idx), 3),
            ("BOTTOMPADDING", (0, vdp_row_idx), (-1, vdp_row_idx), 3),
        ])

        # ── Column header row (blue) ──
        hdr_row_idx = len(data)
        data.append(_col_header_row())
        style_cmds.extend([
            ("BACKGROUND", (0, hdr_row_idx), (-1, hdr_row_idx), _BLUE),
            ("TEXTCOLOR", (0, hdr_row_idx), (-1, hdr_row_idx), _WHITE),
        ])

        # ── Lane data rows for this VDP ──
        start = vdp_idx * mes
        end = min(start + mes, len(banen_summary))
        vdp_subtotal = 0
        vdp_meters = 0.0

        for lane_local, i in enumerate(range(start, end)):
            baan = banen_summary[i]
            baan_nr = baan.get("baan_nr", i + 1)
            rollen = baan.get("rollen", [])
            subtotaal = baan.get("subtotaal", 0)
            meters = meters_per_baan[i] if i < len(meters_per_baan) else 0.0
            vdp_subtotal += subtotaal
            vdp_meters += meters

            if rollen:
                for j, rol in enumerate(rollen):
                    row_idx = len(data)
                    row = [
                        Paragraph(str(baan_nr) if j == 0 else "", _S_TABLE_CELL),
                        Paragraph(str(rol.get("beeld", "")), _S_TABLE_CELL),
                        Paragraph(str(rol.get("omschrijving", "")), _S_TABLE_CELL),
                        Paragraph(str(rol.get("aantal", 0)), _S_TABLE_CELL),
                        Paragraph(str(subtotaal) if j == 0 else "", _S_TABLE_CELL),
                        Paragraph(f"{meters:.1f}" if j == 0 else "", _S_TABLE_CELL),
                    ]
                    data.append(row)
                    bg = _WHITE if lane_local % 2 == 0 else _LIGHT_GREY
                    style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg))
            else:
                row_idx = len(data)
                data.append([
                    Paragraph(str(baan_nr), _S_TABLE_CELL),
                    Paragraph("-", _S_TABLE_CELL),
                    Paragraph("-", _S_TABLE_CELL),
                    Paragraph("-", _S_TABLE_CELL),
                    Paragraph(str(subtotaal), _S_TABLE_CELL),
                    Paragraph(f"{meters:.1f}", _S_TABLE_CELL),
                ])
                bg = _WHITE if lane_local % 2 == 0 else _LIGHT_GREY
                style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg))

        # ── VDP subtotal row (grey, bold) ──
        sub_row_idx = len(data)
        data.append([
            Paragraph(f"Subtotaal VDP {vdp_idx + 1}", _S_TABLE_CELL_BOLD),
            Paragraph("", _S_TABLE_CELL_BOLD),
            Paragraph("", _S_TABLE_CELL_BOLD),
            Paragraph("", _S_TABLE_CELL_BOLD),
            Paragraph(str(vdp_subtotal), _S_TABLE_CELL_BOLD),
            Paragraph(f"{vdp_meters:.1f}", _S_TABLE_CELL_BOLD),
        ])
        style_cmds.extend([
            ("SPAN", (0, sub_row_idx), (3, sub_row_idx)),
            ("ALIGN", (0, sub_row_idx), (3, sub_row_idx), "RIGHT"),
            ("BACKGROUND", (0, sub_row_idx), (-1, sub_row_idx), _MED_GREY),
        ])

    # ── Grand total row ──
    total_meters = sum(meters_per_baan) if meters_per_baan else 0.0
    totals_idx = len(data)
    data.append([
        Paragraph("TOTAAL", _S_TABLE_CELL_BOLD),
        Paragraph("", _S_TABLE_CELL_BOLD),
        Paragraph("", _S_TABLE_CELL_BOLD),
        Paragraph("", _S_TABLE_CELL_BOLD),
        Paragraph(str(totaal_etiketten), _S_TABLE_CELL_BOLD),
        Paragraph(f"{total_meters:.1f}", _S_TABLE_CELL_BOLD),
    ])
    style_cmds.extend([
        ("SPAN", (0, totals_idx), (3, totals_idx)),
        ("ALIGN", (0, totals_idx), (3, totals_idx), "RIGHT"),
        ("BACKGROUND", (0, totals_idx), (-1, totals_idx), _MED_GREY),
        ("LINEABOVE", (0, totals_idx), (-1, totals_idx), 1, _NAVY),
    ])

    # ── Average row ──
    avg_labels = totaal_etiketten / mes if mes else 0
    avg_meters = total_meters / mes if mes else 0.0
    avg_idx = len(data)
    data.append([
        Paragraph("GEMIDDELDE / BAAN", _S_TABLE_CELL_ITALIC),
        Paragraph("", _S_TABLE_CELL_ITALIC),
        Paragraph("", _S_TABLE_CELL_ITALIC),
        Paragraph("", _S_TABLE_CELL_ITALIC),
        Paragraph(f"{avg_labels:.0f}", _S_TABLE_CELL_ITALIC),
        Paragraph(f"{avg_meters:.1f}", _S_TABLE_CELL_ITALIC),
    ])
    style_cmds.extend([
        ("SPAN", (0, avg_idx), (3, avg_idx)),
        ("ALIGN", (0, avg_idx), (3, avg_idx), "RIGHT"),
        ("BACKGROUND", (0, avg_idx), (-1, avg_idx), _LIGHT_GREY),
    ])

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle(style_cmds))
    return t


# ── Zone 5: Footer ───────────────────────────────────────────
def _build_footer(opmerkingen):
    elements = []
    if opmerkingen:
        note_cell = Paragraph(f"<b>Opmerkingen:</b> {opmerkingen}", _S_FOOTER_NOTE)
        note_table = Table([[note_cell]], colWidths=[_CONTENT_W])
        note_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _YELLOW),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("ROUNDEDCORNERS", [1.5 * mm, 1.5 * mm, 1.5 * mm, 1.5 * mm]),
        ]))
        elements.append(note_table)
        elements.append(Spacer(1, 3 * mm))

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    elements.append(Paragraph(f"Gegenereerd: {ts}", _S_FOOTER_TS))
    return elements


# ── Main entry point ─────────────────────────────────────────
def generate_pdf_summary(
    output_path,
    ordernummer,
    mes,
    vdp_aantal,
    totaal_etiketten,
    wikkel,
    kern,
    formaat_hoogte,
    formaat_breedte,
    extra_etiketten,
    afwijking_waarde,
    meters_per_baan,
    banen_summary,
    opmerkingen="",
):
    """Generate a PDF summary for a VDP job.

    Parameters
    ----------
    output_path : str or Path
        Where to write the PDF file.
    ordernummer : str
        Order number (shown prominently in the header).
    mes : int
        Number of lanes.
    vdp_aantal : int
        Number of VDPs.
    totaal_etiketten : int
        Total label count.
    wikkel : int
        Wikkel value.
    kern : int
        Core diameter (mm).
    formaat_hoogte : int
        Label height in mm.
    formaat_breedte : int
        Label width in mm.
    extra_etiketten : int
        Extra labels per roll.
    afwijking_waarde : int
        Deviation value.
    meters_per_baan : list[float]
        Calculated meters per lane.
    banen_summary : list[dict]
        Per-lane roll details. Each dict should have keys:
        ``baan_nr``, ``rollen`` (list of dicts with ``beeld``,
        ``omschrijving``, ``aantal``), ``subtotaal``.
    opmerkingen : str, optional
        Free-text notes shown in the footer.
    """
    output_path = Path(output_path)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        pageCompression=0,
    )

    date_str = date.today().isoformat()
    elements = []

    # Zone 1 — Header banner
    elements.append(_build_header_banner(ordernummer, vdp_aantal, date_str))
    elements.append(Spacer(1, 4 * mm))

    # Zone 2 — Key metrics bar
    elements.append(_build_metrics_bar(
        totaal_etiketten, mes, meters_per_baan,
        formaat_hoogte, formaat_breedte,
    ))
    elements.append(Spacer(1, 5 * mm))

    # Zone 3 — Order parameters (two side-by-side tables)
    elements.append(_build_params_table(
        wikkel, kern, extra_etiketten, afwijking_waarde,
        formaat_hoogte, formaat_breedte, vdp_aantal, totaal_etiketten,
    ))
    elements.append(Spacer(1, 5 * mm))

    # Zone 4 — Lane breakdown table
    elements.append(_build_lanes_table(
        banen_summary, meters_per_baan, totaal_etiketten, mes,
        vdp_aantal=vdp_aantal,
    ))
    elements.append(Spacer(1, 5 * mm))

    # Zone 5 — Footer
    elements.extend(_build_footer(opmerkingen))

    doc.build(elements)
    return output_path
