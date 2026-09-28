"""Question 4: out-of-sample evaluation with 240-month rolling windows for PCA (K = 1, 3), IPCA (K = 1, 3, 5),
the CAPM and the three-factor model.

Timing (our arrays): Z[s] is known at the start of month s and pairs with R[s]. The window for month t uses
rows t-239..t; the model is then evaluated on R[t+1] with instruments Z[t+1], which are not used in estimation
(Z_t and r_{t+1} in the assignment's notation).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_loader import OUTPUT, SORT_FACTOR, load
from factor_models import instruments, ipca, pca
from metrics import error_summary, time_series_ols
from Q3 import in_sample

WINDOW = 240
MODELS = ["PCA1", "PCA3", "IPCA1", "IPCA3", "IPCA5", "CAPM", "3F"]
OBSERVABLE = {"CAPM": ["Mkt-RF"], "3F": ["Mkt-RF", "SMB", SORT_FACTOR]}


def rolling_errors(R: np.ndarray, Z: np.ndarray, F: dict) -> dict:
    """Out-of-sample total-fit residuals eta_{t+1} and pricing errors alpha_{t+1} (each n_oos x N) per model."""
    T, N = R.shape
    eta = {m: [] for m in MODELS}
    alpha = {m: [] for m in MODELS}
    gamma_prev = {}

    for t in range(WINDOW - 1, T - 1):
        win = slice(t - WINDOW + 1, t + 1)
        r_next, z_next = R[t + 1], Z[t + 1]

        # PCA: steps 1, 3, 4, 5 -- B_t orthonormal, f_{t+1} = B_t' r_{t+1}
        for K in (1, 3):
            m = pca(R[win], K)
            B = m["B"]
            eta[f"PCA{K}"].append(r_next - B @ (B.T @ r_next))
            alpha[f"PCA{K}"].append(r_next - B @ m["lambda"])

        # IPCA: steps 2-5 -- predicted loadings B_{t+1} = Z_{t+1} Gamma_t, f_{t+1} by cross-sectional regression
        for K in (1, 3, 5):
            m = ipca(Z[win], R[win], K, gamma0=gamma_prev.get(K))  # warm start from the previous window
            gamma_prev[K] = m["gamma"]
            B = z_next @ m["gamma"]
            f_next = np.linalg.solve(B.T @ B, B.T @ r_next)
            eta[f"IPCA{K}"].append(r_next - B @ f_next)
            alpha[f"IPCA{K}"].append(r_next - B @ m["lambda"])

        # Observable factors: betas from the window (no constant, as in Q2/Q3), lambda_t = window factor means
        for name, f in F.items():
            B = time_series_ols(R[win], f[win], intercept=False)["betas"]
            eta[name].append(r_next - B @ f[t + 1])
            alpha[name].append(r_next - B @ f[win].mean(axis=0))

    return {m: (np.array(eta[m]), np.array(alpha[m])) for m in MODELS}


def plot_comparison(is_summary: pd.DataFrame, oos_summary: pd.DataFrame, path):
    blue, orange = "#2a78d6", "#eb6834"
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    x = np.arange(len(MODELS))
    for ax, row, title in [(axes[0], "Total R2 (%)", "Total R²"), (axes[1], "RMS alpha (%)", "RMS pricing error")]:
        for offset, (summary, label, color) in zip((-0.2, 0.2), [(is_summary, "In-sample (Q3)", blue),
                                                                   (oos_summary, "Out-of-sample (Q4)", orange)]):
            ax.bar(x + offset, summary.loc[row, MODELS], width=0.38, color=color, label=label)
        ax.set_xticks(x, MODELS, fontsize=9)
        ax.set_title(f"{title} (%)", fontsize=10)
        ax.grid(axis="y", color="#e4e3df", lw=0.6)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylim(50, 100)
    axes[0].legend(fontsize=8, frameon=False, loc="upper left")
    fig.suptitle("In-sample vs out-of-sample fit, 25 Size × ST-reversal portfolios", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    data = load()
    excess = data["excess"]
    R = excess.to_numpy()
    Z = instruments(data["chars"])
    F = {name: data["factors"][cols].to_numpy() for name, cols in OBSERVABLE.items()}

    errors = rolling_errors(R, Z, F)
    R_oos = R[WINDOW:]
    oos_months = excess.index[WINDOW:]

    stats = {m: error_summary(R_oos, eta, alpha) for m, (eta, alpha) in errors.items()}
    mean_eta = pd.DataFrame({m: errors[m][0].mean(axis=0) for m in MODELS}, index=excess.columns)
    mean_alpha = pd.DataFrame({m: stats[m].pop("alpha") for m in MODELS}, index=excess.columns)
    summary = pd.DataFrame(stats)[MODELS]
    summary.loc["Mean |eta| (%)"] = mean_eta.abs().mean()

    # In-sample comparison on the same (out-of-sample) months, and on the full sample as in Q3
    is_full = in_sample(data)["summary"][MODELS]

    OUTPUT.mkdir(exist_ok=True)
    table = pd.concat({"mean eta": mean_eta, "mean alpha": mean_alpha}, axis=1)
    table.round(4).to_csv(OUTPUT / "Q4_errors.csv")
    summary.to_csv(OUTPUT / "Q4_summary.csv", float_format="%.4f")
    plot_comparison(is_full, summary, OUTPUT / "Q4_insample_vs_oos.png")

    print(f"Rolling window {WINDOW} months; out-of-sample {oos_months[0]} to {oos_months[-1]} "
          f"({len(oos_months)} months)\n")
    print("Average eta (total-fit residual), % per month:")
    print(mean_eta.round(2).to_string(), "\n")
    print("Average alpha (predicted pricing error), % per month:")
    print(mean_alpha.round(2).to_string(), "\n")
    print("Out-of-sample summary:")
    print(summary.round(2).to_string(), "\n")
    print("In-sample (Q3, full sample):")
    print(is_full.round(2).to_string())


if __name__ == "__main__":
    main()
