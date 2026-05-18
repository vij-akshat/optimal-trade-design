# Parameter Calibration Guide

How to set model parameters from real market data.

---

## Stage 1 — Trade Size Parameters

### α — Expected Profit Per Share (Your Edge)

$\alpha$ represents your signal strength before costs. Estimate it from:

**Factor models**: If you have a predicted return $r$ for the stock over horizon $H$:
$$\alpha \approx \frac{r \cdot P}{H}$$
where $P$ is the current share price and $H$ is measured in trading days.

**Typical range**: 1–10 cents/share for intraday strategies; larger for multi-day holds.

**Red flag**: If $\alpha \leq c$ (your edge doesn't cover costs), $x^* = 0$ — there is no profitable trade.

---

### β — Market Impact Coefficient

$\beta$ controls how quickly your own trading moves prices against you. The quadratic impact model is:

$$\text{Slippage} = \beta x^2$$

**Almgren-Chriss estimate**:
$$\beta \approx \frac{\sigma}{V \cdot \sqrt{T}}$$

where:
- $\sigma$ = daily volatility of the stock
- $V$ = average daily volume (shares)
- $T$ = your trading horizon (days)

**Rule of thumb**: For a liquid large-cap (e.g. SPY, AAPL) with $V = 50M$ shares/day, $\beta \approx 10^{-5}$ to $10^{-4}$.

For small/mid-cap stocks with $V = 1M$ shares/day, $\beta$ can be 50–100× larger.

---

### c — Transaction Cost Per Share

Include everything:
- **Spread**: Half the bid-ask spread (you pay half on entry, half on exit)
- **Commission**: Broker fee per share ($0.001–$0.005 typical)
- **SEC/FINRA fees**: ~$0.0001/share (negligible)

**Typical range**: $0.005–$0.02/share for retail; $0.001–$0.005/share for institutional.

---

## Stage 2 — Leverage Parameters

### μ — Expected Annual Return

Estimate from:
- **Historical mean**: Sample average of monthly/annual returns, annualized
- **Factor model**: CAPM / FF3 expected return
- **Shrinkage**: James-Stein shrinkage toward the market return to correct for estimation error

**Caution**: $\mu$ is extremely noisy. With 5 years of monthly data, the standard error on $\hat{\mu}$ is roughly $\sigma/\sqrt{60} \approx 3\%$ for a typical stock. This is larger than the estimate itself.

**Practical implication**: This is the main reason to use fractional Kelly (½ or ¼) rather than full Kelly. Overestimating $\mu$ by 2× causes you to run 2× too much leverage.

---

### σ — Annual Volatility

Much easier to estimate reliably than $\mu$:

$$\hat{\sigma} = \sqrt{252} \cdot \text{std}(r_{\text{daily}})$$

**GARCH / realized volatility**: For shorter-horizon problems, use GARCH(1,1) conditional vol or 21-day realized vol rather than historical long-run vol.

**Typical ranges**:
- S&P 500 index: 12–20% (low vol regimes) to 30–50% (crisis)
- Large-cap stocks: 20–35%
- Small-cap stocks: 30–60%
- Crypto: 60–120%

---

## Stage 3 — Execution Parameters

### k — Slippage Intensity

$k$ quantifies the total market impact budget (in dollar-minutes):

$$k \approx \text{Order size (\$)} \times \sigma_{\text{intraday}} \times \tau_{\text{typical}}$$

where $\tau_{\text{typical}}$ is the natural execution horizon in minutes.

**Estimation**: Run the execution model backwards. If historical data shows that a $X$ order in $T$ minutes costs $S$ in slippage, then $k \approx S \cdot T$.

---

### λ — Opportunity Cost Rate

$\lambda$ is the cost per minute of *not* being in the position:

$$\lambda \approx \frac{\alpha}{H}$$

where $\alpha$ is the total dollar edge from the signal and $H$ is the signal half-life in minutes.

**Intuition**: A mean-reversion signal with a 30-minute half-life decays fast — $\lambda$ is large, so execute quickly ($t^*$ is small). A multi-day momentum signal has small $\lambda$ — you can afford to execute patiently.

---

## Putting It Together — Example

Suppose you are trading a mean-reversion strategy on AAPL:
- Signal predicts +0.05% move over 60 minutes
- AAPL price: $180, daily volume: 60M shares
- Daily vol: 1.5% → intraday vol ≈ 0.094% per minute

| Parameter | Value | Derivation |
|-----------|-------|------------|
| $\alpha$ | $0.09/share | $0.05\% \times 180$ |
| $\beta$ | $3 \times 10^{-6}$ | Almgren-Chriss with $V = 60M$ |
| $c$ | $0.01/share | spread + commission |
| $x^*$ | ~13,000 shares | $(0.09 - 0.01)/(2 \times 3 \times 10^{-6})$ |
| $\mu$ | 12% | Annual expected return of strategy |
| $\sigma$ | 25% | Annual realized vol |
| $\ell^*$ | 1.92x | Kelly fraction |
| $k$ | 5,000 | Impact budget |
| $\lambda$ | 5.0 | Decay of 60-min signal |
| $t^*$ | ~32 min | $\sqrt{5000/5}$ |

---

## Common Pitfalls

1. **Ignoring impact asymmetry**: The quadratic model assumes symmetric impact. Large sell orders in illiquid names often have worse impact than the model predicts.

2. **Stale volatility**: Using historical $\sigma$ in a regime shift (e.g., earnings, macro event) can severely underestimate risk.

3. **Full Kelly ruin risk**: Kelly maximizes long-run log growth but has ~30% probability of a 50% drawdown at any point. Always use fractional Kelly.

4. **Confusing execution cost units**: $k$ must be in consistent units with $\lambda$. If $\lambda$ is dollars per minute, $k$ must be in dollar-minutes.
