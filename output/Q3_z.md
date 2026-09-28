# Q3: In-sample PCA vs IPCA

**Question:** build 1 and 3 factors with PCA, and 1, 3 and 5 factors with IPCA (Γα = 0), from the 25 portfolios. Report each portfolio's pricing error, the average over time of rᵢₜ − z′ᵢₜΓ̂βλ̂, plus total and predictive R². Compare with Q2. Does IPCA help with 1 factor? With several? Which characteristics were used?

Sample 1972-03 to 2025-04 (T = 638, N = 25). Code: `code/Q3.py` and `code/factor_models.py`.

## Pricing errors (% per month)

| | PCA1 | PCA3 | IPCA1 | IPCA3 | IPCA5 | *CAPM* | *3F* |
|---|---|---|---|---|---|---|---|
| ME1 Lo PRIOR | −0.06 | −0.05 | −0.05 | −0.07 | −0.03 | −0.00 | −0.19 |
| ME1 PRIOR2 | −0.02 | 0.05 | −0.11 | −0.05 | −0.09 | 0.02 | −0.06 |
| ME1 PRIOR3 | 0.01 | 0.12 | −0.08 | 0.06 | 0.00 | 0.05 | 0.00 |
| ME1 PRIOR4 | −0.05 | 0.11 | −0.12 | 0.09 | 0.06 | −0.01 | −0.01 |
| ME1 Hi PRIOR | −0.65 | −0.39 | −0.65 | −0.34 | −0.24 | −0.61 | −0.54 |
| ME2 Lo PRIOR | 0.09 | 0.01 | 0.16 | 0.07 | 0.13 | 0.12 | −0.06 |
| ME2 PRIOR2 | 0.24 | 0.24 | 0.21 | 0.20 | 0.18 | 0.26 | 0.17 |
| ME2 PRIOR3 | 0.11 | 0.17 | 0.08 | 0.15 | 0.11 | 0.12 | 0.09 |
| ME2 PRIOR4 | −0.02 | 0.08 | −0.02 | 0.12 | 0.11 | −0.01 | 0.00 |
| ME2 Hi PRIOR | −0.37 | −0.15 | −0.33 | −0.10 | 0.02 | −0.37 | −0.26 |
| ME3 Lo PRIOR | 0.06 | −0.09 | 0.14 | −0.01 | 0.05 | 0.06 | −0.12 |
| ME3 PRIOR2 | 0.21 | 0.14 | 0.20 | 0.12 | 0.08 | 0.20 | 0.12 |
| ME3 PRIOR3 | 0.17 | 0.16 | 0.17 | 0.18 | 0.11 | 0.16 | 0.12 |
| ME3 PRIOR4 | 0.01 | 0.06 | 0.02 | 0.10 | 0.06 | −0.01 | 0.01 |
| ME3 Hi PRIOR | −0.32 | −0.13 | −0.28 | −0.13 | −0.04 | −0.34 | −0.22 |
| ME4 Lo PRIOR | 0.01 | −0.24 | 0.08 | −0.13 | −0.07 | −0.03 | −0.22 |
| ME4 PRIOR2 | 0.30 | 0.17 | 0.31 | 0.17 | 0.12 | 0.26 | 0.17 |
| ME4 PRIOR3 | 0.20 | 0.13 | 0.20 | 0.13 | 0.06 | 0.15 | 0.12 |
| ME4 PRIOR4 | 0.07 | 0.08 | 0.09 | 0.10 | 0.04 | 0.02 | 0.06 |
| ME4 Hi PRIOR | −0.24 | −0.10 | −0.20 | −0.12 | −0.08 | −0.29 | −0.16 |
| ME5 Lo PRIOR | −0.03 | −0.33 | −0.04 | −0.29 | −0.26 | −0.10 | −0.30 |
| ME5 PRIOR2 | 0.18 | −0.01 | 0.13 | −0.07 | −0.14 | 0.09 | 0.01 |
| ME5 PRIOR3 | 0.18 | 0.06 | 0.13 | −0.00 | −0.09 | 0.09 | 0.07 |
| ME5 PRIOR4 | 0.13 | 0.08 | 0.09 | 0.03 | −0.04 | 0.03 | 0.10 |
| ME5 Hi PRIOR | −0.04 | 0.02 | −0.06 | −0.07 | −0.07 | −0.14 | 0.01 |
| **Mean \|α\|** | 0.15 | 0.13 | 0.16 | 0.12 | **0.09** | 0.14 | 0.13 |
| **RMS α** | 0.21 | 0.16 | 0.20 | 0.14 | **0.11** | 0.20 | 0.17 |
| **Max \|α\|** | 0.65 | 0.39 | 0.65 | 0.34 | **0.26** | 0.61 | 0.54 |
| **Total R² (%)** | 85.42 | 93.45 | 84.97 | 92.72 | **94.22** | 75.43 | 91.27 |
| **Predictive R² (%)** | 1.24 | 1.29 | 1.25 | 1.29 | **1.31** | 1.25 | 1.28 |
| # loading parameters | 25 | 75 | 6 | 18 | 30 | 25 | 75 |

