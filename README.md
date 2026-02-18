# Optimal Trade Design under Transaction Costs and Risk Constraints
This project formulates and solves the optimal trade sizing problem under realistic market frictions. Instead of assuming frictionless rebalancing, it incorporates transaction costs and risk penalties to determine economically optimal position adjustments.
The problem highlights the tradeoff between expected alpha capture and implementation costs — a core issue in systematic trading and portfolio management.
---
## What It Does
Given:
- Current portfolio weights $w_{0}$
- Target signal-implied weights $W^{*}$
- Covariance matrix $\Sigma$
- Expected alpha vector $\mu$
- Linear and/or quadratic transaction costs 
The optimizer solves:
  
$mu^{T} w - \lamda w^{T} \Sigma w - \gamma ||w-w_{0}||_{1}$

---
## Features
- Implements constrained convex optimization
- Models realistic transaction cost penalties
- Demonstrates optimal shrinkage toward current holdings
- Shows how cost strength changes trade aggressiveness
- Visualizes turnover vs. risk tradeoff
---
## Visualization
- Optimal weights under varying cost regimes
- Trade size vs. cost parameter
- Risk-return-cost frontier
- Turnover sensitivity analysis
---
## Why It Matters
In real markets, optimal portfolios are rarely equal to signal portfolios.
This project demonstrates how cost-aware optimization transforms theoretical alpha into executable strategy design.
--- 
## Requirements
Python 3.x
NumPy
Matplotlib
CVXPy
Install dependencies:
```bash 
pip install numpy matplotlib cvxpy
```
