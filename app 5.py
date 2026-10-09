"""NFHS-5 Delhi: Financial Access vs. Financial Autonomy.

Single-file Streamlit dashboard. Every number below was supplied by the project
team as a published aggregate statistic from the NFHS-5 Delhi report excerpt.
Nothing is estimated, imputed or derived except the simple percentage-point
differences calculated in this file. All figures require verification against
the original report.
"""

from decimal import ROUND_HALF_UP, Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Financial access vs. autonomy | NFHS-5 Delhi",
    page_icon="📊",
    layout="wide",
)

# ----------------------------------------------------------------------------
# Design tokens (all text/background pairs checked for WCAG AA contrast)
# ----------------------------------------------------------------------------
INK = "#14213D"      # primary text
MUTED = "#4A5568"    # secondary text
BLUE = "#1F5FA8"     # base not stated / primary series
ORANGE = "#B45309"   # contrasting series / warnings
SURFACE = "#FFFFFF"
PAGE = "#F4F7FA"
LINE = "#D5DDE6"

SOURCE = "Supplied NFHS-5 Delhi report excerpt (team-provided published aggregate)"
VERIFY = "Requires verification against original report"

# ----------------------------------------------------------------------------
# Data: exactly the figures supplied, no more
# ----------------------------------------------------------------------------
NOT_STATED = "Women (base not stated in supplied figures)"
MOBILE_BASE = "Women who have a mobile phone"

indicators = pd.DataFrame(
    [
        ("Has a bank or savings account they themselves use", 73, NOT_STATED, "Overall"),
        ("Has money they can decide how to use", 57, NOT_STATED, "Overall"),
        ("Uses a mobile phone for financial transactions", 37, MOBILE_BASE, "Overall"),
        ("Knows of a microcredit programme in their area", 32, NOT_STATED, "Overall"),
        ("Has ever taken a microcredit-programme loan", 6, NOT_STATED, "Overall"),
    ],
    columns=["indicator", "value_pct", "denominator", "group"],
)
indicators["denominator_status"] = indicators["denominator"].map(
    lambda d: "Stated" if d == MOBILE_BASE else "Not stated"
)

rural_urban = pd.DataFrame(
    [("Rural", 47), ("Urban", 57)], columns=["residence", "value_pct"]
)
education = pd.DataFrame(
    [("No schooling", 7), ("12+ years of schooling", 57)],
    columns=["education", "value_pct"],
)

# Calculated differences (percentage points, not percent)
ru_gap = int(
    rural_urban.loc[rural_urban.residence == "Urban", "value_pct"].iloc[0]
    - rural_urban.loc[rural_urban.residence == "Rural", "value_pct"].iloc[0]
)
edu_gap = int(
    education.loc[education.education == "12+ years of schooling", "value_pct"].iloc[0]
    - education.loc[education.education == "No schooling", "value_pct"].iloc[0]
)
access_vs_control_gap = int(indicators.value_pct[0] - indicators.value_pct[1])

