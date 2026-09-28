"""Question 2: GRS tests of the CAPM and the three-factor model on the 25 portfolios, alphas, KPS R² and Sharpe ratios."""

import numpy as np
import pandas as pd

from data_loader import OUTPUT, SORT_FACTOR, load
from metrics import grs_test, max_sharpe, predictive_r2, time_series_ols, total_r2

MODELS = {"CAPM": ["Mkt-RF"], "3F": ["Mkt-RF", "SMB", SORT_FACTOR]}


def evaluate(excess: pd.DataFrame, factors: pd.DataFrame) -> dict:
    """Alphas with standard errors, GRS test, and KPS total / predictive R² for one factor model.

    Following KPS (2019, p. 30) the R² use betas from time-series regressions without a constant;
    the fitted return is beta_i' f_t (total R²) or beta_i' lambda with lambda the factor means (predictive R²).
    """
    r, f = excess.to_numpy(), factors.to_numpy()
    reg = time_series_ols(r, f)
    betas = time_series_ols(r, f, intercept=False)["betas"]
    return {
        "alpha": reg["alpha"],
        "alpha_se": reg["alpha_se"],
        "grs": grs_test(r, f),
        "total_r2": total_r2(r, f @ betas.T),
        "pred_r2": predictive_r2(r, betas @ f.mean(axis=0)),
    }


def alpha_grid(alpha: np.ndarray, se: np.ndarray) -> pd.DataFrame:
    """5 x 5 grid (size quintile x prior-return quintile) of 'alpha (se)' strings."""
    cells = [f"{a:.2f} ({s:.2f})" for a, s in zip(alpha, se)]
    return pd.DataFrame(np.array(cells).reshape(5, 5), index=[f"ME{i}" for i in range(1, 6)],
                        columns=["Lo PRIOR", "PRIOR2", "PRIOR3", "PRIOR4", "Hi PRIOR"])


def main():
    data = load()
    excess, factors = data["excess"], data["factors"]
    T, N = excess.shape
    results = {name: evaluate(excess, factors[cols]) for name, cols in MODELS.items()}

    # Table of alphas and standard errors (long format)
    table = pd.DataFrame({f"{m} {k}": results[m][key] for m in MODELS
                          for k, key in [("alpha", "alpha"), ("se", "alpha_se")]}, index=excess.columns)
    for m in MODELS:
        table[f"{m} t"] = table[f"{m} alpha"] / table[f"{m} se"]
    OUTPUT.mkdir(exist_ok=True)
    table.round(2).to_csv(OUTPUT / "Q2_alphas.csv")

    # Model-level summary: GRS, R², Sharpe ratios
    summary = pd.DataFrame({m: {
        "GRS": res["grs"]["stat"],
        "p-value": res["grs"]["pvalue"],
        "5% critical value": res["grs"]["crit_5"],
        "Mean |alpha| (%)": np.abs(res["alpha"]).mean(),
        "# |t| > 1.96": int((np.abs(res["alpha"] / res["alpha_se"]) > 1.96).sum()),
        "Total R2 (%)": 100 * res["total_r2"],
        "Predictive R2 (%)": 100 * res["pred_r2"],
        "SR factors (monthly)": res["grs"]["sr_factors"],
        "SR factors + 25 portfolios (monthly)": res["grs"]["sr_all"],
        # Largest ex-post Sharpe ratio of factors + test assets that the GRS test would not reject at 5%
        "SR not rejected at 5% (monthly)": np.sqrt((1 + res["grs"]["sr_factors"] ** 2)
                                                   * (1 + res["grs"]["crit_5"] * N / res["grs"]["df"][1]) - 1),
    } for m, res in results.items()})
    summary.to_csv(OUTPUT / "Q2_summary.csv", float_format="%.4f")

    sr_mkt = max_sharpe(factors[["Mkt-RF"]].to_numpy())
    sr_3f = max_sharpe(factors.to_numpy())
    print(f"Sample {data['start']} to {data['end']}: T = {T}, N = {N}\n")
    for m in MODELS:
        print(f"{m} alphas, % per month (OLS standard errors):")
        print(alpha_grid(results[m]["alpha"], results[m]["alpha_se"]).to_string(), "\n")
    print(summary.round(4).to_string())
    print(f"\nSharpe ratio market: {sr_mkt:.3f} monthly ({sr_mkt * np.sqrt(12):.2f} annual)")
    print(f"Sharpe ratio 3-factor tangency: {sr_3f:.3f} monthly ({sr_3f * np.sqrt(12):.2f} annual)")


if __name__ == "__main__":
    main()
