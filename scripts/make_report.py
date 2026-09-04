"""Generate research-grade PDF report."""
import json
from pathlib import Path
from fpdf import FPDF

proj = Path(r"D:\Python research project")
m = json.loads((proj / "results" / "metrics.json").read_text())
f = m["forecast"]

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "HVAC Energy Optimizer  |  Sabbir Hossain  |  2026", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")
    def h1(self, t):
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 9, t)
        self.ln(1)
    def h2(self, t):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 8, t)
        self.ln(1)
    def body(self, t):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, t)
        self.ln(1)

pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(True, 20)
pdf.add_page()
pdf.h1("Physics-Informed Machine Learning for HVAC Energy Optimization")
pdf.set_font("Helvetica", "", 11)
pdf.multi_cell(0, 6, "Author: Sabbir Hossain  |  Python Research Project  |  September 2026\n2000 sqm commercial building, Dhaka-like hot-humid climate (synthetic BMS data)")
pdf.ln(2)
pdf.h2("Abstract")
pdf.body("This study combines a 2R2C building thermal model and ASHRAE psychrometrics with a gradient-boosting cooling-load forecaster and supervisory control (supply-air-temperature reset, chiller sequencing, MPC pre-cooling). On a 60-day hourly test the forecaster reaches R2 0.99, CVRMSE 8.3% and NMBE 2.3%, passing ASHRAE Guideline 14 hourly limits (30% / 10%). SAT-reset control cuts HVAC electricity by 11.1% versus a fixed-setpoint baseline (full-year: 14.0%; sequencing: 24.5% vs all-chillers-on baseline). All code, data generator, tests and notebooks are kept locally in D:/Python research project.")
pdf.h2("1. Method")
pdf.body("Psychrometrics per ASHRAE Fundamentals (Tetens saturation pressure, Magnus dew-point, h = 1.006T + W(2501+1.86T)). Zone: 2R2C lumped model C_in dT_in/dt = (T_wall-T_in)/R_in + Q_int + Q_sol + Q_hvac. Chiller COP = COP_rated x f(PLR) x f(OAT) with f(PLR)=0.45+0.85 PLR-0.30 PLR^2. Forecaster: GradientBoostingRegressor on T_out, RH, occupancy, cyclical hour/dow/month and lags 1/24/168 h, chronological 80/20 split. Controls: (a) baseline fixed SAT 13 C all chillers on, (b) OAT-reset SAT 12-16 C with VAV fan cube law, (c) minimum-chiller sequencing, (d) look-ahead pre-cooling.")
pdf.h2("2. Results (main file: examples/run_demo.py)")
pdf.set_font("Helvetica", "B", 10.5)
pdf.cell(0, 7, f"Forecast:  MAE {f['mae']:.2f} kW   RMSE {f['rmse']:.2f} kW   CVRMSE {f['cvrmse_pct']:.2f}%   NMBE {f['nmbe_pct']:.2f}%   R2 {f['r2']:.4f}")
pdf.ln(7)
pdf.cell(0, 7, f"Energy (60-day test):  baseline {m['kwh_baseline']:.1f} kWh  ->  optimized {m['kwh_optimized']:.1f} kWh  =  {m['savings_pct']:.2f}% saved")
pdf.ln(9)
pdf.body("Top features: lag168h 45.8% (weekly repeat), q_internal 18.4%, is_occupied 17.9%, T_out 8.1%, occupancy_frac 7.0%. Load is schedule-dominated; weather is secondary. Full-year run: SAT-reset 13.97% and sequencing 24.49% savings. 5/5 pytest tests pass.")
demo = proj / "results" / "demo.png"
if demo.exists():
    pdf.h2("Figure 1 - Load forecast and power comparison (1-week slice)")
    pdf.image(str(demo), w=180)
    pdf.ln(2)
pdf.h2("3. What this means")
pdf.body("- Prediction off by only ~1.5 kW on a ~42 kW mean load: good enough for supervisory control.\n- Passes ASHRAE G14, so the result is citable in a paper.\n- 11% saving comes from raising supply-air temperature in mild hours (less chiller lift), at the cost of slightly more fan power.\n- Weekly history matters most: deploy with at least 2-3 weeks of BMS trend logging.")
pdf.h2("4. Reproduce on this laptop")
pdf.set_font("Courier", "", 9)
pdf.multi_cell(0, 5, 'C:/Users/hp/AppData/Local/Programs/Python/Python311/python.exe examples/run_demo.py --days 60 --model gbm\nC:/Users/hp/AppData/Local/Programs/Python/Python311/python.exe -m pytest -q')
pdf.ln(2)
pdf.h2("References")
pdf.body("1. ASHRAE Handbook Fundamentals (2021), Ch.1.  2. ASHRAE Guideline 14-2014.  3. Braun et al., supervisory control for buildings.  4. Pedregosa et al., Scikit-learn, JMLR 2011.")
out = proj / "results" / "HVAC_Energy_Optimizer_Report.pdf"
pdf.output(str(out))
print(f"Saved {out} ({out.stat().st_size/1024:.0f} KB)")
# easy copy at D: root too
import shutil
shutil.copy(out, r"D:\HVAC_Energy_Optimizer_Report.pdf")
print("Copied to D:\\HVAC_Energy_Optimizer_Report.pdf")
