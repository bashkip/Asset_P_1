# Q2: GRS tests of CAPM and 3-factor model

**Question:** use GRS tests on the CAPM and on Mkt-RF + SMB + ST_Rev with the 25 portfolios as test assets. Report the alphas with standard errors, and the total and predictive R². Compare the Sharpe ratios (SR) of the market and of the 3-factor efficient portfolio with what the GRS test implies.

Sample 1972-03 to 2025-04 (T = 638, N = 25). Excess returns use the Fama-French RF. Code: `code/Q2.py`.

## Alphas (% per month, standard errors in parentheses, **bold** = |t| > 1.96)

| | Lo PRIOR | PRIOR2 | PRIOR3 | PRIOR4 | Hi PRIOR |
|---|---|---|---|---|---|
| **CAPM** | | | | | |
| ME1 | −0.00 (0.20) | 0.02 (0.14) | 0.05 (0.14) | −0.01 (0.14) | **−0.63 (0.16)** |
| ME2 | 0.12 (0.16) | **0.26 (0.12)** | 0.13 (0.11) | −0.01 (0.11) | **−0.38 (0.14)** |
| ME3 | 0.06 (0.15) | **0.20 (0.10)** | 0.16 (0.09) | −0.01 (0.09) | **−0.34 (0.12)** |
| ME4 | −0.03 (0.13) | **0.27 (0.08)** | **0.15 (0.07)** | 0.02 (0.07) | **−0.29 (0.11)** |
| ME5 | −0.11 (0.13) | 0.09 (0.07) | 0.09 (0.06) | 0.03 (0.06) | −0.15 (0.10) |
| **3F** | | | | | |
| ME1 | −0.19 (0.10) | −0.06 (0.07) | 0.00 (0.08) | −0.01 (0.08) | **−0.56 (0.09)** |
| ME2 | −0.06 (0.07) | **0.18 (0.06)** | 0.09 (0.06) | 0.00 (0.06) | **−0.27 (0.06)** |
| ME3 | −0.12 (0.08) | 0.12 (0.06) | 0.13 (0.07) | 0.01 (0.06) | **−0.22 (0.06)** |
| ME4 | **−0.23 (0.08)** | **0.18 (0.06)** | 0.13 (0.07) | 0.06 (0.06) | **−0.16 (0.07)** |
| ME5 | **−0.30 (0.09)** | 0.01 (0.06) | 0.08 (0.05) | 0.10 (0.05) | 0.01 (0.07) |

## Model summary

| | CAPM | 3F |
|---|---|---|
| GRS (p-value) | 2.71 (1.7×10⁻⁵) | 3.00 (1.9×10⁻⁶) |
| Total / predictive R² (%) | 75.43 / 1.25 | 91.27 / 1.28 |
| Mean \|α\| (%), # significant | 0.14, 8 | 0.13, 8 |
| SR of the factors' efficient portfolio (monthly) | 0.13 (market) | 0.16 |
| SR of factors + 25 portfolios, ex post (monthly) | 0.36 | 0.39 |
| Largest SR the test would not reject at 5% | 0.28 | 0.30 |

## Key insights

- **GRS rejects both models** (critical value 1.52). Neither CAPM nor 3F prices these portfolios.
- **The 3F model explains more of the monthly variation, not average returns.** Total R² rises by 16 points, but predictive R² and mean |α| are almost unchanged. GRS even increases, because the smaller residuals make the remaining alphas more precisely estimated.
- **The CAPM misprices recent winners.** Hi PRIOR alphas are negative, from −0.63% for small caps to −0.15% for large caps. This is the reversal effect, strongest in small stocks.
- **ST_Rev overshoots for large stocks.** It fixes the alpha of large-cap winners but creates significantly negative alphas for large-cap losers (−0.23%, −0.30%). This is consistent with Kelly et al. (2019, p. 46), who find reversal insignificant among large stocks.
- **Sharpe ratio view:** the market has SR 0.13 and the 3F efficient portfolio 0.16, but adding the portfolios gives 0.36 to 0.39, well above the 0.28 to 0.30 that GRS tolerates. The portfolios offer a far better risk-return trade-off than the factors, matching the frontier gap in Q1.

*Method notes:*
- *Following Kelly et al. (p. 30), the R² uses betas without an intercept, and the predictive R² uses λ̂ = factor means. The alphas and GRS use regressions with an intercept.*
- *The standard errors are OLS and the covariances in GRS are maximum-likelihood estimates.*
- *The ex-post SR with 25 assets is inflated by estimation error.*
