import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_loader import OUTPUT, SORT_FACTOR, load

RF = 0.25  # fixed risk-free rate, % per month (gross return 1.0025)


def moments(excess: pd.DataFrame):
    """Excess mean vector and (sample) variance matrix of a T x N panel of excess returns."""
    return excess.mean().to_numpy(), excess.cov().to_numpy()


def frontier_risky(mu: np.ndarray, sigma: np.ndarray, targets: np.ndarray) -> np.ndarray:
    """Volatility of the minimum-variance portfolio of risky assets for each target mean return."""
    inv = np.linalg.inv(sigma)
    ones = np.ones(len(mu))
    a, b, c = ones @ inv @ ones, ones @ inv @ mu, mu @ inv @ mu
    return np.sqrt((a * targets**2 - 2 * b * targets + c) / (a * c - b**2))


def tangency(mu_e: np.ndarray, sigma: np.ndarray, rf: float = RF) -> dict:
    """Tangency portfolio: weights summing to one, mean, volatility and Sharpe ratio (monthly, in %)."""
    x = np.linalg.solve(sigma, mu_e)
    w = x / x.sum()
    return {
        "weights": w,
        "mean": rf + w @ mu_e,
        "vol": np.sqrt(w @ sigma @ w),
        "sharpe": np.sqrt(mu_e @ x),  # max Sharpe ratio; equals (mean - rf) / vol when x.sum() > 0
    }


def plot_frontiers(mu_p, sigma_p, mu_f, sigma_f, tan_p, tan_f, asset_names, factor_names, path):
    blue, orange, aqua, grey = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
    fig, ax = plt.subplots(figsize=(7.5, 5.2))

    vol_max = 1.15 * max(tan_p["vol"], np.sqrt(np.diag(sigma_p)).max(), np.sqrt(np.diag(sigma_f)).max())
    vols = np.linspace(0, vol_max, 400)

    # Frontier of the 25 portfolios without the riskless asset (efficient branch solid, inefficient dashed)
    ones = np.ones(len(mu_p))
    inv = np.linalg.inv(sigma_p)
    m_gmv = (ones @ inv @ (mu_p + RF)) / (ones @ inv @ ones)
    upper = np.linspace(m_gmv, RF + tan_p["sharpe"] * vol_max, 400)
    lower = np.linspace(m_gmv - (upper[-1] - m_gmv), m_gmv, 400)
    ax.plot(frontier_risky(mu_p + RF, sigma_p, upper), upper, color=blue, lw=2,
            label="25 portfolios, risky assets only")
    ax.plot(frontier_risky(mu_p + RF, sigma_p, lower), lower, color=blue, lw=1, ls="--")

    # Capital market lines: riskless asset + 25 portfolios, riskless asset + 3 factors
    ax.plot(vols, RF + tan_p["sharpe"] * vols, color=orange, lw=2,
            label=f"25 portfolios + riskless asset (SR = {tan_p['sharpe']:.2f})")
    ax.plot(vols, RF + tan_f["sharpe"] * vols, color=aqua, lw=2,
            label=f"Mkt-RF, SMB, {SORT_FACTOR} + riskless asset (SR = {tan_f['sharpe']:.2f})")

    # Individual assets and factors, tangency portfolios, riskless asset
    ax.scatter(np.sqrt(np.diag(sigma_p)), mu_p + RF, s=18, color=grey, zorder=3, label="Individual portfolios")
    ax.scatter(np.sqrt(np.diag(sigma_f)), mu_f + RF, s=40, marker="D", color=aqua, edgecolor="white", linewidth=1,
               zorder=4, label="Individual factors")
    for name, m, v in zip(factor_names, mu_f + RF, np.sqrt(np.diag(sigma_f))):
        ax.annotate(name, (v, m), textcoords="offset points", xytext=(4, -12), fontsize=8, color="#52514e")
    for tan, color, name in [(tan_p, orange, "Tangency (25 portfolios)"), (tan_f, aqua, "Tangency (factors)")]:
        ax.scatter(tan["vol"], tan["mean"], s=110, marker="*", color=color, edgecolor="white", linewidth=1,
                   zorder=5)
        ax.annotate(name, (tan["vol"], tan["mean"]), textcoords="offset points", xytext=(-6, 8), ha="right",
                    fontsize=8, color="#52514e")
    ax.scatter(0, RF, s=30, color="#0b0b0b", zorder=5)
    ax.annotate(f"$R_f$ = {RF:.2f}%", (0, RF), textcoords="offset points", xytext=(6, -12), fontsize=8)

    ax.set_xlim(0, vol_max)
    ax.set_ylim(-0.5, upper[-1])  # the inefficient branch is only partly shown
    ax.set_xlabel("Volatility (% per month)")
    ax.set_ylabel("Expected return (% per month)")
    ax.set_title("Mean-variance frontiers, 25 Size × ST-reversal portfolios vs. factors", fontsize=11)
    ax.grid(color="#e4e3df", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.axhline(0, color="#b4b2a9", lw=0.8)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".png"), dpi=200)
    plt.close(fig)


def main():
    data = load()
    excess, factors = data["excess"], data["factors"]
    mu_p, sigma_p = moments(excess)
    mu_f, sigma_f = moments(factors)
    tan_p, tan_f = tangency(mu_p, sigma_p), tangency(mu_f, sigma_f)

    OUTPUT.mkdir(exist_ok=True)
    plot_frontiers(mu_p, sigma_p, mu_f, sigma_f, tan_p, tan_f, excess.columns, factors.columns,
                   OUTPUT / "Q1_frontier")

    rows = {"Tangency, 25 portfolios": tan_p, "Tangency, 3 factors": tan_f}
    for name, m, v in zip(factors.columns, mu_f, np.sqrt(np.diag(sigma_f))):
        rows[name] = {"mean": RF + m, "vol": v, "sharpe": m / v}
    table = pd.DataFrame({k: {"E[R] (%)": r["mean"], "Vol (%)": r["vol"], "Sharpe (monthly)": r["sharpe"],
                              "Sharpe (annual)": r["sharpe"] * np.sqrt(12)} for k, r in rows.items()}).T
    table.round(2).to_csv(OUTPUT / "Q1_tangency.csv")

    weights_f = pd.Series(tan_f["weights"], index=factors.columns, name="weight")
    weights_p = pd.Series(tan_p["weights"], index=excess.columns, name="weight")
    weights_p.round(4).to_csv(OUTPUT / "Q1_tangency_weights_portfolios.csv")

    print(f"Sample {data['start']} to {data['end']} ({len(excess)} months), fixed Rf = {RF}% per month\n")
    print(table.round(2))
    print("\nFactor tangency weights:")
    print(weights_f.round(3))
    print("\n25-portfolio tangency weights (rows: size quintile, columns: prior-return quintile):")
    print(pd.DataFrame(tan_p["weights"].reshape(5, 5), index=[f"ME{i}" for i in range(1, 6)],
                       columns=[f"PRIOR{j}" for j in range(1, 6)]).round(2))
    print(f"\nHighest individual-portfolio Sharpe ratio: "
          f"{(mu_p / np.sqrt(np.diag(sigma_p))).max():.2f} ({excess.columns[np.argmax(mu_p / np.sqrt(np.diag(sigma_p)))]})")


if __name__ == "__main__":
    main()
