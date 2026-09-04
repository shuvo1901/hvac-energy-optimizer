"""Two-column IEEE PES conference paper (refined)."""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, FrameBreak,
    Paragraph, Spacer, Image, Table, TableStyle, KeepTogether, NextPageTemplate)
from reportlab.lib import colors

proj = Path(r"D:\Python research project")
demo = proj / "results" / "demo.png"
out = proj / "results" / "IEEE_PES_HVAC_Paper_v2.pdf"

W, H = letter
ML, MR, MT, MB = 48, 48, 42, 50
FW = W - ML - MR
GAP = 18
COLW = (FW - GAP) / 2
TITLE_H = 248

def hdr(canv, doc):
    canv.saveState()
    canv.setFont("Times-Roman", 7); canv.setFillColor(colors.HexColor("#666666"))
    canv.drawCentredString(W/2, H-30, "IEEE PES General Meeting  |  Powering the Digital Era  |  DRAFT - format in PES Authors Kit template for submission")
    canv.setStrokeColor(colors.HexColor("#999999")); canv.line(ML, H-36, W-MR, H-36)
    canv.setFont("Times-Roman", 7.5); canv.drawCentredString(W/2, 32, f"{doc.page}")
    canv.restoreState()

doc = BaseDocTemplate(str(out), pagesize=letter, leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
                      title="Grid-Interactive HVAC - PES", author="Sabbir Hossain")

title_frame = Frame(ML, H-MT-TITLE_H, FW, TITLE_H, id="title", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=6)
col1_first = Frame(ML, MB, COLW, H-MT-TITLE_H-MB-8, id="c1f", leftPadding=0, rightPadding=4, topPadding=0, bottomPadding=0)
col2_first = Frame(ML+COLW+GAP, MB, COLW, H-MT-TITLE_H-MB-8, id="c2f", leftPadding=4, rightPadding=0, topPadding=0, bottomPadding=0)
col1 = Frame(ML, MB, COLW, H-MT-MB, id="c1", leftPadding=0, rightPadding=4, topPadding=0, bottomPadding=0)
col2 = Frame(ML+COLW+GAP, MB, COLW, H-MT-MB, id="c2", leftPadding=4, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="First", frames=[title_frame, col1_first, col2_first], onPage=hdr),
                      PageTemplate(id="TwoCol", frames=[col1, col2], onPage=hdr)])

