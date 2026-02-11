"""
Hallar DSS — Stuðningur fyrir ákvörðun um þróun Hallarsvæðisins
"""
from __future__ import annotations
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from hallar_risk_factors.structural_factors import (
    STRUCTURAL_FACTORS, SCENARIO_FACTORS, get_scenario_profile,
)
from hallar_risk_factors.risk_sensitivities import RISK_PROFILES
from hallar_risk_factors.risk_calculator import (
    calculate_adjusted_probability,
    calculate_scenario_risk_profile,
)
from hallar_risk_factors.goal_impacts import GOALS
from hallar_risk_factors.goal_scoring import (
    calculate_scenario_goal_profile, rank_scenarios,
    WEIGHTS_BALANCED,
)
from justifications_and_calculator import (
    SCENARIO_FACTOR_JUSTIFICATIONS, RISK_CONFIDENCE,
)

# ═════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Hallar DSS",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

SCENARIO_IDS = sorted(SCENARIO_FACTORS.keys(), key=lambda x: int(x[1:]))
GOAL_IDS = list(GOALS.keys())
FACTOR_IDS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]

# ═════════════════════════════════════════════════════════════════════
# SCENARIO NAMES & DESCRIPTIONS (plain Icelandic)
# ═════════════════════════════════════════════════════════════════════

SCENARIO_DISPLAY = {
    "S1": {
        "name": "Borgin byggir innviði og selur byggingarrétt",
        "desc": (
            "Borgin ber ábyrgð á öllum innviðum — götum, innviðum og byggingar- "
            "hæfi lóða og selur síðan byggingarrétt til verktaka sem byggja "
            "íbúðirnar. Borgin hefur fulla stjórn yfir verkefninu en verkefna- "
            "stjórnun er veik og skipulag er aðskilið frá framkvæmdum. "
            "Þetta er hefðbundin leið sem borgin þekkir vel en áhætta er "
            "á hægagangi í framkvæmd og kostnaðarframúrkeyrslu vegna takmarkaðrar "
            "samhæfingar."
        ),
    },
    "S2": {
        "name": "Lífeyrissjóðir eigendur sem ráða til sín verkefnastjóra",
        "desc": (
            "Lífeyrissjóður á verkefnið og ræður sérstakan verkefnastjóra "
            "til að halda utan um framkvæmdir. Sjóðurinn leggur til þolið "
            "fjármagn og verkefnastjórinn sér um daglegan rekstur. "
            "Borgin á ekki hlut en hefur einhverja samningsstöðu. "
            "Hætta er á því að verkefnastjóri hafi takmarkað vald yfir "
            "verktökum þar sem hann er ekki meðeigandi og ber ekki "
            "fjárhagslega áhættu."
        ),
    },
    "S3": {
        "name": "Lífeyrissjóðir og verkefnastjóri eru meðeigendur",
        "desc": (
            "Lífeyrissjóður á verkefnið en verkefnastjóri er einnig "
            "meðeigandi og ber fjárhagslega áhættu ásamt sjóðnum. "
            "Þetta eykur hvata verkefnastjóra til að halda tíma og "
            "kostnaði í skefjum. Sterk verkefnastjórnun og þolið "
            "fjármagn draga úr áhættu. Borgin á ekki hlut en hefur "
            "einhverja samningsstöðu gagnvart verkefninu."
        ),
    },
    "S4": {
        "name": "Lífeyrissjóðir og aðalverktaki eru eigendur",
        "desc": (
            "Lífeyrissjóður á verkefnið og sterkur aðalverktaki er "
            "meðeigandi. Verktakinn ber áhættu ásamt sjóðnum sem tryggir "
            "sterkan hvata til vandaðra og tímanlegra framkvæmda. "
            "Full samþætting skipulags og framkvæmda dregur verulega úr "
            "töfum og kostnaði. Þetta er sterkasta samningsleiðin í "
            "flestum aðstæðum — en borgin hefur ekki beint eignarhald."
        ),
    },
    "S5": {
        "name": "Lífeyrissjóðir eigendur með fasteignaþróunarfélagi",
        "desc": (
            "Tveir eða fleiri lífeyrissjóðir fjárfesta í verkefninu með "
            "fasteignaþróunarfélagi sem stýrir verkefninu og útvegar "
            "verktaka til að byggja upp svæðið. Traust sviðsmynd sem "
            "nýtir þekkingu og reynslu þróunarfyrirtækja og þolinmótt . "
            "fjármagn lífeyrissjóðanna. Fjöldi eigenda eykur hins vegar  "
            "samhæfingaráhættu og borgin hefur litla beina aðkomu."
        ),
    },
    "S6": {
        "name": "Innviðafélag byggir innviði og selur áfram BR",
        "desc": (
            "Lífeyrissjóður byggir innviðin og selur síðan byggingarrétt "
            "til ýmissa verktaka. Algjör aðskilnaður milli innviða og "
            "íbúðabygginga skapar áskoranir í samhæfingu. "
            "Borgin á ekki hlut og hefur veika samningsstöðu. Hætta er á "
            "gæðavandamálum þegar margir verktakar starfa sjálfstætt án "
            "sameiginlegrar stjórnunar."
        ),
    },
    "S7": {
        "name": "2–3 stórir verktakar eigendur með bankafjármögnun ",
        "desc": (
            "Tveir til þrír stórir verktakar stofna sameiginlegt félag "
            "og fjármagna verkefnið með bankalánum. Verktakarnir bera áhættu "
            "og hafa hvata til að ljúka framkvæmdum sem fyrst. "
            "Bankafjármögnun er hins vegar óþolinmóð — bankar geta þrýst á "
            "uppgreiðslu lána eða stöðvun framkvæmda í niðursveiflu en eigin-. "
            "fjárstaða verktaka dregur úr þessari áhættu. Borgin hefur litla "
            "samningsstöðu. "
        ),
    },
    "S8": {
        "name": "1 stór verktaki eigandi verkefnis með bankafjármögnun ",
        "desc": (
            "Einn stór verktaki tekur verkefnið að sér og fjármagnar "
            "með bankalánum. Full samþætting og sterk verkefnisstjórnun "
            "draga úr töfum. Fáir eigendur einfalda ákvarðanatöku. "
            "Hætta er þó á að verktakinn verði of ráðandi og eiginfjár-"
            "staða ekki nægilega traust í niðursveiflu eða við vaxtabreytingu. "
        ),
    },
    "S9": {
        "name": "Margir smáir verktakar — engin samhæfing",
        "desc": (
            "Mörgum litlum verktökum er úthlutað lóðum og þeir byggja "
            "sjálfstætt. Engin sameiginleg verkefnisstjórnun og engin "
            "samþætting skipulags og framkvæmda. "
            "Þetta er áhættusamasta leiðin — mikil hætta á töfum, "
            "gæðavandamálum og jafnvel gjaldþroti einstakra verktaka. "
            "Borgin hefur nánast enga stjórn á framgangi verkefnisins."
        ),
    },
    "S10": {
        "name": "Reykjavíkurborg og lífeyrissjóðir eru eigendur",
        "desc": (
            "Borgin og lífeyrissjóðir stofna sameiginlegt félag um "
            "verkefnið. Borgin hefur beina aðkomu og stjórn á meðan "
            "sjóðirnir leggja til þolinmótt fjármagn. "
            "Styrkur verktaka og verkefnisstjórnun er í meðallagi í "
            "þessari sviðsmynd. Góð leið ef borgin vill halda áhrifum "
            "en deila áhættu og kostnaði með lífeyrissjóðunum."
        ),
    },
    "S11": {
        "name": "Reykjavíkurborg, lífeyrissjóðir og aðalverktaki eigendur",
        "desc": (
            "Borgin, lífeyrissjóðir og sterkur aðalverktaki eru eigendur. "
            "Sameinar styrk lífeyrisfjármagns, reynslu aðalverktaka og "
            "stjórn borgarinnar. Full samþætting og sterk verkefnisstjórnun. "
            " Flóknara eignarhald en dreifir áhættu vel og tryggir að hagsmunir "
            " allra aðila séu amræmdir. "
        ),
    },
    "S12": {
        "name": "Lífeyrissjóðir eru eigendur og ráða til sín aðalverktaka",
        "desc": (
            "Lífeyrissjóðir eiga verkefnið og ráða aðalverktaka til stýringar "
            "og framkvæmda, en verktakinn er ekki meðeigandi. Gott skipulag "
            "og sterk verkefnisstjórnun. Verktakinn hefur þó minni hvata en í"
            " sviðsmynd S4 þar sem hann ber ekki eignarhaldsáhættu. Þolið "
            "fjármagn sjóðsins dregur úr fjárhagslegri áhættu verkefnisins. "
        ),
    },
}

