# Mathematical Derivations

Full proofs for all three optimization problems in *Optimal Trade Design*.

---

## Stage 1 — Trade Size

### Setup

Define profit as a function of trade size $x \geq 0$:

$$P(x) = \alpha x - \beta x^2 - cx$$

where:
- $\alpha > c > 0$ (edge must exceed cost for a profitable trade to exist)
- $\beta > 0$ (market impact is strictly increasing)

### First-Order Condition

$$\frac{dP}{dx} = \alpha - 2\beta x - c = 0$$

$$\Rightarrow \quad x^* = \frac{\alpha - c}{2\beta}$$

### Second-Order Condition

$$\frac{d^2P}{dx^2} = -2\beta < 0$$

Since $\beta > 0$, the profit function is strictly concave everywhere. $x^*$ is a global maximum.

### Break-Even

$P(x) = 0$ at $x = 0$ and $x = \frac{\alpha - c}{\beta}$. The profitable interval is $\left(0, \frac{\alpha - c}{\beta}\right)$, and the optimum lies at its midpoint.

### Comparative Statics

$$\frac{\partial x^*}{\partial \alpha} = \frac{1}{2\beta} > 0 \qquad \text{(larger edge → larger position)}$$

$$\frac{\partial x^*}{\partial \beta} = -\frac{\alpha - c}{2\beta^2} < 0 \qquad \text{(more impact → smaller position)}$$

$$\frac{\partial x^*}{\partial c} = -\frac{1}{2\beta} < 0 \qquad \text{(higher costs → smaller position)}$$

---

## Stage 2 — Leverage (Kelly Criterion)

### Setup

Define risk-adjusted return as a function of leverage $\ell \geq 0$:

$$R(\ell) = \ell\mu - \frac{1}{2}\ell^2\sigma^2$$

The $\frac{1}{2}$ coefficient derives from the second-order Taylor expansion of log wealth:

$$\mathbb{E}[\log(1 + \ell r)] \approx \ell\mu - \frac{1}{2}\ell^2\sigma^2$$

where $r \sim \mathcal{N}(\mu, \sigma^2)$ is the per-period return.

### First-Order Condition

$$\frac{dR}{d\ell} = \mu - \ell\sigma^2 = 0$$

$$\Rightarrow \quad \ell^* = \frac{\mu}{\sigma^2}$$

This is the **Kelly fraction** — equivalently, the Sharpe ratio divided by volatility:

$$\ell^* = \frac{\mu/\sigma}{\sigma} = \frac{\text{SR}}{\sigma}$$

### Second-Order Condition

$$\frac{d^2R}{d\ell^2} = -\sigma^2 < 0$$

Strictly concave — $\ell^*$ is a global maximum.

### Maximum Value

Substituting $\ell^*$ back:

$$R(\ell^*) = \frac{\mu^2}{2\sigma^2} = \frac{\text{SR}^2}{2}$$

The maximum risk-adjusted return equals half the squared Sharpe ratio.

### Fractional Kelly

In practice, $\mu$ and $\sigma$ are estimated with error. Using $f \cdot \ell^*$ where $f \in (0,1)$ reduces variance of outcomes at the cost of expected log growth. The half-Kelly ($f = 0.5$) is a common convention that halves drawdown risk while only reducing expected growth by 25%.

---

## Stage 3 — Execution Time

### Setup

Define total execution cost as:

$$C(t) = \frac{k}{t} + \lambda t, \qquad t > 0$$

- $k/t$: slippage (executes faster → more market impact, $k > 0$)
- $\lambda t$: opportunity cost (waits longer → price drifts, $\lambda > 0$)

### First-Order Condition

$$\frac{dC}{dt} = -\frac{k}{t^2} + \lambda = 0$$

$$\Rightarrow \quad t^* = \sqrt{\frac{k}{\lambda}}$$

### Second-Order Condition

$$\frac{d^2C}{dt^2} = \frac{2k}{t^3} > 0$$

Strictly convex — $t^*$ is a global minimum.

### Slippage-Drift Parity

At the optimum:

$$\frac{k}{t^*} = \lambda t^* = \sqrt{k\lambda}$$

Slippage and opportunity cost are **equal** at the optimum. This is the AM-GM equality condition: for two positive terms summing to a constant, the product (and hence the geometric mean) is maximized when they are equal.

### Minimum Cost

$$C(t^*) = \frac{k}{t^*} + \lambda t^* = 2\sqrt{k\lambda}$$

---

## Unifying Pattern

All three problems are instances of one structure:

$$\text{Optimize } F(z) = B(z) - C(z)$$

where $B(z)$ grows at most linearly and $C(z)$ is strictly convex. The FOC $B'(z) = C'(z)$ — marginal benefit equals marginal cost — always yields an interior solution when the functions cross.

This pattern recurs in:
- Markowitz portfolio optimization (return vs. variance)
- Black-Scholes hedging (replication vs. transaction costs)
- Market making (bid-ask spread vs. inventory risk)
- Almgren-Chriss execution (permanent vs. temporary impact)
