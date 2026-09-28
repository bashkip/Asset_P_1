"""Question 3: in-sample PCA (K = 1, 3) and restricted IPCA (K = 1, 3, 5) on the 25 portfolios; pricing errors and KPS R²."""

import numpy as np
import pandas as pd

from data_loader import OUTPUT, SORT_FACTOR, load
from factor_models import CHARACTERISTICS, instruments, ipca, pca
from metrics import error_summary, time_series_ols

OBSERVABLE = {"CAPM": ["Mkt-RF"], "3F": ["Mkt-RF", "SMB", SORT_FACTOR]}  # Q2 models, for comparison


def fit_pca(R, K):
    m = pca(R, K)
    B = m["B"]
    return {"fitted": m["f"] @ B.T, "predicted": np.tile(B @ m["lambda"], (len(R), 1)), "lambda": m["lambda"]}


def fit_ipca(Z, R, K):
    m = ipca(Z, R, K)
    beta = Z @ m["gamma"]  # T x N x K, conditional loadings
    return {"fitted": np.einsum("tnk,tk->tn", beta, m["f"]), "predicted": beta @ m["lambda"],
            "lambda": m["lambda"], "gamma": m["gamma"], "iterations": m["iterations"]}


def fit_observable(R, F):
    """Static betas without a constant (KPS, p. 30), lambda = factor means."""
    betas = time_series_ols(R, F, intercept=False)["betas"]
    return {"fitted": F @ betas.T, "predicted": np.tile(betas @ F.mean(axis=0), (len(R), 1))}


def in_sample(data: dict) -> dict:
    """Fit all Q3 models (plus CAPM and 3F) on the full sample; pricing errors per asset and fit statistics."""
    excess = data["excess"]
    R = excess.to_numpy()
    Z = instruments(data["chars"])
    fits = {
        "PCA1": fit_pca(R, 1), "PCA3": fit_pca(R, 3),
        "IPCA1": fit_ipca(Z, R, 1), "IPCA3": fit_ipca(Z, R, 3), "IPCA5": fit_ipca(Z, R, 5),
        **{name: fit_observable(R, data["factors"][cols].to_numpy()) for name, cols in OBSERVABLE.items()},
    }

    stats = {m: error_summary(R, R - fit["fitted"], R - fit["predicted"]) for m, fit in fits.items()}
    alphas = pd.DataFrame({m: s.pop("alpha") for m, s in stats.items()}, index=excess.columns)
    return {"fits": fits, "alphas": alphas, "summary": pd.DataFrame(stats), "Z": Z, "R": R}


def main():
    data = load()
    res = in_sample(data)
    fits, alphas, summary, Z, R = res["fits"], res["alphas"], res["summary"], res["Z"], res["R"]

    gammas = pd.concat({m: pd.DataFrame(fits[m]["gamma"], index=CHARACTERISTICS + ["constant"],
                                        columns=[f"f{k + 1}" for k in range(fits[m]["gamma"].shape[1])])
                        for m in ["IPCA1", "IPCA3", "IPCA5"]}, axis=1)
    lambdas = {m: fits[m]["lambda"] for m in ["PCA1", "PCA3", "IPCA1", "IPCA3", "IPCA5"]}

    OUTPUT.mkdir(exist_ok=True)
    alphas.round(4).to_csv(OUTPUT / "Q3_alphas.csv")
    summary.to_csv(OUTPUT / "Q3_summary.csv", float_format="%.4f")
    gammas.round(4).to_csv(OUTPUT / "Q3_ipca_gamma.csv")

    print(f"Sample {data['start']} to {data['end']}: T = {len(R)}, N = {R.shape[1]}, "
          f"L = {Z.shape[2]} ({', '.join(CHARACTERISTICS)}, constant; rank-transformed)\n")
    print("Pricing errors (% per month):")
    print(alphas.round(2).to_string(), "\n")
    print(summary.round(2).to_string(), "\n")
    print("IPCA Gamma_beta:")
    print(gammas.round(2).to_string(), "\n")
    for m, lam in lambdas.items():
        print(f"{m} lambda: {np.round(lam, 3)}" + (f"  ({fits[m]['iterations']} ALS iterations)" if "iterations" in fits[m] else ""))


if __name__ == "__main__":
    main()