# CSV export: every supplied figure in one tidy table
export = pd.concat(
    [
        indicators.assign(
            comparison="Overall indicator",
            subgroup="All women",
        )[["comparison", "subgroup", "indicator", "value_pct", "denominator", "denominator_status"]],
        rural_urban.assign(
            comparison="Rural vs urban",
            indicator="Control over money (assumed to be the 'money they can decide how to use' indicator; verify)",
            denominator=NOT_STATED,
            denominator_status="Not stated",
        ).rename(columns={"residence": "subgroup"})[
            ["comparison", "subgroup", "indicator", "value_pct", "denominator", "denominator_status"]
        ],
        education.assign(
            comparison="Education",
            indicator="Uses a mobile phone for financial transactions",
            denominator=MOBILE_BASE,
            denominator_status="Stated",
        ).rename(columns={"education": "subgroup"})[
            ["comparison", "subgroup", "indicator", "value_pct", "denominator", "denominator_status"]
        ],
    ],
    ignore_index=True,
)
export["geography"] = "Delhi (NCT)"
export["source"] = SOURCE
export["verification_status"] = VERIFY
csv_bytes = export.to_csv(index=False).encode("utf-8")

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600&family=Source+Serif+4:wght@500;600&display=swap');
html, body, [class*="css"], .stMarkdown, p, li, label {{
  font-family: 'Public Sans', 'Segoe UI', system-ui, sans-serif;
  color: {INK};
}}
.stApp {{ background: {PAGE}; }}
.block-container {{ max-width: 1150px; padding-top: 2.2rem; padding-bottom: 4rem; }}
h1, h2, h3 {{ font-family: 'Source Serif 4', Georgia, serif; color: {INK}; letter-spacing: -0.01em; }}
h2 {{ margin-top: 2.6rem; font-size: 1.6rem; }}
.hero {{ border-left: 6px solid {BLUE}; padding: 0.4rem 0 0.4rem 1.2rem; margin-bottom: 1.2rem; }}
.hero h1 {{ font-size: 2.3rem; line-height: 1.2; margin: 0 0 0.5rem 0; }}
.hero p {{ font-size: 1.05rem; color: {MUTED}; max-width: 70ch; margin: 0; line-height: 1.6; }}
.banner {{ background: #FFF7E6; border: 1px solid #E8C37A; border-radius: 6px;
  padding: 0.8rem 1rem; font-size: 0.95rem; color: #5B3A00; line-height: 1.55; }}
.kpi {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 8px;
  padding: 1rem 1rem 0.9rem 1rem; height: 100%; }}
.kpi .num {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 2.4rem; font-weight: 600; color: {BLUE}; line-height: 1; }}
.kpi .lbl {{ font-size: 0.93rem; margin-top: 0.5rem; line-height: 1.4; }}
.kpi .base {{ font-size: 0.82rem; color: {MUTED}; margin-top: 0.5rem; line-height: 1.35; }}
.card {{ background: {SURFACE}; border: 1px solid {LINE}; border-top: 4px solid {BLUE};
  border-radius: 8px; padding: 1.1rem 1.2rem; height: 100%; }}
