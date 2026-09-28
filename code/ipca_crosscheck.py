"""Cross-check of our IPCA (factor_models.ipca) against Seth Pruitt's `ipca` package (pip install ipca, v0.6.7).

Not part of the main pipeline: run it in an environment where the `ipca` package is installed, from inside code/.
For K = 1, 3, 5 it prints total / predictive R² of both implementations and the max difference in Gamma_beta.
"""

import warnings

import numpy as np
import pandas as pd
from ipca import InstrumentedPCA

from data_loader import load
from factor_models import CHARACTERISTICS, instruments, ipca
from metrics import predictive_r2, total_r2

warnings.filterwarnings("ignore")

d = load(); R = d["excess"].to_numpy(); Z = instruments(d["chars"]); T, N, L = Z.shape
idx = pd.MultiIndex.from_product([range(N), range(T)], names=["entity", "time"])
X = pd.DataFrame(Z.transpose(1, 0, 2).reshape(N * T, L), index=idx, columns=CHARACTERISTICS + ["const"])
y = pd.Series(R.T.reshape(N * T), index=idx)
for K in [1, 3, 5]:
    ours = ipca(Z, R, K)
    pkg = InstrumentedPCA(n_factors=K, intercept=False, iter_tol=1e-8, max_iter=10000)
    pkg = pkg.fit(X=X, y=y, data_type="panel")
    G, F = np.asarray(pkg.Gamma), np.asarray(pkg.Factors).T  # L x K, T x K
    fit_pkg = np.einsum("tnk,tk->tn", Z @ G, F)
    fit_ours = np.einsum("tnk,tk->tn", Z @ ours["gamma"], ours["f"])
    # compare Gamma up to column signs
    s = np.sign((G * ours["gamma"]).sum(0))
    print(f"K={K}: total R2 ours {100*total_r2(R, fit_ours):.4f}  pkg {100*total_r2(R, fit_pkg):.4f} | "
          f"max|dGamma| {np.abs(G*s - ours['gamma']).max():.1e} | max|d fitted| {np.abs(fit_pkg - fit_ours).max():.1e} | "
          f"pred R2 ours {100*predictive_r2(R, Z @ ours['gamma'] @ ours['lambda']):.4f} pkg {100*predictive_r2(R, Z @ G @ F.mean(0)):.4f}")