def scenario_name(sid: str) -> str:
    return SCENARIO_DISPLAY.get(sid, {}).get("name", SCENARIO_FACTORS[sid].name_is)

def scenario_desc(sid: str) -> str:
    return SCENARIO_DISPLAY.get(sid, {}).get("desc", "")


# ═════════════════════════════════════════════════════════════════════
# GOAL DESCRIPTIONS (plain Icelandic)
# ═════════════════════════════════════════════════════════════════════

GOAL_DESCRIPTIONS = {
    "G1": "Götur og hluti innviða tilbúnir áður en flutt hefur verið inn í 300 íbúðir",
    "G2": "Að minnsta kosti 400 íbúðir tilbúnar til afhendingar á hverju ári",
    "G3": "Íbúðaverð verði 15-20% undir markaðsverði",
    "G4": "Að borgin verði ekki af fjármunum við samningsgerð",
    "G5": "Að verkefnið klárist að fullu eins og áætlað er",
    "G6": "Að innviðaframkvæmdir haldist innan fjárhagsáætlunar",
    "G7": "Að götur, innviðir og almenningssvæði séu vönduð og endingargóð",
    "G8": "Að íbúðir og byggingar séu vandaðar og uppfylli gæðakröfur",
    "G9": "Að borgin hafi áhrif á framkvæmdir og geti tryggt almannahagsmuni",
    "G10": "Að fjölbreyttur hópur fólks geti búið á svæðinu, þ.m.t. tekjulágir",
}

GOAL_SHORT_LABELS = {
    "G1": "Innviðahraði",
    "G2": "Byggingarhraði",
    "G3": "Hagkvæmni",
    "G4": "Fjárhagslegir hagsmunir",
    "G5": "Verklok",
    "G6": "Kostnaður við innviði",
    "G7": "Gæði innviða",
    "G8": "Gæði bygginga",
    "G9": "Stýring borgarinnar",
    "G10": "Félagsleg blöndun",
}


# ═════════════════════════════════════════════════════════════════════
# GOAL RANKING — comparative scores across all 12 scenarios
# ═════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def compute_goal_rankings():
    """Compute 1-12 score for every (scenario, goal) pair.

    Score 12 = best among all scenarios, 1 = worst.
    This is a pure ranking — it doesn't claim to predict absolute outcomes.
    """
    # Step 1: compute raw expected values
    raw = {}
    for sid in SCENARIO_IDS:
        profile = calculate_scenario_goal_profile(sid)
        for gid in GOAL_IDS:
            gs = profile.goal_scores[gid]
            raw[(sid, gid)] = gs.expected_value

    # Step 2: rank within each goal
    rankings = {}  # (sid, gid) → 1-12 score
    for gid in GOAL_IDS:
        goal = GOALS[gid]
        vals = [(sid, raw[(sid, gid)]) for sid in SCENARIO_IDS]

        # Sort: best first
        if goal.direction == "higher_better":
            vals.sort(key=lambda x: x[1], reverse=True)
        else:
            vals.sort(key=lambda x: x[1])

        for rank_0, (sid, _val) in enumerate(vals):
            rankings[(sid, gid)] = 12 - rank_0  # 12=best, 1=worst

    return rankings


def goal_rank_color(score: int) -> str:
    """Return color for a 1-12 ranking score."""
    if score >= 10:
        return "#22c55e"   # green
    elif score >= 7:
        return "#84cc16"   # lime
    elif score >= 4:
        return "#f59e0b"   # amber
    else:
        return "#ef4444"   # red


def goal_rank_emoji(score: int) -> str:
    """Return emoji for a 1-12 ranking score."""
    if score >= 10:
        return "🟢"
    elif score >= 7:
        return "🟡"
    elif score >= 4:
        return "🟠"
    else:
        return "🔴"