.card h3 {{ font-size: 1.1rem; margin: 0 0 0.6rem 0; line-height: 1.3; }}
.card p {{ font-size: 0.93rem; line-height: 1.55; margin: 0 0 0.7rem 0; }}
.card .tag {{ font-weight: 600; color: {BLUE}; }}
.card .caveat {{ color: {MUTED}; font-size: 0.86rem; }}
.small {{ color: {MUTED}; font-size: 0.88rem; line-height: 1.5; }}
a:focus, button:focus, [tabindex]:focus {{ outline: 3px solid {ORANGE} !important; outline-offset: 2px; }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
</style>
""",
    unsafe_allow_html=True,
)


def style_fig(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family="Public Sans, Segoe UI, sans-serif", size=14, color=INK),
        margin=dict(l=10, r=20, t=40, b=40),
        legend=dict(orientation="h", y=-0.2, x=0),
    )
    fig.update_xaxes(gridcolor=LINE, zeroline=False)
    fig.update_yaxes(gridcolor=LINE)
    return fig


# ----------------------------------------------------------------------------
# 1. Header
# ----------------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
  <h1>Financial access vs. financial autonomy for women in Delhi</h1>
  <p>Many women in Delhi have access to financial tools, but fewer report having money they
  can decide how to use. This dashboard sets out published NFHS-5 figures so
  public-welfare teams can see where access and autonomy diverge, and where to look next.</p>
</div>
<div class="banner">
  <strong>Data status:</strong> All figures are published aggregate statistics from the NFHS-5 Delhi
  report excerpt supplied by our team. They have <strong>not</strong> been independently checked.
  Verify every number against the original report before external use. Findings describe Delhi only
  and are not representative of all India.
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# 2. KPI cards
# ----------------------------------------------------------------------------
st.markdown("## Headline indicators")
cols = st.columns(5)
short_labels = [
    "Women with a bank or savings account they use themselves",
    "Women with money they can decide how to use",
    "Women with a mobile phone who use it for financial transactions",
    "Women who know of a microcredit programme in their area",
    "Women who have ever taken a microcredit-programme loan",
]
for col, (_, row), label in zip(cols, indicators.iterrows(), short_labels):
    base = (
        "Base: women with a mobile phone"
        if row.denominator_status == "Stated"
        else "Base: not stated in supplied figures"
    )
    col.markdown(
        f"""<div class="kpi" role="group" aria-label="{label}: {row.value_pct} percent">
        <div class="num">{row.value_pct}%</div>
        <div class="lbl">{label}</div>
        <div class="base">{base}</div></div>""",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# 3. Indicator chart with denominator warnings
# ----------------------------------------------------------------------------
st.markdown("## Financial indicators side by side")
st.warning(
    "**Read with care.** The bars do not all use the same base. The mobile-transaction figure is "
    "calculated among women who have a mobile phone. For the other four, the supplied figures do not "
    "state the base, so we cannot confirm they are comparable. Do not compute ratios between bars "
    "(for example, loans relative to awareness) without checking the report."
)
choices = st.multiselect(
    "Choose indicators to show",
    options=list(indicators.indicator),
    default=list(indicators.indicator),
)
view = indicators[indicators.indicator.isin(choices)]
if view.empty:
    st.info("Select at least one indicator to draw the chart.")
else:
    fig = go.Figure()
    for status, color in [("Stated", ORANGE), ("Not stated", BLUE)]:
        sub = view[view.denominator_status == status]
        if sub.empty:
            continue
        legend_name = (
            "Base stated: women with a mobile phone"
            if status == "Stated"
            else "Base not stated in supplied figures"
        )
        fig.add_trace(
            go.Bar(
                y=sub.indicator,
                x=sub.value_pct,
                orientation="h",
                name=legend_name,
                marker_color=color,
                text=[f"{v}%" for v in sub.value_pct],
                textposition="outside",
                customdata=sub[["denominator"]],
                hovertemplate="<b>%{y}</b><br>%{x}%<br>Base: %{customdata[0]}<extra></extra>",
            )
        )
    fig.update_xaxes(range=[0, 100], title="Percent of women (axis starts at 0)", ticksuffix="%")
    fig.update_yaxes(autorange="reversed")
    style_fig(fig, height=140 + 62 * len(view))
    st.plotly_chart(fig, width="stretch")
    st.caption("Source: " + SOURCE + ". " + VERIFY + ".")

with st.expander("View this chart as a table"):
    st.dataframe(
        view[["indicator", "value_pct", "denominator"]].rename(
            columns={"indicator": "Indicator", "value_pct": "Percent", "denominator": "Base"}
        ),
        hide_index=True,
        width="stretch",
    )

# ----------------------------------------------------------------------------
# 4. Rural vs urban
# ----------------------------------------------------------------------------
st.markdown("## Control over money: rural vs. urban")
c1, c2 = st.columns([3, 2], gap="large")
with c1:
    fig = go.Figure(
        go.Bar(
            x=rural_urban.residence,
            y=rural_urban.value_pct,
            marker_color=[ORANGE, BLUE],
            text=[f"{v}%" for v in rural_urban.value_pct],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y}%<extra></extra>",
        )
    )
    fig.add_annotation(
        x=0.5, xref="paper", y=84, yref="y",
        text=f"<b>Urban is {ru_gap} percentage points higher than rural</b> (57 − 47)",
        showarrow=False, font=dict(size=14, color=INK),
    )
    fig.update_yaxes(range=[0, 100], title="Percent of women (axis starts at 0)", ticksuffix="%")
    style_fig(fig, height=380)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")
with c2:
    st.metric("Urban minus rural", f"{ru_gap} percentage points")
    st.markdown(
        f"""<p class="small">The difference is 57% − 47% = {ru_gap} <em>percentage points</em>.
        It is not a 10% difference. Relative to rural women, it is about
        {ru_gap / 47 * 100:.0f}% higher, but the percentage-point gap is the clearer measure.</p>
        <p class="small"><strong>Not available from supplied figures:</strong> sample sizes, confidence
        intervals or a significance test. We cannot say whether the gap is statistically reliable,
        and rural Delhi may be a small group. We have also assumed this is the same indicator as
        "money they can decide how to use"; please verify.</p>""",
        unsafe_allow_html=True,
    )
st.caption("Source: " + SOURCE + ". " + VERIFY + ".")

# ----------------------------------------------------------------------------
# 5. Education
# ----------------------------------------------------------------------------
st.markdown("## Mobile financial transactions by education")
c1, c2 = st.columns([3, 2], gap="large")
with c1:
    fig = go.Figure(
        go.Bar(
            x=education.education,
            y=education.value_pct,
            marker_color=[ORANGE, BLUE],
            text=[f"{v}%" for v in education.value_pct],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y}% of women with a mobile phone<extra></extra>",
        )
    )
    fig.update_yaxes(range=[0, 100], title="Percent of women with a mobile phone", ticksuffix="%")
    style_fig(fig, height=380)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")
with c2:
    st.metric("12+ years minus no schooling", f"{edu_gap} percentage points")
    st.markdown(
        """<p class="small"><strong>Base:</strong> women who have a mobile phone, so women without
        a phone are not counted here.</p>
        <p class="small"><strong>Not available:</strong> figures for intermediate education levels, and
        sample sizes. Only two groups were supplied, so the pattern between them cannot be described.</p>""",
        unsafe_allow_html=True,
    )
st.caption("Source: " + SOURCE + ". " + VERIFY + ".")

# ----------------------------------------------------------------------------
# 6. Insight cards
# ----------------------------------------------------------------------------
st.markdown("## What the figures suggest")
st.markdown(
    '<p class="small">Each card separates what the figures show from what it might mean for policy. '
    "These are descriptive observations, not causal claims.</p>",
    unsafe_allow_html=True,
)
i1, i2, i3 = st.columns(3, gap="medium")
i1.markdown(
    f"""<div class="card"><h3>Having an account and deciding how to use money are different measures</h3>
    <p><span class="tag">What the figures show:</span> 73% have a bank or savings account they use,
    and 57% have money they can decide how to use, a gap of {access_vs_control_gap} percentage points.</p>
    <p><span class="tag">Public-welfare implication:</span> Programmes that open accounts may not by
    themselves translate into control over money. Pairing them with financial-autonomy components is worth considering.</p>
    <p class="caveat">Caveat: the two figures are different indicators and their bases are not stated,
    so this gap is not a measure of women who have an account but no control.</p></div>""",
    unsafe_allow_html=True,
)
i2.markdown(
    f"""<div class="card"><h3>Rural women report less control over money</h3>
    <p><span class="tag">What the figures show:</span> 47% of rural women and 57% of urban women
    report control over money, a {ru_gap} percentage-point difference.</p>
    <p><span class="tag">Public-welfare implication:</span> Rural Delhi may merit targeted outreach and
    follow-up analysis of what drives the difference.</p>
    <p class="caveat">Caveat: sample sizes and uncertainty were not supplied, and residence is
    associated with many other characteristics. We cannot say rural residence causes the gap.</p></div>""",
    unsafe_allow_html=True,
)
i3.markdown(
    f"""<div class="card"><h3>Mobile financial use varies sharply with schooling</h3>
    <p><span class="tag">What the figures show:</span> Among women with a mobile phone, 7% with no
    schooling and 57% with 12+ years use it for financial transactions, a {edu_gap} percentage-point difference.</p>
    <p><span class="tag">Public-welfare implication:</span> Digital financial literacy support for
    women with little schooling could be considered, with design tested for accessibility.</p>
    <p class="caveat">Caveat: only two education groups were supplied. Education is linked to age, wealth
    and other factors, so this is an association, not evidence that schooling causes the difference.</p></div>""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# 6b. Before vs. After: Financial Empowerment Intervention (hypothetical simulator)
# ----------------------------------------------------------------------------
GREEN = "#1B7F3B"  # increase (AA on white)
RED = "#B3261E"    # decrease (AA on white)
SIM_WARNING = (
    "Illustrative scenario only. Follow-up values are hypothetical assumptions, not measured "
    "outcomes. NFHS-5 baseline statistics do not establish intervention effectiveness."
)
SCENARIO_NAME = "Illustrative Financial Empowerment Programme"

# key, short label, baseline (from `indicators`, same order), illustrative example value
SIM_META = [
    ("acct", "Personal-use bank account", 80),
    ("ctrl", "Money they can decide how to use", 65),
    ("mob", "Mobile phone used for financial transactions", 50),
    ("aware", "Aware of a microcredit programme", 50),
    ("loan", "Has taken a microcredit-programme loan", 8),
]
SIM = pd.DataFrame(
    [
        dict(
            key=k, label=lbl, full=indicators.indicator[i], baseline=int(indicators.value_pct[i]),
            example=ex, denominator=indicators.denominator[i],
        )
        for i, (k, lbl, ex) in enumerate(SIM_META)
    ]
)


def round_half_up(x: float, places: int = 1) -> float:
    q = Decimal(1).scaleb(-places)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def _apply_preset():
    for _, r in SIM.iterrows():
        st.session_state[f"sim_{r.key}"] = (
            r.example if st.session_state["sim_preset"].startswith("Example") else r.baseline
        )


st.markdown("## Before vs. After: Financial Empowerment Intervention")
st.error("**" + SIM_WARNING + "**")
st.markdown(
    f"""<p class="small"><strong>Scenario:</strong> {SCENARIO_NAME}. <strong>Baseline</strong> = the
    published NFHS-5 Delhi figures from the supplied report excerpt, <em>pending verification</em>.
    <strong>Follow-up</strong> = values <em>you</em> assume using the sliders. No follow-up survey exists
    in this dashboard; nothing below is an observed result.</p>""",
    unsafe_allow_html=True,
)

if "sim_preset" not in st.session_state:
    st.session_state["sim_preset"] = "Example assumptions (arbitrary, for demonstration)"
    _apply_preset()
st.radio(
    "Starting assumptions",
    ["Example assumptions (arbitrary, for demonstration)", "No change (follow-up equals baseline)"],
    key="sim_preset", on_change=_apply_preset, horizontal=True,
)
st.caption(
    "The example values are arbitrary round numbers chosen only to demonstrate the calculations. "
    "They are not forecasts and have no evidence behind them. Replace them with your own assumptions."
)

st.markdown("**Set hypothetical follow-up values (0–100%)**")
sl1, sl2 = st.columns(2, gap="large")
follow = {}
for n, r in SIM.iterrows():
    with (sl1 if n % 2 == 0 else sl2):
        follow[r.key] = st.slider(
            f"{r.label} (baseline {r.baseline}%)",
            min_value=0, max_value=100, step=1, key=f"sim_{r.key}",
            help=f"Base: {r.denominator}",
        )

sim = SIM.copy()
sim["followup"] = sim.key.map(follow).astype(int)
sim["pp_change"] = sim.followup - sim.baseline
sim["rel_change"] = [
    round_half_up((f - b) / b * 100) if b > 0 else None
    for b, f in zip(sim.baseline, sim.followup)
]


def _fmt_pp(v: int) -> str:
    return f"{v:+d} pp" if v else "0 pp"


def _fmt_rel(v) -> str:
    return "n/a (baseline is 0)" if v is None else (f"{v:+.1f}%" if v else "0.0%")


def _dir(v: int):
    if v > 0:
        return GREEN, "▲ increase"
    if v < 0:
        return RED, "▼ decrease"
    return MUTED, "■ no change"


st.markdown("### Before-and-after indicator cards")
card_cols = st.columns(5, gap="small")
for col, (_, r) in zip(card_cols, sim.iterrows()):
    color, word = _dir(r.pp_change)
    col.markdown(
        f"""<div class="kpi" role="group" aria-label="{r.label}: baseline {r.baseline} percent, hypothetical follow-up {r.followup} percent">
        <div class="lbl"><strong>{r.label}</strong></div>
        <div class="small" style="margin-top:.5rem">Baseline (published, unverified)</div>
        <div class="num" style="font-size:1.7rem">{r.baseline}%</div>
        <div class="small" style="margin-top:.4rem">Follow-up (hypothetical)</div>
        <div class="num" style="font-size:1.7rem;color:{ORANGE}">{r.followup}%</div>
        <div style="margin-top:.6rem;font-weight:600;color:{color}">{word}: {_fmt_pp(r.pp_change)}</div>
        <div style="color:{color};font-size:.9rem">Relative: {_fmt_rel(r.rel_change)}</div>
        <div class="base">Base: {r.denominator}</div></div>""",
        unsafe_allow_html=True,
    )
st.caption(
    "Green = value assumed higher than baseline; red = assumed lower. Direction is not automatically "
    "better or worse welfare for every indicator."
)

st.markdown("### Baseline vs. hypothetical follow-up")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=sim.label, y=sim.baseline, name="Baseline (published NFHS-5 Delhi, unverified)",
    marker_color=BLUE, text=[f"{v}%" for v in sim.baseline], textposition="outside",
    hovertemplate="<b>%{x}</b><br>Baseline: %{y}%<extra></extra>",
))
fig.add_trace(go.Bar(
    x=sim.label, y=sim.followup, name="Follow-up: hypothetical assumption (not observed)",
    marker=dict(color=ORANGE, pattern=dict(shape="/")),
    text=[f"{v}%" for v in sim.followup], textposition="outside",
    hovertemplate="<b>%{x}</b><br>Hypothetical follow-up: %{y}%<extra></extra>",
))
fig.update_layout(barmode="group")
fig.update_yaxes(range=[0, 110], title="Percent (axis starts at 0)", ticksuffix="%")
fig.update_xaxes(tickangle=0)
style_fig(fig, height=430)
st.plotly_chart(fig, width="stretch")

