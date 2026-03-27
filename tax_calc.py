import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="UK Tax Calculator 25/26",
    page_icon="£",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

* { font-family: 'IBM Plex Sans', sans-serif; }

.stApp {
    background-color: #0a0a0f;
    color: #e8e8e0;
}

h1, h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #f0e040 !important;
    letter-spacing: -1px;
}

.metric-card {
    background: #12121a;
    border: 1px solid #2a2a3a;
    border-left: 4px solid #f0e040;
    border-radius: 4px;
    padding: 20px;
    margin: 8px 0;
}

.metric-card.danger {
    border-left-color: #ff4444;
}

.metric-card.success {
    border-left-color: #44ff88;
}

.metric-card.neutral {
    border-left-color: #4488ff;
}

.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #666680;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 6px;
}

.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #f0e040;
}

.metric-value.danger { color: #ff4444; }
.metric-value.success { color: #44ff88; }
.metric-value.neutral { color: #4488ff; }

.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #666680;
    text-transform: uppercase;
    letter-spacing: 3px;
    border-bottom: 1px solid #2a2a3a;
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}

.zone-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
}

.zone-red { background: #3a0a0a; color: #ff4444; border: 1px solid #ff4444; }
.zone-amber { background: #3a2a0a; color: #f0a040; border: 1px solid #f0a040; }
.zone-green { background: #0a3a1a; color: #44ff88; border: 1px solid #44ff88; }

.table-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #1a1a2a;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
}

.table-row .label { color: #999; }
.table-row .value { color: #e8e8e0; font-weight: 600; }
.table-row .value.highlight { color: #f0e040; }

.saving-pill {
    background: #0a3a1a;
    border: 1px solid #44ff88;
    color: #44ff88;
    padding: 3px 10px;
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
}

.comparison-table th {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #f0e040;
    text-transform: uppercase;
    letter-spacing: 1px;
}

div[data-testid="stSlider"] > div > div > div {
    background: #f0e040 !important;
}

.stSlider [data-baseweb="slider"] {
    padding: 0;
}

label[data-testid="stWidgetLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
    color: #999 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stNumberInput input, .stTextInput input {
    background: #12121a !important;
    border: 1px solid #2a2a3a !important;
    color: #e8e8e0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    border-radius: 4px !important;
}

.stSlider { padding: 0 4px; }

hr { border-color: #2a2a3a !important; }

div[data-testid="column"] { padding: 0 8px; }

.big-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 48px;
    font-weight: 700;
    line-height: 1;
}

.stDataFrame { 
    border: 1px solid #2a2a3a !important;
}
</style>
""", unsafe_allow_html=True)


def calculate_tax(employment_income, property_income, savings_interest,
                  salary_sacrifice_extra, sipp_contribution, paye_paid):
    """Core UK tax calculation for 2025-26"""
    
    # SIPP gross up (basic rate relief at source adds 25%)
    sipp_gross = sipp_contribution * 1.25

    # Adjusted net income (pension sacrifice reduces this directly)
    adjusted_net_income = employment_income + property_income + savings_interest - salary_sacrifice_extra - sipp_gross

    # Personal Allowance taper
    standard_pa = 12570
    if adjusted_net_income <= 100000:
        personal_allowance = standard_pa
    elif adjusted_net_income >= 125140:
        personal_allowance = 0
    else:
        excess = adjusted_net_income - 100000
        personal_allowance = max(0, standard_pa - (excess // 2))

    # Taxable non-savings income (employment + property)
    non_savings = employment_income - salary_sacrifice_extra + property_income
    taxable_non_savings = max(0, non_savings - personal_allowance)

    basic_rate_band = 37700
    basic_rate_taxable = min(taxable_non_savings, basic_rate_band)
    higher_rate_taxable = max(0, taxable_non_savings - basic_rate_band)

    tax_basic = basic_rate_taxable * 0.20
    tax_higher = higher_rate_taxable * 0.40

    # Savings interest
    psa = 500  # Higher rate taxpayer PSA
    taxable_savings = max(0, savings_interest - psa)
    tax_savings = taxable_savings * 0.40

    total_tax_due = tax_basic + tax_higher + tax_savings

    # Additional higher rate relief on SIPP (already got basic rate via provider)
    sipp_higher_relief = sipp_gross * 0.20

    total_tax_after_relief = total_tax_due - sipp_higher_relief

    owe_hmrc = total_tax_after_relief - paye_paid

    # Determine zone
    if adjusted_net_income > 125140:
        zone = "red"
        zone_label = "NO PERSONAL ALLOWANCE"
    elif adjusted_net_income > 100000:
        zone = "amber"
        zone_label = "60% EFFECTIVE RELIEF ZONE"
    else:
        zone = "green"
        zone_label = "FULL PERSONAL ALLOWANCE"

    return {
        "adjusted_net_income": adjusted_net_income,
        "personal_allowance": personal_allowance,
        "taxable_non_savings": taxable_non_savings,
        "basic_rate_taxable": basic_rate_taxable,
        "higher_rate_taxable": higher_rate_taxable,
        "tax_basic": tax_basic,
        "tax_higher": tax_higher,
        "tax_savings": tax_savings,
        "total_tax_due": total_tax_due,
        "sipp_higher_relief": sipp_higher_relief,
        "sipp_gross": sipp_gross,
        "total_tax_after_relief": total_tax_after_relief,
        "owe_hmrc": owe_hmrc,
        "zone": zone,
        "zone_label": zone_label,
        "paye_paid": paye_paid,
    }


def fmt(n):
    return f"£{n:,.2f}"


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# UK TAX CALCULATOR")
st.markdown("### 2025 / 26 · SELF ASSESSMENT PLANNER")
st.markdown("---")

# ── INPUTS ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Income Parameters</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    employment_income = st.number_input(
        "Taxable Employment Pay (after regular pension)",
        value=0.0, step=500.0, format="%.2f"
    )

with col2:
    property_income = st.number_input(
        "Net Property Income",
        value=0.0, step=250.0, format="%.2f"
    )

with col3:
    savings_interest = st.number_input(
        "Savings Interest Earned",
        value=0.0, step=100.0, format="%.2f"
    )

paye_paid = st.number_input(
    "Total PAYE Tax Already Paid This Year",
    value=0.0, step=100.0, format="%.2f"
)

st.markdown("---")
st.markdown('<div class="section-header">Pension Contributions</div>', unsafe_allow_html=True)

col_s, col_p = st.columns(2)

with col_s:
    st.markdown("**SALARY SACRIFICE** — reduces gross pay, saves tax + NIC")
    salary_sacrifice = st.slider(
        "Extra Salary Sacrifice (£)",
        min_value=0, max_value=30000, value=8000, step=500
    )
    st.markdown(f'<span style="font-family: IBM Plex Mono; color: #f0e040; font-size:20px; font-weight:700">{fmt(salary_sacrifice)}</span>', unsafe_allow_html=True)

with col_p:
    st.markdown("**SIPP CONTRIBUTION** — you pay net, HMRC adds 25% on top")
    sipp = st.slider(
        "SIPP Contribution — your cash out (£)",
        min_value=0, max_value=30000, value=0, step=500
    )
    sipp_gross = sipp * 1.25
    st.markdown(f'<span style="font-family: IBM Plex Mono; color: #4488ff; font-size:20px; font-weight:700">{fmt(sipp)}</span> <span style="font-family: IBM Plex Mono; color: #666; font-size:13px">→ {fmt(sipp_gross)} gross in pension</span>', unsafe_allow_html=True)

st.markdown("---")

# ── MAIN CALCULATION ──────────────────────────────────────────────────────────
result = calculate_tax(
    employment_income, property_income, savings_interest,
    salary_sacrifice, sipp, paye_paid
)

# ── ZONE INDICATOR ────────────────────────────────────────────────────────────
zone_css = {"red": "zone-red", "amber": "zone-amber", "green": "zone-green"}
zone_emoji = {"red": "⚠", "amber": "◈", "green": "✓"}
st.markdown(
    f'<span class="zone-badge {zone_css[result["zone"]]}">'
    f'{zone_emoji[result["zone"]]} {result["zone_label"]}</span>'
    f'&nbsp;&nbsp;<span style="font-family: IBM Plex Mono; color: #666; font-size:13px">'
    f'Adjusted Net Income: {fmt(result["adjusted_net_income"])}</span>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ── KEY METRICS ROW ───────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Tax Due</div>
        <div class="metric-value danger">{fmt(result['total_tax_after_relief'])}</div>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card neutral">
        <div class="metric-label">PAYE Already Paid</div>
        <div class="metric-value neutral">{fmt(paye_paid)}</div>
    </div>""", unsafe_allow_html=True)

with m3:
    color = "danger" if result['owe_hmrc'] > 0 else "success"
    label = "You Owe HMRC" if result['owe_hmrc'] > 0 else "HMRC Owes You"
    st.markdown(f"""
    <div class="metric-card {color}">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{fmt(abs(result['owe_hmrc']))}</div>
    </div>""", unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card success">
        <div class="metric-label">Personal Allowance</div>
        <div class="metric-value success">{fmt(result['personal_allowance'])}</div>
    </div>""", unsafe_allow_html=True)

# ── BREAKDOWN ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Tax Breakdown</div>', unsafe_allow_html=True)

b1, b2 = st.columns(2)

with b1:
    rows = [
        ("Employment (taxable)", fmt(employment_income - salary_sacrifice), False),
        ("Property income", fmt(property_income), False),
        ("Total non-savings", fmt(employment_income - salary_sacrifice + property_income), False),
        ("Personal Allowance", f"({fmt(result['personal_allowance'])})", False),
        ("Basic rate taxable @ 20%", fmt(result['basic_rate_taxable']), False),
        ("Higher rate taxable @ 40%", fmt(result['higher_rate_taxable']), False),
        ("Tax on non-savings income", fmt(result['tax_basic'] + result['tax_higher']), True),
        ("Savings interest", fmt(savings_interest), False),
        ("Less PSA (higher rate)", "(£500.00)", False),
        ("Tax on savings @ 40%", fmt(result['tax_savings']), True),
        ("Gross tax due", fmt(result['total_tax_due']), True),
    ]
    if sipp > 0:
        rows.append(("SIPP higher rate relief", f"({fmt(result['sipp_higher_relief'])})", False))
        rows.append(("Tax after SIPP relief", fmt(result['total_tax_after_relief']), True))

    for label, value, highlight in rows:
        val_class = "highlight" if highlight else ""
        st.markdown(f"""
        <div class="table-row">
            <span class="label">{label}</span>
            <span class="value {val_class}">{value}</span>
        </div>""", unsafe_allow_html=True)

with b2:
    if sipp > 0:
        st.markdown(f"""
        <div class="metric-card neutral">
            <div class="metric-label">SIPP Summary</div>
            <div style="font-family: IBM Plex Mono; font-size: 13px; margin-top: 8px;">
                Your cash out: <span style="color:#4488ff">{fmt(sipp)}</span><br>
                HMRC adds (20%): <span style="color:#4488ff">{fmt(sipp*0.25)}</span><br>
                Total in pension: <span style="color:#f0e040">{fmt(sipp_gross)}</span><br>
                Higher rate relief: <span style="color:#44ff88">{fmt(result['sipp_higher_relief'])}</span><br>
                <br>
                <span style="color:#666">Net cost to you:</span> <span style="color:#f0e040; font-size:18px; font-weight:700">{fmt(sipp - result['sipp_higher_relief'])}</span><br>
                <span style="color:#666">Return:</span> <span style="color:#44ff88">{fmt(sipp_gross)} for {fmt(sipp - result['sipp_higher_relief'])} out of pocket</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # Distance to next milestone
    ani = result['adjusted_net_income']
    if ani > 125140:
        dist = ani - 125140
        st.markdown(f"""
        <div class="metric-card danger">
            <div class="metric-label">Distance to 60% Relief Zone</div>
            <div class="metric-value danger">{fmt(dist)}</div>
            <div style="font-family: IBM Plex Mono; font-size: 11px; color:#666; margin-top:6px">
                Contribute {fmt(dist / 1.25)} net to SIPP or salary sacrifice to enter zone
            </div>
        </div>""", unsafe_allow_html=True)
    elif ani > 100000:
        dist = ani - 100000
        dist_to_full = ani - 100000
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #f0a040;">
            <div class="metric-label">Distance to Full Personal Allowance</div>
            <div class="metric-value" style="color:#f0a040">{fmt(dist)}</div>
            <div style="font-family: IBM Plex Mono; font-size: 11px; color:#666; margin-top:6px">
                IN THE 60% ZONE — every £1 pension = 60p tax saving<br>
                Contribute ~{fmt(dist / 1.25)} more net to fully restore PA
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="metric-label">Personal Allowance Status</div>
            <div class="metric-value success">FULLY RESTORED</div>
            <div style="font-family: IBM Plex Mono; font-size: 11px; color:#666; margin-top:6px">
                Full £12,570 personal allowance active
            </div>
        </div>""", unsafe_allow_html=True)

# ── SCENARIO TABLE ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">Sensitivity Analysis — Incremental £2,000 Steps</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 SALARY SACRIFICE SCENARIOS", "📊 SIPP SCENARIOS"])

def build_scenario_table(vary_sacrifice, vary_sipp, current_sacrifice, current_sipp):
    steps = [-6000, -4000, -2000, 0, 2000, 4000, 6000]
    rows = []
    baseline = calculate_tax(employment_income, property_income, savings_interest,
                              current_sacrifice, current_sipp, paye_paid)
    
    for step in steps:
        if vary_sacrifice:
            s = max(0, current_sacrifice + step)
            p = current_sipp
        else:
            s = current_sacrifice
            p = max(0, current_sipp + step)
        
        r = calculate_tax(employment_income, property_income, savings_interest, s, p, paye_paid)
        saving = baseline['owe_hmrc'] - r['owe_hmrc']
        
        label = "◀ CURRENT" if step == 0 else (f"+{fmt(abs(step))}" if step > 0 else f"-{fmt(abs(step))}")
        
        rows.append({
            "Scenario": label,
            "Contribution": fmt(s if vary_sacrifice else p),
            "Adj. Net Income": fmt(r['adjusted_net_income']),
            "Personal Allowance": fmt(r['personal_allowance']),
            "Total Tax Due": fmt(r['total_tax_after_relief']),
            "Owe HMRC": fmt(r['owe_hmrc']),
            "Zone": r['zone_label'],
            "vs Current": ("—" if step == 0 else (f"SAVE {fmt(saving)}" if saving > 0 else f"PAY {fmt(abs(saving))} MORE")),
        })
    
    return pd.DataFrame(rows)

with tab1:
    df1 = build_scenario_table(True, False, salary_sacrifice, sipp)
    st.dataframe(df1, use_container_width=True, hide_index=True)

with tab2:
    df2 = build_scenario_table(False, True, salary_sacrifice, sipp)
    st.dataframe(df2, use_container_width=True, hide_index=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<span style="font-family: IBM Plex Mono; font-size: 11px; color: #444;">'
    'TAX YEAR 2025/26 · ENGLAND & WALES · FOR PLANNING PURPOSES ONLY · '
    'CONSULT A QUALIFIED TAX ADVISER FOR FORMAL ADVICE'
    '</span>',
    unsafe_allow_html=True
)
