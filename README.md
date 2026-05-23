# Optimal Trade Design: Size, Leverage & Execution

**A calculus-based interactive framework for quantitative trading decisions**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-ff4b4b)](https://optimal-trade-design-pjsdmh5jbteenuy6w4kqhx.streamlit.app)

**[Open Live App](https://optimal-trade-design-pjsdmh5jbteenuy6w4kqhx.streamlit.app)**

---

## Overview

Every trading decision involves balancing competing forces. This project implements and visualizes three fundamental optimization problems in quantitative finance — each derived analytically and explored interactively:

| Stage | Problem | Closed-Form Solution |
|-------|---------|----------------------|
| **1** | Trade Size | $x^* = \frac{\alpha - c}{2\beta}$ |
| **2** | Leverage (Kelly) | $\ell^* = \frac{\mu}{\sigma^2}$ |
| **3** | Execution Timing | $t^* = \sqrt{\frac{k}{\lambda}}$ |

The core insight: **interior optima arise when benefits grow sublinearly while costs accelerate**. Calculus finds where they balance.

---

## Mathematical Foundation

### Stage 1 — Trade Size Optimization

$$\max_x \; P(x) = \alpha x - \beta x^2 - cx$$

- $\alpha$: expected profit per share (your edge)
- $\beta$: market impact coefficient (quadratic slippage)
- $c$: transaction cost per share

First-order condition gives $x^* = \frac{\alpha - c}{2\beta}$. Trade more than this and impact destroys your edge. Trade less and you leave money on the table.

### Stage 2 — Leverage Optimization (Kelly Criterion)

$$\max_\ell \; R(\ell) = \ell\mu - \frac{1}{2}\ell^2\sigma^2$$

The $\frac{1}{2}$ factor arises from the Taylor expansion of log utility. This yields the **Kelly fraction** $\ell^* = \mu/\sigma^2$ — the Sharpe ratio divided by volatility.

### Stage 3 — Execution Time Optimization

$$\min_t \; C(t) = \frac{k}{t} + \lambda t$$

The classical slippage-vs-drift tradeoff. Fast execution incurs market impact ($k/t$); slow execution lets price drift against you ($\lambda t$). The geometric mean $t^* = \sqrt{k/\lambda}$ splits the difference exactly.

---

## Project Structure

```
optimal-trade-design/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── docs/
│   ├── math_derivations.md # Full derivations with proofs
│   └── parameter_guide.md  # How to calibrate parameters to real data
│
└── assets/
    └── .gitkeep
```

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/vij-akshat/optimal-trade-design.git
cd optimal-trade-design

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Features

- **Animated build-up**: Every chart assembles step-by-step so you see *how* the solution emerges — not just the endpoint
- **Live parameter sliders**: Drag to see how $\alpha$, $\sigma$, $\lambda$ etc. shift the optimum in real time
- **Marginal analysis**: Visualizes MB = MC condition explicitly
- **Sensitivity surfaces**: 2D sweeps showing how the optimum moves as parameters change
- **Fractional Kelly panel**: Compares full vs. ½ vs. ¼ Kelly strategies
- **Unified summary**: Side-by-side view of all three optima with the common mathematical pattern

---

## Parameter Calibration

See [`docs/parameter_guide.md`](docs/parameter_guide.md) for guidance on estimating:
- $\alpha$ from alpha decay studies or factor backtests
- $\beta$ from Almgren-Chriss market impact models
- $\mu$, $\sigma$ from historical return series
- $\lambda$ from intraday price drift estimates

---

## Key Results

All three problems share the same structural logic:

```
Benefit grows linearly in the decision variable
Cost grows faster (quadratically, or as a convex pair)
→ Interior optimum where marginal benefit = marginal cost
```

This pattern recurs across portfolio optimization, option replication, and market making. Recognizing it is a core skill in quant finance.

---

## Extensions

Real-world implementations go further:
- **Trade size**: Almgren-Chriss model adds temporary/permanent impact separation
- **Leverage**: Practitioners use fractional Kelly (½ or ¼) to hedge estimation risk
- **Execution**: TWAP/VWAP/IS algorithms use dynamic programming with stochastic drift

---

## License

MIT License — see [LICENSE](LICENSE).
