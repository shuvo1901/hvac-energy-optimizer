"""Build full research-report PDF from docs/RESEARCH_REPORT.md content."""
from pathlib import Path
from fpdf import FPDF
import json

proj = Path(r"D:\Python research project")
m = json.loads((proj / "results" / "metrics.json").read_text())

class R(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, "Physics-Informed ML for HVAC Energy Optimization  |  Sabbir Hossain (2026)",
                  align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(2)
    def footer(self):
        self.set_y(-15); self.set_font("Helvetica", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")
    def h1(self, t):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Helvetica", "B", 16); self.set_text_color(20, 60, 120)
        self.multi_cell(0, 9, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def h2(self, t):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Helvetica", "B", 12.5); self.set_text_color(25, 25, 25)
        self.multi_cell(0, 8, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def h3(self, t):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Helvetica", "B", 11); self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def p(self, t):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Helvetica", "", 10); self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.6, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def bullets(self, items):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Helvetica", "", 10); self.set_text_color(30, 30, 30)
        for b in items:
            self.multi_cell(0, 5.6, "-  " + b, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
    def table(self, head, rows, widths=None):
        self.set_font("Helvetica", "B", 9); self.set_fill_color(230, 238, 250)
        w = widths or [62, 30, 30, 30, 38]
        for i, h in enumerate(head):
            self.cell(w[i], 7, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9)
        for r in rows:
            for i, c in enumerate(r):
                self.cell(w[i], 6.5, str(c), border=1)
            self.ln()
        self.ln(2)

pdf = R(); pdf.alias_nb_pages(); pdf.set_auto_page_break(True, 20)
pdf.add_page()
pdf.h1("Physics-Informed Machine Learning for HVAC Energy Optimization:\nForecasting, Supply-Air-Temperature Reset, and Chiller Sequencing")
pdf.set_font("Helvetica", "", 11); pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 6, "Author: Sabbir Hossain   |   September 2026   |   2000 m2 commercial building, Dhaka-like hot-humid climate (synthetic BMS data)\nLocal package: D:/Python research project  |  Main file: examples/run_demo.py")
pdf.ln(2)
pdf.h2("Abstract")
pdf.p("HVAC is 40-60% of commercial-building electricity in hot-humid climates. This study unifies a 2R2C thermal model and ASHRAE psychrometrics with a gradient-boosting cooling-load forecaster and supervisory control (SAT reset, chiller sequencing, look-ahead pre-cooling). On a 60-day hourly test: MAE 1.55 kW, RMSE 2.76 kW, R2 0.9907, CVRMSE 8.30%, NMBE 2.29% - passing ASHRAE Guideline 14 (30%/10%). SAT reset saves 11.11% (13.97% full-year); sequencing saves 24.49% vs all-chillers-on. Lag-168 h (45.8%) dominates, proving schedule-aware control is highest leverage. Laptop-reproducible; 5/5 tests pass.")
pdf.p("Keywords: HVAC, energy optimization, forecasting, gradient boosting, SAT reset, chiller sequencing, ASHRAE G14, MPC.")
pdf.h2("1. Introduction")
pdf.p("Buildings are ~1/3 of final energy; HVAC is the largest end use. In Bangladesh cooling drives grid peaks, so 10% HVAC savings matter. Operators lack calibrated forecasts and run fixed setpoints. RQ1: can a lightweight forecaster pass G14? RQ2: savings of SAT reset/sequencing? RQ3: what drives load? Contribution: open laptop package hvac-energy-optimizer with models + harness.")
pdf.h2("2. Related work")
pdf.p("Supervisory control (Braun; Guideline 36): SAT reset trades lift vs fan/reheat; sequencing exploits concave COP(PLR). Forecasting: boosted trees Pareto-optimal at hourly horizons (interpretable, no GPU). G14 CVRMSE/NMBE judge calibration. MPC needs a model - here 2R2C; this study uses a greedy look-ahead proxy to stay solver-free.")
pdf.h2("3. Methodology")
pdf.h3("3.1 Psychrometrics"); pdf.p("Tetens psat (err <1% at 0-45 C), W=0.621945 pv/(p-pv), h=1.006T+W(2501+1.86T) kJ/kg, Magnus dew-point, coil Q=m_dot(h_in-h_out). Vectorised in psychrometrics.py.")
pdf.h3("3.2 Building + plant"); pdf.p("2R2C: C_in dT_in/dt=(T_wall-T_in)/R_in+Q_int+Q_sol+Q_hvac; C_wall dT_wall/dt=(T_out-T_wall)/R_out+(T_in-T_wall)/R_in (R_in 1.5, R_out 2.5 K/kW; C_in 2, C_wall 8 kWh/K). COP=COP_rated(0.45+0.85PLR-0.30PLR^2)(1-k(T_out-35)), k=0.012/0.010. Proportional control 8 kW/K, 200 kW cap.")
pdf.h3("3.3 Data"); pdf.p("synthetic.py: hourly t_out, rh_out, occupancy, q_internal, q_solar, cooling_load for 2000 m2 office, mean 27 C, weekday 08-18 + holidays, solar bell 13:00, UA + latent. Year: 8760 h, mean 42.2 kW. Seed-reproducible.")
pdf.h3("3.4 Forecaster"); pdf.p("Cyclical hour/dow/month, weekend/occupied flags, lags 1/24/168 h. GBM default (RF/Ridge options), 80/20 chronological split, TimeSeriesSplit CV, MAE/RMSE/CVRMSE/NMBE/R2.")
pdf.h3("3.5 Controllers"); pdf.bullets(["Baseline: SAT 13 C, 2x175 kW all-on, CV fan 2% peak.", "SAT reset: 12-16 C by OAT, VAV fan ~flow^3, +2% COP.", "Sequencing: fewest chillers above 15% PLR.", "SimpleMPC: pre-cool at 60% if OAT>=32 C in 4-h horizon, 22-25.5 C band."])
pdf.h3("3.6 Metrics"); pdf.p("CVRMSE=RMSE/mean*100 <=30%, |NMBE|<=10% (hourly). Saving=(E_base-E_opt)/E_base*100.")
pdf.h2("4. Experimental setup")
pdf.p("Windows laptop, Python 3.11.9, sklearn 1.9, pandas 3.0. Run: examples/run_demo.py --days 60 --model gbm; scripts/train_forecaster.py + evaluate_controls.py (full-year); pytest -q. Under 1 min, no GPU.")
pdf.h2("5. Results")
pdf.h3("5.1 Forecasting (RQ1)")
pdf.table(["Split", "MAE", "RMSE", "CVRMSE", "NMBE/R2"],
          [["60-day", "1.55 kW", "2.76 kW", "8.30%", "+2.29% / 0.9907"],
           ["Full-year", "1.71 kW", "2.95 kW", "9.82%", "-1.57% / 0.9877"]],
          [45, 30, 30, 30, 55])
pdf.p("Both pass G14 with margin. Importances: lag168 45.8%, q_internal 18.4%, is_occupied 17.9%, t_out 8.1%, occ_frac 7.0%, q_solar 1.9%. Weekly periodicity dominates.")
pdf.h3("5.2 Control savings (RQ2)")
pdf.table(["Strategy", "60-day kWh", "Save", "Year kWh", "Save"],
          [["Baseline", "4291.1", "-", "191582.8", "-"],
           ["SAT reset", "3814.5", "11.11%", "164825.4", "13.97%"],
           ["Sequencing", "-", "-", "144655.4", "24.49%"]],
          [45, 35, 25, 40, 25])
pdf.p("Sequencing gain is large because baseline runs both chillers at ~12% mean PLR; optimiser runs one near 25%. SAT-reset 11-14% matches hot-humid VAV literature.")
demo = proj / "results" / "demo.png"
if demo.exists():
    pdf.h3("Figure 1 - Load forecast + power (1-week slice)")
    pdf.image(str(demo), w=180); pdf.ln(2)
pdf.h3("5.3 Sanity"); pdf.p("simulate_zone at 34 C engages cooling after 1 h, COP in range. 5/5 pytest pass.")
pdf.h2("6. Discussion (RQ3 + limitations)")
pdf.p("Schedule/history beats weather: log occupancy + 3 weeks history before MPC. SAT reset is cheapest decarbonisation (setpoint change only). Limits: synthetic data, proxy fan/COP, no humidity/demand/PMV, single seed/climate. Replace data/synthetic_hvac.csv with BMS trends to re-run unchanged.")
pdf.h2("7. Conclusion"); pdf.p("Laptop pipeline passes G14 and shows 11-14% SAT-reset (24% sequencing) savings. Next: real BMS validation, PMV/CO2 + pricing, full CasADi MPC, FDD study.")
pdf.h2("References")
pdf.p("1. ASHRAE Fundamentals (2021) Ch.1. 2. ASHRAE Guideline 14-2014. 3. Guideline 36-2024. 4. Braun et al., supervisory control. 5. Pedregosa et al., Scikit-learn, JMLR 2011.")
pdf.h2("Appendix - Reproduce")
pdf.set_font("Courier", "", 8.5)
pdf.multi_cell(0, 5, "python scripts/generate_synthetic_data.py --days 365\npython scripts/train_forecaster.py --csv data/synthetic_hvac.csv --model gbm\npython scripts/evaluate_controls.py --csv data/synthetic_hvac.csv\npython examples/run_demo.py --days 60 --model gbm\npython -m pytest -q")
out = proj / "results" / "HVAC_Research_Report.pdf"
pdf.output(str(out))
print(f"Saved {out} ({out.stat().st_size/1024:.0f} KB)")
import shutil; shutil.copy(out, r"D:\HVAC_Research_Report.pdf")
print("Copied to D:\\HVAC_Research_Report.pdf")
