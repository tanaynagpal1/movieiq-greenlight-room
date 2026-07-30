# Movie Revenue Analysis

A risk-intelligence console for film investment, built on `movies.csv` (2,000 films)
— or on any CSV you upload.

**Live app:** https://movieiq-greenlight-room.streamlit.app

---

## The finding that shapes this project

None of the four usable features — budget, popularity, runtime, vote average —
predict whether a film succeeds. A Random Forest trained on all four scores
**80.2% accuracy**, while simply guessing "success" every time scores **80.8%**.
Cross-validated ROC-AUC is **0.506** — a coin flip.

So instead of pretending to pick winners, this dashboard pivots to what the data
*can* answer: how much capital should be at risk, and across how many titles.

> The classifier cannot beat a coin weighted 80/20 — and it proves that live,
> in-app, before pivoting to sizing risk instead of predicting hits.

---

## What's inside

| Section | What it does |
|---|---|
| **Dashboard** | KPIs, EDA charts (budget vs revenue, correlation matrix, genre success rates), the Random Forest model with an honest baseline comparison, and a live predictor |
| **Upload Data** | Shows the active dataset, offers the cleaned data as a CSV download, and lets you run the whole dashboard on your own CSV instead |
| **Data Quality** | 12 automated data-health checks, computed live from the raw file, with a weighted health score |
| **Statistical Tests** | T-test (vote average) and chi-square (genre) against success, with an adjustable significance threshold and Bonferroni correction toggle |
| **Risk Simulator** | Monte Carlo break-even simulator for a single film, plus a slate-diversification builder showing why studios greenlight slates rather than single films |
| **Report** | A full written report — business problem, objective, stakeholders and methodology are fixed; every finding, chart, statistic and recommendation is recomputed from the active dataset. Exports as PDF or Markdown |
| **Conclusions** | Key insights and an honest reflection on the model's limitations |

Every sidebar filter (genre, minimum vote average) is shared across all analysis
sections — one filtered view, so no section can disagree with another.

### The report rewrites itself

Upload a different CSV and the Report section doesn't just swap the numbers — the
narrative adapts. If a model trained on your data actually finds signal, the
recommendations change from "do not use this for greenlight decisions" to
"validate before operational use." The α and budget sliders inside the report
recompute its statistics and risk figures live.

---

## Tech stack

- **Python** 3.13
- **Streamlit** 1.42.0 — app framework
- **Plotly** — interactive charts in the app
- **Matplotlib** — print-resolution chart rendering for the PDF export
- **fpdf2** — themed PDF generation
- **scikit-learn** — Random Forest classifier
- **SciPy** — t-test, chi-square, Kolmogorov–Smirnov tests
- **pandas / NumPy** — data handling and Monte Carlo simulation

## Running locally

```bash
git clone https://github.com/tanaynagpal1/movieiq-greenlight-room.git
cd movieiq-greenlight-room
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows PowerShell
python -m pip install -r requirements.txt
streamlit run MovieIQ.py
```

Then open `http://localhost:8501` in your browser.

## Project structure

```
movieiq-greenlight-room/
├─ MovieIQ.py                 # entry point, sidebar nav + filters + routing
├─ requirements.txt
├─ data/movies.csv            # default dataset, committed so the app is never empty
├─ src/
│  ├─ theme.py                # design system, CSS, KPI cards
│  ├─ loader.py               # loading + cleaning, for bundled or uploaded data
│  ├─ audit.py                # 12-check data health audit
│  ├─ charts.py               # Plotly figures for the app
│  ├─ mpl_charts.py           # Matplotlib figures for the PDF export
│  ├─ model.py                # Random Forest training + prediction
│  ├─ stats_lab.py            # t-test, chi-square, permutation logic
│  ├─ simulate.py             # Monte Carlo break-even + slate simulation
│  └─ pdf_report.py           # themed PDF builder
└─ sections/
   ├─ s0_pitch.py             # Dashboard
   ├─ s1_cutting_room.py      # Data Quality
   ├─ s2_statistical_tests.py # Statistical Tests
   ├─ s3_risk_simulator.py    # Risk Simulator
   ├─ s4_conclusions.py       # Conclusions
   ├─ s5_upload.py            # Upload Data
   └─ s6_report.py            # Report
```

## Reflection

If a studio asked whether their next film will succeed, the honest answer is the
base rate — and it would be the same answer for every film ever made. The
limitation is the data, not the algorithm: the variables that would plausibly
predict success (cast, release window, marketing spend, competing titles,
franchise status, critical reception) are absent from this file. Given more time,
the natural next step is joining real sources — TMDB and Box Office Mojo — to
obtain those missing predictors and re-running this analysis on real releases.