st.markdown("### Percentage-point change from baseline")
fig = go.Figure(go.Bar(
    x=sim.label, y=sim.pp_change,
    marker_color=[GREEN if v > 0 else RED if v < 0 else MUTED for v in sim.pp_change],
    text=[_fmt_pp(v) for v in sim.pp_change], textposition="outside",
    customdata=[_fmt_rel(v) for v in sim.rel_change],
    hovertemplate="<b>%{x}</b><br>Change: %{y} pp<br>Relative: %{customdata}<extra></extra>",
))
lim = max(10, int(sim.pp_change.abs().max()) + 12)
fig.update_yaxes(range=[-lim, lim], title="Percentage points", zeroline=True, zerolinecolor=INK)
fig.update_xaxes(tickangle=0)
style_fig(fig, height=380)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")

with st.expander("View calculations as a table"):
    st.dataframe(
        sim.assign(
            relative=sim.rel_change.map(_fmt_rel), pp=sim.pp_change.map(_fmt_pp)
        )[["full", "baseline", "followup", "pp", "relative", "denominator"]].rename(columns={
            "full": "Indicator", "baseline": "Baseline % (published)",
            "followup": "Follow-up % (hypothetical)", "pp": "Change (pp)",
            "relative": "Relative change", "denominator": "Base",
        }),
        hide_index=True, width="stretch",
    )
    st.markdown(
        '<p class="small">Percentage-point change = follow-up − baseline. Relative change = '
        "(follow-up − baseline) ÷ baseline × 100, shown only when baseline &gt; 0. Relative changes "
        "are rounded half-up to one decimal.</p>",
        unsafe_allow_html=True,
    )

