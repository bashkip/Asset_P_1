# Asset Pricing assignment (FEM21003): IPCA vs PCA vs observable factors

Test assets: 25 portfolios double-sorted on size and short-term reversal (Kenneth French data library), sample 1972-03 to 2025-04 (638 months). The period is taken from the team member with the lowest student number, see `code/data_loader.py`.

## Structure

| Path | Content |
|---|---|
| `data/` | Raw inputs: `25_Portfolios_ME_Prior_1_0.csv`, `F-F_Research_Data_5_Factors_2x3.csv`, `F-F_ST_Reversal_Factor.csv` (monthly, from French's library), `start_end_fem21003.xlsx` (sample periods) |
| `code/data_loader.py` | Sample period, parsing of the French CSVs, excess returns, factors, characteristics |
| `code/metrics.py` | Time-series OLS, GRS test, max Sharpe ratio, Kelly-Pruitt-Su total / predictive R² |
| `code/factor_models.py` | Rank-transformed instruments, static PCA, restricted IPCA (ALS) |
| `code/Q1.py` … `code/Q4.py` | One script per question |
| `code/main.py` | Runs Q1–Q4 in order |
| `code/ipca_crosscheck.py` | Optional check of our IPCA against Pruitt's `ipca` package (needs `pip install ipca`) |
| `output/` | Figures (`.png`), tables (`.csv`) and a results summary per question (`Q{n}_z.md`) |
| `sort_choice.md` | Why we chose the size × short-term reversal sort |

## Running

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python code/main.py      # or a single question, e.g. .venv/bin/python code/Q3.py
```

Q4 re-estimates every model on 398 rolling windows and takes about 2 minutes. The other questions take a few seconds.
