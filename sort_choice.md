# Choice of test assets: 25 portfolios on Size × Short-Term Reversal

**Decision:** we use the 5 × 5 portfolios formed on size and short-term reversal (prior return from month −1 to −1) from Kenneth French's data library. The third factor in Q1, Q2 and Q4 is therefore the **ST_Rev** factor, so the 3-factor model is Mkt-RF + SMB + ST_Rev.

Page numbers for Kelly, Pruitt and Su (2019) (KPS) refer to the SSRN version in `pdfs/Kelly(2019).pdf`. The published JFE version is paginated differently.

## Data files (monthly, CSV)

| File | Content used |
|---|---|
| `25_Portfolios_ME_Prior_1_0.csv` | Returns: *Average Value Weighted Returns -- Monthly*. Characteristics: *Average Firm Size*, *Equally-Weighted Average of Prior Returns*, *Value-Weighted Average of Prior Returns* |
| `F-F_ST_Reversal_Factor.csv` | ST_Rev factor |
| `F-F_Research_Data_5_Factors_2x3.csv` | Mkt-RF, SMB, RF |

The portfolios are re-formed every month: "ME is market cap at the end of the previous month. PRIOR_RET is from −1 to −1" (file header). None of the portfolio files has missing values (−99.99 / −999) in our sample period, 1972-03 to 2025-04.

## Why short-term reversal

1. **KPS find that short-term reversal matters for IPCA.** Of their 36 characteristics, only 10 are significant at the 1% level, and short-term reversal is one of them, along with market cap, book assets, beta, momentum, turnover, price relative to the 52-week high, long-term reversal, unexplained volume and idiosyncratic volatility (Section 4.9, p. 45). In Table XI, strev ranks fourth by contribution to total R² (0.47, significant at 1%), behind only mktcap, assets and beta. KPS also say the model "is driven to a significant extent by fast-moving characteristics like momentum and short-term reversal" (p. 39).

2. **It suits what IPCA adds over PCA.** IPCA's contribution is loadings that vary over time with characteristics (KPS, Section 2.1). B/M, OP and Inv portfolios are rebalanced once a year in June, so their characteristics hardly move within a year. The ST-reversal portfolios are re-sorted every month on last month's return, so their composition, and plausibly their risk exposures, change month to month. This is where instrumented loadings should have the best chance to beat static PCA loadings.

3. **It is a less studied set of test assets.** The 5 × 5 Size × B/M portfolios are the standard test assets (KPS p. 27 mention them explicitly), and Size × OP/Inv have been standard since Fama and French (2015). Size × Momentum is a well-known hard case. The 5 × 5 Size × ST-reversal portfolios are used much less as test assets. This is our reading of the literature, not a claim made in KPS. Short-term reversal itself goes back to Jegadeesh (1990) and Lehmann (1990), and Nagel (2012) interprets it as compensation for providing liquidity.

## Potential issues and complications

1. **Few characteristics in the file.** The assignment requires at least 5 characteristics, excluding the number of firms. The file gives us 3 (firm size, EW prior return, VW prior return), and the two prior-return averages are highly correlated. We have to construct at least 2 more from past portfolio returns, for example:
   - momentum: the sum of returns from t−12 to t−2 (the example in the assignment);
   - long-term reversal: the sum of returns from t−60 to t−13;
   - volatility: the rolling standard deviation of returns over 12 or 36 months.

   All of these must use only information available at the start of month t. The data start in 1926, so the lookback windows are filled well before 1972-03.

2. **Characteristics built from returns describe the strategy, not the current holdings.** Because each portfolio is re-formed monthly, "portfolio i's return 6 months ago" is the return of a *different set of stocks* that happened to sit in the same size/prior-return bucket then. Momentum or volatility built from these series is therefore a noisier proxy for the current constituents' characteristics than it would be for annually rebalanced B/M portfolios. We should state this in the Q3 bullet points.

3. **We need enough characteristics for 5 IPCA factors.** When K = L there is no dimension reduction: the IPCA factors are simply the characteristic-managed portfolios, and Γβ = I (KPS, p. 16). For the K = 5 model in Q3 and Q4 to be a real reduction we need L > 5. KPS include a constant in z (p. 8 and p. 28), so 5 characteristics plus a constant gives L = 6. Adding a sixth characteristic, or a transformation such as a rank-transformed version of a raw one, gives more room.

4. **The IPCA gain on portfolios may be modest.** KPS report that static PCA does very well on managed portfolios, "generally excellent and only exceeded by IPCA" (p. 32), and that PCA's weakness shows up mainly at the individual-stock level (p. 34). With only N = 25 diversified portfolios, IPCA's improvement over PCA may be small, particularly in total R². We should not over-claim, and the out-of-sample exercise in Q4 is where any difference is more likely to show.

5. **Short-term reversal is weaker among large stocks.** KPS find strev highly significant for the full sample and for small stocks, but insignificant for large stocks (p. 46). Our portfolios are value-weighted, so the big-stock rows are dominated by large caps. We may find that the reversal characteristics add little for those portfolios.

6. **Time variation in the ST_Rev factor.** The reversal premium is widely documented to have weakened in recent decades, which is often attributed to lower trading costs and more liquidity provision. Our long sample (638 months) spans both regimes, so the premium and the tangency weights in Q1 average over them. The 240-month rolling windows in Q4 may show the change directly. We should verify this in our own data before stating it in the report.

7. **Timing convention.** The characteristics in the file (firm size, prior returns) are known at the start of month t, while the portfolio returns are realised at its end. In KPS notation, z_t pairs with r_{t+1}. Characteristics we build ourselves must follow the same alignment, for example momentum for month t uses returns up to t−2 only.

8. **Transaction costs are ignored.** As in KPS (p. 39), all returns and Sharpe ratios are gross of costs. For a monthly-rebalanced reversal strategy with high turnover this matters more than for value or profitability sorts. It is worth a line in the Q1 discussion and in the conclusion.

## References

- Fama, E. F. and French, K. R. (2015). A five-factor asset pricing model. *Journal of Financial Economics*, 116(1):1–22.
- Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3):881–898.
- Kelly, B. T., Pruitt, S., and Su, Y. (2019). Characteristics are covariances: A unified model of risk and return. *Journal of Financial Economics*, 134(3):501–524.
- Lehmann, B. N. (1990). Fads, martingales, and market efficiency. *Quarterly Journal of Economics*, 105(1):1–28.
- Nagel, S. (2012). Evaporating liquidity. *Review of Financial Studies*, 25(7):2005–2039.