# ---- Dynamic summary -------------------------------------------------------
st.markdown("### Summary of the hypothetical scenario")
S = sim.set_index("key")


def _phrase(k: str) -> str:
    r = S.loc[k]
    if r.pp_change == 0:
        return f"**{r.label}** is assumed unchanged at {r.baseline}%"
    d = "rises" if r.pp_change > 0 else "falls"
    rel = "" if r.rel_change is None else f", {r.rel_change:+.1f}% relative"
    return f"**{r.label}** {d} from {r.baseline}% to {r.followup}% ({r.pp_change:+d} pp{rel})"


moved = int((sim.pp_change != 0).sum())
if moved == 0:
    st.markdown(
        f"Under the *{SCENARIO_NAME}* assumptions, no indicator differs from its baseline, so there is nothing to compare."
    )
else:
    st.markdown(
        f"Under the *{SCENARIO_NAME}* assumptions, {moved} of 5 indicators differ from baseline. "
        "These are the numbers you entered, not results:"
    )
    st.markdown(
        "- **Access:** " + _phrase("acct") + ".\n"
        "- **Autonomy:** " + _phrase("ctrl") + ".\n"
        "- **Digital use:** " + _phrase("mob") + ", among women with a mobile phone.\n"
        "- **Microcredit awareness:** " + _phrase("aware") + ".\n"
        "- **Microcredit uptake:** " + _phrase("loan") + "."
    )
    st.markdown(
        f"Assumed gap between account access and money control: baseline "
        f"{S.loc['acct','baseline'] - S.loc['ctrl','baseline']} pp, hypothetical follow-up "
        f"{S.loc['acct','followup'] - S.loc['ctrl','followup']} pp. These are different indicators with "
        "bases not stated, so this is not a count of women with an account but no control."
    )
    st.markdown(
        "**Awareness is not uptake.** Knowing about a microcredit programme and having taken a loan "
        "are separate indicators. A higher assumed loan figure does not mean better welfare: repayment, "
        "debt burden, how loans are used and wellbeing are not measured here, and a fall in borrowing "
        "is not automatically worse."
    )
    if S.loc["loan", "followup"] > S.loc["aware", "followup"]:
        st.info(
            "Your assumed loan figure is higher than your assumed awareness figure. The bases of these "
            "indicators are not stated, so this may or may not be possible; check the report."
        )