The CAPM and 3F columns use the same pricing-error definition, with β̂ from regressions without an intercept and λ̂ equal to the factor means. They therefore differ slightly from the Q2 intercepts.

## Key insights

- **1 factor: IPCA brings no improvement.** IPCA1 and PCA1 are almost identical: total R² 84.97% vs 85.42%, mean |α| 0.16% vs 0.15%. The single IPCA factor loads mainly on the constant (Γ = 0.90), so its loadings barely vary. It is essentially a market factor and, like the CAPM, leaves the small-winner error at −0.65%.
- **3 factors: similar fit, better pricing.** PCA3 fits returns over time slightly better (93.45% vs 92.72%) because it has 75 free loadings against IPCA's 18. IPCA3 prices better: mean |α| 0.12% vs 0.13%, RMS 0.14% vs 0.16%, max 0.34% vs 0.39%. With far fewer parameters, the characteristics describe the risk exposures about as well.
- **5 factors: IPCA5 is the best model on every metric.** It has the highest R² and roughly halves the pricing errors of the 3F model (mean |α| 0.09% vs 0.13%, small-winner α −0.24% vs −0.54%). However, with L = 6, K = 5 is close to no dimension reduction; at K = L the factors would simply be the characteristic-managed portfolios (Kelly et al., p. 16).
- **Compared with Q2:** all latent 3- and 5-factor models beat CAPM and 3F on both total R² and pricing errors. Two errors remain in every multi-factor model: large-cap losers (−0.26 to −0.33) and mid-cap PRIOR2 portfolios (+0.12 to +0.24). Predictive R² stays around 1.3% for every model, because monthly return variation is almost all noise.
- **What drives the IPCA loadings:** size and last month's return, the two sorting variables. In IPCA3, f1 is market-like (constant 0.82), f2 is size minus prior return, and f3 is size plus prior return. The constructed return-history characteristics only matter from K = 5 onwards (f4: ltrev 0.83, mom −0.52; f5: vol −0.82).

## Characteristics (L = 6)

- **From the French file (2):** average firm size (`size`) and the value-weighted average prior-month return (`prior_vw`). The equal-weighted version was dropped because its correlation with `prior_vw` is 0.998.
- **Constructed from each portfolio's own returns (3):**
  - `mom`: sum of returns from t−12 to t−2.
  - `ltrev`: sum of returns from t−60 to t−13.
  - `vol`: 12-month standard deviation of returns from t−12 to t−1.
- **Transformation:** each month, rank / N − 0.5, as in Kelly et al. (p. 24), plus a constant (Kelly et al., p. 8).

*Method notes:*
- *IPCA is estimated by ALS exactly as in Kelly et al. (Appendix A). It starts from the eigenvectors of the managed portfolios' second-moment matrix and stops when the largest change is below 10⁻⁶. Identification follows Kelly et al. p. 14: Γ′Γ = I, a diagonal factor second-moment matrix, and non-negative factor means.*
- *PCA uses the uncentered second-moment matrix of excess returns (Kelly et al., p. 15).*
- *Our IPCA was cross-checked against Pruitt's `ipca` package (v0.6.7, `code/ipca_crosscheck.py`). Total and predictive R² agree to 4 decimals for K = 1, 3, 5, and Γβ agrees to within 5×10⁻⁷.*
