"""Latent factor models shared by Q3 and Q4: instruments, static PCA and restricted IPCA (Gamma_alpha = 0).

Notation follows Kelly, Pruitt and Su (2019): r_{t+1} = Z_t Gamma_beta f_{t+1} + e_{t+1}. In our data, row t of a
characteristic is known at the start of month t and row t of the returns is realised at its end, so Z[t] pairs
with R[t] in all arrays below.
"""

import numpy as np

CHARACTERISTICS = ["size", "prior_vw", "mom", "ltrev", "vol"]  # prior_ew dropped: 0.998 correlated with prior_vw


def instruments(chars: dict, names: list = CHARACTERISTICS) -> np.ndarray:
    """T x N x L instrument array: per month, cross-sectional rank / N - 0.5 of each characteristic (KPS, p. 24),
    plus a constant as the last instrument (KPS, p. 8)."""
    ranked = [chars[n].rank(axis=1).div(chars[n].shape[1]).sub(0.5).to_numpy() for n in names]
    T, N = ranked[0].shape
    return np.stack(ranked + [np.ones((T, N))], axis=2)


def _normalize(gamma: np.ndarray, f: np.ndarray):
    """Impose KPS (p. 14) identification: Gamma'Gamma = I, f'f diagonal with descending entries, mean f >= 0."""
    chol = np.linalg.cholesky(gamma.T @ gamma).T  # Gamma'Gamma = chol' chol
    gamma, f = gamma @ np.linalg.inv(chol), f @ chol.T
    eigval, eigvec = np.linalg.eigh(f.T @ f)
    order = np.argsort(eigval)[::-1]
    gamma, f = gamma @ eigvec[:, order], f @ eigvec[:, order]
    sign = np.where(f.mean(axis=0) < 0, -1.0, 1.0)
    return gamma * sign, f * sign


def ipca_factors(Z: np.ndarray, R: np.ndarray, gamma: np.ndarray) -> np.ndarray:
    """First-order condition (6): f_t = (Gamma' Z_t' Z_t Gamma)^-1 Gamma' Z_t' r_t for every t (T x K)."""
    beta = Z @ gamma  # T x N x K
    return np.linalg.solve(np.einsum("tnk,tnj->tkj", beta, beta), np.einsum("tnk,tn->tk", beta, R)[..., None])[..., 0]


def ipca(Z: np.ndarray, R: np.ndarray, K: int, tol: float = 1e-6, max_iter: int = 10_000,
         gamma0: np.ndarray | None = None) -> dict:
    """Restricted IPCA by alternating least squares (KPS, Appendix A).

    Initial guess: leading K eigenvectors of the managed-portfolio second moment X'X, with x_t = Z_t' r_t / N
    (or `gamma0`, e.g. the previous window's estimate). Iterates (6) and (7) until the largest absolute change in
    any element of Gamma or f is below `tol`.
    """
    T, N, L = Z.shape
    if gamma0 is None:
        X = np.einsum("tnl,tn->tl", Z, R) / N
        eigval, eigvec = np.linalg.eigh(X.T @ X)
        gamma0 = eigvec[:, np.argsort(eigval)[::-1][:K]]
    gamma, f = _normalize(gamma0, ipca_factors(Z, R, gamma0))

    for iteration in range(1, max_iter + 1):
        # (7): pooled regression of r_it on kron(z_it, f_t); coefficient (l, k) is Gamma[l, k]
        design = (Z[:, :, :, None] * f[:, None, None, :]).reshape(T * N, L * K)
        coef, *_ = np.linalg.lstsq(design, R.reshape(T * N), rcond=None)
        gamma_new = coef.reshape(L, K)
        gamma_new, f_new = _normalize(gamma_new, ipca_factors(Z, R, gamma_new))  # (6), then identification
        change = max(np.abs(gamma_new - gamma).max(), np.abs(f_new - f).max())
        gamma, f = gamma_new, f_new
        if change < tol:
            break
    else:
        raise RuntimeError(f"IPCA (K={K}) did not converge in {max_iter} iterations")
    return {"gamma": gamma, "f": f, "lambda": f.mean(axis=0), "iterations": iteration}


def pca(R: np.ndarray, K: int) -> dict:
    """Static PCA as the least-squares latent factor model (KPS, p. 15): B = leading K eigenvectors of the
    uncentered second moment matrix sum_t r_t r_t' (orthonormal, N x K), f_t = B' r_t, signs set so mean f >= 0."""
    eigval, eigvec = np.linalg.eigh(R.T @ R)
    B = eigvec[:, np.argsort(eigval)[::-1][:K]]
    f = R @ B
    sign = np.where(f.mean(axis=0) < 0, -1.0, 1.0)
    B, f = B * sign, f * sign
    return {"B": B, "f": f, "lambda": f.mean(axis=0)}