st.error("**" + SIM_WARNING + "**")

# ---- Scenario CSV ------------------------------------------------------------
sim_export = pd.DataFrame({
    "scenario": SCENARIO_NAME,
    "indicator": sim.full,
    "baseline_pct": sim.baseline,
    "baseline_status": "Published figure from supplied NFHS-5 Delhi report excerpt; requires verification",
    "followup_pct": sim.followup,
    "followup_status": "HYPOTHETICAL ASSUMPTION; not observed data",
    "pp_change": sim.pp_change,
    "relative_change_pct": sim.rel_change,
    "denominator": sim.denominator,
    "geography": "Delhi (NCT)",
    "warning": SIM_WARNING,
})
st.download_button(
    "Download scenario data (CSV)",
    data=sim_export.to_csv(index=False).encode("utf-8"),
    file_name="nfhs5_delhi_illustrative_scenario.csv",
    mime="text/csv",
)

# ----------------------------------------------------------------------------
# 7. Methodology & limitations
# ----------------------------------------------------------------------------
st.markdown("## Methodology and data limitations")
st.markdown(
    f"""
**Source.** Nine published aggregate percentage values (five overall indicators, two rural/urban values, two education values), supplied by the project team from an NFHS-5
report excerpt for Delhi (National Capital Territory). The original excerpt was not available to the
developer of this dashboard, so **no figure has been independently verified.**

**What was calculated.** Only three percentage-point differences: {ru_gap} pp rural vs. urban, {edu_gap} pp by education, and {access_vs_control_gap} pp between the first two indicators. These are simple subtractions. The before-vs-after simulator additionally calculates percentage-point and relative changes between the published baseline and user-entered hypothetical values.

**Limitations.**
- **Bases (denominators):** only the mobile-transaction figure has a stated base. The others are labelled "not stated"; do not assume they are all women aged 15–49, or the same group.
- **No sample sizes, confidence intervals or weights.** The supplied figures are published estimates from a complex survey. Without sample sizes, small-group figures (such as rural Delhi) cannot be assessed for reliability, and no significance claims can be made.
- **Descriptive only.** Nothing here establishes cause and effect.
- **Simulator is hypothetical.** Follow-up values are user assumptions, not observed data. The simulator estimates no intervention effect and makes no causal or statistical-significance claim.
- **Delhi only.** Results should not be generalised to all India or other states.
- **Limited disaggregation.** Only residence and two education groups were supplied. Age, wealth, employment and other breakdowns are not included.
- **Violence-related indicators are not included.**
- **Rural vs. urban indicator:** assumed to be the same "money they can decide how to use" indicator as in the headline figure. Please confirm.
""",
)

# ----------------------------------------------------------------------------
# 8. Download
# ----------------------------------------------------------------------------
st.markdown("## Download the data")
st.markdown(
    '<p class="small">The CSV contains every figure shown on this page, with its base, source and verification status.</p>',
    unsafe_allow_html=True,
)
st.download_button(
    "Download indicator data (CSV)",
    data=csv_bytes,
    file_name="nfhs5_delhi_financial_access_vs_autonomy.csv",
    mime="text/csv",
)
with st.expander("Preview the CSV"):
    st.dataframe(export, hide_index=True, width="stretch")

st.markdown(
    '<p class="small" style="margin-top:3rem">Prepared from team-supplied figures. '
    "Verify against the original NFHS-5 Delhi report before publishing or decision-making.</p>",
    unsafe_allow_html=True,
)
