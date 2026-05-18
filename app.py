"""
Optimal Trade Design — Interactive Streamlit App
Stages: Trade Size | Kelly Leverage | Execution Timing
"""

import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Optimal Trade Design",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME COLOURS
# ─────────────────────────────────────────────
C = {
    "primary":   "#2ecc71",
    "secondary": "#3498db",
    "accent":    "#e74c3c",
    "warn":      "#f39c12",
    "neutral":   "#95a5a6",
    "bg":        "#0e1117",
    "surface":   "#1c1c2e",
}

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .metric-box {
        background: #1c1c2e;
        border-left: 4px solid #2ecc71;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 6px 0;
    }
    .metric-label { color: #95a5a6; font-size: 0.78rem; letter-spacing: 0.05em; text-transform: uppercase; }
    .metric-value { color: #ffffff; font-size: 1.45rem; font-weight: 700; }
    .metric-sub   { color: #2ecc71;  font-size: 0.82rem; margin-top: 2px; }
    .formula-box {
        background: #161b27;
        border: 1px solid #2ecc71;
        border-radius: 10px;
        padding: 16px 22px;
        margin: 10px 0 18px 0;
        font-family: monospace;
        font-size: 0.95rem;
        color: #e8e8e8;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #3498db;
        border-bottom: 1px solid #1c2d40;
        padding-bottom: 4px;
        margin: 18px 0 10px 0;
    }
    .insight-box {
        background: #12211a;
        border-left: 3px solid #2ecc71;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        color: #b8f0cc;
        font-size: 0.9rem;
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPER: metric card
# ─────────────────────────────────────────────
def metric_card(label, value, sub=""):
    st.markdown(
        f'<div class="metric-box">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# HELPER: animated chart builder
# ─────────────────────────────────────────────
def animated_line(
    x_full, y_full, n_steps=40,
    name="", color=C["secondary"],
    x_label="", y_label="", title="",
    extra_traces=None,  # list of dicts {x, y, name, color, dash}
    vline=None, vline_label="",
    scatter_point=None,  # (x, y, label, color)
    fill_positive=False,
    fill_negative=False,
    height=400,
):
    """Return a go.Figure built by slicing x_full/y_full into n_steps frames."""
    frames = []
    step = max(1, len(x_full) // n_steps)

    for i in range(step, len(x_full) + 1, step):
        frame_data = [
            go.Scatter(
                x=x_full[:i], y=y_full[:i],
                mode="lines", name=name,
                line=dict(color=color, width=2.5),
                fill="tozeroy" if fill_positive else None,
                fillcolor=f"rgba(46,204,113,0.12)" if fill_positive else None,
            )
        ]
        if extra_traces:
            for et in extra_traces:
                frame_data.append(go.Scatter(
                    x=et["x"][:i], y=et["y"][:i],
                    mode="lines", name=et["name"],
                    line=dict(color=et["color"], width=2, dash=et.get("dash", "solid")),
                ))
        frames.append(go.Frame(data=frame_data, name=str(i)))

    # Build full final figure
    data = [
        go.Scatter(
            x=x_full, y=y_full,
            mode="lines", name=name,
            line=dict(color=color, width=2.5),
            fill="tozeroy" if fill_positive else None,
            fillcolor="rgba(46,204,113,0.12)" if fill_positive else None,
        )
    ]
    if extra_traces:
        for et in extra_traces:
            data.append(go.Scatter(
                x=et["x"], y=et["y"],
                mode="lines", name=et["name"],
                line=dict(color=et["color"], width=2, dash=et.get("dash", "solid")),
            ))
    if vline is not None:
        y_lo = min(0, min(y_full)) * 1.1
        y_hi = max(y_full) * 1.3
        data.append(go.Scatter(
            x=[vline, vline], y=[y_lo, y_hi],
            mode="lines", name=vline_label,
            line=dict(color=C["primary"], width=2, dash="dash"),
            showlegend=bool(vline_label),
        ))
    if scatter_point:
        sx, sy, sl, sc = scatter_point
        data.append(go.Scatter(
            x=[sx], y=[sy],
            mode="markers+text",
            text=[sl],
            textposition="top right",
            marker=dict(color=sc, size=12, line=dict(color="white", width=2)),
            name=sl,
        ))

    fig = go.Figure(data=data, frames=frames)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        height=height,
        title=dict(text=title, font=dict(size=15)),
        xaxis=dict(title=x_label, gridcolor="#1e2a38"),
        yaxis=dict(title=y_label, gridcolor="#1e2a38"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        margin=dict(l=50, r=20, t=50, b=50),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=1.15, x=0.5, xanchor="center",
            buttons=[
                dict(label="▶  Animate", method="animate",
                     args=[None, {"frame": {"duration": 30, "redraw": True},
                                  "fromcurrent": True, "mode": "immediate"}]),
                dict(label="⏹  Reset", method="animate",
                     args=[[None], {"frame": {"duration": 0}, "mode": "immediate",
                                    "transition": {"duration": 0}}]),
            ],
        )],
    )
    return fig


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📐 Optimal Trade Design")
    st.markdown("*A calculus-based framework*")
    st.divider()

    stage = st.radio(
        "**Navigate to Stage**",
        ["🏠 Overview", "1️⃣  Trade Size", "2️⃣  Kelly Leverage", "3️⃣  Execution Timing", "🔗 Unified View"],
        index=0,
    )

    st.divider()
    st.markdown("### ⚙️ Animation")
    n_steps = st.slider("Steps", 15, 60, 35, help="Frames in the animated build")
    auto_play = st.checkbox("Auto-play on load", value=False)

    st.divider()
    st.markdown("### 🔗 Resources")
    st.markdown("[Math Derivations](docs/math_derivations.md)")
    st.markdown("[Parameter Guide](docs/parameter_guide.md)")


# ═══════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════
if stage == "🏠 Overview":
    st.markdown("# Optimal Trade Design")
    st.markdown("### A Calculus-Based Framework for Trading Decisions")

    st.markdown("""
    Every trading decision involves balancing competing forces. This app implements and animates
    three fundamental optimization problems — each with a clean closed-form solution derived
    from first-order conditions.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="formula-box">Stage 1 — Trade Size<br><br>max P(x) = αx − βx² − cx<br><br>x* = (α − c) / (2β)</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="formula-box">Stage 2 — Kelly Leverage<br><br>max R(ℓ) = ℓμ − ½ℓ²σ²<br><br>ℓ* = μ / σ²</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="formula-box">Stage 3 — Execution Time<br><br>min C(t) = k/t + λt<br><br>t* = √(k / λ)</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### The Unifying Principle")
    st.markdown("""
    All three are instances of the same structural pattern:

    > **Benefits grow at most linearly. Costs grow faster (quadratically, or as a convex pair).
    > An interior optimum exists where marginal benefit = marginal cost.**

    This principle recurs across quantitative finance: portfolio optimization, option replication,
    market making, and execution algorithms. Master it once and you'll recognize it everywhere.
    """)

    st.divider()
    st.info("Use the sidebar to navigate to each stage. Every chart animates step-by-step to show *how* the solution emerges, not just the final answer.")


# ═══════════════════════════════════════════════════════════════
# PAGE: STAGE 1 — TRADE SIZE
# ═══════════════════════════════════════════════════════════════
elif stage == "1️⃣  Trade Size":
    st.markdown("## Stage 1 — Trade Size Optimization")
    st.markdown("**Problem**: Given your edge $\\alpha$ and market impact $\\beta$, how many shares should you trade?")

    st.markdown("""
    $$P(x) = \\underbrace{\\alpha x}_{\\text{gross profit}} - \\underbrace{\\beta x^2}_{\\text{market impact}} - \\underbrace{cx}_{\\text{transaction costs}}$$
    """)

    # ── Parameter panel ──
    st.markdown('<div class="section-header">Parameters</div>', unsafe_allow_html=True)
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        alpha = st.slider("α — edge (¢/share)", 1, 15, 5, help="Expected profit per share in cents") / 100
    with col_p2:
        beta = st.slider("β — impact (×10⁻⁴)", 1, 20, 10, help="Market impact coefficient ×10⁻⁴") * 1e-4
    with col_p3:
        c_cost = st.slider("c — cost (¢/share)", 1, 10, 2, help="Transaction cost in cents") / 100
    with col_p4:
        x_max = st.slider("Chart range (shares)", 100, 2000, 600)

    # ── Compute ──
    def profit(x, a, b, c): return a * x - b * x**2 - c * x
    def x_star(a, b, c): return max(0, (a - c) / (2 * b))
    def x_breakeven(a, b, c): return (a - c) / b if a > c else 0

    xs = x_star(alpha, beta, c_cost)
    ps = profit(xs, alpha, beta, c_cost)
    xb = x_breakeven(alpha, beta, c_cost)

    # ── Metrics row ──
    st.markdown('<div class="section-header">Optimal Solution</div>', unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: metric_card("Optimal Size x*", f"{xs:,.0f} shares", f"x* = (α−c)/(2β)")
    with mc2: metric_card("Maximum Profit", f"${ps:.2f}", f"P(x*)")
    with mc3: metric_card("Break-Even Size", f"{xb:,.0f} shares", "P(x) = 0")
    with mc4: metric_card("Net Edge", f"${(alpha - c_cost)*100:.2f}¢/share", f"α − c = {(alpha-c_cost)*100:.2f}¢")

    if alpha <= c_cost:
        st.warning("⚠️  Edge α ≤ cost c — no profitable trade exists. Increase α or reduce c.")

    # ── Charts ──
    st.markdown('<div class="section-header">Visualizations</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📈 Profit Curve", "📊 Marginal Analysis", "🌡️ Sensitivity"])

    x_range = np.linspace(1, x_max, 400)
    profits = profit(x_range, alpha, beta, c_cost)

    with tab1:
        st.markdown("The profit curve peaks at $x^*$. Regions where $P(x) < 0$ are shaded red.")
        fig = animated_line(
            x_range, profits, n_steps=n_steps,
            name="P(x) = αx − βx² − cx", color=C["secondary"],
            x_label="Trade Size (shares)", y_label="Profit ($)",
            title="Profit Function",
            vline=xs, vline_label=f"x* = {xs:,.0f}",
            scatter_point=(xs, ps, f"  Max profit ${ps:.2f}", C["primary"]),
            fill_positive=True,
            height=420,
        )
        st.plotly_chart(fig, width='stretch')
        st.markdown(
            f'<div class="insight-box">At x* = {xs:,.0f} shares, P\'(x*) ≈ 0. '
            f'Trading more destroys value through impact; trading less leaves edge on the table.</div>',
            unsafe_allow_html=True,
        )

    with tab2:
        mb = np.full_like(x_range, alpha - c_cost)
        mc = 2 * beta * x_range
        fig2 = animated_line(
            x_range, mb, n_steps=n_steps,
            name=f"Marginal Benefit = α−c = {(alpha-c_cost)*100:.2f}¢",
            color=C["primary"],
            x_label="Trade Size (shares)", y_label="Marginal $/share",
            title="Marginal Analysis: MB = MC at Optimum",
            extra_traces=[{"x": x_range, "y": mc, "name": "Marginal Cost = 2βx",
                           "color": C["accent"], "dash": "solid"}],
            vline=xs, vline_label=f"x* = {xs:,.0f}",
            scatter_point=(xs, alpha - c_cost, f"  MB=MC = {(alpha-c_cost)*100:.2f}¢", C["secondary"]),
            height=420,
        )
        st.plotly_chart(fig2, width='stretch')
        st.markdown(
            f'<div class="insight-box">Marginal benefit (α−c) is constant per share. '
            f'Marginal cost (2βx) rises with size. They cross at x* = {xs:,.0f}.</div>',
            unsafe_allow_html=True,
        )

    with tab3:
        st.markdown("How does x* respond to each parameter?")
        sc1, sc2, sc3 = st.columns(3)

        alphas = np.linspace(0.02, 0.15, 60)
        betas  = np.linspace(5e-5, 4e-4, 60)
        costs  = np.linspace(0.001, 0.04, 60)

        x_a = [x_star(a, beta, c_cost) for a in alphas]
        x_b = [x_star(alpha, b, c_cost) for b in betas]
        x_c = [x_star(alpha, beta, c) for c in costs]

        def sens_fig(x_vals, y_vals, x_label, color, highlight_x, highlight_y, title):
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="lines",
                                     line=dict(color=color, width=2.5)))
            fig.add_trace(go.Scatter(x=[highlight_x], y=[highlight_y], mode="markers",
                                     marker=dict(color=C["accent"], size=10,
                                                 line=dict(color="white", width=2)),
                                     showlegend=False))
            fig.update_layout(template="plotly_dark", paper_bgcolor=C["bg"],
                               plot_bgcolor=C["bg"], height=280,
                               title=dict(text=title, font=dict(size=13)),
                               xaxis=dict(title=x_label, gridcolor="#1e2a38"),
                               yaxis=dict(title="x* (shares)", gridcolor="#1e2a38"),
                               margin=dict(l=40, r=10, t=40, b=40))
            return fig

        with sc1:
            st.plotly_chart(
                sens_fig(alphas*100, x_a, "α (¢/share)", C["primary"], alpha*100, xs, "∂x*/∂α > 0"),
                use_container_width=True)
        with sc2:
            st.plotly_chart(
                sens_fig(betas*1e4, x_b, "β (×10⁻⁴)", C["secondary"], beta*1e4, xs, "∂x*/∂β < 0"),
                use_container_width=True)
        with sc3:
            st.plotly_chart(
                sens_fig(costs*100, x_c, "c (¢/share)", C["accent"], c_cost*100, xs, "∂x*/∂c < 0"),
                use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: STAGE 2 — KELLY LEVERAGE
# ═══════════════════════════════════════════════════════════════
elif stage == "2️⃣  Kelly Leverage":
    st.markdown("## Stage 2 — Leverage Optimization (Kelly Criterion)")
    st.markdown("**Problem**: How much leverage maximizes long-run growth while accounting for risk?")

    st.markdown("""
    $$R(\\ell) = \\underbrace{\\ell\\mu}_{\\text{expected return}} - \\underbrace{\\frac{1}{2}\\ell^2\\sigma^2}_{\\text{risk penalty}} \\qquad \\Rightarrow \\qquad \\ell^* = \\frac{\\mu}{\\sigma^2}$$
    """)

    # ── Parameters ──
    st.markdown('<div class="section-header">Parameters</div>', unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        mu = st.slider("μ — expected annual return (%)", 2, 25, 8) / 100
    with col_p2:
        sigma = st.slider("σ — annual volatility (%)", 5, 60, 20) / 100
    with col_p3:
        ell_max = st.slider("Chart range (leverage x)", 3, 12, 6)

    # ── Compute ──
    def R(ell, mu, sigma): return ell * mu - 0.5 * ell**2 * sigma**2
    def kelly(mu, sigma): return mu / sigma**2

    ell_star = kelly(mu, sigma)
    r_star   = R(ell_star, mu, sigma)
    sharpe   = mu / sigma
    ell_be   = 2 * mu / sigma**2

    # ── Metrics ──
    st.markdown('<div class="section-header">Optimal Solution</div>', unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: metric_card("Kelly Leverage ℓ*", f"{ell_star:.2f}×", "ℓ* = μ/σ²")
    with mc2: metric_card("Max Risk-Adj Return", f"{r_star*100:.2f}%", "R(ℓ*) = SR²/2")
    with mc3: metric_card("Sharpe Ratio", f"{sharpe:.2f}", "μ/σ")
    with mc4: metric_card("Break-Even Leverage", f"{ell_be:.2f}×", "R(ℓ) = 0")

    if ell_star > 5:
        st.warning("⚠️  Kelly leverage > 5× — consider using fractional Kelly (½ or ¼) to reduce drawdown risk.")

    # ── Charts ──
    st.markdown('<div class="section-header">Visualizations</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["📈 R(ℓ) Curve", "📊 Risk-Return", "📉 Fractional Kelly", "🌡️ Vol Regime Table"])

    ell_range = np.linspace(0.05, ell_max, 400)
    returns   = R(ell_range, mu, sigma) * 100

    with tab1:
        fig = animated_line(
            ell_range, returns, n_steps=n_steps,
            name="R(ℓ) = ℓμ − ½ℓ²σ²", color=C["secondary"],
            x_label="Leverage (ℓ)", y_label="Risk-Adjusted Return (%)",
            title="Kelly Criterion: Risk-Adjusted Return",
            vline=ell_star, vline_label=f"ℓ* = {ell_star:.2f}×",
            scatter_point=(ell_star, r_star*100, f"  {r_star*100:.2f}%", C["primary"]),
            fill_positive=True,
            height=420,
        )
        st.plotly_chart(fig, width='stretch')
        st.markdown(
            f'<div class="insight-box">ℓ* = {ell_star:.2f}× — the leverage where marginal return (μ) '
            f'equals marginal risk cost (ℓσ²). Using more leverage destroys log wealth.</div>',
            unsafe_allow_html=True,
        )

    with tab2:
        exp_rets = ell_range * mu * 100
        vols     = ell_range * sigma * 100
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=vols, y=exp_rets, mode="lines",
                                  line=dict(color=C["secondary"], width=2.5),
                                  name="Leveraged portfolio"))
        fig2.add_trace(go.Scatter(
            x=[ell_star * sigma * 100], y=[ell_star * mu * 100],
            mode="markers+text", text=[f"  Kelly ({ell_star:.1f}×)"],
            textposition="top right",
            marker=dict(color=C["primary"], size=12, line=dict(color="white", width=2)),
            name=f"Kelly ({ell_star:.1f}×)"))
        fig2.add_trace(go.Scatter(
            x=[sigma * 100], y=[mu * 100],
            mode="markers+text", text=["  Unlevered (1×)"],
            textposition="top right",
            marker=dict(color=C["neutral"], size=10, line=dict(color="white", width=2)),
            name="Unlevered (1×)"))
        # Iso-utility lines
        for u in [r_star * 0.3, r_star * 0.6, r_star * 0.9]:
            v_curve = np.linspace(1, 120, 200)
            r_curve = u * 100 + 0.5 * (v_curve / 100) ** 2 / sigma ** 2 * mu * 100
            fig2.add_trace(go.Scatter(x=v_curve, y=r_curve, mode="lines",
                                      line=dict(color=C["neutral"], width=1, dash="dot"),
                                      showlegend=False, opacity=0.4))
        fig2.update_layout(template="plotly_dark", paper_bgcolor=C["bg"],
                            plot_bgcolor=C["bg"], height=420,
                            xaxis=dict(title="Portfolio Volatility (%)", gridcolor="#1e2a38"),
                            yaxis=dict(title="Expected Return (%)", gridcolor="#1e2a38"),
                            title="Risk-Return Tradeoff with Leverage",
                            margin=dict(l=50, r=20, t=50, b=50))
        st.plotly_chart(fig2, width='stretch')

    with tab3:
        fracs = [0.25, 0.5, 0.75, 1.0]
        frac_data = []
        for f in fracs:
            ell = f * ell_star
            frac_data.append({
                "Fraction": f"{f:.0%} Kelly",
                "Leverage": f"{ell:.2f}×",
                "E[Return] %": round(ell * mu * 100, 2),
                "Volatility %": round(ell * sigma * 100, 2),
                "Risk-Adj Return %": round(R(ell, mu, sigma) * 100, 2),
            })
        df_frac = pd.DataFrame(frac_data)

        fig3 = go.Figure()
        for _, row in df_frac.iterrows():
            fig3.add_trace(go.Bar(
                name=row["Fraction"],
                x=["E[Return] %", "Volatility %", "Risk-Adj Return %"],
                y=[row["E[Return] %"], row["Volatility %"], row["Risk-Adj Return %"]],
            ))
        fig3.update_layout(
            barmode="group", template="plotly_dark",
            paper_bgcolor=C["bg"], plot_bgcolor=C["bg"],
            height=380, title="Fractional Kelly Comparison",
            yaxis=dict(title="%", gridcolor="#1e2a38"),
            margin=dict(l=50, r=20, t=50, b=50),
        )
        st.plotly_chart(fig3, width='stretch')
        st.dataframe(df_frac.set_index("Fraction"), use_container_width=True)
        st.markdown(
            '<div class="insight-box">½ Kelly halves drawdown risk while losing only ~25% of expected log growth. '
            'Most practitioners use ½ or ¼ Kelly to hedge estimation error in μ.</div>',
            unsafe_allow_html=True,
        )

    with tab4:
        vols_table = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.60]
        rows = []
        for s in vols_table:
            ell_k = kelly(mu, s)
            rows.append({
                "Volatility σ": f"{s*100:.0f}%",
                "Kelly ℓ*": f"{ell_k:.2f}×",
                "½ Kelly": f"{ell_k/2:.2f}×",
                "Risk-Adj Return": f"{R(ell_k, mu, s)*100:.2f}%",
                "Sharpe": f"{mu/s:.2f}",
                "Current?": "✅" if abs(s - sigma) < 0.01 else "",
            })
        st.dataframe(pd.DataFrame(rows).set_index("Volatility σ"), use_container_width=True)
        st.markdown(
            f'<div class="insight-box">As σ increases from 10% to 60%, Kelly leverage drops from '
            f'{kelly(mu, 0.10):.1f}× to {kelly(mu, 0.60):.2f}×. '
            f'Volatility punishes leverage quadratically.</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════
# PAGE: STAGE 3 — EXECUTION TIMING
# ═══════════════════════════════════════════════════════════════
elif stage == "3️⃣  Execution Timing":
    st.markdown("## Stage 3 — Execution Time Optimization")
    st.markdown("**Problem**: How long should you spread your trade to minimize slippage *and* opportunity cost?")

    st.markdown("""
    $$C(t) = \\underbrace{\\frac{k}{t}}_{\\text{slippage}} + \\underbrace{\\lambda t}_{\\text{opportunity cost}} \\qquad \\Rightarrow \\qquad t^* = \\sqrt{\\frac{k}{\\lambda}}$$
    """)

    # ── Parameters ──
    st.markdown('<div class="section-header">Parameters</div>', unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        k = st.slider("k — slippage intensity", 100, 5000, 1000, step=100)
    with col_p2:
        lam = st.slider("λ — opportunity cost rate", 1, 20, 5)
    with col_p3:
        t_max = st.slider("Chart range (minutes)", 30, 200, 90)

    # ── Compute ──
    def exec_cost(t, k, lam): return k / t + lam * t
    def t_star(k, lam): return np.sqrt(k / lam)

    ts     = t_star(k, lam)
    cs     = exec_cost(ts, k, lam)
    slip_s = k / ts
    opp_s  = lam * ts

    # ── Metrics ──
    st.markdown('<div class="section-header">Optimal Solution</div>', unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: metric_card("Optimal Time t*", f"{ts:.1f} min", "t* = √(k/λ)")
    with mc2: metric_card("Minimum Total Cost", f"${cs:.2f}", "C(t*) = 2√(kλ)")
    with mc3: metric_card("Slippage @ t*", f"${slip_s:.2f}", "k/t*")
    with mc4: metric_card("Opp. Cost @ t*", f"${opp_s:.2f}", "λt*  (= slippage)")

    # ── Charts ──
    st.markdown('<div class="section-header">Visualizations</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📈 Cost Curve (U-shape)", "📊 Component Breakdown", "🌡️ λ Regime Analysis"])

    # Start at ts/4 so the spike at t≈0 doesn't crush the chart
    t_start = max(3.0, ts / 4)
    t_range = np.linspace(t_start, t_max, 400)
    total   = exec_cost(t_range, k, lam)
    slip    = k / t_range
    opp     = lam * t_range
    y_ceil  = cs * 4   # cap y-axis at 4× the minimum so U-shape is visible

    with tab1:
        fig = animated_line(
            t_range, total, n_steps=n_steps,
            name="Total: C(t) = k/t + λt", color=C["secondary"],
            x_label="Execution Time (minutes)", y_label="Cost ($)",
            title="Execution Cost — U-Shaped Tradeoff",
            extra_traces=[
                {"x": t_range, "y": slip, "name": "Slippage: k/t",
                 "color": C["accent"], "dash": "dash"},
                {"x": t_range, "y": opp, "name": "Opportunity: λt",
                 "color": C["primary"], "dash": "dash"},
            ],
            vline=ts, vline_label=f"t* = {ts:.1f} min",
            scatter_point=(ts, cs, f"  Min cost ${cs:.2f}", C["secondary"]),
            height=440,
        )
        fig.update_layout(yaxis=dict(range=[0, y_ceil]))
        st.plotly_chart(fig, width='stretch')
        st.markdown(
            f'<div class="insight-box">At t* = {ts:.1f} min, slippage (${slip_s:.2f}) exactly equals '
            f'opportunity cost (${opp_s:.2f}). This is the AM-GM equality condition — '
            f'the minimum of two terms that multiply to a constant.</div>',
            unsafe_allow_html=True,
        )

    with tab2:
        # Animated stacked area — build component areas step by step
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=t_range, y=opp,
            fill="tozeroy", mode="lines",
            name="Opportunity cost: λt",
            line=dict(color=C["primary"], width=1.5),
            fillcolor="rgba(46,204,113,0.2)",
        ))
        fig2.add_trace(go.Scatter(
            x=t_range, y=total,
            fill="tonexty", mode="lines",
            name="Slippage: k/t",
            line=dict(color=C["accent"], width=1.5),
            fillcolor="rgba(231,76,60,0.2)",
        ))
        fig2.add_vline(x=ts, line=dict(color=C["neutral"], dash="dash", width=1.5))
        fig2.add_annotation(x=ts, y=cs * 1.05,
                             text=f"t* = {ts:.1f} min<br>Total = ${cs:.2f}",
                             showarrow=False, bgcolor=C["surface"],
                             font=dict(color="white", size=11))
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor=C["bg"], plot_bgcolor=C["bg"],
            height=420, title="Cost Component Breakdown",
            xaxis=dict(title="Execution Time (minutes)", gridcolor="#1e2a38"),
            yaxis=dict(title="Cost ($)", gridcolor="#1e2a38", range=[0, y_ceil]),
            margin=dict(l=50, r=20, t=50, b=50),
        )
        st.plotly_chart(fig2, width='stretch')

    with tab3:
        lambdas = [1, 2, 5, 10, 20]
        fig3 = go.Figure()
        palette = px.colors.sequential.Reds[2:]
        y_ceil3 = exec_cost(t_start, k, max(lambdas)) * 0.6
        for i, l in enumerate(lambdas):
            t_r3 = np.linspace(t_start, t_max, 400)
            costs_l = exec_cost(t_r3, k, l)
            ts_l = t_star(k, l)
            cs_l = exec_cost(ts_l, k, l)
            fig3.add_trace(go.Scatter(
                x=t_r3, y=costs_l,
                mode="lines", name=f"λ = {l}  (t* = {ts_l:.1f} min)",
                line=dict(color=palette[i % len(palette)], width=2),
            ))
            fig3.add_trace(go.Scatter(
                x=[ts_l], y=[cs_l], mode="markers",
                marker=dict(color=palette[i % len(palette)], size=9,
                            line=dict(color="white", width=1.5)),
                showlegend=False,
            ))
        fig3.update_layout(
            template="plotly_dark", paper_bgcolor=C["bg"], plot_bgcolor=C["bg"],
            height=440, title="Impact of Market Drift λ on Optimal Execution",
            xaxis=dict(title="Execution Time (minutes)", gridcolor="#1e2a38",
                       range=[0, t_max]),
            yaxis=dict(title="Cost ($)", gridcolor="#1e2a38", range=[0, y_ceil3]),
            margin=dict(l=50, r=20, t=50, b=50),
        )
        st.plotly_chart(fig3, width='stretch')
        st.markdown(
            '<div class="insight-box">As λ increases (faster-decaying signal), the optimal execution '
            'time shortens. In trending or volatile markets, execute aggressively. '
            'For slow signals, execute patiently.</div>',
            unsafe_allow_html=True,
        )

        # Regime table
        rows = []
        for l in lambdas:
            ts_l = t_star(k, l)
            rows.append({
                "λ (drift rate)": l,
                "t* (min)": f"{ts_l:.1f}",
                "Min Cost ($)": f"{exec_cost(ts_l, k, l):.2f}",
                "Signal type": ("Very slow" if l <= 1 else "Slow" if l <= 3
                                else "Medium" if l <= 7 else "Fast" if l <= 15 else "Very fast"),
            })
        st.dataframe(pd.DataFrame(rows).set_index("λ (drift rate)"), use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: UNIFIED VIEW
# ═══════════════════════════════════════════════════════════════
elif stage == "🔗 Unified View":
    st.markdown("## Unified View — The Common Structure")
    st.markdown("All three problems share the same mathematical skeleton.")

    st.markdown("""
    | Problem | Benefit | Cost | Solution |
    |---------|---------|------|----------|
    | Trade Size | α·x (linear) | β·x² (quadratic) | x* = (α−c)/(2β) |
    | Kelly Leverage | ℓ·μ (linear) | ½ℓ²σ² (quadratic) | ℓ* = μ/σ² |
    | Execution | — | k/t + λt (convex pair) | t* = √(k/λ) |
    """)

    # Global params
    st.markdown('<div class="section-header">Parameters (all stages)</div>', unsafe_allow_html=True)
    row1 = st.columns(3)
    with row1[0]:
        alpha_u = st.slider("α edge (¢)", 1, 15, 5, key="u_a") / 100
        beta_u  = st.slider("β impact (×10⁻⁴)", 1, 20, 10, key="u_b") * 1e-4
        c_u     = st.slider("c cost (¢)", 1, 10, 2, key="u_c") / 100
    with row1[1]:
        mu_u    = st.slider("μ annual return (%)", 2, 25, 8, key="u_mu") / 100
        sigma_u = st.slider("σ volatility (%)", 5, 60, 20, key="u_sg") / 100
    with row1[2]:
        k_u     = st.slider("k slippage", 100, 5000, 1000, step=100, key="u_k")
        lam_u   = st.slider("λ drift rate", 1, 20, 5, key="u_lm")

    # Compute
    xs_u  = max(0, (alpha_u - c_u) / (2 * beta_u))
    ps_u  = alpha_u * xs_u - beta_u * xs_u**2 - c_u * xs_u
    ell_u = mu_u / sigma_u**2
    ru_u  = ell_u * mu_u - 0.5 * ell_u**2 * sigma_u**2
    ts_u  = np.sqrt(k_u / lam_u)
    cs_u  = k_u / ts_u + lam_u * ts_u

    # Summary metrics
    st.markdown('<div class="section-header">Summary</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Trade Size x*", f"{xs_u:,.0f} shares", f"Max profit: ${ps_u:.2f}")
    with col2: metric_card("Kelly Leverage ℓ*", f"{ell_u:.2f}×", f"Risk-adj return: {ru_u*100:.2f}%")
    with col3: metric_card("Execution Time t*", f"{ts_u:.1f} min", f"Min cost: ${cs_u:.2f}")

    # Side-by-side trio
    st.markdown('<div class="section-header">All Three Optima</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    def mini_fig(x, y, title, vline, vline_label, sp, color, xl, yl):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines",
                                 line=dict(color=color, width=2.5), name=""))
        fig.add_vline(x=vline, line=dict(color=C["primary"], dash="dash", width=1.5))
        if sp:
            fig.add_trace(go.Scatter(x=[sp[0]], y=[sp[1]], mode="markers",
                                     marker=dict(color=C["primary"], size=11,
                                                 line=dict(color="white", width=2)),
                                     showlegend=False))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor=C["bg"], plot_bgcolor=C["bg"],
            height=300, title=dict(text=title, font=dict(size=13)),
            xaxis=dict(title=xl, gridcolor="#1e2a38", showgrid=True),
            yaxis=dict(title=yl, gridcolor="#1e2a38", showgrid=True),
            margin=dict(l=40, r=10, t=45, b=40),
            showlegend=False,
        )
        return fig

    x_r = np.linspace(1, xs_u * 2.5 if xs_u > 0 else 500, 300)
    e_r = np.linspace(0.05, max(ell_u * 2, 4), 300)
    t_r = np.linspace(1, ts_u * 3, 300)

    with c1:
        st.plotly_chart(mini_fig(
            x_r,
            alpha_u * x_r - beta_u * x_r**2 - c_u * x_r,
            f"Trade Size: x* = {xs_u:,.0f}",
            xs_u, f"x*={xs_u:,.0f}", (xs_u, ps_u),
            C["secondary"], "Shares", "P(x) ($)"),
            use_container_width=True)
        st.latex(r"x^* = \frac{\alpha - c}{2\beta}")

    with c2:
        st.plotly_chart(mini_fig(
            e_r,
            (e_r * mu_u - 0.5 * e_r**2 * sigma_u**2) * 100,
            f"Kelly: ℓ* = {ell_u:.2f}×",
            ell_u, f"ℓ*={ell_u:.2f}×", (ell_u, ru_u * 100),
            C["secondary"], "Leverage ℓ", "R(ℓ) (%)"),
            use_container_width=True)
        st.latex(r"\ell^* = \frac{\mu}{\sigma^2}")

    with c3:
        st.plotly_chart(mini_fig(
            t_r,
            k_u / t_r + lam_u * t_r,
            f"Execution: t* = {ts_u:.1f} min",
            ts_u, f"t*={ts_u:.1f}", (ts_u, cs_u),
            C["secondary"], "Time (min)", "C(t) ($)"),
            use_container_width=True)
        st.latex(r"t^* = \sqrt{\frac{k}{\lambda}}")

    # Insight
    st.divider()
    st.markdown("### The Pattern")
    st.markdown("""
    <div class="insight-box">
    Interior optima exist because <strong>one force diminishes while another accelerates</strong>.
    In each case the first-order condition MB = MC (or dC/dt = 0) yields a clean closed form.
    The skill is recognizing this structure when it appears in novel problems — 
    portfolio optimization, option replication, market making — and applying the same machinery.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    | Principle | Trade Size | Leverage | Execution |
    |-----------|-----------|----------|-----------|
    | **Diminishing force** | Constant edge α−c | Constant return μ | Slippage falls as 1/t |
    | **Accelerating force** | Impact 2βx rises | Risk cost ℓσ² rises | Drift λt rises |
    | **Balance point** | MB = MC | dR/dℓ = 0 | dC/dt = 0 |
    | **Formula type** | Linear / quadratic | Linear / quadratic | Harmonic / linear |
    """)
