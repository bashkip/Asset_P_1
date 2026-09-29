"""Estimation and evaluation helpers shared by several questions: time-series regressions, GRS test, KPS R²."""

import numpy as np
from scipy import stats


def newey_west_lags(T: int) -> int:
    """Rule-of-thumb Newey-West truncation lag, floor(4 (T/100)^(2/9))."""
    return int(np.floor(4 * (T / 100) ** (2 / 9)))


def time_series_ols(excess: np.ndarray, factors: np.ndarray, intercept: bool = True,
                    hac_lags: int | None = None) -> dict:
    """Regress each column of the T x N excess-return panel on the T x K factors.

    Returns alphas (N), betas (N x K) and residuals (T x N). With an intercept it also returns Newey-West HAC
    standard errors of the alphas ("alpha_se"), homoskedastic OLS ones ("alpha_se_ols") and the HAC lag length
    ("hac_lags", default `newey_west_lags(T)`). HAC covariance: (X'X)^-1 S (X'X)^-1 with u_t = x_t e_t and
    S = sum_t u_t u_t' + sum_{j=1}^{L} (1 - j/(L+1)) (Gamma_j + Gamma_j'), Gamma_j = sum_{t>j} u_t u_{t-j}'.
    """
    T = excess.shape[0]
    X = np.column_stack([np.ones(T), factors]) if intercept else factors
    coef, *_ = np.linalg.lstsq(X, excess, rcond=None)
    resid = excess - X @ coef
    out = {"betas": (coef[1:] if intercept else coef).T, "resid": resid}
    if intercept:
        L = newey_west_lags(T) if hac_lags is None else hac_lags
        XtX_inv = np.linalg.inv(X.T @ X)
        U = X[:, :, None] * resid[:, None, :]  # T x p x N
        S = np.einsum("tpn,tqn->npq", U, U)
        for j in range(1, L + 1):
            G = np.einsum("tpn,tqn->npq", U[j:], U[:-j])
            S += (1 - j / (L + 1)) * (G + G.transpose(0, 2, 1))
        s2 = (resid**2).sum(axis=0) / (T - X.shape[1])
        out["alpha"] = coef[0]
        out["alpha_se"] = np.sqrt((XtX_inv @ S @ XtX_inv)[:, 0, 0])
        out["alpha_se_ols"] = np.sqrt(s2 * XtX_inv[0, 0])
        out["hac_lags"] = L
    return out


def max_sharpe(excess: np.ndarray) -> float:
    """Maximum (tangency) Sharpe ratio of a set of excess returns, using ML (divide-by-T) moments."""
    mu = excess.mean(axis=0)
    cov = np.atleast_2d(np.cov(excess, rowvar=False, bias=True))
    return float(np.sqrt(mu @ np.linalg.solve(cov, mu)))


def grs_test(excess: np.ndarray, factors: np.ndarray) -> dict:
    """Gibbons-Ross-Shanken test of H0: all alphas are zero, with ML estimates of the covariance matrices.

    GRS = (T-N-K)/N * a' S^-1 a / (1 + SR_f^2) ~ F(N, T-N-K), which equals
    (T-N-K)/N * (SR_all^2 - SR_f^2) / (1 + SR_f^2), where SR_all is the max Sharpe ratio of factors + test assets.
    """
    T, N = excess.shape
    K = factors.shape[1]
    reg = time_series_ols(excess, factors)
    sigma = reg["resid"].T @ reg["resid"] / T
    sr_f = max_sharpe(factors)
    stat = (T - N - K) / N * reg["alpha"] @ np.linalg.solve(sigma, reg["alpha"]) / (1 + sr_f**2)
    return {
        "stat": stat,
        "pvalue": stats.f.sf(stat, N, T - N - K),
        "crit_5": stats.f.ppf(0.95, N, T - N - K),
        "sr_factors": sr_f,
        "sr_all": max_sharpe(np.column_stack([factors, excess])),
        "df": (N, T - N - K),
    }


def total_r2(returns: np.ndarray, fitted: np.ndarray) -> float:
    """Kelly, Pruitt and Su (2019) total R²: 1 - sum of squared errors / uncentered sum of squared returns."""
    return 1 - ((returns - fitted) ** 2).sum() / (returns**2).sum()


def predictive_r2(returns: np.ndarray, predicted: np.ndarray) -> float:
    """KPS predictive R²: as total R², but the fit uses expected returns (loadings times factor risk premia)."""
    return total_r2(returns, np.broadcast_to(predicted, returns.shape))


def error_summary(returns: np.ndarray, resid: np.ndarray, pricing_errors: np.ndarray) -> dict:
    """Fit statistics from total-fit residuals (r - beta f) and pricing errors (r - beta lambda), both T x N.

    Pricing error of asset i = time average of its pricing-error series; R² as in KPS (uncentered denominator).
    """
    alpha = pricing_errors.mean(axis=0)
    return {
        "alpha": alpha,
        "Total R2 (%)": 100 * total_r2(returns, returns - resid),
        "Predictive R2 (%)": 100 * predictive_r2(returns, returns - pricing_errors),
        "Mean |alpha| (%)": np.abs(alpha).mean(),
        "RMS alpha (%)": np.sqrt((alpha**2).mean()),
        "Max |alpha| (%)": np.abs(alpha).max(),
    }


if __name__ == "__main__":
    # Check the Newey-West alpha standard errors against statsmodels on a random panel
    import statsmodels.api as sm

    rng = np.random.default_rng(0)
    T, N, K = 500, 5, 3
    f = rng.standard_normal((T, K))
    r = f @ rng.standard_normal((K, N)) + rng.standard_normal((T, N))
    r[1:] += 0.5 * r[:-1]  # add serial correlation
    reg = time_series_ols(r, f)
    L = reg["hac_lags"]
    for i in range(N):
        bse = sm.OLS(r[:, i], sm.add_constant(f)).fit(cov_type="HAC", cov_kwds={"maxlags": L, "use_correction": False}).bse[0]
        assert abs(reg["alpha_se"][i] - bse) < 1e-10, (i, reg["alpha_se"][i], bse)
    print(f"Newey-West alpha SEs match statsmodels (T = {T}, L = {L}, N = {N})")
