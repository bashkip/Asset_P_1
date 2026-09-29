"""Question 2: GRS tests of the CAPM and the three-factor model on the 25 portfolios, alphas, KPS R² and Sharpe ratios."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch

from data_loader import OUTPUT, SORT_FACTOR, load
from metrics import grs_test, max_sharpe, predictive_r2, time_series_ols, total_r2

MODELS = {"CAPM": ["Mkt-RF"], "3F": ["Mkt-RF", "SMB", SORT_FACTOR]}
ACF_LAGS = 12
DIAG_LAGS = 6  # lags of the Ljung-Box and ARCH LM residual diagnostics


def evaluate(excess: pd.DataFrame, factors: pd.DataFrame) -> dict:
    """Alphas with Newey-West (and OLS) standard errors, GRS test, and KPS total / predictive R² for one factor model.

    Following KPS (2019, p. 30) the R² use betas from time-series regressions without a constant;
    the fitted return is beta_i' f_t (total R²) or beta_i' lambda with lambda the factor means (predictive R²).
    """
    r, f = excess.to_numpy(), factors.to_numpy()
    reg = time_series_ols(r, f)
    betas = time_series_ols(r, f, intercept=False)["betas"]
    return {
        "resid": reg["resid"],
        "alpha": reg["alpha"],
        "alpha_se": reg["alpha_se"],
        "alpha_se_ols": reg["alpha_se_ols"],
        "hac_lags": reg["hac_lags"],
        "grs": grs_test(r, f),
        "total_r2": total_r2(r, f @ betas.T),
        "pred_r2": predictive_r2(r, betas @ f.mean(axis=0)),
    }


def alpha_grid(alpha: np.ndarray, se: np.ndarray) -> pd.DataFrame:
    """5 x 5 grid (size quintile x prior-return quintile) of 'alpha (se)' strings."""
    cells = [f"{a:.2f} ({s:.2f})" for a, s in zip(alpha, se)]
    return pd.DataFrame(np.array(cells).reshape(5, 5), index=[f"ME{i}" for i in range(1, 6)],
                        columns=["Lo PRIOR", "PRIOR2", "PRIOR3", "PRIOR4", "Hi PRIOR"])


def autocorrelations(resid: np.ndarray, lags: int = ACF_LAGS) -> np.ndarray:
    """Sample autocorrelations at lags 1..`lags` of each residual column (lags x N)."""
    e = resid - resid.mean(axis=0)
    return np.array([(e[k:] * e[:-k]).sum(axis=0) for k in range(1, lags + 1)]) / (e**2).sum(axis=0)


def residual_diagnostics(resid: np.ndarray) -> dict:
    """Per model: number of portfolios where Ljung-Box(6) or ARCH(6) LM rejects at 5%, mean |lag-1 autocorrelation|."""
    lb = [acorr_ljungbox(e, lags=[DIAG_LAGS])["lb_pvalue"].iloc[0] for e in resid.T]
    arch = [het_arch(e, nlags=DIAG_LAGS, result_object=False)[1] for e in resid.T]
    return {
        f"# Ljung-Box({DIAG_LAGS}) rejects at 5%": int((np.array(lb) < 0.05).sum()),
        f"# ARCH({DIAG_LAGS}) LM rejects at 5%": int((np.array(arch) < 0.05).sum()),
        "Mean |lag-1 autocorrelation|": np.abs(autocorrelations(resid, 1)[0]).mean(),
    }


def plot_residuals(resid: np.ndarray, dates: pd.Index, names: pd.Index, model: str, path):
    """Two 5 x 5 grids (size quintile x prior-return quintile) of time-series regression residuals, to judge whether
    HAC standard errors are needed: residuals over time (heteroskedasticity, volatility clustering) and their
    autocorrelations with +/- 1.96 / sqrt(T) bands (serial correlation)."""
    blue, orange, grey = "#2a78d6", "#eb6834", "#8a8984"
    T = len(resid)
    times = dates.to_timestamp() if isinstance(dates, pd.PeriodIndex) else dates

    fig, axes = plt.subplots(5, 5, figsize=(12, 9), sharex=True, sharey=True)
    for ax, e, name in zip(axes.flat, resid.T, names):
        ax.plot(times, e, color=blue, lw=0.5)
        ax.axhline(0, color=grey, lw=0.6)
        ax.set_title(name, fontsize=7)
        ax.tick_params(labelsize=6)
        ax.spines[["top", "right"]].set_visible(False)
    fig.supylabel("Residual (% per month)", fontsize=9)
    fig.suptitle(f"{model} time-series regression residuals", fontsize=11)
    fig.tight_layout()
    fig.savefig(path.with_name(f"{path.name}_{model}_resid.png"), dpi=200)
    plt.close(fig)

    acf = autocorrelations(resid)
    band = 1.96 / np.sqrt(T)
    lags = np.arange(1, ACF_LAGS + 1)
    fig, axes = plt.subplots(5, 5, figsize=(12, 9), sharex=True, sharey=True)
    for ax, rho, name in zip(axes.flat, acf.T, names):
        ax.bar(lags, rho, color=np.where(np.abs(rho) > band, orange, blue), width=0.7)
        ax.axhspan(-band, band, color="#e4e3df", zorder=0)
        ax.axhline(0, color=grey, lw=0.6)
        ax.set_title(name, fontsize=7)
        ax.tick_params(labelsize=6)
        ax.spines[["top", "right"]].set_visible(False)
    fig.supxlabel("Lag (months)", fontsize=9)
    fig.supylabel("Autocorrelation", fontsize=9)
    fig.suptitle(f"{model} residual autocorrelations (shaded: ±1.96/√T, orange: outside band)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path.with_name(f"{path.name}_{model}_resid_acf.png"), dpi=200)
    plt.close(fig)


def main():
    data = load()
    excess, factors = data["excess"], data["factors"]
    T, N = excess.shape
    results = {name: evaluate(excess, factors[cols]) for name, cols in MODELS.items()}

    # Table of alphas, Newey-West and OLS standard errors, HAC t-statistics (long format)
    table = pd.DataFrame(index=excess.columns)
    for m in MODELS:
        table[f"{m} alpha"] = results[m]["alpha"]
        table[f"{m} se"] = results[m]["alpha_se"]
        table[f"{m} se_ols"] = results[m]["alpha_se_ols"]
        table[f"{m} t"] = table[f"{m} alpha"] / table[f"{m} se"]
    OUTPUT.mkdir(exist_ok=True)
    table.round(2).to_csv(OUTPUT / "Q2_alphas.csv")
    for m in MODELS:
        plot_residuals(results[m]["resid"], excess.index, excess.columns, m, OUTPUT / "Q2")

    # Model-level summary: GRS, R², Sharpe ratios
    summary = pd.DataFrame({m: {
        "GRS": res["grs"]["stat"],
        "p-value": res["grs"]["pvalue"],
        "5% critical value": res["grs"]["crit_5"],
        "Mean |alpha| (%)": np.abs(res["alpha"]).mean(),
        "# |t| > 1.96 (HAC)": int((np.abs(res["alpha"] / res["alpha_se"]) > 1.96).sum()),
        "# |t| > 1.96 (OLS se)": int((np.abs(res["alpha"] / res["alpha_se_ols"]) > 1.96).sum()),
        "HAC lags": res["hac_lags"],
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
        print(f"{m} alphas, % per month (Newey-West standard errors, {results[m]['hac_lags']} lags):")
        print(alpha_grid(results[m]["alpha"], results[m]["alpha_se"]).to_string(), "\n")
    print(summary.round(4).to_string())
    print(f"\nResidual diagnostics ({N} portfolios):")
    print(pd.DataFrame({m: residual_diagnostics(results[m]["resid"]) for m in MODELS}).round(3).to_string())
    print(f"\nSharpe ratio market: {sr_mkt:.3f} monthly ({sr_mkt * np.sqrt(12):.2f} annual)")
    print(f"Sharpe ratio 3-factor tangency: {sr_3f:.3f} monthly ({sr_3f * np.sqrt(12):.2f} annual)")


if __name__ == "__main__":
    main()
