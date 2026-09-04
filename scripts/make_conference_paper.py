"""Build IEEE-style conference paper PDF (single-column draft ready to paste into IEEE template)."""
from pathlib import Path
from fpdf import FPDF

proj = Path(r"D:\Python research project")

class IEEE(FPDF):
    def header(self):
        self.set_font("Times", "", 7.5); self.set_text_color(90, 90, 90)
        self.cell(0, 6, "Proc. IEEE-style draft - HVAC Energy Optimization - S. Hossain (2026) - DRAFT - do not distribute",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(2)
    def footer(self):
        self.set_y(-15); self.set_font("Times", "", 7.5); self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"{self.page_no()}", align="C")
    def paper_title(self, t):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Times", "B", 17); self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, t, align="C", new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def authors(self, t):
        self.set_font("Times", "", 10.5)
        self.multi_cell(0, 5.5, t, align="C", new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def abstract(self, t):
        self.set_font("Times", "B", 9); self.cell(0, 6, "Abstract-", new_x="END")
        self.set_font("Times", "I", 9); self.set_text_color(20, 20, 20)
        self.multi_cell(0, 5, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def keywords(self, t):
        self.set_font("Times", "B", 9); self.cell(0, 5.5, "Keywords- ", new_x="END")
        self.set_font("Times", "", 9); self.multi_cell(0, 5, t, new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def sec(self, t):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Times", "B", 11.5)
        self.multi_cell(0, 7, t.upper(), new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def sub(self, t):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Times", "B", 10.5)
        self.multi_cell(0, 6.5, t, new_x="LMARGIN", new_y="NEXT")
    def p(self, t):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Times", "", 10); self.set_text_color(15, 15, 15)
        self.multi_cell(0, 5.4, t, align="J", new_x="LMARGIN", new_y="NEXT"); self.ln(1)
    def tbl(self, head, rows, widths):
        self.set_xy(self.l_margin, self.get_y())
        self.set_font("Times", "B", 8.5); self.set_fill_color(235, 235, 235)
        x0 = self.get_x()
        for i, h in enumerate(head):
            self.cell(widths[i], 6.5, h, border=1, fill=True)
        self.ln(); self.set_x(x0)
        self.set_font("Times", "", 8.5)
        for r in rows:
            for i, c in enumerate(r):
                self.cell(widths[i], 6, str(c), border=1)
            self.ln(); self.set_x(x0)
        self.ln(1)
        self.set_font("Times", "I", 8); self.set_text_color(60, 60, 60)
        self.set_x(x0); self.ln(1); self.set_text_color(15, 15, 15)

pdf = IEEE(); pdf.alias_nb_pages(); pdf.set_auto_page_break(True, 18)
pdf.add_page()
pdf.paper_title("Physics-Informed Machine Learning for HVAC\nEnergy Optimization: Load Forecasting with\nSupervisory Reset and Sequencing Control")
pdf.authors("Sabbir Hossain\nIndependent Researcher, Dhaka, Bangladesh\nsabbir.hossain.research@example.com")
pdf.abstract("HVAC systems account for 40-60% of commercial building electricity in hot-humid climates, yet most operate on fixed setpoints that waste part-load and mild-hour efficiency. We present a laptop-reproducible, physics-informed pipeline unifying (i) ASHRAE psychrometrics and a 2R2C zone model, (ii) a gradient-boosting hourly cooling-load forecaster, and (iii) supervisory control via supply-air-temperature (SAT) reset, minimum-chiller sequencing, and look-ahead pre-cooling. On synthetic BMS data for a 2000 m2 office in a Dhaka-like climate (8760 h, mean 42.2 kW), the forecaster achieves MAE 1.55 kW, RMSE 2.76 kW, R2 0.9907, CVRMSE 8.30% and NMBE 2.29% on a 60-day test, satisfying ASHRAE Guideline 14 hourly limits (30%/10%). SAT reset cuts HVAC electricity by 11.11% on the test slice (13.97% full-year); optimal sequencing saves 24.49% versus an all-chillers-committed baseline. Weekly history (168-h lag, 45.8%) dominates occupancy and outdoor temperature, motivating schedule-aware control. The 7-module package runs in under one minute without GPU; 5/5 tests pass.")
pdf.keywords("HVAC energy optimization, cooling load forecasting, gradient boosting, supply air temperature reset, chiller sequencing, ASHRAE Guideline 14, model predictive control.")
pdf.sec("I. Introduction")
pdf.p("Commercial buildings consume roughly one third of global final energy, with HVAC as the largest end use. In Bangladesh, rising cooling degree-days make air-conditioning the dominant driver of commercial tariffs and grid peaks, so a 10% HVAC saving defers generation investment and cuts emissions at scale. Two gaps block deployment: operators lack calibrated short-horizon forecasts, and prevalent fixed-setpoint practice (constant SAT near 13 C, all chillers committed) ignores the concave part-load COP curve and mild-hour lift savings. We ask: (Q1) can a lightweight forecaster without deep learning reach Guideline-14 quality? (Q2) what do classical supervisory retrofits save against a fair baseline? (Q3) which signals drive load? Contributions are: (1) an open 7-module package with one evaluation harness; (2) a part-load-consistent comparison of SAT reset and sequencing; (3) full laptop reproducibility with seeds and tests.")
pdf.sec("II. Related Work")
pdf.p("Supervisory HVAC control originates with Braun's optimal setpoint studies and is codified in ASHRAE Guideline 36. SAT reset trades chiller lift and reheat against fan power; sequencing exploits COP(PLR). For hourly horizons with strong calendar structure, boosted trees remain Pareto-optimal on accuracy, interpretability, and cost versus LSTM. Calibration is judged by Guideline 14 CVRMSE/NMBE. MPC commonly uses RC networks; we adopt 2R2C with a solver-free greedy look-ahead that preserves the pre-cooling insight without CasADi/pyomo dependencies.")
pdf.sec("III. Methodology")
pdf.sub("A. Psychrometrics")
pdf.p("Per ASHRAE Fundamentals Ch.1: Tetens saturation pressure psat = 610.78 exp(17.27 T/(T+237.3)) Pa (error below 1% at 0-45 C), humidity ratio W = 0.621945 pv/(p-pv), enthalpy h = 1.006 T + W(2501+1.86 T) kJ/kg-da, Magnus dew-point, and coil load Q = m_dot (h_in - h_out). Implemented vectorised in psychrometrics.py with unit tests (saturation pressure, saturated-air identity, enthalpy monotonicity, non-negative coil load).")
pdf.sub("B. Zone and Plant Model")
pdf.p("The 2R2C network is C_in dT_in/dt = (T_wall-T_in)/R_in + Q_int + Q_sol + Q_hvac and C_wall dT_wall/dt = (T_out-T_wall)/R_out + (T_in-T_wall)/R_in, with R_in 1.5, R_out 2.5 K/kW and C_in 2, C_wall 8 kWh/K. Chiller COP = COP_rated (0.45+0.85 PLR-0.30 PLR^2)(1-k(T_out-35)) with k = 0.012 baseline and 0.010 under reset. Proportional control (8 kW/K, 200 kW cap) with comfort band 22-25.5 C closes the loop in simulate_zone(). A frozen-state integration bug discovered during testing was fixed and regression-covered.")
pdf.sub("C. Dataset")
pdf.p("The synthetic generator (synthetic.py) emits hourly t_out, rh_out, occupancy, q_internal, q_solar, and cooling_load_kw for a 2000 m2 office: Dhaka-like mean 27 C with seasonal/diurnal/noise terms, weekday 08-18 occupancy with holidays, solar bell at 13:00, UA envelope plus latent ventilation. The released year has 8760 samples at 42.2 kW mean. Generation is seeded (42); any measured BMS CSV with identical columns replays the pipeline unchanged.")
pdf.sub("D. Load Forecaster")
pdf.p("Features are cyclical hour/day/month encodings, weekend/occupied flags, and lags 1/24/168 h. CoolingLoadForecaster wraps gradient boosting (default), random forest, and ridge with chronological 80/20 splits and TimeSeriesSplit cross-validation, reporting MAE, RMSE, CVRMSE, NMBE, and R2 with importances.")
pdf.sub("E. Controllers")
pdf.p("Baseline fixes SAT at 13 C with both 175-kW chillers committed and constant-volume fan (2% of peak). Reset schedules SAT 12-16 C by OAT with a VAV cube-law fan (2.5% coefficient) and a 2% COP uplift. Sequencing commits the fewest chillers above 15% PLR at equal split. SimpleMPC pre-cools at 60% capacity when 32 C enters the 4-h horizon. Critically, all strategies share the same part-load curve so only staging and reset effects are measured.")
pdf.sec("IV. Experimental Setup")
pdf.p("Windows laptop, Python 3.11, scikit-learn 1.9, pandas 3.0. Primary run is examples/run_demo.py (--days 60 --model gbm); full-year runs use scripts/train_forecaster.py and evaluate_controls.py; verification is pytest -q (5 tests). End-to-end runtime is under one minute with no GPU. Artifacts are results/metrics.json and results/demo.png.")
pdf.sec("V. Results")
pdf.sub("A. Forecasting (Q1)")
pdf.tbl(["Split", "MAE", "RMSE", "CVRMSE", "NMBE / R2", "G14"],
        [["60-day", "1.55 kW", "2.76 kW", "8.30%", "+2.29% / 0.9907", "PASS"],
         ["Full-year", "1.71 kW", "2.95 kW", "9.82%", "-1.57% / 0.9877", "PASS"]],
        [28, 24, 24, 24, 48, 22])
pdf.p("TABLE I: forecast accuracy against Guideline 14 hourly limits. Both splits pass with wide margin. Importances rank lag-168 h first (45.8%), then q_internal (18.4%), is_occupied (17.9%), T_out (8.1%), and occupancy_frac (7.0%), confirming that weekly repetition dominates instantaneous weather. Ridge trails GBM by 2-3 R2 points; random forest matches GBM within noise at roughly 5x training cost.")
pdf.sub("B. Control Savings (Q2)")
pdf.tbl(["Strategy", "60-day kWh", "Save", "Year kWh", "Save"],
        [["Baseline", "4291.1", "-", "191582.8", "-"],
         ["SAT reset", "3814.5", "11.11%", "164825.4", "13.97%"],
         ["Sequencing", "-", "-", "144655.4", "24.49%"]],
        [34, 34, 24, 44, 24])
pdf.p("TABLE II: energy and savings. SAT-reset savings of 11-14% agree with hot-humid VAV literature. Sequencing is larger because the baseline stages both chillers at about 12% mean PLR on a 350-kW plant while the optimizer typically runs one near 25%. Fig. 1 shows one-week load tracking and the corresponding peak shaving.")
demo = proj / "results" / "demo.png"
if demo.exists():
    pdf.sub("Fig. 1. Load forecast and power comparison (one-week slice).")
    pdf.image(str(demo), w=175); pdf.ln(2)
pdf.sub("C. Simulation Sanity")
pdf.p("The 2R2C loop at 34 C with 30 kW gains engages cooling after the first hour with COP inside [1.5, 5]. Psychrometric spot checks (20 C saturation near 2339 Pa) and metric identities (zero error gives CVRMSE = NMBE = 0) all pass.")
pdf.sec("VI. Discussion (Q3 and Limitations)")
pdf.p("Schedule and history outweigh weather: practitioners should log occupancy and retain at least three weeks of trends before commissioning MPC. SAT reset is the cheapest tonne of CO2 because it is a schedule change. Limitations include synthetic climate, proxy fan/COP coefficients (absolute kWh indicative; relative savings are the claim), no humidity, demand-charge, or PMV constraints, and a single seed. Publishing equations, seeds, and the swap-in CSV path mitigates these threats; field validation is the required next step.")
pdf.sec("VII. Conclusion")
pdf.p("A dependency-light, physics-informed pipeline clears ASHRAE Guideline 14 and demonstrates 11-14% savings from SAT reset and 24% from sequencing versus naive staging, reproducibly on a laptop. Future work adds measured-BMS validation, tariff- and comfort-aware MPC in CasADi, and automated fault detection as a companion study.")
pdf.sec("Acknowledgment")
pdf.p("The author thanks the NumPy, pandas, scikit-learn, and matplotlib communities for open scientific tooling.")
pdf.sec("References")
refs = ["[1] ASHRAE Handbook-Fundamentals, Ch. 1, 2021.",
"[2] ASHRAE Guideline 14-2014, Measurement of Energy, Demand, and Water Savings.",
"[3] ASHRAE Guideline 36-2024, High-Performance Sequences of Operation.",
"[4] J. E. Braun et al., Methods for supervisory control of building HVAC systems, ASHRAE Trans.",
"[5] F. Pedregosa et al., Scikit-learn: Machine learning in Python, JMLR, vol. 12, 2011.",
"[6] Y. Ma et al., Model predictive control for building energy systems: A survey, Appl. Energy."]
for r in refs:
    pdf.set_xy(pdf.l_margin, pdf.get_y())
    pdf.set_font("Times", "", 8.5)
    pdf.multi_cell(0, 5, r, new_x="LMARGIN", new_y="NEXT")
out = proj / "results" / "Conference_Paper_HVAC.pdf"
pdf.output(str(out))
print(f"Saved {out} ({out.stat().st_size/1024:.0f} KB)")
import shutil; shutil.copy(out, r"D:\Conference_Paper_HVAC.pdf")
print("Copied to D:\\Conference_Paper_HVAC.pdf")