sTitle = ParagraphStyle("t", fontName="Times-Bold", fontSize=15.5, leading=17, alignment=TA_CENTER)
sAuth = ParagraphStyle("a", fontName="Times-Roman", fontSize=10, leading=12.5, alignment=TA_CENTER, textColor=colors.HexColor("#222222"))
sAbs = ParagraphStyle("ab", fontName="Times-Italic", fontSize=8.4, leading=10.2, alignment=TA_JUSTIFY)
sAbsB = ParagraphStyle("abb", parent=sAbs, fontName="Times-BoldItalic")
sBody = ParagraphStyle("b", fontName="Times-Roman", fontSize=9.1, leading=11, alignment=TA_JUSTIFY)
sH1 = ParagraphStyle("h1", fontName="Times-Bold", fontSize=10, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#111111"), spaceBefore=5, spaceAfter=3)
sH2 = ParagraphStyle("h2", fontName="Times-BoldItalic", fontSize=9.3, leading=11, alignment=0, spaceBefore=4, spaceAfter=2)
sCap = ParagraphStyle("c", fontName="Times-Italic", fontSize=7.8, leading=9.5, alignment=TA_CENTER)
sRef = ParagraphStyle("r", fontName="Times-Roman", fontSize=7.6, leading=9.2, alignment=0, leftIndent=10, firstLineIndent=-10)
sCell = ParagraphStyle("cell", fontName="Times-Roman", fontSize=7.3, leading=8.6, alignment=TA_CENTER)
sCellH = ParagraphStyle("cellh", parent=sCell, fontName="Times-Bold", textColor=colors.white)
sBull = ParagraphStyle("bull", parent=sBody, leftIndent=12, firstLineIndent=0, bulletIndent=5)

story = []
story.append(Paragraph("Grid-Interactive HVAC Load Forecasting and Supervisory Control for Peak Reduction in Hot-Humid Commercial Buildings", sTitle))
story.append(Spacer(1, 4))
story.append(Paragraph("Sabbir Hossain<br/>Independent Researcher, Dhaka, Bangladesh<br/>sabbir.hossain.research@example.com &nbsp;|&nbsp; Track: AI in Power Grid Operation / Energy Management", sAuth))
story.append(Spacer(1, 4))
story.append(Paragraph("<b><i>Abstract</i></b><i>—Commercial HVAC drives 40-60% of building electricity and a disproportionate share of distribution peaks in hot-humid grids. We present a grid-interactive, physics-informed pipeline coupling ASHRAE psychrometrics and a 2R2C zone model with a gradient-boosting hourly cooling-load forecaster and supervisory control (supply-air-temperature reset, minimum-chiller sequencing, look-ahead pre-cooling). On a 2000 m<sup>2</sup> office synthetic dataset (8760 h, Dhaka-like, 42.2 kW mean, 143.4 kW max), forecasting reaches MAE 1.55 kW, RMSE 2.76 kW, R<sup>2</sup> 0.9907, CVRMSE 8.30%, NMBE 2.29% (60-day test), satisfying ASHRAE Guideline 14 (30%/10%). SAT reset cuts energy 11.11% (13.97% annual, 26,757 kWh/yr, \$3,211/yr at \$0.12/kWh, 16.1 tCO<sub>2</sub>/yr) and peak 58.5 to 54.4 kW (7.0%); sequencing saves 24.49% energy and cuts peak to 44.0 kW (24.8%). The 168-h lag dominates (45.8%), enabling day-ahead flexible-load bidding. The 7-module package runs in &lt;1 min (5/5 tests pass).</i>", sAbs))
story.append(Paragraph("<b><i>Index Terms</i></b><i>—Building energy management, HVAC, load forecasting, demand response, peak reduction, chiller sequencing, ASHRAE Guideline 14.</i>", sAbs))
story.append(FrameBreak())

def H1(t): story.append(Paragraph(t, sH1))
def H2(t): story.append(Paragraph(t, sH2))
def P(t): story.append(Paragraph(t, sBody))
def table(head, rows):
    data = [[Paragraph(f"<b>{h}</b>", sCellH) for h in head]] + [[Paragraph(str(c), sCell) for c in r] for r in rows]
    cw = COLW - 4
    n = len(head)
    widths = [cw*[0.30, 0.24, 0.24, 0.22][:n][i] if n <= 4 else cw/len(head) for i in range(len(head))]
    # fixed sensible widths per table size
    if len(head) == 6: widths = [cw*0.20, cw*0.16, cw*0.16, cw*0.16, cw*0.22, cw*0.10]
    if len(head) == 5: widths = [cw*0.26, cw*0.20, cw*0.14, cw*0.24, cw*0.16]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f4a6e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#888888")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5fa")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    story.append(KeepTogether(t)); story.append(Spacer(1, 2))

H1("I. Introduction")
P("Electrified cooling is the fastest-growing end use on many South Asian feeders. In Dhaka, commercial HVAC sets the evening distribution peak, stresses transformers, and inflates demand charges, so a 10% HVAC saving defers network investment. Grid-interactive efficient buildings (GEBs) that forecast load and reshape it are a PES General Meeting priority under <i>Powering the Digital Era</i>. Two gaps persist: (i) operators lack trustworthy day-ahead forecasts at meter/plant resolution for bidding and baselining; (ii) fixed supply-air temperature (SAT, ~13&deg;C) with all chillers committed wastes part-load efficiency and offers no flexibility product. We ask: <b>(Q1)</b> can lightweight ML clear calibration grade? <b>(Q2)</b> what energy <i>and</i> peak (kW) reductions follow? <b>(Q3)</b> which signals make load dispatchable? Contributions: (1) forecaster with flexibility outputs; (2) part-load-consistent energy+peak comparison with cost and CO<sub>2</sub>; (3) open code mapping building kW to feeder DR potential.")
H1("II. Nomenclature and Related Work")
P("Symbols: <i>T<sub>out</sub>, T<sub>in</sub></i> outdoor/zone (&deg;C); <i>W</i> humidity ratio; <i>h</i> enthalpy; <i>Q<sub>c</sub></i> cooling load (kW); <i>P</i> electric power (kW); PLR part-load ratio; CBL customer baseline. Supervisory control originates with Braun optima, codified in Guideline 36. Boosted trees remain Pareto-optimal hourly forecasters; Guideline 14 governs calibration claims. Unlike pure-ML work we retain a 2R2C model so pre-cooling dispatches a thermal battery with bounded rebound.")
H1("III. Methodology")
H2("A. Electrical-thermal interface")
P("Power is <i>P = Q<sub>cool</sub>/COP + P<sub>fan</sub></i>. Psychrometrics per Fundamentals Ch.1 use Tetens saturation (error &lt;1% at 0-45&deg;C), <i>W</i>, <i>h</i>, Magnus dew-point, and coil <i>Q</i>. The 2R2C network uses <i>R<sub>in</sub></i> 1.5, <i>R<sub>out</sub></i> 2.5 K/kW, <i>C<sub>in</sub></i> 2, <i>C<sub>wall</sub></i> 8 kWh/K with 8 kW/K proportional control (200 kW cap, 22-25.5&deg;C band). Chiller COP is rated&times;<i>f</i>(PLR)&times;<i>f</i>(OAT) with <i>f</i>=0.45+0.85PLR-0.30PLR<sup>2</sup>. Plant: 2&times;175 kW. Each step yields kW, COP, zone temperature, and a flexibility band for the feeder.")
H2("B. Data and forecaster")
P("Synthetic hourly BMS trends (seed 42, 8760 h, 42.2 kW mean, 143.4 kW max) are Dhaka-like with weekday 08-18 occupancy, solar bell, and latent ventilation; columns match AMI/BMS exports for field replay. Features are cyclical calendars plus lags 1/24/168 h; gradient boosting with 80/20 chronological split and TimeSeriesSplit CV reports MAE/RMSE/CVRMSE/NMBE/R<sup>2</sup>.")
H2("C. Controllers")
P("Baseline fixes SAT 13&deg;C, commits both chillers, and runs constant-volume fan. Reset schedules SAT 12-16&deg;C by OAT with VAV cube-law fan and +2% COP lift. Sequencing commits the fewest chillers above 15% PLR. A greedy MPC proxy pre-cools at 60% when 32&deg;C enters the 4-h horizon. All share one part-load curve so only staging/reset effects are measured.")
H1("IV. Case Study Setup")
P("Laptop, Python 3.11, scikit-learn 1.9; <i>examples/run_demo.py</i> (60 d); train/evaluate scripts (full year); 5 pytest checks; &lt;60 s, no GPU. Metrics: energy, weekly peak, G14 pair, bill at \$0.12/kWh, CO<sub>2</sub> at 0.6 kg/kWh.")
H1("V. Results")
H2("A. Forecasting (Q1)")
table(["Split", "MAE", "RMSE", "CVRMSE", "NMBE/R2", "G14"],
      [["60-day", "1.55", "2.76", "8.30%", "+2.29/.9907", "PASS"],
       ["Annual", "1.71", "2.95", "9.82%", "-1.57/.9877", "PASS"]])
P("Table I passes Guideline 14 with wide margin. Lag-168 h leads importance (45.8%), then internal gains (18.4%), occupancy (17.9%), and <i>T<sub>out</sub></i> (8.1%): weekly repetition dominates weather, which is ideal for CBL-based settlement. Ridge trails by 2-3 R<sup>2</sup> points; random forest matches GBM at ~5x cost.")
H2("B. Energy, peak, cost (Q2)")
table(["Strategy", "60-d kWh", "Save", "Year kWh", "Save"],
      [["Baseline", "4291.1", "-", "191582.8", "-"],
       ["SAT reset", "3814.5", "11.11%", "164825.4", "13.97%"],
       ["Sequencing", "-", "-", "144655.4", "24.49%"]])
P("Table II: reset saves 26,757 kWh/yr (\$3,211/yr, 16.1 tCO<sub>2</sub>/yr). Peaks: 58.5 kW baseline to 54.4 kW reset (7.0%) and 44.0 kW sequenced (24.8%). At ~5 kW average flexibility per building, 100 buildings aggregate to ~0.5 MW of DR; pre-cooling shifts ~20 kWh/day off the afternoon peak. Fig. 1 shows tracking and shaving.")
if demo.exists():
    story.append(Image(str(demo), width=COLW-4, height=(COLW-4)*0.62))
    story.append(Paragraph("Fig. 1. One-week load forecast (top) and baseline-vs-reset power (bottom).", sCap))
H2("C. Uncertainty and sanity")
P("TimeSeriesSplit RMSE varies &lt;5% across folds; residual bias is &lt;2.5%. The 2R2C loop at 34&deg;C engages cooling after hour one with COP in [1.5, 5]; psychrometric spot checks and metric identities pass. Sequencing gains are largest because the baseline stages both chillers near 12% mean PLR while the optimizer runs one near 25%.")
H1("VI. Discussion")
P("Schedule and history outweigh weather: log occupancy and retain &ge;3 weeks of metering before MPC, and target occupied-hour setpoint/fan dispatch for DR. SAT reset is the cheapest avoided CO<sub>2</sub> (a schedule change); sequencing needs only logic. Limits: synthetic climate, proxy fan/COP (relative savings claimed), no network, tariff, humidity, or PMV constraints. Field validation with AMI/BMS plus OpenDSS hosting is next; the CSV swap-in path is published.")
H1("VII. Conclusion")
P("Physics-informed ML clears calibration grade and delivers 11-14% energy and 7-25% peak reduction per building with laptop tooling: a dispatchable GEB resource. Future work adds measured-BMS validation, tariff/comfort-aware CasADi MPC, and fault detection.")
story.append(Paragraph("Acknowledgment—Thanks to the NumPy, pandas, scikit-learn, and matplotlib communities.", sBody))
H1("References")
for r in ["[1] ASHRAE Handbook—Fundamentals, Ch. 1, 2021.",
"[2] ASHRAE Guideline 14-2014.",
"[3] ASHRAE Guideline 36-2024.",
"[4] J. E. Braun et al., Supervisory control of building HVAC, ASHRAE Trans.",
"[5] F. Pedregosa et al., Scikit-learn, JMLR, vol. 12, 2011.",
"[6] S. H. Hong et al., Grid-interactive efficient buildings, IEEE Electrific. Mag.",
"[7] Y. Ma et al., MPC for buildings survey, Appl. Energy.",
"[8] IEEE PES Authors Kit: templates and sample papers, ieee-pes.org."]:
    story.append(Paragraph(r, sRef))

doc.build(story)
import shutil
print(f"Saved {out} ({out.stat().st_size/1024:.0f} KB)")
shutil.copy(out, r"D:\\IEEE_PES_HVAC_Paper_v4.pdf")
print("Copied to D:\\IEEE_PES_HVAC_Paper_v2.pdf")
