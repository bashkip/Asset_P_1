# Q5: Conclusion

**Question:** how does IPCA perform relative to standard PCA and a priori constructed factor models?

Test assets: 25 Size × Short-Term Reversal portfolios, 1972-03 to 2025-04 (638 months).

## Answer

**With a single factor, IPCA performs about the same as PCA. With several factors it prices the portfolios better than both PCA and the Fama-French-style models, and this advantage holds out of sample.**

1. **The observable factors are not enough.** The three factors (Mkt-RF, SMB, ST_Rev) reach a Sharpe ratio of only 0.16 per month. Their frontier lies far inside that of the 25 portfolios (Q1). GRS rejects both the CAPM and the 3-factor model (Q2). ST_Rev raises the total R² from 75% to 91%, but it does not reduce the pricing errors: it corrects large-cap winners but overshoots on large-cap losers.

2. **With one factor, IPCA brings nothing.** IPCA1 and PCA1 both end up with essentially a market factor. In-sample they are almost identical. Out of sample, IPCA1 prices slightly better (RMS α 0.18% vs 0.20%) and PCA1 fits slightly better (Q3, Q4). One factor cannot capture the reversal pattern, however it is built.

3. **With several factors, IPCA prices better than PCA.** PCA3 explains slightly more of the return variation, but it needs 75 loadings against IPCA3's 18. IPCA3 has smaller pricing errors in-sample (RMS α 0.14% vs 0.16%) and the gap widens out of sample (0.15% vs 0.18%). IPCA5 is the best model on every measure. Out of sample it has a total R² of 93% and an RMS α of 0.09%, about half that of the 3-factor model (0.20%).

4. **The reason is that IPCA's loadings move with the characteristics.** These portfolios are re-formed every month, so their risk exposures change with size and last month's return. IPCA links loadings to exactly these characteristics, so its estimates stay valid in new months. PCA and time-series regressions assume fixed loadings per portfolio, and their pricing errors grow out of sample.

5. **The gains are real but modest.** Predictive R² is about 1% for every model, since most monthly return variation is unpredictable. Some errors remain in all models, notably small losers and mid/large PRIOR2–3 portfolios. IPCA5, with 6 instruments, is close to no dimension reduction at all.

**Overall, IPCA is at least as good as PCA and clearly better than a priori factors, with the largest gains in the multi-factor, out-of-sample setting that matters most for asset pricing.** This matches Kelly et al. (2019), although on portfolios the advantage over PCA is smaller than they report for individual stocks.

## Strengths, weaknesses and further research

- **Strengths:**
  - We compare in-sample and out-of-sample results on the same portfolios.
  - The pricing-error and R² definitions are the same for all seven models.
  - Our IPCA code reproduces Pruitt's `ipca` package.
- **Weaknesses:**
  - The results rest on only 25 portfolios and 5 characteristics.
  - Three of the characteristics are built from the portfolios' own past returns. Because the portfolios are re-formed monthly, these describe the strategy rather than the stocks currently held.
  - All returns are gross of transaction costs, which matter for a monthly reversal strategy.
- **Further research:**
  - Apply IPCA to individual stocks, or to a larger set of portfolios (other sorts combined), with richer characteristics such as turnover and idiosyncratic volatility.
  - Test IPCA with Γα ≠ 0 to see whether characteristics also generate alphas.
  - Evaluate net-of-cost Sharpe ratios of the IPCA tangency portfolio.

## Reflection on the peer review

*[To be completed after receiving the feedback.]*

## References

- Cochrane, J. H. (2011). Presidential address: Discount rates. *Journal of Finance*, 66(4):1047–1108.
- Fama, E. F. and French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1):3–56.
- Fama, E. F. and French, K. R. (2015). A five-factor asset pricing model. *Journal of Financial Economics*, 116(1):1–22.
- Gibbons, M. R., Ross, S. A. and Shanken, J. (1989). A test of the efficiency of a given portfolio. *Econometrica*, 57(5):1121–1152.
- Kelly, B. T., Pruitt, S. and Su, Y. (2019). Characteristics are covariances: A unified model of risk and return. *Journal of Financial Economics*, 134(3):501–524.
- Kenneth R. French Data Library, https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html.

## Software and use of generative AI

- **Software:**
  - Python 3.12 with numpy, pandas, scipy, matplotlib and openpyxl.
  - IPCA was implemented from scratch following Kelly et al. (2019, Appendix A) and cross-checked against the `ipca` package (v0.6.7) by S. Pruitt.
- **Generative AI:** *[team to confirm wording]* Claude (Anthropic) was used as a coding assistant to structure and write the Python code, check the implementation against Kelly et al. (2019), and draft summaries of the results. The team verified all results, choices and interpretations.
