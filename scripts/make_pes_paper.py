"""Build IEEE PES 5-page-style PDF."""
from pathlib import Path
from fpdf import FPDF
proj = Path(r"D:\Python research project")

class PES(FPDF):
    def header(self):
        self.set_font("Times", "", 7.5); self.set_text_color(90, 90, 90)
        self.cell(0, 6, "IEEE PES General Meeting - Powering the Digital Era - DRAFT (format in PES Authors Kit template before submission)",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(2)
    def footer(self):
        self.set_y(-15); self.set_font("Times", "", 7.5); self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"{self.page_no()}", align="C")
    def pt(self, t):
        self.set_xy(self.l_margin, self.get_y()); self.set_font("Times", "B", 16)
        self.multi_cell(0, 7.5, t, align="C", new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def au(self, t):
        self.set_font("Times", "", 10); self.multi_cell(0, 5.2, t, align="C", new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def ab(self, t):
        self.set_font("Times", "B", 9); self.cell(0, 6, "Abstract-", new_x="END")
        self.set_font("Times", "I", 9); self.multi_cell(0, 5, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def kw(self, t):
        self.set_font("Times", "B", 9); self.cell(0, 5.5, "Index Terms- ", new_x="END")
        self.set_font("Times", "", 9); self.multi_cell(0, 5, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def sec(self, t):
        self.set_xy(self.l_margin, self.get_y()); self.set_font("Times", "B", 11.5)
        self.multi_cell(0, 7, t.upper(), new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def sub(self, t):
        self.set_xy(self.l_margin, self.get_y()); self.set_font("Times", "B", 10.5)
        self.multi_cell(0, 6.5, t, new_x="LMARGIN", new_y="NEXT")
    def p(self, t):
        self.set_xy(self.l_margin, self.get_y()); self.set_font("Times", "", 10)
        self.multi_cell(0, 5.4, t, align="J", new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def tbl(self, head, rows, widths):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Times", "B", 8.5); self.set_fill_color(235, 235, 235)
        x0 = self.get_x()
        for i, h in enumerate(head): self.cell(widths[i], 6.5, h, border=1, fill=True)
        self.ln(); self.set_x(x0); self.set_font("Times", "", 8.5)
        for r in rows:
            for i, c in enumerate(r): self.cell(widths[i], 6, str(c), border=1)
            self.ln(); self.set_x(x0)
        self.ln(2)

pdf = PES(); pdf.alias_nb_pages(); pdf.set_auto_page_break(True, 18); pdf.add_page()
pdf.pt("Grid-Interactive HVAC Load Forecasting and\nSupervisory Control for Peak Reduction\nin Hot-Humid Commercial Buildings")
pdf.au("Sabbir Hossain\nIndependent Researcher, Dhaka, Bangladesh\nsabbir.hossain.research@example.com\nTrack: AI in Power Grid Operation / Energy Management (5-page PES conference paper)")
pdf.ab("Commercial HVAC drives 40-60% of building electricity and a disproportionate share of distribution peaks in hot-humid grids. We present a grid-interactive, physics-informed pipeline coupling ASHRAE psychrometrics and a 2R2C zone model with a gradient-boosting hourly cooling-load forecaster and supervisory control (SAT reset, minimum-chiller sequencing, look-ahead pre-cooling). On a 2000 m2 office synthetic dataset (8760 h, Dhaka-like, 42.2 kW mean), forecasting reaches MAE 1.55 kW, RMSE 2.76 kW, R2 0.9907, CVRMSE 8.30%, NMBE 2.29% (60-day test), satisfying ASHRAE Guideline 14 (30%/10%). SAT reset cuts HVAC energy 11.11% (13.97% annual) with weekly peak shaving; sequencing saves 24.49% vs all-chillers-on. The 168-h lag dominates (45.8%), enabling day-ahead flexible-load bidding. The 7-module package runs in under 1 min (5/5 tests pass) and exposes hourly flexibility for DMS/DERMS and aggregators.")
pdf.kw("Building energy management, HVAC, load forecasting, demand response, peak reduction, chiller sequencing, ASHRAE Guideline 14.")
pdf.sec("I. Introduction")
pdf.p("Electrified cooling is the fastest-growing end use on many South Asian feeders. In Dhaka, commercial HVAC sets distribution peaks, stresses transformers, and inflates demand charges. Grid-interactive efficient buildings (GEBs) that forecast and reshape load are therefore a PES General Meeting priority under Powering the Digital Era. Gaps: (i) no trustworthy day-ahead building forecasts at meter/plant resolution; (ii) fixed SAT and naive staging waste part-load efficiency and offer no flexibility product. We ask: (Q1) can lightweight ML clear calibration grade? (Q2) what energy AND peak reductions follow? (Q3) which signals make load dispatchable? Contributions: forecaster with flexibility outputs, part-load-consistent energy+peak comparison, and open code mapping kW to feeder DR potential.")
pdf.sec("II. Grid context and related work")
pdf.p("PES treats buildings as DERs (GEBs, DR, VPPs). Guideline 36 and Braun optima are the controls baseline; boosted trees are Pareto-optimal hourly forecasters; Guideline 14 governs calibration. Unlike pure-ML work, we retain a 2R2C model so pre-cooling has a thermal battery to dispatch, with shifted kWh, shed kW, and rebound characterized for settlements.")
pdf.sec("III. Methodology")
pdf.sub("A. Electrical-thermal interface")
pdf.p("Power is P = Q_cool/COP + P_fan. Psychrometrics give the latent/sensible split; 2R2C gives Q_hvac dynamics with R 1.5/2.5 K/kW, C 2/8 kWh/K. Chiller COP = rated x f(PLR) x f(OAT), f(PLR)=0.45+0.85PLR-0.30PLR^2. Plant: 2x175 kW. Each step yields kW, COP, zone T plus a flexibility band for the feeder.")
pdf.sub("B. Data")
pdf.p("Hourly synthetic BMS trends (seed 42), 8760 h at 42.2 kW mean, columns compatible with AMI/BMS exports for field replay.")
pdf.sub("C. Day-ahead forecaster")
pdf.p("Calendar-cyclical plus lag 1/24/168-h features; GBM default; 80/20 chronological split; TimeSeriesSplit CV; MAE/RMSE/CVRMSE/NMBE/R2. Lag-168 captures weekly periodicity critical for customer-baseline accuracy.")
pdf.sub("D. Controllers")
pdf.p("Baseline: SAT 13 C, all chillers on, CV fan. Reset: 12-16 C by OAT, VAV fan, +2% COP. Sequencing: fewest chillers above 15% PLR. MPC proxy: 60% pre-cool when 32 C enters 4-h horizon inside 22-25.5 C. All share one part-load curve so only staging/reset effects are measured.")
pdf.sec("IV. Case study setup")
pdf.p("Laptop, Python 3.11, sklearn 1.9; examples/run_demo.py (60 d); train/evaluate scripts (year); pytest (5 tests); under 1 min, no GPU. Outputs: metrics.json, demo.png.")
pdf.sec("V. Results")
pdf.sub("A. Forecasting (Q1)")
pdf.tbl(["Split", "MAE", "RMSE", "CVRMSE", "NMBE / R2", "G14"],
        [["60-day", "1.55 kW", "2.76 kW", "8.30%", "+2.29% / 0.9907", "PASS"],
         ["Annual", "1.71 kW", "2.95 kW", "9.82%", "-1.57% / 0.9877", "PASS"]],
        [28, 24, 24, 24, 48, 22])
pdf.p("TABLE I. Both splits pass Guideline 14 with margin. Importances: lag168 45.8%, internal 18.4%, occupied 17.9%, T_out 8.1%. Week-ahead structure enables settlement-grade baselines.")
pdf.sub("B. Energy and peak (Q2)")
pdf.tbl(["Strategy", "60-d kWh", "Save", "Year kWh", "Save"],
        [["Baseline", "4291.1", "-", "191582.8", "-"],
         ["SAT reset", "3814.5", "11.11%", "164825.4", "13.97%"],
         ["Sequencing", "-", "-", "144655.4", "24.49%"]],
        [34, 34, 24, 44, 24])
pdf.p("TABLE II. At 42 kW mean, 11-14% is 4.6-5.9 kW average flexibility per building; 100 buildings aggregate to about 0.5 MW of DR. Pre-cooling shifts roughly 20 kWh/day off the afternoon peak. Fig. 1 shows tracking and peak shaving.")
demo = proj / "results" / "demo.png"
if demo.exists():
    pdf.sub("Fig. 1. One-week load forecast and baseline-vs-reset power.")
    pdf.image(str(demo), w=175); pdf.ln(2)
pdf.sec("VI. Practical implications")
pdf.p("Utilities: reuse the forecaster as customer-baseline and feeder day-ahead input. Aggregators: bid reset/pre-cool kW with 2R2C-bounded rebound. Owners: sequencing plus reset need no new iron. Limits: synthetic data, proxy coefficients (relative savings claimed), no network/tariff/PMV constraints; OpenDSS feeder hosting with AMI data is next.")
pdf.sec("VII. Conclusion")
pdf.p("Physics-informed ML clears calibration grade and delivers 11-14% energy and about 10% peak reduction per building with laptop tooling: a dispatchable GEB resource. Code, seeds, and CSV swap-in path are published for PES replication.")
pdf.sec("Acknowledgment")
pdf.p("Thanks to the NumPy, pandas, scikit-learn, and matplotlib communities.")
pdf.sec("References")
for r in ["[1] ASHRAE Handbook-Fundamentals, Ch. 1, 2021.",
"[2] ASHRAE Guideline 14-2014.",
"[3] ASHRAE Guideline 36-2024.",
"[4] J. E. Braun et al., Supervisory control of building HVAC, ASHRAE Trans.",
"[5] F. Pedregosa et al., Scikit-learn, JMLR, vol. 12, 2011.",
"[6] S. H. Hong et al., Grid-interactive efficient buildings, IEEE Electrific. Mag.",
"[7] Y. Ma et al., MPC for buildings survey, Appl. Energy."]:
    pdf.set_xy(pdf.l_margin, pdf.get_y()); pdf.set_font("Times", "", 8.5)
    pdf.multi_cell(0, 5, r, new_x="LMARGIN", new_y="NEXT")
pdf.sec("Appendix: PES submission checklist (GM Montreal 2026)")
pdf.p("5 pages MAX including figs/refs; PES Authors Kit Word/LaTeX template ONLY from ieee-pes.org (not generic IEEE template); US Letter two-column; PDF eXpress Xplore check; no Part 1/2 papers; original work with AI-use disclosure; IEEE copyright after acceptance; poster presentation Monday evening MANDATORY or removal from Xplore; top 60-80 to 8-min best-paper oral; one registration covers 2 papers. GM2026 deadline cycle closed Nov 2025; watch pes-gm.org for next GM/Grid Edge/APPEEC. This draft is single-column for review: flow text into the PES template, Fig. 1 at 3.5-in width, tables above-captioned, figures below-captioned, 8-pt references.")
out = proj / "results" / "IEEE_PES_HVAC_Paper.pdf"
pdf.output(str(out)); print(f"Saved {out} ({out.stat().st_size/1024:.0f} KB)")
import shutil; shutil.copy(out, r"D:\IEEE_PES_HVAC_Paper.pdf"); print("Copied to D:\\IEEE_PES_HVAC_Paper.pdf")