# ═════════════════════════════════════════════════════════════════════
# CSS — LIGHT THEME
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* ── Reset to light theme ──────────────────────────── */
    .stApp { background: #ffffff; }
    .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1200px;
    }
    #MainMenu, footer, .stDeployButton { display: none; }
    header[data-testid="stHeader"] { display: none; }

    /* ── Force dark text on all widgets ────────────────── */
    .stSlider label, .stRadio label, .stSelectbox label,
    .stNumberInput label, .stTextInput label, .stCheckbox label,
    .stMultiSelect label {
        color: #334155 !important;
    }
    .stSlider p, .stRadio p, .stRadio div[role="radiogroup"] label,
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #334155 !important;
    }
    .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        color: #334155 !important;
    }
    /* Slider current value */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"],
    .stSlider div[data-baseweb="slider"] div {
        color: #334155 !important;
    }

    /* ── Sidebar ───────────────────────────────────────── */
    [data-testid="stSidebar"] { background: #f8fafc; border-right: 1px solid #e2e8f0; }

    /* ── Typography ────────────────────────────────────── */
    .page-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .page-intro {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .section-label {
        font-size: 1.05rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    /* ── Metric widget text fix ────────────────────────── */
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"] p,
    [data-testid="stMetric"] [data-testid="stMetricLabel"] div,
    [data-testid="stMetric"] [data-testid="stMetricLabel"] span {
        color: #475569 !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricValue"] div {
        color: #1e293b !important;
    }

    /* ── Expander text fix ─────────────────────────────── */
    .streamlit-expanderHeader p, .streamlit-expanderHeader span,
    details summary p, details summary span,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        color: #1e293b !important;
    }
    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
        background: #ffffff !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] details > summary {
        background: #ffffff !important;
        color: #1e293b !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #ffffff !important;
    }

    /* ── Tab labels fix ────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] button p,
    .stTabs [data-baseweb="tab-list"] button span,
    .stTabs [data-baseweb="tab-list"] button div {
        color: #475569 !important;
        font-size: 0.9rem !important;
    }
    .stTabs [data-baseweb="tab-list"] [aria-selected="true"] p,
    .stTabs [data-baseweb="tab-list"] [aria-selected="true"] span,
    .stTabs [data-baseweb="tab-list"] [aria-selected="true"] div {
        color: #1e293b !important;
        font-weight: 600 !important;
    }

    /* ── Goal Cards ────────────────────────────────────── */
    .goal-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 16px 10px 16px;
        margin-bottom: 12px;
    }
    .goal-card-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 2px;
    }
    .goal-card-desc {
        font-size: 0.75rem;
        color: #64748b;
        line-height: 1.4;
        margin-bottom: 8px;
    }

    /* ── Result Cards ──────────────────────────────────── */
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .result-card.top-1 { border-left: 5px solid #16a34a; }
    .result-card.top-2 { border-left: 5px solid #2563eb; }
    .result-card.top-3 { border-left: 5px solid #64748b; }

    .result-rank {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .result-rank.top-1 { color: #16a34a; }
    .result-rank.top-2 { color: #2563eb; }
    .result-rank.top-3 { color: #64748b; }

    .result-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .result-desc {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.6;
        margin-bottom: 16px;
    }

    /* ── Goal Ranking Bars ─────────────────────────────── */
    .rank-row {
        display: flex;
        align-items: center;
        margin: 5px 0;
        gap: 8px;
    }
    .rank-label {
        font-size: 0.78rem;
        color: #475569;
        min-width: 130px;
        text-align: right;
    }
    .rank-bar-bg {
        flex: 1;
        background: #f1f5f9;
        border-radius: 4px;
        height: 22px;
        overflow: hidden;
        max-width: 250px;
        display: flex;
    }
    .rank-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    .rank-score {
        font-size: 0.80rem;
        font-weight: 700;
        min-width: 50px;
        text-align: left;
    }

    /* ── Ranking Bar Chart ─────────────────────────────── */
    .ranking-bar-row {
        display: flex;
        align-items: center;
        margin: 4px 0;
        gap: 8px;
    }
    .ranking-bar-label {
        font-size: 0.78rem;
        color: #475569;
        min-width: 280px;
        text-align: right;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .ranking-bar-bg {
        flex: 1;
        background: #f1f5f9;
        border-radius: 4px;
        height: 24px;
        overflow: hidden;
    }
    .ranking-bar-fill {
        height: 100%;
        border-radius: 4px;
        display: flex;
        align-items: center;
        padding: 0 8px;
        font-size: 0.72rem;
        font-weight: 600;
        color: white;
        white-space: nowrap;
        transition: width 0.3s ease;
    }
    .ranking-bar-rank {
        font-size: 0.72rem;
        color: #94a3b8;
        min-width: 24px;
    }

    /* ── Risk Detail ───────────────────────────────────── */
    .risk-detail-row {
        padding: 8px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .risk-detail-row:last-child { border-bottom: none; }
    .risk-name-detail {
        font-weight: 600;
        color: #334155;
        font-size: 0.85rem;
    }
    .risk-explain {
        color: #64748b;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-top: 2px;
    }

    /* ── Forsendur / Kostnaður Page ─────────────────────── */
    .forsendur-metric {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
    }
    .forsendur-metric-label {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
    }
    .forsendur-metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.2;
    }
    .forsendur-metric-value.small {
        font-size: 1.2rem;
    }
    .forsendur-breakdown {
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.7;
        margin-top: 4px;
    }
    .forsendur-note {
        font-size: 0.85rem;
        color: #64748b;
        line-height: 1.6;
        margin: 8px 0;
    }
    .forsendur-note strong {
        color: #334155;
    }
    .forsendur-divider {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 2rem 0;
    }
    .forsendur-result-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 12px;
    }
    .forsendur-result-label {
        font-size: 0.78rem;
        color: #15803d;
        font-weight: 600;
    }
    .forsendur-result-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #166534;
    }
    .forsendur-info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 12px;
    }
    .forsendur-info-label {
        font-size: 0.78rem;
        color: #1e40af;
        font-weight: 600;
    }
    .forsendur-info-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e3a5f;
    }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🏗️ Hallar DSS")
    st.caption("Stuðningur við\nþróun Hallarsvæðis")

    page = st.radio(
        "Síður",
        ["📊 Kostnaður við innviði", "📊 Markmið og áherslur uppbyggingar", "🔍 Ítarleg lýsing á sviðsmyndum og áhættun", "📖 Aðferðafræði"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption(
        " "
    )


# ═════════════════════════════════════════════════════════════════════
# PAGE 0: KOSTNAÐUR VIÐ INNVIÐI
# ═════════════════════════════════════════════════════════════════════

if page == "📊 Kostnaður við innviði":

    st.markdown('<div class="page-header">Innviðir  ↔  Byggingarréttur</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-intro">'
        'Stilltu forsendur um fjölda íbúða, íbúa og barna → reiknaðu skólaþörf '
        'og innviðakostnað → veldu hvort borgin muni eiga innviði eða leigja þá og sjáðu hversu mikið byggingarrétt '
        'þarf að afhenda.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Helper functions ──
    def _pv_annuity(payment, r, n_years):
        if r <= 0:
            return payment * n_years
        return payment * (1 - (1 + r) ** (-n_years)) / r

    def _annuity_payment(pv_target, r, n_years):
        if r <= 0:
            return pv_target / max(1, n_years)
        return pv_target * r / (1 - (1 + r) ** (-n_years))

    # ── A) Íbúðir, íbúar og börn ──────────────────────────────────
    st.markdown('<hr class="forsendur-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">A) Íbúðir, íbúar og börn</div>', unsafe_allow_html=True)

    a_left, a_right = st.columns([1.3, 0.7], gap="large")

    with a_left:
        apartments = st.slider("Fjöldi íbúða (heild)", 500, 5000, 2500, 50)
        avg_unit_sqm = st.slider("Meðalstærð íbúðar (m²)", 50, 120, 85, 5)
        residents_per_unit = st.slider("Íbúar á íbúð (meðaltal)", 1.5, 3.5, 2.3, 0.1)
        kids_per_unit = st.slider("Börn á íbúð (meðaltal)", 0.0, 1.5, 0.45, 0.05)

    population = apartments * residents_per_unit
    children = apartments * kids_per_unit
    total_res_sqm = apartments * avg_unit_sqm

    with a_right:
        st.markdown(
            f'<div class="forsendur-metric">'
            f'<div class="forsendur-metric-label">Áætlaðir íbúar</div>'
            f'<div class="forsendur-metric-value">{population:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="forsendur-metric">'
            f'<div class="forsendur-metric-label">Áætluð börn (alls)</div>'
            f'<div class="forsendur-metric-value">{children:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="forsendur-metric">'
            f'<div class="forsendur-metric-label">Heildarflatarmál íbúða (m²)</div>'
            f'<div class="forsendur-metric-value">{total_res_sqm:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── B) Þjónustuþörf og skólaþörf ──────────────────────────────
    st.markdown('<hr class="forsendur-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">B) Þjónustuþörf og skólaþörf</div>', unsafe_allow_html=True)

    b_left, b_right = st.columns([1.3, 0.7], gap="large")

    with b_left:
        kg_share = st.slider("Hlutfall barna sem eru á leikskólaaldri", 0.10, 0.70, 0.45, 0.05)
        school_share = st.slider("Hlutfall barna sem eru á grunnskólaaldri", 0.10, 0.90, 0.55, 0.05)
        kg_capacity = st.slider("Leikskóli — pláss (börn)", 60, 200, 120, 10)
        school_capacity = st.slider("Grunnskóli — pláss (nemendur)", 300, 1200, 600, 50)

    kg_children = children * kg_share
    school_children = children * school_share
    n_kindergartens = int(np.ceil(kg_children / kg_capacity)) if kg_capacity > 0 else 0
    n_schools = int(np.ceil(school_children / school_capacity)) if school_capacity > 0 else 0

    with b_right:
        st.markdown(
            f'<div class="forsendur-breakdown">'
            f'Leikskólabörn (áætlað): <strong>{kg_children:,.0f}</strong><br>'
            f'Grunnskólabörn (áætlað): <strong>{school_children:,.0f}</strong>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="forsendur-metric">'
            f'<div class="forsendur-metric-label">Leikskólar (fjöldi)</div>'
            f'<div class="forsendur-metric-value">{n_kindergartens}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="forsendur-metric">'
            f'<div class="forsendur-metric-label">Grunnskólar (fjöldi)</div>'
            f'<div class="forsendur-metric-value">{n_schools}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="forsendur-note">Markmiðið er að sjá næmni: fleiri íbúar/börn → '
        'meiri þörf fyrir innviði → Aukinn kostnaður við innviði → Afhending stærri hluta af byggingarrétti.</div>',
        unsafe_allow_html=True,
    )

    # ── C) Kostnaðarforsendur (M ISK) ─────────────────────────────
    st.markdown('<hr class="forsendur-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">C) Kostnaðarforsendur (M ISK)</div>', unsafe_allow_html=True)

    c_left, c_right = st.columns([1.3, 0.7], gap="large")

    with c_left:
        st.markdown(
            '<div class="forsendur-note">Stórir grunnskólar 6–8 ma.kr., '
            'leikskólar ~2 ma.kr. (stillanlegt).</div>',
            unsafe_allow_html=True,
        )
        kg_cost_misk = st.slider("Leikskóli kostnaður (M ISK / hver)", 1000, 4000, 2000, 100)
        school_cost_misk = st.slider("Grunnskóli kostnaður (M ISK / hver)", 6000, 9000, 7000, 250)
        open_areas_misk = st.slider("Opin svæði / almenningsrými (M ISK heild)", 0, 20000, 6000, 250)

    infra_total_misk = n_kindergartens * kg_cost_misk + n_schools * school_cost_misk + open_areas_misk

    with c_right:
        st.markdown(
            f'<div class="forsendur-metric">'
            f'<div class="forsendur-metric-label">Heildarkostnaður innviða (M ISK)</div>'
            f'<div class="forsendur-metric-value">{infra_total_misk:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="forsendur-breakdown">'
            f'• Leikskólar: {n_kindergartens} × {kg_cost_misk:,} = <strong>{n_kindergartens * kg_cost_misk:,.0f} M ISK</strong><br>'
            f'• Grunnskólar: {n_schools} × {school_cost_misk:,} = <strong>{n_schools * school_cost_misk:,.0f} M ISK</strong><br>'
            f'• Opin svæði: <strong>{open_areas_misk:,.0f} M ISK</strong>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── D) Samningsform ────────────────────────────────────────────
    st.markdown('<hr class="forsendur-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">D) Samningsform (byggingarréttur vs leiga/eign)</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="forsendur-note">'
        f'Heildarkostnaður innviða: '
        f'<strong>{infra_total_misk:,.0f} M ISK</strong>.'
        f'</div>',
        unsafe_allow_html=True,
    )

    model = st.radio(
        "Veldu samningsgerð",
        [
            "EIGN: Borg afhendir byggingarrétt sem nemur innviðakostnaði og eignar innviði",
            "LEIGA + KAUP: Borg afhendir hluta í byggingarrétt og leigir í X ár, eignast svo innviði",
            "LEIGA ÆVILÖNG: Borg afhendir hluta í byggingarrétt og leigir til frambúðar, eignast ekki innviði",
        ],
        index=0,
    )

    st.markdown(
        '<div class="forsendur-note">'
        'Hér stillir þú skiptingu milli byggingarréttar og leigu. Kerfið reiknar leigu þannig '
        'að þú yfirborgir ekki (PV leigu + byggingarréttur = nettókostnaður innviða).</div>',
        unsafe_allow_html=True,
    )

    if model.startswith("EIGN"):
        rights_given_misk = float(infra_total_misk)
        st.markdown(
            f'Byggingarréttur sem borg afhendir: **{rights_given_misk:,.0f} M ISK**'
        )
        st.markdown('Árleg leiga: **0 M ISK**')
    else:
        e_left, e_right = st.columns([1.3, 0.7], gap="large")
        with e_left:
            roi = st.slider("Kröfuávöxtun (ROI) fjárfesta", 0.05, 0.15, 0.10, 0.005)
            alpha = st.slider(
                "Hlutfall nettókostnaðar greitt með byggingarrétti (0–100%)",
                0.0, 1.0, 0.50, 0.01,
            )

        rights_given_misk = float(infra_total_misk) * float(alpha)
        pv_rent_target = float(infra_total_misk) * float(1.0 - alpha)

        if model.startswith("LEIGA + KAUP"):
            with e_left:
                term_years = st.slider("Leigutími (ár) þar til borg eignast innviði", 1, 40, 15, 1)
            annual_rent_misk = _annuity_payment(pv_rent_target, float(roi), int(term_years))
            pv_rent = _pv_annuity(float(annual_rent_misk), float(roi), int(term_years))
        else:
            term_years = None
            annual_rent_misk = pv_rent_target * float(roi)
            pv_rent = pv_rent_target

        with e_right:
            st.markdown(
                f'<div class="forsendur-metric">'
                f'<div class="forsendur-metric-label">Byggingarréttur (M ISK)</div>'
                f'<div class="forsendur-metric-value small">{rights_given_misk:,.0f}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="forsendur-metric">'
                f'<div class="forsendur-metric-label">Árleg leiga (M ISK / ár)</div>'
                f'<div class="forsendur-metric-value small">{annual_rent_misk:,.0f}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="forsendur-breakdown">'
                f'PV(leigu) við ROI={roi:.3f}'
                f'{f" og {term_years} ár" if term_years else ""}: '
                f'<strong>{pv_rent:,.0f} M ISK</strong><br>'
                f'Samtals PV (byggingarréttur + leiga): '
                f'<strong>{(rights_given_misk + pv_rent):,.0f} M ISK</strong>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── E) Umbreyting: M ISK → m² ─────────────────────────────────
    st.markdown('<hr class="forsendur-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">E) Umbreyting: byggingarréttur (M ISK) → m² af byggingarrétti</div>', unsafe_allow_html=True)

    f_left, f_right = st.columns(2, gap="large")

    with f_left:
        price_per_sqm = st.slider("Verð byggingarréttar (ISK/m²)", 50_000, 150_000, 90_000, 1_000)

    rights_value_isk = float(rights_given_misk) * 1_000_000.0
    sqm_required = rights_value_isk / float(price_per_sqm) if price_per_sqm > 0 else 0.0
    units_equiv = sqm_required / float(avg_unit_sqm) if avg_unit_sqm > 0 else 0.0

    f_res_left, f_res_right = st.columns(2, gap="large")
    with f_res_left:
        st.markdown(
            f'<div class="forsendur-metric">'
            f'<div class="forsendur-metric-label">Byggingarréttur afhentur (M ISK)</div>'
            f'<div class="forsendur-metric-value">{float(rights_given_misk):,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with f_res_right:
        st.markdown(
            f'<div class="forsendur-metric">'
            f'<div class="forsendur-metric-label">Byggingarréttur sem m²</div>'
            f'<div class="forsendur-metric-value">{sqm_required:,.0f} m²</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'Jafngildir um það bil **{units_equiv:,.0f}** íbúðum (miðað við {avg_unit_sqm} m² meðalíbúð).'
    )

    # ── Vista forsendur ────────────────────────────────────────────
    st.markdown('<hr class="forsendur-divider">', unsafe_allow_html=True)

    if st.button("Vista forsendur"):
        st.session_state["assumptions"] = {
            "apartments": apartments,
            "population": population,
            "children": children,
            "n_kindergartens": n_kindergartens,
            "n_schools": n_schools,
            "infra_total_misk": infra_total_misk,
            "infra_total_misk": infra_total_misk,
            "rights_given_misk": rights_given_misk,
            "model": model.split(":")[0].strip(),
        }
        st.success("Forsendur vistaðar.")


# ═════════════════════════════════════════════════════════════════════
# PAGE 1: MARKMIÐ OG ÁHERSLUR
# ═════════════════════════════════════════════════════════════════════

elif page == "📊 Markmið og áherslur uppbyggingar":

    st.markdown('<div class="page-header">Markmið uppbyggingar Hallarsvæðisins</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-intro">'
        'Hér eru markmið uppbyggingarinnar á Hallarsvæðinu. '
        'Gefðu þeim markmiðum sem skipta þig mestu máli hærra vægi — '
        'Líkanið finnur þær samningsleiðir sem lágmarka áhættu miðað '
        'við þínar áherslur.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Goal Sliders ─────────────────────────────────────────────
    st.markdown('<div class="section-label">Hvaða markmið skipta þig mestu máli?</div>', unsafe_allow_html=True)

    weights = {}
    col_left, col_right = st.columns(2)

    for i, gid in enumerate(GOAL_IDS):
        goal = GOALS[gid]
        short = GOAL_SHORT_LABELS[gid]
        desc = GOAL_DESCRIPTIONS[gid]
        target_col = col_left if i < 5 else col_right

        with target_col:
            st.markdown(
                f'<div class="goal-card">'
                f'<div class="goal-card-title">{gid}: {short}</div>'
                f'<div class="goal-card-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            w = st.slider(
                f"{gid}: {short}",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
                key=f"w_{gid}",
                label_visibility="collapsed",
            )
            weights[gid] = float(w)

    # ── Check if all weights are zero ────────────────────────────
    if sum(weights.values()) == 0:
        st.info("Dragðu einn eða fleiri renna til hægri til að forgangsraða markmiðum.")
        st.stop()

    # ── Run Rankings ─────────────────────────────────────────────
    rankings = rank_scenarios(weights)

    # Compute goal profiles for top scenarios
    all_goal_profiles = {}
    all_risk_profiles = {}
    for r in rankings:
        all_goal_profiles[r.scenario_id] = calculate_scenario_goal_profile(r.scenario_id)
        all_risk_profiles[r.scenario_id] = calculate_scenario_risk_profile(r.scenario_id)

    # ── Results: Top 3 ───────────────────────────────────────────
    st.markdown("")
    st.markdown("")
    st.markdown(
        '<div class="section-label">'
        'Bestu samningsleiðirnar miðað við þínar áherslur'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-intro" style="margin-top:-4px;">'
        'Þessar þrjár samningsleiðir lágmarka heildaráhættuna miðað við '
        'þau markmið sem þú hefur valið. Smelltu á „Sjá nánari greiningu" '
        'til að skoða hvað liggur að baki.'
        '</div>',
        unsafe_allow_html=True,
    )

    rank_labels = {1: "Besta leiðin", 2: "Næstbesta leiðin", 3: "Þriðja besta leiðin"}
    rank_styles = {1: "top-1", 2: "top-2", 3: "top-3"}

    for rank_obj in rankings[:3]:
        sid = rank_obj.scenario_id
        rank = rank_obj.rank
        style = rank_styles[rank]
        label = rank_labels[rank]
        name = scenario_name(sid)
        desc = scenario_desc(sid)
        gp = all_goal_profiles[sid]
        rp = all_risk_profiles[sid]

        score = rank_obj.total_score

        st.markdown(
            f'<div class="result-card {style}">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
            f'<div>'
            f'<div class="result-rank {style}">{label}</div>'
            f'<div class="result-name">{name}</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:0.65rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;">Áhættuskor</div>'
            f'<div style="font-size:1.4rem;font-weight:700;color:#334155;">{score:.1f}</div>'
            f'</div>'
            f'</div>'
            f'<div class="result-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Ranking visualization ─────────────────────────────
        if gp:
            goal_ranks = compute_goal_rankings()
            rank_html = ""
            active_goals = [(gid, weights[gid]) for gid in GOAL_IDS if weights[gid] > 0]
            # Sort by user weight (highest priority first) — same order on all cards
            active_goals.sort(key=lambda x: x[1], reverse=True)

            for gid, w in active_goals:
                short = GOAL_SHORT_LABELS[gid]
                score = goal_ranks.get((sid, gid), 6)
                bar_pct = score / 12 * 100
                color = goal_rank_color(score)

                rank_html += (
                    f'<div class="rank-row">'
                    f'<span class="rank-label">{short}</span>'
                    f'<div class="rank-bar-bg">'
                    f'<div class="rank-bar-fill" style="width:{bar_pct:.0f}%;background:{color};"></div>'
                    f'</div>'
                    f'<span class="rank-score" style="color:{color};">{score}/12</span>'
                    f'</div>'
                )

            if rank_html:
                st.markdown(
                    f'<div style="margin-top:-12px;margin-bottom:8px;padding:0 24px;">'
                    f'<div style="font-size:0.8rem;font-weight:600;color:#64748b;'
                    f'margin-bottom:6px;">Staða miðað við aðrar samningsleiðir (12 = best):</div>'
                    f'{rank_html}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # ── Expandable detail ────────────────────────────────
        with st.expander(f"Sjá nánari greiningu — {name}"):
            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.markdown("**Helstu áhættur í þessari sviðsmynd:**")
                if rp:
                    for risk in rp.top_risks(5):
                        p = risk.prob_likely
                        if p > 0.40:
                            icon = "🔴"
                        elif p > 0.20:
                            icon = "🟡"
                        else:
                            icon = "🟢"

                        # Get confidence
                        conf = RISK_CONFIDENCE.get(risk.risk_id)
                        conf_note = ""
                        if conf:
                            conf_note = f" · Öryggi mats: {conf.tier}"

                        st.markdown(
                            f'{icon} **{risk.name_is}** — {p*100:.0f}% líkur{conf_note}'
                        )

                        # Show what drives this risk
                        if risk.breakdown:
                            drivers = []
                            for fid, effect, _desc in risk.breakdown:
                                if effect < 0.85:
                                    drivers.append(f"{STRUCTURAL_FACTORS[fid].name_is} lækkar áhættu")
                                elif effect > 1.15:
                                    drivers.append(f"{STRUCTURAL_FACTORS[fid].name_is} hækkar áhættu")
                            if drivers:
                                st.caption("  " + " · ".join(drivers[:2]))

            with detail_col2:
                st.markdown("**Staða í samanburði við aðrar leiðir:**")
                if gp:
                    goal_ranks = compute_goal_rankings()
                    for gid in GOAL_IDS:
                        short = GOAL_SHORT_LABELS[gid]
                        score = goal_ranks.get((sid, gid), 6)
                        emoji = goal_rank_emoji(score)
                        st.markdown(f"{emoji} **{short}:** {score}/12")

        st.markdown("")  # spacer

    # ── Full Ranking Chart ───────────────────────────────────────
    st.markdown("")
    st.markdown('<div class="section-label">Allar 12 samningsleiðir í röð</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-intro" style="margin-top:-4px;">'
        'Styttri súla þýðir minni áhættu. Röðunin breytist í rauntíma '
        'eftir því hvaða markmið eru valin hér að ofan.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Normalize scores for display
    scores = [(r.scenario_id, r.total_score, r.rank) for r in rankings]
    max_score = max(s[1] for s in scores) if scores else 1
    min_score = min(s[1] for s in scores) if scores else 0

    chart_html = ""
    for sid, score, rank in scores:
        name = scenario_name(sid)
        # Bar width: best = 20%, worst = 100%
        bar_pct = 20 + (score - min_score) / (max_score - min_score + 0.01) * 80

        if rank <= 3:
            color = "#16a34a"
        elif rank <= 6:
            color = "#2563eb"
        elif rank <= 9:
            color = "#f59e0b"
        else:
            color = "#ef4444"

        chart_html += (
            f'<div class="ranking-bar-row">'
            f'<span class="ranking-bar-rank">#{rank}</span>'
            f'<span class="ranking-bar-label">{name}</span>'
            f'<div class="ranking-bar-bg">'
            f'<div class="ranking-bar-fill" style="width:{bar_pct:.0f}%;background:{color};">'
            f'{sid}</div>'
            f'</div>'
            f'</div>'
        )

    st.markdown(chart_html, unsafe_allow_html=True)
    st.caption("Grænnar súlur = lægri áhætta. Rauðar súlur = hærri áhætta.")


# ═════════════════════════════════════════════════════════════════════
# PAGE 2: ÍTARLEG LÝSING Á SVIÐSMYNDUM OG ÁHÆTTUM
# ═════════════════════════════════════════════════════════════════════

elif page == "🔍 Ítarleg lýsing á sviðsmyndum og áhættun":

    st.markdown('<div class="page-header">Ítarleg lýsing á sviðsmyndum</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-intro">'
        'Veldu sviðsmynd til að sjá ítarlega greiningu — hvernig hún er uppbyggð, '
        'hvaða áhættur liggja í henni og hvaða markmið hún þjónar best.'
        '</div>',
        unsafe_allow_html=True,
    )

    selected = st.selectbox(
        "Veldu sviðsmynd",
        SCENARIO_IDS,
        format_func=lambda sid: f"{sid}: {scenario_name(sid)}",
    )

    sf = SCENARIO_FACTORS[selected]
    name = scenario_name(selected)
    desc = scenario_desc(selected)

    # ── Hero: scenario description ────────────────────────────────
    st.markdown(
        f'<div style="background:#f8fafc;border:1px solid #e2e8f0;'
        f'border-radius:12px;padding:28px 32px;margin:16px 0 28px 0;">'
        f'<div style="font-size:1.35rem;font-weight:700;color:#1e293b;'
        f'margin-bottom:12px;">{name}</div>'
        f'<div style="font-size:0.95rem;color:#475569;line-height:1.7;">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Compute data for all tabs ─────────────────────────────────
    factor_profile = get_scenario_profile(selected)
    justifications = SCENARIO_FACTOR_JUSTIFICATIONS.get(selected, {})
    risk_profile = calculate_scenario_risk_profile(selected)
    goal_ranks = compute_goal_rankings()

    # ── Three tabs ────────────────────────────────────────────────
    tab_factors, tab_risks, tab_goals = st.tabs([
        "📐 Uppbyggingarþættir",
        "⚠️ Áhættur",
        "🎯 Markmið",
    ])

    # ══════════════════════════════════════════════════════════════
    # TAB 1: UPPBYGGINGARÞÆTTIR (F1–F7)
    # ══════════════════════════════════════════════════════════════
    with tab_factors:
        st.markdown(
            '<div style="font-size:0.92rem;color:#1e293b;line-height:1.6;margin-bottom:20px;">'
            'Hvert uppbyggingarform er metið á sjö þáttum sem lýsa skipulagi '
            'samstarfsins. Þessir þættir stýra síðan öllum áhættuútreikningi '
            'í líkaninu — betri einkunn á þætti dregur úr tengdri áhættu.'
            '</div>',
            unsafe_allow_html=True,
        )

        for fid in FACTOR_IDS:
            factor = STRUCTURAL_FACTORS[fid]
            score = factor_profile[fid]
            just = justifications.get(fid, "")

            # Color logic: F1 is inverted (lower = better)
            if fid == "F1":
                color = "#22c55e" if score <= 2 else ("#f59e0b" if score <= 3 else "#ef4444")
            else:
                color = "#ef4444" if score <= 2 else ("#f59e0b" if score <= 3 else "#22c55e")

            bar_pct = score / 5 * 100

            with st.expander(f"**{fid}: {factor.name_is}** — {score}/5"):
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
                    f'<div style="font-size:1.8rem;font-weight:800;color:{color};">{score}</div>'
                    f'<div style="flex:1;">'
                    f'<div style="background:#e2e8f0;border-radius:4px;height:10px;overflow:hidden;">'
                    f'<div style="background:{color};border-radius:4px;height:10px;width:{bar_pct}%;"></div>'
                    f'</div>'
                    f'<div style="display:flex;justify-content:space-between;margin-top:4px;'
                    f'font-size:0.7rem;color:#64748b;">'
                    f'<span>{factor.scale_low}</span><span>{factor.scale_high}</span>'
                    f'</div></div></div>',
                    unsafe_allow_html=True,
                )
                if just:
                    st.markdown(
                        f'<div style="color:#1e293b;font-size:0.9rem;line-height:1.6;">{just}</div>',
                        unsafe_allow_html=True,
                    )

    # ══════════════════════════════════════════════════════════════
    # TAB 2: ÁHÆTTUR
    # ══════════════════════════════════════════════════════════════
    with tab_risks:
        if not risk_profile:
            st.error("Villa við útreikning.")
            st.stop()

        sorted_risks = sorted(risk_profile.risks, key=lambda r: r.prob_likely, reverse=True)

        # ── Summary metrics ───────────────────────────────────
        high = sum(1 for r in sorted_risks if r.prob_likely > 0.40)
        med = sum(1 for r in sorted_risks if 0.20 <= r.prob_likely <= 0.40)
        low = sum(1 for r in sorted_risks if r.prob_likely < 0.20)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Samtals áhættur", len(sorted_risks))
        m2.metric("🔴 Háar (>40%)", high)
        m3.metric("🟡 Miðlungs", med)
        m4.metric("🟢 Lágar (<20%)", low)

        # ── Top threats ───────────────────────────────────────
        top_threats = [r for r in sorted_risks if r.prob_likely > 0.15][:6]
        if top_threats:
            st.markdown(
                '<div style="font-size:1rem;font-weight:600;color:#1e293b;'
                'margin:20px 0 12px 0;">Stærstu áhætturnar</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="font-size:0.85rem;color:#1e293b;margin-bottom:16px;">'
                'Þær áhættur sem eru líklegastar í þessari sviðsmynd og hvers vegna.'
                '</div>',
                unsafe_allow_html=True,
            )

            for risk in top_threats:
                p = risk.prob_likely
                icon = "🔴" if p > 0.40 else ("🟡" if p > 0.20 else "🟠")
                color = "#ef4444" if p > 0.40 else ("#f59e0b" if p > 0.20 else "#fb923c")

                with st.expander(
                    f"{icon} **{risk.name_is}** — {p*100:.0f}% líkur",
                    expanded=(p > 0.50),
                ):
                    # Probability bar
                    st.markdown(
                        f'<div style="background:#e2e8f0;border-radius:4px;height:10px;'
                        f'overflow:hidden;margin-bottom:8px;">'
                        f'<div style="background:{color};border-radius:4px;height:10px;'
                        f'width:{min(p*100,100):.0f}%;"></div></div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div style="font-size:0.8rem;color:#475569;">'
                        f'Svið: {risk.prob_low*100:.0f}% – '
                        f'<strong style="color:#1e293b;">{p*100:.0f}%</strong> – '
                        f'{risk.prob_high*100:.0f}%</div>',
                        unsafe_allow_html=True,
                    )

                    # What drives this risk
                    if risk.breakdown:
                        drivers_up = []
                        drivers_down = []
                        for fid, effect, _desc in risk.breakdown:
                            fname = STRUCTURAL_FACTORS[fid].name_is
                            fscore = sf.get_factor(fid)
                            if effect > 1.15:
                                drivers_up.append(f"⚡ {fname} = {fscore}/5 → {effect:.2f}× (hækkar áhættu)")
                            elif effect < 0.85:
                                drivers_down.append(f"🛡️ {fname} = {fscore}/5 → {effect:.2f}× (lækkar áhættu)")

                        if drivers_up or drivers_down:
                            st.markdown(
                                '<div style="font-size:0.85rem;font-weight:600;color:#1e293b;'
                                'margin-top:12px;">Hvað stýrir þessari áhættu:</div>',
                                unsafe_allow_html=True,
                            )
                            for d in drivers_up:
                                st.markdown(f'<div style="color:#1e293b;font-size:0.85rem;">{d}</div>', unsafe_allow_html=True)
                            for d in drivers_down:
                                st.markdown(f'<div style="color:#1e293b;font-size:0.85rem;">{d}</div>', unsafe_allow_html=True)

                    # Affected goals
                    aff = [f"{gid}: {GOAL_SHORT_LABELS[gid]}" for gid in risk.affected_goals if gid in GOALS]
                    if aff:
                        st.markdown(
                            f'<div style="font-size:0.82rem;color:#1e293b;margin-top:8px;">'
                            f'<strong>Hefur áhrif á:</strong> {", ".join(aff)}</div>',
                            unsafe_allow_html=True,
                        )

        # ── Best-protected risks ──────────────────────────────
        low_risks = [r for r in sorted_risks if r.prob_likely < 0.15]
        low_risks.sort(key=lambda r: r.prob_likely)
        best_protected = low_risks[:4]

        if best_protected:
            st.markdown(
                '<div style="font-size:1rem;font-weight:600;color:#1e293b;'
                'margin:28px 0 12px 0;">Vel varið — lágar áhættur</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="font-size:0.85rem;color:#1e293b;margin-bottom:16px;">'
                'Þessar áhættur eru ólíklegar í þessu uppbyggingarformi vegna uppbyggingar þess.'
                '</div>',
                unsafe_allow_html=True,
            )

            for risk in best_protected:
                p = risk.prob_likely
                st.markdown(
                    f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;'
                    f'border-radius:8px;padding:12px 16px;margin-bottom:8px;">'
                    f'<div style="font-size:0.88rem;font-weight:600;color:#166534;">'
                    f'🟢 {risk.name_is} — {p*100:.0f}%</div>',
                    unsafe_allow_html=True,
                )
                # Show protective factors
                if risk.breakdown:
                    shields = []
                    for fid, effect, _desc in risk.breakdown:
                        if effect < 0.85:
                            fname = STRUCTURAL_FACTORS[fid].name_is
                            shields.append(fname)
                    if shields:
                        st.markdown(
                            f'<div style="font-size:0.8rem;color:#15803d;">'
                            f'Varið af: {", ".join(shields)}</div>',
                            unsafe_allow_html=True,
                        )
                st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # TAB 3: MARKMIÐ
    # ══════════════════════════════════════════════════════════════
    with tab_goals:
        st.markdown(
            '<div style="font-size:0.92rem;color:#1e293b;line-height:1.6;margin-bottom:20px;">'
            'Hvert markmið fær skor frá 1 til 12 miðað við allar 12 sviðsmyndir. '
            '<strong>12 = besta leiðin</strong>, <strong>1 = versta leiðin</strong>. '
            'Hér sjáum við hvar þessi sviðsmynd er sterkust og hvar hún er veikust.'
            '</div>',
            unsafe_allow_html=True,
        )

        # Rank all goals for this scenario
        scenario_goal_scores = []
        for gid in GOAL_IDS:
            score = goal_ranks.get((selected, gid), 6)
            scenario_goal_scores.append((gid, score))

        scenario_goal_scores.sort(key=lambda x: x[1], reverse=True)

        # ── Top 3 strengths ───────────────────────────────────
        top_3 = scenario_goal_scores[:3]
        st.markdown(
            '<div style="font-size:1rem;font-weight:600;color:#1e293b;'
            'margin-bottom:12px;">Sterkustu markmið þessarar sviðsmyndar</div>',
            unsafe_allow_html=True,
        )

        for gid, score in top_3:
            short = GOAL_SHORT_LABELS[gid]
            full_desc = GOAL_DESCRIPTIONS[gid]
            color = goal_rank_color(score)
            bar_pct = score / 12 * 100

            st.markdown(
                f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;'
                f'border-radius:10px;padding:14px 18px;margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div>'
                f'<div style="font-size:0.92rem;font-weight:700;color:#166534;">'
                f'{gid}: {short}</div>'
                f'<div style="font-size:0.8rem;color:#1e293b;margin-top:2px;">{full_desc}</div>'
                f'</div>'
                f'<div style="text-align:right;min-width:70px;">'
                f'<div style="font-size:1.4rem;font-weight:800;color:{color};">{score}/12</div>'
                f'</div></div>'
                f'<div style="background:#dcfce7;border-radius:4px;height:6px;'
                f'overflow:hidden;margin-top:8px;">'
                f'<div style="background:{color};border-radius:4px;height:6px;'
                f'width:{bar_pct}%;"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Bottom 2 weaknesses ───────────────────────────────
        bottom_2 = scenario_goal_scores[-2:]
        bottom_2.reverse()  # worst first

        st.markdown(
            '<div style="font-size:1rem;font-weight:600;color:#1e293b;'
            'margin:28px 0 12px 0;">Veikustu markmið — þar sem aðrar leiðir standa betur</div>',
            unsafe_allow_html=True,
        )

        for gid, score in bottom_2:
            short = GOAL_SHORT_LABELS[gid]
            full_desc = GOAL_DESCRIPTIONS[gid]
            color = goal_rank_color(score)
            bar_pct = score / 12 * 100

            st.markdown(
                f'<div style="background:#fef2f2;border:1px solid #fecaca;'
                f'border-radius:10px;padding:14px 18px;margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div>'
                f'<div style="font-size:0.92rem;font-weight:700;color:#991b1b;">'
                f'{gid}: {short}</div>'
                f'<div style="font-size:0.8rem;color:#1e293b;margin-top:2px;">{full_desc}</div>'
                f'</div>'
                f'<div style="text-align:right;min-width:70px;">'
                f'<div style="font-size:1.4rem;font-weight:800;color:{color};">{score}/12</div>'
                f'</div></div>'
                f'<div style="background:#fee2e2;border-radius:4px;height:6px;'
                f'overflow:hidden;margin-top:8px;">'
                f'<div style="background:{color};border-radius:4px;height:6px;'
                f'width:{bar_pct}%;"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── All goals overview bar chart ──────────────────────
        st.markdown(
            '<div style="font-size:1rem;font-weight:600;color:#1e293b;'
            'margin:28px 0 12px 0;">Öll markmið — yfirlit</div>',
            unsafe_allow_html=True,
        )

        for gid, score in scenario_goal_scores:
            short = GOAL_SHORT_LABELS[gid]
            color = goal_rank_color(score)
            bar_pct = score / 12 * 100

            st.markdown(
                f'<div class="rank-row">'
                f'<span class="rank-label">{short}</span>'
                f'<div class="rank-bar-bg">'
                f'<div class="rank-bar-fill" style="width:{bar_pct:.0f}%;background:{color};"></div>'
                f'</div>'
                f'<span class="rank-score" style="color:{color};">{score}/12</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ═════════════════════════════════════════════════════════════════════
# PAGE 3: AÐFERÐAFRÆÐI
# ═════════════════════════════════════════════════════════════════════

elif page == "📖 Aðferðafræði":

    st.markdown('<div class="page-header">Aðferðafræði</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-intro">'
        'Reiknilíkanið sem liggur að baki ákvörðunarstuðningskerfinu. '
        'Ætlað endurskoðendum, lögfræðingum og ákvarðanatökum.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Fimm-laga reiknilíkan")
    st.markdown("""
**Lag 1 — Skipulagsþættir (F1–F7):**
Hver sviðsmynd fær einkunn 1–5 á sjö þáttum sem lýsa uppbyggingu
eignarhaldsleiðar: hverjir eiga, hverjir byggja, hvernig er fjármagnað,
hver stýrir, o.s.frv. Hver einkunn er rökstudd.

**Lag 2 — Áhættuþolni (Risk Sensitivities):**
Hvert af 33 áhættum hefur skilgreint þolni gagnvart þáttum.
Stefna (PROTECTIVE/EXPOSURE) og styrkur (LOW/MEDIUM/HIGH/CRITICAL)
ákvarða hvernig þáttaskor breytir áhættulíkum.

**Lag 3 — Áhættureikningur (Logistic Model):**
Grunnlíkur → log-odds → aðlagað eftir þáttaáhrifum → sigmoid → líkur.
Tryggir 0–100% mörk stærðfræðilega. Engin gervileg þök.

**Lag 4 — Áhrif á markmið (Goal Impacts):**
Hvert par áhætta × markmið: PERT-mat (besta/líklegast/versta).
Vænt framlag = P(áhætta) × E[áhrif].

**Lag 5 — Vegið skor:**
Einingarnar stöðlaðar, vegnar eftir vali notanda, summað.
Lægra skor = betri sviðsmynd.
    """)

    st.markdown("### Stærðfræðilegar forsendur")
    st.markdown("""
**Áhrifafall þáttar:**

PROTECTIVE: `effect = (3 / (3 + d))^s`

EXPOSURE: `effect = ((3 + d) / 3)^s`

þar sem `d = skor − 3` og `s = styrkleikaveldi` (0.5 / 1.0 / 1.5 / 2.0)

**Logistic umbreyting:**

1. `L₀ = ln(p / (1−p))` — grunnlíkur → log-odds
2. `L₁ = L₀ + Σ ln(effect)` — aðlögun í log-odds rúmi
3. `p' = 1 / (1 + e^(−L₁))` — sigmoid → líkur
4. Klemma: `[1×10⁻¹⁵, 1 − 1×10⁻¹⁵]` — float64 öryggismörk

**PERT-meðaltal:** `E = (besta + 4×líklegast + versta) / 6`
    """)

    st.markdown("### Öryggisstig gagna")

    conf_data = []
    for rid in sorted(RISK_PROFILES.keys(), key=lambda x: int(x[1:])):
        risk = RISK_PROFILES[rid]
        conf = RISK_CONFIDENCE.get(rid)
        if conf:
            icons = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
            conf_data.append({
                "Áhætta": f"{rid}: {risk.name_is}",
                "Öryggi": f"{icons.get(conf.tier_en, '')} {conf.tier}",
                "Rökstuðningur": conf.justification,
            })
    st.dataframe(pd.DataFrame(conf_data), use_container_width=True, hide_index=True)

    st.markdown("### Staðfesting")
    st.markdown("""
Reiknilíkanið hefur verið staðfest með **2.874 sjálfvirkum prófunum:**

| Flokkur | Lýsing | Staða |
|---------|--------|-------|
| Skipulag | 84 þáttagildi í bili 1–5, allar 12 sviðsmyndir | ✅ |
| Gagnaheilleiki | 33 áhættur, grunnlíkur, þolni, markmið | ✅ |
| Áhrifaformerki | 100 áhrif, rétt stefna og röð | ✅ |
| Stærðfræði | Logistic: auðkenni, mörk, monotonía, overflow | ✅ |
| Stærðfræði | PERT-röðun varðveitt eftir umbreytingu | ✅ |
| Stigagjöf | Stöðlun, formerki, abs() öryggi | ✅ |
| Heilbrigðisathugun | S11 = #1, S9 = #12 á jafnvægi | ✅ |
| Rökstuðningur | 84 textar, >80 stafir, rétt einkunn | ✅ |
| Öryggisstig | 33 stig, gilt form | ✅ |
| Samræmi | affected_goals = RISK_GOAL_IMPACTS | ✅ |
    """)

    st.markdown("### Uppfærsluskrá")
    st.markdown("""
**v5 — 33 áhættur, G9 lagfært, stöðlun endurkvörðuð (febrúar 2026)**
- R34–R37 bætt við: skattar, útboðsreglur, slit samstarfs, hagsmunaárekstrar
- R30 útvíkkað: millisala byggingarréttar og virðisaukning lands
- G9 grunngildi breytilegt eftir F6/F7 (40–100 í stað 100 alltaf)
- R04→G9 og R11→G9 fjarlægð (verktakaþættir, ekki borgarstjórnun)
- Stöðlun endurkvörðuð: öll markmið jafn áhrifarík við sömu vægi
- 2.874 sjálfvirk próf standast

**v4 — 29 áhættur og uppfærð staðfesting (febrúar 2026)**
- 29. áhætta bætt við (R29–R33), 4 áhættur sameinaðar/fjarlægðar
- Öll 28→29 tilvísanir lagfærðar
- Staðfestingarpróf uppfærð

**v3 — Endanleg útgáfa (febrúar 2026)**
- Logistic (sigmoid) líkan í stað capped multiplicative
- G6 styrktur: 3 áhættur í stað 1
- 4 vantar þolni bætt við
- 10 rökstuðningstextar endurbættir
- Float64 útkomuklemma
- Dead code fjarlægður
    """)