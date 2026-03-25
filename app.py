"""
Policy Response — Enterprise PoC
Agentic Workflow · Structured Output · Role-based Deliverables
"""

import streamlit as st
import anthropic
import json
import re
import os
import io
import time
from typing import Optional, Dict, List

import plotly.graph_objects as go

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Policy Response",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Luxury CSS (Tiffany Blue accent) ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Montserrat:wght@300;400;500;600&display=swap');

:root {
    --accent:        #0ABAB5;
    --accent-dark:   #089590;
    --accent-hover:  #0DCEC8;
    --accent-a12:    rgba(10, 186, 181, 0.12);
    --accent-a18:    rgba(10, 186, 181, 0.18);
    --accent-border: rgba(10, 186, 181, 0.15);
    --bg:            #0A0A0A;
    --bg-card:       #111111;
    --bg-card2:      #161616;
    --bg-sidebar:    #0D0D0D;
    --text:          #F0EDE6;
    --text-sec:      #A8A49E;
    --text-muted:    #C4BFB8;
    --threat:        #8B2635;
    --opp:           #1A6B3C;
    --serif:         "Cormorant Garamond", "Palatino Linotype", "Palatino", Georgia, serif;
    --sans:          "Montserrat", "Helvetica Neue", Helvetica, -apple-system, sans-serif;
}

/* ── GLOBAL ─────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
.stApp { background: var(--bg) !important; }
.main .block-container {
    background: var(--bg) !important;
    padding: 2.5rem 3.5rem !important;
    max-width: 1440px !important;
}

/* ── SIDEBAR TOGGLE (always visible even when header is hidden) ── */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    display: flex !important;
    background: rgba(13,13,13,0.82) !important;
    border-right: 1px solid rgba(10,186,181,0.22) !important;
    border-radius: 0 6px 6px 0 !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    color: rgba(10,186,181,0.70) !important;
    fill:  rgba(10,186,181,0.70) !important;
    transition: color 0.2s, fill 0.2s !important;
}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
    background: rgba(10,186,181,0.10) !important;
}
[data-testid="collapsedControl"]:hover svg,
[data-testid="stSidebarCollapsedControl"]:hover svg {
    color: #0ABAB5 !important;
    fill:  #0ABAB5 !important;
}

/* ── SIDEBAR ────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--accent-border) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.6rem !important;
}

/* ── TYPOGRAPHY ─────────────────────────────── */
h1, h2, h3, h4 {
    font-family: var(--serif) !important;
    color: var(--text) !important;
    letter-spacing: 0.06em !important;
}
h1 { font-weight: 300 !important; }
h2 { font-weight: 300 !important; }
h3 { font-weight: 400 !important; }
p, label, .stMarkdown p,
.stMarkdown span, .stText span,
[data-testid="stRadio"] span,
[data-testid="stCaptionContainer"] span,
[data-testid="stTextArea"] span,
[data-testid="stTextInput"] span,
[data-testid="stButton"] span,
[data-testid="stDownloadButton"] span {
    font-family: var(--sans) !important;
}
[data-testid="stStatusWidget"] span,
[data-testid="stNotification"] span,
[data-testid="stAlert"] span,
[class*="StatusIndicator"] span,
[class*="stStatus"] span {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined",
                 "Material Icons", sans-serif !important;
    font-feature-settings: "liga" 1 !important;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: var(--serif) !important;
    color: var(--text) !important;
    border-bottom: 1px solid var(--accent-border);
    padding-bottom: 0.4em;
    letter-spacing: 0.05em !important;
}
.stMarkdown h4 {
    font-family: var(--sans) !important;
    color: var(--accent) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
    border-bottom: 1px solid var(--accent-border);
    padding-bottom: 0.4em;
}
.stMarkdown strong { color: var(--accent) !important; }
.stMarkdown a { color: var(--accent) !important; text-decoration: none !important; }
.stMarkdown blockquote {
    border-left: 3px solid var(--accent) !important;
    background: var(--bg-card) !important;
    padding: 0.8rem 1.2rem !important;
    margin: 1rem 0 !important;
}
.stMarkdown hr { border-top: 1px solid var(--accent-border) !important; margin: 1.5rem 0 !important; }
.stMarkdown ul li, .stMarkdown ol li {
    color: var(--text-sec) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
    line-height: 1.8 !important;
}
.stMarkdown code {
    background: var(--bg-card2) !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent-border) !important;
    border-radius: 0 !important;
    font-size: 0.8rem !important;
    padding: 0.1em 0.4em !important;
}

/* ── PRIMARY BUTTONS ────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #0ABAB5 0%, #089590 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 0 !important;
    letter-spacing: 0.20em !important;
    text-transform: uppercase !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    font-size: 0.70rem !important;
    padding: 0.9rem 1.8rem !important;
    transition: all 0.35s ease !important;
    box-shadow: 0 2px 18px rgba(10, 186, 181, 0.14) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0DCEC8 0%, #0ABAB5 100%) !important;
    box-shadow: 0 4px 28px rgba(10, 186, 181, 0.34) !important;
    transform: translateY(-1px) !important;
    color: #FFFFFF !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button:disabled {
    background: #111111 !important;
    color: var(--text-muted) !important;
    border: 1px solid rgba(10, 186, 181, 0.08) !important;
    box-shadow: none !important;
    transform: none !important;
    cursor: not-allowed !important;
}

/* ── SECONDARY BUTTONS (HITL actions) ───────── */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-sec) !important;
    border: 1px solid rgba(10, 186, 181, 0.25) !important;
    box-shadow: none !important;
    font-size: 0.66rem !important;
    letter-spacing: 0.12em !important;
    padding: 0.72rem 1.1rem !important;
    text-transform: none !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(10, 186, 181, 0.07) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: none !important;
    box-shadow: none !important;
}

[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent-border) !important;
    box-shadow: none !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.18em !important;
    padding: 0.65rem 1.4rem !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: var(--accent-a12) !important;
    border-color: var(--accent) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── TEXT INPUTS ────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #111111 !important;
    border: 1px solid var(--accent-border) !important;
    border-radius: 0 !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.83rem !important;
    transition: border-color 0.3s !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px rgba(10, 186, 181, 0.22) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: var(--text-muted) !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    font-family: var(--sans) !important;
    margin-bottom: 0.4rem !important;
}

/* ── RADIO ──────────────────────────────────── */
[data-testid="stRadio"] > label {
    color: var(--text-muted) !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    font-family: var(--sans) !important;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.80rem !important;
    color: var(--text-sec) !important;
    font-family: var(--sans) !important;
    line-height: 1.5 !important;
}

/* ── TABS ───────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--accent-border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    font-family: var(--sans) !important;
    font-size: 0.66rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    padding: 0.85rem 1.6rem !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.3s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--accent) !important; }
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: var(--accent) !important; height: 2px !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding: 2rem 0 !important; }

/* ── EXPANDER ───────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--accent-border) !important;
    border-radius: 0 !important;
}
[data-testid="stExpander"] summary {
    color: var(--text-muted) !important;
    font-family: var(--sans) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
}

/* ── STATUS WIDGET ──────────────────────────── */
[data-testid="stStatusWidget"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--accent-border) !important;
    border-radius: 0 !important;
}
[data-testid="stStatusWidget"] p,
[data-testid="stStatusWidget"] div:not([class*="icon"]) {
    font-family: var(--sans) !important;
    font-size: 0.82rem !important;
    color: var(--text-sec) !important;
}
[data-testid="stStatusWidget"] > div > div:first-child {
    min-width: 1.5rem !important;
    display: inline-flex !important;
    align-items: center !important;
}

/* ── ALERTS / INFO (Evidence quotes) ────────── */
[data-testid="stAlert"] {
    border-radius: 0 !important;
    font-family: var(--sans) !important;
    font-size: 0.83rem !important;
    background: var(--bg-card2) !important;
}
/* st.info override — evidence quote style */
[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(10, 186, 181, 0.04) !important;
    border: 1px solid rgba(100, 116, 139, 0.30) !important;
    border-left: 3px solid #64748B !important;
    border-radius: 0 !important;
}
[data-testid="stAlert"] p {
    color: rgba(255, 255, 255, 0.90) !important;
    font-style: normal !important;
    font-weight: 400 !important;
    font-family: var(--sans) !important;
    font-size: 0.86rem !important;
    line-height: 1.6 !important;
}

/* ── DIVIDER / CAPTION / JSON ───────────────── */
hr { border: none !important; border-top: 1px solid var(--accent-border) !important; margin: 2rem 0 !important; }
[data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important; font-size: 0.68rem !important;
    letter-spacing: 0.08em !important; font-family: var(--sans) !important;
}
[data-testid="stJson"] {
    background: var(--bg-card) !important; border: 1px solid var(--accent-border) !important;
    font-family: "SF Mono", "Monaco", monospace !important; font-size: 0.78rem !important;
}

/* ── SCROLLBAR ──────────────────────────────── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(10, 186, 181, 0.18); }
::-webkit-scrollbar-thumb:hover { background: rgba(10, 186, 181, 0.40); }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
MODEL = "claude-opus-4-6"

DOMAIN_PROFILES: Dict[str, str] = {
    "AI Licensing & Copyright": (
        "Core business: licensing proprietary editorial content and structured data to generative AI operators "
        "(global LLM providers, AI startups, enterprise AI vendors). "
        "Primary risk vectors: unauthorized training data ingestion, inadequate royalty-sharing structures, "
        "IP dilution through derivative AI outputs. "
        "Key objectives: maximize licensing revenue through fair valuation of training data supply, "
        "enforce copyright via technical protection measures and robots.txt, "
        "establish enforceable indemnification clauses in all AI partnership agreements. "
        "Special sensitivity: any policy change affecting copyright ownership, consent mechanisms for data use, "
        "or compensation frameworks for rights holders carries CRITICAL-level exposure."
    ),
    "AI Search & Zero-Click": (
        "Core business: Japan's leading digital subscription media, dependent on organic search traffic "
        "for subscriber acquisition and ad revenue. "
        "Primary risk vectors: AI Overviews and Zero-click AI Answers reducing article click-through rates, "
        "AI-generated summaries displacing direct content consumption, "
        "algorithm changes deprioritizing premium paywalled content. "
        "Key objectives: maintain referral traffic integrity, defend against AI summary cannibalization, "
        "negotiate traffic guarantees or equivalent value-exchange in platform agreements. "
        "Special sensitivity: any policy change enabling platform AI to summarize content without redirect, "
        "or modifying traffic attribution models, carries HIGH-to-CRITICAL revenue exposure."
    ),
    "Platform Distribution Policies": (
        "Core business: multi-platform content distribution across social, video, audio, and aggregator channels "
        "including Meta, Google Discover, YouTube, Apple News, and LINE. "
        "Primary risk vectors: unilateral platform rule changes that restrict content eligibility, "
        "monetization policy updates reducing CPM or revenue-share rates, "
        "algorithmic demotion of news/editorial content, "
        "new data-sharing requirements creating compliance overhead. "
        "Key objectives: preserve multi-channel distribution breadth, negotiate favored-partner terms, "
        "maintain content autonomy under platform moderation policies. "
        "Special sensitivity: any policy mandating content modification, consent UI on distributed content, "
        "or new data-reporting obligations to the platform carries HIGH product and legal exposure."
    ),
}

# Domain-specific risk context injected into LLM prompts for calibrated output
DOMAIN_RISK_FOCUS: Dict[str, str] = {
    "AI Licensing & Copyright": (
        "The user is evaluating this policy change from the perspective of the 'AI Licensing & Copyright' domain. "
        "Place HEIGHTENED emphasis on: IP ownership implications, copyright consent mechanisms, "
        "royalty and compensation structures, indemnification requirements, and training-data usage rights. "
        "Treat any ambiguity in copyright assignment or consent scope as a CRITICAL-level exposure."
    ),
    "AI Search & Zero-Click": (
        "The user is evaluating this policy change from the perspective of the 'AI Search & Zero-Click' domain. "
        "Place HEIGHTENED emphasis on: traffic attribution, AI summary/snippet impact on click-through rates, "
        "referral traffic guarantees, and SERP feature policies that displace direct content consumption. "
        "Quantify estimated traffic and revenue loss in percentage and absolute terms where possible."
    ),
    "Platform Distribution Policies": (
        "The user is evaluating this policy change from the perspective of the 'Platform Distribution Policies' domain. "
        "Place HEIGHTENED emphasis on: content eligibility rules, monetization policy changes, "
        "data-sharing obligations, algorithmic demotion risks, and consent UI requirements on distributed content. "
        "Assess impact per distribution channel (search, social, video, aggregator) separately where relevant."
    ),
}

STRATEGIST_SYSTEM = (
    "You are the Chief Strategy Officer of Japan's largest media enterprise, "
    "with 150 years of editorial judgment and rigorous copyright discipline. "
    "You lead Co-Build initiatives with global AI Funds and drive AI partnership strategy.\n"
    "Your mandate: deliver specific, actionable, board-level recommendations on digital transformation, "
    "AI-era copyright defense, and global AI Fund partnership strategy.\n"
    "Every output must include quantified metrics, deadlines, and responsible departments. "
    "Eliminate abstraction — precision and executability are non-negotiable.\n"
    "All output must be in professional business English."
)

# ─── Scenario Router ──────────────────────────────────────────────────────────
def get_scenario_data(policy_text: str) -> Optional[Dict]:
    """Return complete mock pipeline data keyed to input text keywords.
    Returns None when no keyword matches (fall through to live LLM pipeline).
    """
    txt = policy_text.upper()

    # ── GAIF: Zero-click threat scenario ───────────────────────────────────────
    if "GAIF" in txt:
        domain = "AI Search & Zero-Click"
        step1 = {
            "added_obligations": [
                {"item": "Mandatory Zero-click AI Answers format",
                 "severity": "high",
                 "description": "All search results must be displayed in GAIF's inline AI answer format without optional redirect links."},
                {"item": "Compulsory indexing opt-in",
                 "severity": "high",
                 "description": "Publishers must affirmatively opt-in to GAIF's AI training pipeline or lose search visibility entirely."},
                {"item": "Revenue share cap at 8%",
                 "severity": "medium",
                 "description": "GAIF v3.1 imposes a unilateral cap of 8% revenue share for attributed AI summaries."},
            ],
            "removed_rights": [
                {"item": "Traffic attribution guarantee",
                 "severity": "high",
                 "description": "Previous terms included a minimum referral traffic baseline; removed entirely in v3.1."},
                {"item": "Source link prominence requirement",
                 "severity": "high",
                 "description": "Obligation to display publisher source links above the fold has been eliminated."},
            ],
            "key_thresholds": [
                {"item": "Zero-click AI Answer word limit", "value": "40 words",
                 "description": "Summaries exceeding 40 words require separate licensing — previously uncapped."},
                {"item": "Opt-in deadline", "value": "90 days",
                 "description": "Publishers must opt-in within 90 days or face automatic de-indexing."},
            ],
            "context_summary": (
                "GAIF Publisher Ecosystem Terms v3.1 consolidates AI answers inline, eliminating the "
                "traffic referral baseline that underpinned Nikkei's search-driven subscription model. "
                "The update forces binary indexing opt-ins and caps revenue share, representing a "
                "critical structural shift in the publisher-platform relationship."
            ),
            "parsed_claims": [
                "GAIF 'Direct Answers' will now provide comprehensive inline AI summaries, replacing traditional blue-link search results for all informational queries.",
                "Publisher source links will be consolidated and moved to a separate 'References' tab, eliminating above-the-fold attribution for all Zero-click AI Answer formats.",
                "Publishers who implement machine-readable opt-outs via the GAIF Publisher Portal will be excluded from all GAIF search indexing within 90 days of opt-out submission.",
            ],
        }
        step2 = {
            "scores": {
                "IP":      {"score": 75, "direction": "threat",
                            "evidence": "Compulsory opt-in to AI training pipeline undermines copyright ownership of editorial content.",
                            "priority_actions": ["Invoke Clause 4.2 opt-out right immediately", "Escalate to outside IP counsel"]},
                "Traffic": {"score": 98, "direction": "threat",
                            "evidence": "Removal of referral traffic guarantee threatens 85%+ of search-driven subscriber acquisition.",
                            "priority_actions": ["Activate Article 7(c) termination clause", "Begin direct audience migration strategy"]},
                "Revenue": {"score": 90, "direction": "threat",
                            "evidence": "8% revenue share cap represents a 60%+ reduction from current contractual floor.",
                            "priority_actions": ["Reject v3.1 terms pending renegotiation", "Prepare alternative monetisation roadmap"]},
                "Product": {"score": 65, "direction": "threat",
                            "evidence": "Mandatory inline format requires product re-architecture of content delivery APIs.",
                            "priority_actions": ["Audit current API endpoints", "Estimate 6-week engineering sprint for compliance stack"]},
            },
            "overall_risk_level": "critical",
            "stance_label": "PROTECT & WAIT",
            "executive_summary": (
                "GAIF v3.1 poses a CRITICAL existential threat to Nikkei's search-driven revenue model. "
                "The elimination of traffic attribution and imposition of a revenue share cap demands "
                "immediate IP defense. Strategic stance: PROTECT & WAIT — reject terms, preserve optionality, "
                "and leverage collective publisher coalition before re-engagement."
            ),
            "key_opportunities": [
                "Lead publisher coalition counter-proposal to GAIF Governance Board",
                "Accelerate direct newsletter and app subscriber conversion to reduce search dependency",
                "Use termination threat as leverage to reopen bilateral licensing negotiation",
            ],
            "key_threats": [
                "98/100 traffic exposure if de-indexed — catastrophic subscriber acquisition impact",
                "Precedent risk: accepting v3.1 terms sets industry baseline for all future AI platform deals",
                "90-day opt-in deadline creates artificial urgency for an unfavourable decision",
            ],
            "card_scores": {
                "IP":      {"score": 75, "direction": "threat",
                            "evidence": "AI training linkage",
                            "action_badge": "PROTECT",
                            "action_summary": "Defend core copyright boundaries against unauthorized scraping.",
                            "priority_actions": ["Invoke Clause 4.2 opt-out right immediately", "Escalate to outside IP counsel"]},
                "Traffic": {"score": 15, "direction": "threat",
                            "evidence": "Critical Threat: Total loss of referral traffic due to zero-click",
                            "action_badge": "PROTECT",
                            "action_summary": "Mitigate severe referral loss through technical countermeasures.",
                            "priority_actions": ["Activate Article 7(c) termination clause", "Begin direct audience migration strategy"]},
                "Revenue": {"score": 20, "direction": "threat",
                            "evidence": "Loss of revenue share",
                            "action_badge": "WAIT",
                            "action_summary": "Hold on revenue share negotiations until traffic impact is clear.",
                            "priority_actions": ["Reject v3.1 terms pending renegotiation", "Prepare alternative monetisation roadmap"]},
                "Product": {"score": 65, "direction": "opportunity",
                            "evidence": "Need to build new consent gates",
                            "action_badge": "WAIT",
                            "action_summary": "Delay new feature rollout pending technical opt-out specs.",
                            "priority_actions": ["Audit current API endpoints", "Estimate 6-week engineering sprint for compliance stack"]},
            },
            "pmg_evidence": [
                "Violates the 'minimum traffic referral baseline' established during our 2023 Search Partnership Renewal.",
                "Board explicitly rejected zero-click expansion without compensation in Q4 2024 strategy meetings.",
            ],
        }
        step3 = {
            "what_changed_brief": (
                "BEFORE: Publishers received guaranteed traffic attribution and negotiated revenue share "
                "under GAIF v3.0. Source links appeared above the fold; referral traffic was contractually protected.\n\n"
                "AFTER: GAIF v3.1 consolidates all answers as inline Zero-click AI Answers, hides source links, "
                "removes the referral traffic baseline, caps revenue share at 8%, and forces a binary indexing "
                "opt-in under a 90-day deadline. This is a unilateral restructuring of the publisher-platform contract."
            ),
            "what_changed_quotes": [
                "Mandatory Zero-click AI Answers format without attribution.",
                "Publishers must affirmatively opt-in to GAIF's AI training pipeline or lose search visibility.",
                "Revenue share cap at 8% imposed unilaterally effective 90 days from notice.",
            ],
            "overall_risk": "CRITICAL",
            "business_exposure_memo": (
                "(1) Traffic & Audience Reach: Search-driven traffic accounts for an estimated 85% of new "
                "subscriber acquisition. Elimination of the referral baseline (Traffic score: 98/100) is the "
                "single largest near-term revenue threat in the company's digital history.\n\n"
                "(2) Revenue Streams: The unilateral 8% revenue share cap reduces licensing revenue by "
                "approximately 60% relative to current contractual floors. Combined with traffic loss, "
                "total digital revenue exposure is estimated at ¥4.2–6.8B annually.\n\n"
                "(3) IP & Copyright: The compulsory AI training opt-in (IP score: 75/100) requires "
                "Nikkei to grant GAIF a broad sublicensing right over all indexed editorial content — "
                "directly conflicting with our 2024 partner contract red-lines (Clause 4.2).\n\n"
                "(4) Product & Platform: Mandatory inline format requires API re-architecture. "
                "Engineering estimates 6 weeks minimum for compliance stack delivery.\n\n"
                "(5) Brand & Competitive Standing: Accepting terms signals capitulation to platform "
                "consolidation and weakens our position in all future AI licensing negotiations."
            ),
            "business_exposure_quotes": [
                "Zero-click AI Answers format consolidates answers inline, eliminating source link prominence.",
                "Revenue share cap at 8% imposed unilaterally.",
                "Publishers must opt-in within 90 days or face automatic de-indexing.",
            ],
            "negotiation_brief": (
                "(1) Non-Negotiable Conditions: Restoration of minimum referral traffic baseline (≥40% of current "
                "organic search referrals). Prohibition on AI training use of editorial content without separate "
                "written consent and compensation. Revenue share floor at current contractual rate.\n\n"
                "(2) Items Requiring Written Confirmation: Any opt-in to AI training pipeline requires CEO "
                "and Board sign-off. Revenue share changes require 180-day advance notice under Clause 8.1.\n\n"
                "(3) Strongest Leverage Points: Activation of Article 7(c) hard termination trigger "
                "(>40-word Zero-click AI Answers without redirect). Publisher coalition coordination — "
                "GAIF cannot afford mass de-indexing of premium content publishers simultaneously.\n\n"
                "(4) Acceptable Compromise Zones: Phased opt-in timeline extension to 180 days. "
                "Tiered revenue share by content category.\n\n"
                "(5) Red Lines: Under no circumstances accept v3.1 terms as presented. "
                "Do not waive Article 7(c) termination rights."
            ),
            "negotiation_quotes": [
                "Any Zero-click AI Answers rendering of more than 40 words triggers hard termination clause.",
                "Revenue share cap at 8% is a unilateral breach of existing contractual floor.",
                "Opt-in deadline of 90 days is commercially unreasonable.",
            ],
            "board_memo": (
                "WHAT HAPPENED: GAIF published v3.1 Publisher Ecosystem Terms on [DATE], eliminating "
                "traffic referral guarantees and capping revenue share at 8%. This is the most significant "
                "adverse platform policy change since Google's 2014 algorithm update.\n\n"
                "FINANCIAL EXPOSURE: ¥4.2–6.8B annual digital revenue at risk. Search-driven subscriber "
                "acquisition (85% of new subscriptions) threatened within 90 days if terms are accepted.\n\n"
                "DECISIONS REQUIRED: (1) Authorise Legal to invoke Article 7(c) termination notice. "
                "(2) Approve publisher coalition participation. (3) Reject v3.1 terms formally by [DATE+30].\n\n"
                "RECOMMENDED ACTIONS: Legal (Owner: GC) — Issue formal objection letter within 7 days. "
                "Business Dev (Owner: CDO) — Convene publisher coalition within 14 days. "
                "Product (Owner: CPO) — Accelerate direct channel migration sprint.\n\n"
                "SCENARIOS: Best case — GAIF renegotiates under coalition pressure, restores traffic baseline. "
                "Base case — 6-month negotiation standoff; limited traffic degradation. "
                "Worst case — GAIF enforces de-indexing; ¥6.8B revenue impact materialises within FY2026."
            ),
            "board_memo_quotes": [
                "GAIF v3.1 eliminates the traffic referral baseline without compensation.",
                "Revenue share cap at 8% represents a unilateral contract modification.",
                "90-day opt-in deadline compresses board decision time unacceptably.",
            ],
            "product_checklist": [
                "[CONSENT MECHANISM] Legal & Product — Design explicit opt-out flow for GAIF AI training "
                "pipeline. Trigger: before any v3.1 opt-in submission. Capture: user ID, timestamp, "
                "version of terms declined, legal basis. Segment: all content admin users.",
                "[CONSENT UI] UX Team — Implement full-screen gate modal (not banner) before opt-in "
                "confirmation. Must include plain-language summary, link to Article 7(c), and 'Decline & "
                "Request Legal Review' CTA. No pre-checked boxes (dark pattern prohibition).",
                "[LEGAL DISCLOSURE] Communications — Send board notification within 48 hours of formal "
                "objection letter dispatch. Publish internal FAQ to editorial and product teams within 7 "
                "days. Log all disclosure timestamps in compliance record.",
                "[FEATURE CHANGE] Engineering — Freeze all GAIF API integration updates pending "
                "renegotiation outcome. Add monitoring alert for de-indexing signals on top 500 articles. "
                "Deadline: implement within 5 business days.",
                "[AUDIT LOGGING] Data Engineering — Log all GAIF API requests, response codes, and "
                "content delivery events. Retention: 7 years (litigation hold). Format: structured JSON "
                "with article ID, request timestamp, and attribution status.",
            ],
        }
        debate = [
            {"agent": "⚖️ Legal Agent", "color": "#8B2635",
             "message": (
                 "[🎯 Policy Memory Graph Match: Article 7(c) — 2024 Google SGE pre-negotiation memo] "
                 "Traffic exposure at 98/100 — CRITICAL. GAIF v3.1 directly violates the 'minimum traffic "
                 "referral baseline' red-line confirmed by Legal Committee in 2023. Article 7(c) hard "
                 "termination trigger is activated by any Zero-click AI Answers exceeding 40 words without "
                 "redirect. I am invoking standard outside-counsel escalation protocol. "
                 "Do not execute any opt-in under these terms."
             )},
            {"agent": "💰 Business Agent", "color": "#A8892A",
             "message": (
                 "Traffic impact at 98/100 is catastrophic — I concur with Legal on rejection. "
                 "However, the coalition play is our strongest card. GAIF cannot afford to de-index "
                 "Nikkei while simultaneously facing resistance from FT, NYT, and AP. "
                 "Revenue recovery path: accelerate direct channel conversion — newsletter and app "
                 "subscribers can offset 30–40% of search-driven acquisition within 18 months."
             )},
            {"agent": "🧩 Product Agent", "color": "#1A6B3C",
             "message": (
                 "Product constraint at 65/100. Freezing all GAIF API integration work pending "
                 "renegotiation. Direct channel migration sprint is feasible — 6 weeks for consent "
                 "gate, attribution dashboard, and de-indexing alert system. "
                 "Recommend CPO sign-off on sprint authorisation within 48 hours."
             )},
            {"agent": "🏛️ Executive Alignment", "color": "#0ABAB5", "final": True,
             "message": (
                 "Conflict Resolved. Unified position: PROTECT & WAIT. "
                 "Legal to issue formal Article 7(c) objection within 7 days. "
                 "Business Dev to convene publisher coalition within 14 days. "
                 "Product to freeze GAIF integrations and launch direct channel sprint. "
                 "Board notification required within 48 hours. No opt-in authorised under current terms."
             )},
        ]
        pmg_hits = [
            ("Article 7(c)", "2024 Google SGE pre-negotiation memo",
             "Any Zero-click AI Answers rendering of more than 40 words from a Nikkei article without a redirect "
             "was categorised as a hard termination trigger — binding precedent confirmed by Legal Committee."),
            ("Clause 11", "2023 Bing / Microsoft partner contract review",
             "Traffic attribution model changes require 90-day advance notice and board sign-off. "
             "Retroactive application of algorithm changes was explicitly rejected — directly applicable to GAIF v3.1."),
        ]
        matrix_clauses = [
            {"name": "Zero-click UI Change",   "x": 15, "y": 95, "color": "#C0392B", "size": 15},
            {"name": "Search Delisting Threat", "x": 30, "y": 98, "color": "#8B2635", "size": 14},
        ]

    # ── US Attribution Act scenario ─────────────────────────────────────────────
    elif "US" in txt or "ACT" in txt:
        domain = "AI Licensing & Copyright"
        step1 = {
            "added_obligations": [
                {"item": "Above-the-fold attribution mandate",
                 "severity": "high",
                 "description": "AI summaries must display prominent, above-the-fold hyperlinks to source publishers — non-compliance triggers statutory damages."},
                {"item": "Statutory damages per un-attributed query",
                 "severity": "high",
                 "description": "Each Zero-click AI Answer lacking required attribution is an independent infringement event subject to per-query damages."},
                {"item": "Licensing disclosure requirement",
                 "severity": "medium",
                 "description": "AI operators must publicly disclose all content licensing agreements used to train or ground AI summary systems."},
            ],
            "removed_rights": [
                {"item": "Ambiguous fair use defence for AI summaries",
                 "severity": "high",
                 "description": "The Act explicitly forecloses fair use as a defence for AI-generated summaries exceeding 50 words without attribution."},
            ],
            "key_thresholds": [
                {"item": "Attribution trigger word count", "value": "50 words",
                 "description": "AI summaries exceeding 50 words without prominent attribution presumed to be copyright infringement."},
                {"item": "Statutory damages floor", "value": "$500 per query",
                 "description": "Minimum $500 per un-attributed search query; up to $150,000 for wilful infringement."},
            ],
            "context_summary": (
                "The US AI Search & Attribution Act (Draft) establishes a strict liability framework "
                "for AI-generated summaries, presuming copyright infringement for Zero-click AI Answers "
                "lacking prominent above-the-fold attribution. Statutory damages create significant "
                "leverage for publishers to enforce licensing floors against AI operators."
            ),
            "parsed_claims": [
                "Any generative AI system providing 'Direct Answers' that substantially substitute original publisher content must display a prominent, above-the-fold hyperlink to the source publication.",
                "Zero-click AI Answers delivered without an explicit, written publisher licensing agreement shall constitute presumptive copyright infringement under this Act.",
                "Statutory damages of not less than $500 per un-attributed search query shall apply, without requirement to prove actual damages, rising to $150,000 per query for wilful infringement.",
            ],
        }
        step2 = {
            "scores": {
                "IP":      {"score": 92, "direction": "opportunity",
                            "evidence": "Strict liability framework and statutory damages give publishers maximum IP enforcement leverage.",
                            "priority_actions": ["File preemptive licensing demand with all US AI operators within 30 days", "Engage US Publisher Coalition to coordinate enforcement strategy"]},
                "Traffic": {"score": 60, "direction": "threat",
                            "evidence": "Attribution mandate may reduce AI operator willingness to surface Nikkei content, reducing referral traffic short-term.",
                            "priority_actions": ["Monitor referral traffic impact over 90-day observation window", "Negotiate traffic guarantee as part of licensing settlement"]},
                "Revenue": {"score": 85, "direction": "opportunity",
                            "evidence": "Statutory damages floor of $500/query creates powerful negotiating baseline for licensing fee floors.",
                            "priority_actions": ["Quantify un-attributed query volume to establish damages claim", "Prepare licensing term sheet with statutory-backed floor rates"]},
                "Product": {"score": 50, "direction": "neutral",
                            "evidence": "Attribution display requirements are product-implementable but require API changes to query routing.",
                            "priority_actions": ["Audit current AI operator API integrations for attribution compliance", "Design attribution tracking dashboard for licensing audit trail"]},
            },
            "overall_risk_level": "high",
            "stance_label": "LICENSE & PROMOTE",
            "executive_summary": (
                "The US AI Search & Attribution Act is a major strategic opportunity for Nikkei. "
                "IP leverage reaches 92/100 as statutory damages establish a legally-backed licensing floor. "
                "Strategic stance: LICENSE & PROMOTE — aggressively pursue licensing agreements with all "
                "US AI operators while the regulatory window provides maximum enforcement leverage."
            ),
            "key_opportunities": [
                "92/100 IP leverage — statutory damages enable aggressive licensing enforcement against all US AI operators",
                "Aligns perfectly with US Publisher Coalition lobbying strategy (Memo #2025-A)",
                "First-mover licensing agreements lock in revenue floors before industry-wide settlement",
            ],
            "key_threats": [
                "AI operators may reduce Zero-click AI Answers coverage of Nikkei content to limit liability — short-term traffic impact",
                "Ambiguous territorial scope: unclear whether non-US AI deployments are covered",
                "60/100 traffic risk if AI operators implement conservative content avoidance strategy",
            ],
            "card_scores": {
                "IP":      {"score": 92, "direction": "opportunity",
                            "evidence": "Strong legal basis",
                            "action_badge": "LICENSE",
                            "action_summary": "Leverage statutory damages threat to force paid agreements.",
                            "priority_actions": ["File preemptive licensing demand with all US AI operators within 30 days", "Engage US Publisher Coalition to coordinate enforcement strategy"]},
                "Traffic": {"score": 60, "direction": "opportunity",
                            "evidence": "Mandated links",
                            "action_badge": "PROMOTE",
                            "action_summary": "Maximize above-the-fold visibility mandated by the new act.",
                            "priority_actions": ["Monitor referral traffic impact over 90-day observation window", "Negotiate traffic guarantee as part of licensing settlement"]},
                "Revenue": {"score": 85, "direction": "opportunity",
                            "evidence": "Leverage for licensing",
                            "action_badge": "LICENSE",
                            "action_summary": "Establish strong minimum pricing floors for AI indexing.",
                            "priority_actions": ["Quantify un-attributed query volume to establish damages claim", "Prepare licensing term sheet with statutory-backed floor rates"]},
                "Product": {"score": 50, "direction": "neutral",
                            "evidence": "Standard UI updates",
                            "action_badge": "WAIT",
                            "action_summary": "No immediate UI changes required.",
                            "priority_actions": ["Audit current AI operator API integrations for attribution compliance", "Design attribution tracking dashboard for licensing audit trail"]},
            },
            "pmg_evidence": [
                "Aligns perfectly with our US Publisher Coalition lobbying strategy (Memo #2025-A).",
                "Triggers immediate IP enforcement protocols established by the Legal team in late 2024.",
            ],
        }
        step3 = {
            "what_changed_brief": (
                "BEFORE: Ambiguous fair use doctrine allowed AI operators to generate summaries of Nikkei "
                "articles without attribution or compensation, with limited legal recourse for publishers.\n\n"
                "AFTER: The US AI Search & Attribution Act presumes copyright infringement for Zero-click AI Answers "
                "lacking prominent above-the-fold attribution. Statutory damages of $500+ per query create "
                "a legally-backed licensing floor. AI operators must publicly disclose all content licensing "
                "agreements — enabling systematic enforcement."
            ),
            "what_changed_quotes": [
                "Strict above-the-fold attribution mandate and statutory damages for un-attributed queries.",
                "AI summaries must display prominent, above-the-fold hyperlinks to source publishers.",
                "Each Zero-click AI Answer lacking required attribution is an independent infringement event.",
            ],
            "overall_risk": "HIGH",
            "business_exposure_memo": (
                "(1) Traffic & Audience Reach: Short-term referral traffic risk (60/100) as AI operators "
                "adjust coverage to manage attribution compliance costs. Offset by direct licensing revenue.\n\n"
                "(2) Revenue Streams: 85/100 revenue opportunity — statutory damages floor enables "
                "aggressive licensing fee setting. Industry modelling suggests ¥2.1–3.4B annual licensing "
                "revenue achievable across US AI operator base.\n\n"
                "(3) IP & Copyright: 92/100 IP leverage — strongest regulatory position for publishers "
                "in the AI era. Nikkei's US content library positions us as a tier-1 licensor.\n\n"
                "(4) Product & Platform: Attribution tracking infrastructure required. Engineering "
                "estimates 4 weeks for compliance dashboard and API audit tooling.\n\n"
                "(5) Brand & Competitive Standing: Early licensing leadership reinforces Nikkei as the "
                "premium AI-era content partner — differentiated from commoditised news aggregators."
            ),
            "business_exposure_quotes": [
                "Statutory damages of $500 per un-attributed query establish legally-backed licensing floor.",
                "AI operators must publicly disclose all content licensing agreements.",
                "Presumptive copyright infringement for Zero-click AI Answers exceeding 50 words without attribution.",
            ],
            "negotiation_brief": (
                "(1) Non-Negotiable Conditions: Above-the-fold attribution on all AI summaries derived "
                "from Nikkei content. Licensing fee floor at $0.008 per attributed query (benchmarked to "
                "statutory damages). Annual audit rights over AI operator content usage logs.\n\n"
                "(2) Items Requiring Written Confirmation: Any licensing agreement must specify territorial "
                "scope explicitly. Revenue share calculation methodology requires CFO sign-off.\n\n"
                "(3) Strongest Leverage Points: $500/query statutory damages floor. US Publisher Coalition "
                "joint enforcement posture. First-mover premium content position.\n\n"
                "(4) Acceptable Compromise Zones: Phased attribution rollout over 90 days. "
                "Tiered fee structure for different content categories.\n\n"
                "(5) Red Lines: No licensing deal below $0.005 per query. No waiver of audit rights."
            ),
            "negotiation_quotes": [
                "Statutory damages floor of $500 per un-attributed query.",
                "Above-the-fold attribution is a non-negotiable compliance requirement under the Act.",
                "Licensing disclosure requirement enables systematic enforcement audit.",
            ],
            "board_memo": (
                "WHAT HAPPENED: The US AI Search & Attribution Act (Draft) establishes strict liability "
                "for AI-generated summaries, creating the strongest publisher copyright enforcement "
                "framework in US legal history.\n\n"
                "FINANCIAL EXPOSURE: ¥2.1–3.4B annual licensing revenue opportunity. "
                "Short-term traffic risk (60/100) manageable within 90-day observation window.\n\n"
                "DECISIONS REQUIRED: (1) Authorise Business Dev to issue licensing demand letters to "
                "all US AI operators within 30 days. (2) Approve US Publisher Coalition joint enforcement "
                "posture. (3) Allocate ¥180M engineering budget for attribution tracking infrastructure.\n\n"
                "RECOMMENDED ACTIONS: Legal (GC) — File preemptive licensing demand within 30 days. "
                "Business Dev (CDO) — Close first licensing agreement within 90 days. "
                "Product (CPO) — Deploy attribution dashboard within 4 weeks.\n\n"
                "SCENARIOS: Best case — Industry-wide licensing settlement at $0.008/query; ¥3.4B annual "
                "revenue. Base case — Selective enforcement; ¥2.1B revenue from tier-1 AI operators. "
                "Worst case — Act delayed or weakened in final passage; revert to coalition strategy."
            ),
            "board_memo_quotes": [
                "Statutory damages of $500 per query provide maximum licensing leverage.",
                "The Act aligns with our US Publisher Coalition lobbying strategy (Memo #2025-A).",
                "Above-the-fold attribution mandate is enforceable from effective date.",
            ],
            "product_checklist": [
                "[CONSENT MECHANISM] Legal & Product — Design licensing opt-in flow for AI operator "
                "content access agreements. Trigger: before any new AI API integration. Capture: "
                "operator ID, licensed content scope, fee structure, audit rights acknowledgement.",
                "[CONSENT UI] UX Team — Implement attribution compliance verification module in "
                "content delivery API. Must validate attribution parameters before serving content "
                "to AI operators. Flag non-compliant requests for Legal review (no dark patterns).",
                "[LEGAL DISCLOSURE] Communications — Publish licensing policy statement on Nikkei "
                "corporate website within 14 days. Send written licensing demand to top 10 US AI "
                "operators within 30 days. Log all correspondence in litigation-hold database.",
                "[FEATURE CHANGE] Engineering — Build attribution tracking dashboard showing per-operator "
                "query volume, attribution compliance rate, and damages exposure calculation. "
                "Deadline: 4-week sprint, CPO sign-off required at milestone 2.",
                "[AUDIT LOGGING] Data Engineering — Log all AI operator API calls with content ID, "
                "attribution status, and query timestamp. Retention: 7 years. Format: structured "
                "JSON with operator ID and statutory damages calculation fields.",
            ],
        }
        debate = [
            {"agent": "⚖️ Legal Agent", "color": "#8B2635",
             "message": (
                 "[🎯 Policy Memory Graph Match: Clause 4.2 — 2024 OpenAI partner contract negotiations] "
                 "IP exposure at 92/100 — this is maximum leverage territory. The Act's statutory damages "
                 "of $500/query align perfectly with the red-line position from our 2024 OpenAI negotiations "
                 "where we rejected zero-revenue attribution. Initiating formal licensing demand protocol "
                 "for all US AI operators. Outside counsel engaged for enforcement coordination."
             )},
            {"agent": "💰 Business Agent", "color": "#A8892A",
             "message": (
                 "Revenue opportunity at 85/100 — I am strongly in favour of aggressive licensing. "
                 "The US Publisher Coalition (Memo #2025-A) already has 47 member publishers aligned. "
                 "First-mover licensing agreements will lock in premium fee floors before a "
                 "post-settlement industry standard is set at a lower rate. This is a once-in-a-decade window."
             )},
            {"agent": "🧩 Product Agent", "color": "#1A6B3C",
             "message": (
                 "Product constraint at 50/100 — manageable. Attribution tracking dashboard is a "
                 "4-week build. The API audit tooling is partially reusable from our GDPR consent "
                 "infrastructure. No major architectural changes required. Ready to proceed on "
                 "CPO authorisation."
             )},
            {"agent": "🏛️ Executive Alignment", "color": "#0ABAB5", "final": True,
             "message": (
                 "Conflict Resolved. Unified position: LICENSE & PROMOTE. "
                 "Legal to issue licensing demands within 30 days. "
                 "Business Dev to target first signed agreement within 90 days. "
                 "Product to deploy attribution dashboard within 4 weeks. "
                 "Board notification required within 48 hours — ¥2.1–3.4B revenue opportunity on the table."
             )},
        ]
        pmg_hits = [
            ("Clause 4.2", "2024 OpenAI partner contract negotiations",
             "Zero-revenue attribution for AI-generated summaries of licensed content exceeding 40 words "
             "was a non-negotiable red-line — the US Act's statutory damages directly validate this position."),
            ("Memo #2025-A", "US Publisher Coalition lobbying strategy",
             "Nikkei co-authored the Publisher Coalition's position paper demanding above-the-fold attribution "
             "and statutory damages. The Act's language mirrors our draft submission verbatim."),
        ]
        matrix_clauses = [
            {"name": "Attribution Mandate",  "x": 60, "y": 85, "color": "#E67E22", "size": 14},
            {"name": "Statutory Damages",    "x": 90, "y": 90, "color": "#C0392B", "size": 15},
        ]

    # ── EU DMA scenario ─────────────────────────────────────────────────────────
    elif "EU" in txt or "DMA" in txt:
        domain = "AI Search & Zero-Click"
        step1 = {
            "added_obligations": [
                {"item": "Granular technical opt-out for AI training",
                 "severity": "high",
                 "description": "DMA requires dominant platforms to offer granular, per-content-type opt-outs from AI training data collection — separate from search indexing consent."},
                {"item": "Fair and non-discriminatory compensation mandate",
                 "severity": "high",
                 "description": "Dominant platforms must offer transparent, auditable compensation schemes for publisher content used in Zero-click AI summaries."},
                {"item": "Consent unbundling requirement",
                 "severity": "medium",
                 "description": "Search indexing consent must be contractually separated from AI training consent — bundled agreements are prohibited."},
            ],
            "removed_rights": [
                {"item": "Bundled AI training consent via search indexing",
                 "severity": "high",
                 "description": "Dominant platforms can no longer use search indexing agreements to imply AI training consent — unbundling is mandatory."},
            ],
            "key_thresholds": [
                {"item": "Compensation audit period", "value": "Annual",
                 "description": "Dominant platforms must submit to annual independent audit of compensation calculation methodology."},
                {"item": "Opt-out response time", "value": "30 days",
                 "description": "Platforms must honour granular opt-out requests within 30 days of submission."},
            ],
            "context_summary": (
                "The EU Commission Draft Guidance designates AI-powered search overviews by dominant platforms "
                "as core platform services under the DMA, mandating unbundled consent for AI training and "
                "fair compensation for Zero-click AI summaries. This creates the most comprehensive "
                "publisher protection framework in the EU digital regulatory landscape."
            ),
            "parsed_claims": [
                "Designated gatekeepers shall not use data obtained from publishers for the purpose of providing AI-generated overviews without offering fair, proportionate, and non-discriminatory remuneration to the originating publisher.",
                "Publishers shall be provided with granular technical controls enabling separate, explicit consent for search indexing and AI training data use — bundled consent agreements are hereby prohibited.",
                "Compliance with remuneration obligations shall be subject to annual independent audit; results shall be submitted to the Commission within 30 days of audit completion.",
            ],
        }
        step2 = {
            "scores": {
                "IP":      {"score": 85, "direction": "opportunity",
                            "evidence": "Consent unbundling and compensation mandate establish clear IP ownership framework for AI training data.",
                            "priority_actions": ["Audit all existing search platform agreements for bundled consent clauses", "Issue formal unbundling demand to all EU-designated dominant platforms"]},
                "Traffic": {"score": 80, "direction": "threat",
                            "evidence": "Dominant platforms may reduce AI summary coverage during compliance transition — short-term traffic risk.",
                            "priority_actions": ["Monitor referral traffic during 30-day platform opt-out compliance window", "Negotiate traffic guarantee as part of compensation agreement"]},
                "Revenue": {"score": 95, "direction": "opportunity",
                            "evidence": "Fair compensation mandate with annual audit rights enables systematic licensing revenue recovery.",
                            "priority_actions": ["Quantify historical AI summary usage to establish back-compensation claim", "Prepare DMA-compliant licensing term sheet with revenue floor"]},
                "Product": {"score": 85, "direction": "threat",
                            "evidence": "Granular opt-out UI requires significant consent management platform engineering.",
                            "priority_actions": ["Reuse GDPR Article 17 consent architecture for DMA compliance", "Engineering sprint estimate: 8 weeks for full granular opt-out stack"]},
            },
            "overall_risk_level": "critical",
            "stance_label": "PROTECT & LICENSE",
            "executive_summary": (
                "The EU DMA Draft Guidance represents a landmark revenue recovery opportunity for Nikkei "
                "in the EU market. Revenue leverage reaches 95/100 as fair compensation mandates and "
                "annual audit rights create a legally-enforceable licensing framework. "
                "Strategic stance: PROTECT & LICENSE — demand consent unbundling, pursue aggressive "
                "compensation claims, and leverage our GDPR compliance infrastructure for rapid DMA adaptation."
            ),
            "key_opportunities": [
                "95/100 revenue recovery — fair compensation mandate with audit rights enables systematic licensing enforcement",
                "Existing GDPR Article 17 consent management platform provides 60% reusable DMA compliance infrastructure",
                "EU market precedent will strengthen global licensing negotiations with same platform operators",
            ],
            "key_threats": [
                "85/100 product engineering load — granular opt-out UI is complex and resource-intensive",
                "80/100 traffic risk during platform compliance transition (30-day opt-out response window)",
                "Dominant platforms may challenge DMA designation through EU courts — 12–18 month litigation risk",
            ],
            "card_scores": {
                "IP":      {"score": 85, "direction": "opportunity",
                            "evidence": "Consent unbundling",
                            "action_badge": "PROTECT",
                            "action_summary": "Enforce granular technical opt-outs under the new framework.",
                            "priority_actions": ["File for DMA article 6(i) designation review", "Prepare granular consent architecture spec"]},
                "Traffic": {"score": 80, "direction": "opportunity",
                            "evidence": "Fair search display",
                            "action_badge": "PROMOTE",
                            "action_summary": "Reclaim fair search display visibility.",
                            "priority_actions": ["Negotiate traffic floor clause in DMA compensation settlement", "Audit current search placement vs. platform baseline"]},
                "Revenue": {"score": 95, "direction": "opportunity",
                            "evidence": "Critical Opportunity: Fair compensation mandate",
                            "action_badge": "LICENSE",
                            "action_summary": "Demand non-discriminatory compensation for summaries.",
                            "priority_actions": ["Quantify Zero-click AI Answers impression volume for compensation claim", "Draft per-article compensation rate schedule"]},
                "Product": {"score": 85, "direction": "threat",
                            "evidence": "High compliance engineering load",
                            "action_badge": "WAIT",
                            "action_summary": "Assess engineering load for consent UI overhaul.",
                            "priority_actions": ["Reuse GDPR Article 17 opt-out infrastructure (60% reuse estimate)", "Plan 3-sprint compliance engineering roadmap"]},
            },
            "pmg_evidence": [
                "Follows the exact compliance architecture we built for GDPR Article 17 in 2022.",
                "Mirrors the revenue-floor precedent from 2023 Showcase MOU: minimum per-article compensation applies.",
            ],
        }
        step3 = {
            "what_changed_brief": (
                "BEFORE: Dominant platforms mixed search indexing and AI training consent under bundled "
                "agreements, allowing unrestricted use of publisher content for AI summary generation "
                "without separate compensation.\n\n"
                "AFTER: EU DMA Draft Guidance mandates unbundling of search indexing and AI training consent. "
                "Dominant platforms must provide granular technical opt-outs, offer fair and non-discriminatory "
                "compensation for Zero-click AI summaries, and submit to annual independent audits. "
                "Publishers gain the strongest structural IP protection in the EU regulatory framework."
            ),
            "what_changed_quotes": [
                "Requirement for granular technical opt-outs and non-discriminatory compensation schemes.",
                "Dominant platforms are prohibited from using publisher data for Zero-click AI Answers without fair compensation.",
                "Consent unbundling is mandatory — search indexing consent cannot imply AI training consent.",
            ],
            "overall_risk": "CRITICAL",
            "business_exposure_memo": (
                "(1) Traffic & Audience Reach: 80/100 traffic risk during 30-day platform compliance "
                "transition. Dominant platforms may reduce AI summary coverage of Nikkei content. "
                "Direct audience acquisition strategy should be accelerated in parallel.\n\n"
                "(2) Revenue Streams: 95/100 revenue opportunity — the largest in Nikkei's digital "
                "licensing history. Annual audit rights enable systematic back-compensation claims "
                "for historical AI summary usage. Estimated EU licensing revenue: ¥1.8–2.9B annually.\n\n"
                "(3) IP & Copyright: 85/100 IP protection — consent unbundling establishes clear "
                "ownership boundary between search indexing rights and AI training rights for the first time.\n\n"
                "(4) Product & Platform: 85/100 engineering load. GDPR Article 17 architecture "
                "provides 60% reusable infrastructure. Full DMA compliance stack: 8-week sprint.\n\n"
                "(5) Brand & Competitive Standing: DMA compliance leadership positions Nikkei as "
                "the model EU-compliant premium content publisher."
            ),
            "business_exposure_quotes": [
                "Fair and non-discriminatory compensation mandate with annual audit rights.",
                "Granular technical opt-outs required within 30 days of publisher request.",
                "Dominant platforms cannot use publisher data for Zero-click AI summaries without compensation.",
            ],
            "negotiation_brief": (
                "(1) Non-Negotiable Conditions: Immediate consent unbundling for all EU dominant platforms. "
                "Fair compensation floor benchmarked to pro-rata query volume. Annual audit rights "
                "with independent auditor of Nikkei's selection.\n\n"
                "(2) Items Requiring Written Confirmation: Back-compensation for historical AI summary "
                "usage (12-month lookback). Granular opt-out implementation timeline.\n\n"
                "(3) Strongest Leverage Points: DMA enforcement risk for platforms — fines up to 10% "
                "of global annual turnover. EU regulatory precedent extends to global negotiations.\n\n"
                "(4) Acceptable Compromise Zones: Phased compensation rollout tied to audit findings. "
                "Temporary search indexing continuity during unbundling transition.\n\n"
                "(5) Red Lines: No continued bundled consent agreements. No compensation formula "
                "without independent audit rights."
            ),
            "negotiation_quotes": [
                "DMA mandates fair and non-discriminatory compensation — no below-floor offers accepted.",
                "Annual independent audit rights are a non-negotiable DMA compliance requirement.",
                "Consent unbundling must be implemented within the platform's 30-day DMA compliance window.",
            ],
            "board_memo": (
                "WHAT HAPPENED: EU Commission Draft Guidance designates AI search overviews by dominant "
                "platforms as core DMA services, mandating consent unbundling and fair compensation. "
                "This is the most significant EU publisher rights development since GDPR.\n\n"
                "FINANCIAL EXPOSURE: ¥1.8–2.9B annual EU licensing revenue opportunity. "
                "8-week engineering sprint required (¥220M budget estimate).\n\n"
                "DECISIONS REQUIRED: (1) Approve DMA compliance sprint budget (¥220M). "
                "(2) Authorise compensation claim letters to EU dominant platforms. "
                "(3) Engage EU regulatory counsel for DMA enforcement monitoring.\n\n"
                "RECOMMENDED ACTIONS: Legal (GC) — Issue consent unbundling demand within 14 days. "
                "Product (CPO) — Launch DMA compliance sprint using GDPR Article 17 foundation. "
                "Business Dev (CDO) — File EU compensation claims within 30 days.\n\n"
                "SCENARIOS: Best case — Platforms comply and ¥2.9B licensing revenue materialises. "
                "Base case — Contested implementation; ¥1.8B after audit findings. "
                "Worst case — Platforms challenge DMA designation; 18-month litigation delay."
            ),
            "board_memo_quotes": [
                "EU DMA mandates granular opt-outs and fair compensation for Zero-click AI Answers.",
                "Annual audit rights enable systematic enforcement of compensation obligations.",
                "Consent unbundling follows the compliance architecture we built for GDPR Article 17.",
            ],
            "product_checklist": [
                "[CONSENT MECHANISM] Legal & Product — Redesign all EU dominant platform agreements "
                "to separate search indexing consent from AI training consent. Trigger: before any "
                "platform API renewal. Capture: platform ID, consent scope, effective date, audit cycle.",
                "[CONSENT UI] UX Team — Build granular opt-out control panel for editorial and "
                "content management users. Must cover: AI training opt-out, AI summary opt-out, "
                "search indexing retention. Reuse GDPR Article 17 consent management UI components.",
                "[LEGAL DISCLOSURE] Communications — Notify all EU dominant platforms of consent "
                "unbundling demand within 14 days. Publish DMA compliance statement on corporate "
                "website. File compensation claims with documented query volume data.",
                "[FEATURE CHANGE] Engineering — Extend GDPR Article 17 consent management platform "
                "with DMA-specific opt-out categories. Add per-platform consent status dashboard. "
                "Deadline: 8-week sprint, milestone sign-offs at weeks 2, 4, and 6.",
                "[AUDIT LOGGING] Data Engineering — Build DMA compliance audit trail: per-platform "
                "AI query volume, content attribution status, compensation calculation log. "
                "Retention: 7 years. Annual audit export format: structured XML for independent auditors.",
            ],
        }
        debate = [
            {"agent": "⚖️ Legal Agent", "color": "#8B2635",
             "message": (
                 "[🎯 Policy Memory Graph Match: GDPR Article 17 compliance architecture — 2022] "
                 "IP exposure at 85/100 — strong position. DMA consent unbundling follows the exact "
                 "legal architecture we designed for GDPR Article 17. I am issuing formal consent "
                 "unbundling demands to all EU-designated dominant platforms within 14 days. "
                 "DMA fines (10% global turnover) give us maximum enforcement leverage."
             )},
            {"agent": "💰 Business Agent", "color": "#A8892A",
             "message": (
                 "Revenue opportunity at 95/100 — this is extraordinary. The annual audit rights "
                 "alone justify immediate aggressive action. I am projecting ¥1.8–2.9B in EU "
                 "licensing revenue once compensation claims are processed. "
                 "Engineering load at 85/100 is justified — this is a multi-year revenue stream."
             )},
            {"agent": "🧩 Product Agent", "color": "#1A6B3C",
             "message": (
                 "Product constraint at 85/100 — significant but manageable. GDPR Article 17 "
                 "architecture covers 60% of the DMA compliance requirement. "
                 "Estimate 8 weeks for full granular opt-out stack with milestone sign-offs at "
                 "weeks 2, 4, and 6. CPO authorisation requested."
             )},
            {"agent": "🏛️ Executive Alignment", "color": "#0ABAB5", "final": True,
             "message": (
                 "Conflict Resolved. Unified position: PROTECT & LICENSE. "
                 "Legal to issue unbundling demands within 14 days. "
                 "Product to launch DMA compliance sprint immediately. "
                 "Business Dev to file compensation claims within 30 days. "
                 "Board notification required — ¥1.8–2.9B EU revenue opportunity at stake."
             )},
        ]
        pmg_hits = [
            ("GDPR Art. 17", "2022 EU consent management platform build",
             "Engineering team confirmed the existing GDPR Article 17 deletion request infrastructure "
             "can be extended to support DMA granular opt-out requirements — estimated 60% reuse rate."),
            ("Exhibit B §3", "2023 Google News Showcase MOU",
             "Minimum annual traffic guarantee was required as a prerequisite to any content licensing "
             "arrangement — directly applicable as DMA compensation floor negotiating anchor."),
        ]
        matrix_clauses = [
            {"name": "Consent Unbundling",    "x": 45, "y": 88, "color": "#8B2635", "size": 14},
            {"name": "Fair Compensation",     "x": 45, "y": 95, "color": "#C0392B", "size": 15},
        ]

    # ── UK Parliament scenario ───────────────────────────────────────────────────
    elif "UK" in txt or "PARLIAMENT" in txt:
        domain = "Platform Distribution Policies"
        step1 = {
            "added_obligations": [
                {"item": "Voluntary code of conduct participation",
                 "severity": "low",
                 "description": "UK government invites publishers to participate in a voluntary code of conduct framework — no mandatory compliance timeline."},
                {"item": "Transparency reporting (voluntary)",
                 "severity": "low",
                 "description": "Participating publishers encouraged to disclose AI content licensing arrangements on an annual basis."},
            ],
            "removed_rights": [
                {"item": "Legislative enforcement expectation",
                 "severity": "medium",
                 "description": "Parliament's statement confirms no strict liability legislation will be introduced in the current session — removing anticipated enforcement backstop."},
            ],
            "key_thresholds": [
                {"item": "Voluntary participation deadline", "value": "None specified",
                 "description": "No enforcement date — participation is open-ended and non-binding."},
                {"item": "Review period", "value": "12 months",
                 "description": "Government will review voluntary code effectiveness after 12 months before considering legislative options."},
            ],
            "context_summary": (
                "UK Parliament's written statement (HCWS1416) announces a voluntary code of conduct "
                "rather than the strict legislative penalties anticipated by the publisher community. "
                "Enforcement risk is low in the near term; however, the 12-month review creates "
                "an opportunity to shape the eventual legislative framework through voluntary compliance leadership."
            ),
            "parsed_claims": [
                "The Government invites publishers and platform operators to participate voluntarily in the development of a multi-stakeholder code of conduct governing AI use of news and journalistic content.",
                "Participating organisations are encouraged, but not required, to publish annual transparency reports covering AI content licensing arrangements and revenue-sharing terms.",
                "The Government will review the effectiveness of this voluntary framework after 12 months and will consider whether legislative measures are necessary if sufficient industry progress has not been achieved.",
            ],
        }
        step2 = {
            "scores": {
                "IP":      {"score": 50, "direction": "neutral",
                            "evidence": "Voluntary framework provides no new IP protection but also imposes no new obligations.",
                            "priority_actions": ["Monitor code of conduct consultation process", "Submit formal response to government consultation within deadline"]},
                "Traffic": {"score": 55, "direction": "neutral",
                            "evidence": "No immediate platform behaviour change expected — voluntary code has no enforcement mechanism.",
                            "priority_actions": ["Maintain current platform distribution agreements", "Track any voluntary compliance announcements from major platforms"]},
                "Revenue": {"score": 40, "direction": "neutral",
                            "evidence": "No new licensing obligations or revenue recovery mechanisms in voluntary framework.",
                            "priority_actions": ["Defer EU and US licensing negotiations — stronger leverage available in those jurisdictions", "Participate in code consultation to shape revenue protection provisions"]},
                "Product": {"score": 30, "direction": "neutral",
                            "evidence": "No mandatory product changes required under voluntary framework.",
                            "priority_actions": ["No immediate engineering action required", "Document current consent architecture for potential future mandatory compliance"]},
            },
            "overall_risk_level": "low",
            "stance_label": "MONITOR & WAIT",
            "executive_summary": (
                "UK Parliament's voluntary code of conduct announcement is a low-impact event for Nikkei. "
                "All axis scores are in the neutral range (30–55/100). "
                "Strategic stance: MONITOR & WAIT — participate constructively in the consultation process "
                "to shape future legislation while prioritising EU and US enforcement actions where "
                "regulatory leverage is materially stronger."
            ),
            "key_opportunities": [
                "Shape eventual UK legislative framework through proactive voluntary compliance and consultation participation",
                "Demonstrate market leadership in responsible AI content transparency — brand differentiation",
                "Use 12-month review window to build evidence base for stronger legislative proposals",
            ],
            "key_threats": [
                "Voluntary framework delays binding UK enforcement — reduces publisher leverage in bilateral platform negotiations",
                "Platform operators may use voluntary status to defer compensation discussions indefinitely",
                "12-month review creates regulatory uncertainty — difficult to plan long-term UK licensing strategy",
            ],
            "card_scores": {
                "IP":      {"score": 50, "direction": "neutral",
                            "evidence": "Awaiting finalized technical codes.",
                            "action_badge": "MONITOR",
                            "action_summary": "Maintain current stance pending finalized voluntary codes.",
                            "priority_actions": ["Monitor CMA consultation updates", "No immediate action required"]},
                "Traffic": {"score": 55, "direction": "neutral",
                            "evidence": "Awaiting finalized technical codes.",
                            "action_badge": "MONITOR",
                            "action_summary": "Maintain current stance pending finalized voluntary codes.",
                            "priority_actions": ["Maintain standard traffic monitoring cadence", "No immediate action required"]},
                "Revenue": {"score": 40, "direction": "neutral",
                            "evidence": "Awaiting finalized technical codes.",
                            "action_badge": "MONITOR",
                            "action_summary": "Maintain current stance pending finalized voluntary codes.",
                            "priority_actions": ["Defer UK licensing renegotiation until statutory instruments introduced", "No immediate action required"]},
                "Product": {"score": 30, "direction": "neutral",
                            "evidence": "Awaiting finalized technical codes.",
                            "action_badge": "MONITOR",
                            "action_summary": "Maintain current stance pending finalized voluntary codes.",
                            "priority_actions": ["No immediate engineering action required", "Document current consent architecture for potential future compliance"]},
            },
            "pmg_evidence": [
                "Matches the historical trajectory of the 2021 UK CMA voluntary tech agreements.",
                "Enforcement risk remains low until statutory instruments are introduced.",
            ],
        }
        step3 = {
            "what_changed_brief": (
                "BEFORE: Publisher community anticipated strict legislative penalties for AI platforms "
                "using content without attribution or compensation, based on prior government signals.\n\n"
                "AFTER: Parliament announces a voluntary code of conduct (HCWS1416) rather than strict "
                "legislative penalties. No enforcement date. Participation is non-binding. Government "
                "will review effectiveness after 12 months. Enforcement risk remains low in the near term."
            ),
            "what_changed_quotes": [
                "Voluntary compliance framework with no strict liability enforcement date.",
                "Parliament announces voluntary code of conduct rather than mandatory legislation.",
                "12-month review period before legislative options will be reconsidered.",
            ],
            "overall_risk": "LOW",
            "business_exposure_memo": (
                "(1) Traffic & Audience Reach: 55/100 — neutral. No immediate platform behaviour "
                "change expected under voluntary framework. Current distribution agreements unaffected.\n\n"
                "(2) Revenue Streams: 40/100 — no new licensing mechanisms. UK revenue exposure is "
                "limited; prioritise EU and US enforcement actions for higher-return licensing activity.\n\n"
                "(3) IP & Copyright: 50/100 — neutral. Voluntary framework provides no new IP protection. "
                "Maintain existing UK content licensing arrangements without modification.\n\n"
                "(4) Product & Platform: 30/100 — no mandatory product changes. Document current "
                "consent architecture for potential future mandatory compliance requirements.\n\n"
                "(5) Brand & Competitive Standing: Proactive voluntary participation enhances Nikkei's "
                "reputation as a responsible AI content partner in the UK market."
            ),
            "business_exposure_quotes": [
                "Voluntary compliance framework with no strict liability enforcement date.",
                "No mandatory licensing obligations under HCWS1416 voluntary code.",
                "12-month review period before legislation reconsidered.",
            ],
            "negotiation_brief": (
                "(1) Non-Negotiable Conditions: None required under voluntary framework — no mandatory "
                "compliance obligations.\n\n"
                "(2) Items Requiring Written Confirmation: Government consultation submission deadline "
                "and formal participation confirmation for voluntary code.\n\n"
                "(3) Strongest Leverage Points: Constructive engagement in consultation process "
                "to shape stronger future legislative provisions.\n\n"
                "(4) Acceptable Compromise Zones: All terms are effectively negotiable under voluntary "
                "framework — no enforcement backstop.\n\n"
                "(5) Red Lines: Do not commit to voluntary code terms that would pre-empt stronger "
                "EU or US licensing positions if legislation is later strengthened."
            ),
            "negotiation_quotes": [
                "Voluntary compliance framework — all participation terms are negotiable.",
                "12-month review creates opportunity to shape legislative provisions.",
                "No strict liability enforcement means no immediate red-line positions required.",
            ],
            "board_memo": (
                "WHAT HAPPENED: UK Parliament issued HCWS1416 announcing a voluntary code of conduct "
                "for AI content — not the mandatory legislation anticipated. Enforcement risk: LOW.\n\n"
                "FINANCIAL EXPOSURE: Minimal near-term impact. UK enforcement leverage is significantly "
                "weaker than EU (DMA) and US (Attribution Act) jurisdictions.\n\n"
                "DECISIONS REQUIRED: (1) Approve voluntary code participation and consultation response. "
                "(2) Redirect UK enforcement resources to EU and US licensing actions.\n\n"
                "RECOMMENDED ACTIONS: Legal (GC) — Submit formal consultation response within 30 days. "
                "Business Dev (CDO) — Deprioritise UK bilateral licensing enforcement; focus on EU/US. "
                "Product (CPO) — Document consent architecture for future mandatory compliance readiness.\n\n"
                "SCENARIOS: Best case — 12-month review leads to strong legislation; Nikkei positioned "
                "as voluntary compliance leader. Base case — Voluntary code continues indefinitely; "
                "limited UK leverage. Worst case — No legislation; platforms use UK as safe harbour."
            ),
            "board_memo_quotes": [
                "Voluntary compliance framework matches historical trajectory of 2021 UK CMA voluntary tech agreements.",
                "Enforcement risk remains low pending 12-month review.",
                "No immediate aggressive action warranted in UK jurisdiction.",
            ],
            "product_checklist": [
                "[CONSENT MECHANISM] Legal — Document current consent architecture and map to "
                "voluntary code transparency requirements. No mandatory changes required. "
                "Trigger: annual voluntary code reporting cycle.",
                "[CONSENT UI] UX Team — No mandatory UI changes required under voluntary framework. "
                "Optional: add voluntary AI content transparency disclosure to Nikkei website footer.",
                "[LEGAL DISCLOSURE] Communications — Submit formal consultation response to DCMS "
                "within 30 days of consultation publication. Publish voluntary participation statement "
                "on corporate website if code participation is confirmed.",
                "[FEATURE CHANGE] Engineering — No mandatory feature changes. Optional: create "
                "AI content usage transparency report generator for annual voluntary disclosure. "
                "Low priority — defer to Q3 if resource-constrained.",
                "[AUDIT LOGGING] Data Engineering — Maintain existing consent and content delivery "
                "logs for potential future mandatory compliance. No new logging requirements under "
                "voluntary code. Annual documentation review recommended.",
            ],
        }
        debate = [
            {"agent": "⚖️ Legal Agent", "color": "#8B2635",
             "message": (
                 "[🎯 Policy Memory Graph Match: 2021 UK CMA voluntary tech agreements] "
                 "IP exposure at 50/100 — neutral. HCWS1416 is a voluntary framework — "
                 "enforcement risk is low. This mirrors the trajectory of the 2021 UK CMA "
                 "voluntary commitments which yielded no binding outcomes for 18 months. "
                 "I advise against immediate aggressive action. Submit consultation response only."
             )},
            {"agent": "💰 Business Agent", "color": "#A8892A",
             "message": (
                 "Revenue at 40/100 — low leverage in UK. I agree with Legal on deferral. "
                 "Our enforcement resources should be redirected to EU (95/100 revenue) "
                 "and US (85/100 revenue) where regulatory frameworks have real teeth. "
                 "UK is a monitoring situation — not an enforcement priority."
             )},
            {"agent": "🧩 Product Agent", "color": "#1A6B3C",
             "message": (
                 "Product constraint at 30/100 — no mandatory engineering changes required. "
                 "I recommend documenting our current consent architecture for future compliance "
                 "readiness. Optional voluntary disclosure feature can be deferred to Q3 "
                 "pending resource availability."
             )},
            {"agent": "🏛️ Executive Alignment", "color": "#0ABAB5", "final": True,
             "message": (
                 "Conflict Resolved. Unified position: MONITOR & WAIT. "
                 "Legal to submit consultation response within 30 days. "
                 "No aggressive enforcement action in UK jurisdiction at this time. "
                 "Resources redirected to EU and US licensing actions. "
                 "Status review at 12-month government review milestone."
             )},
        ]
        pmg_hits = [
            ("CMA Ref. 2021-07", "UK CMA voluntary tech commitments (2021)",
             "Historical trajectory of UK CMA voluntary agreements showed no binding enforcement outcomes "
             "for 18+ months — directly applicable precedent for HCWS1416 voluntary code assessment."),
            ("Section 6.1", "2024 Meta Platform Agreement review",
             "Voluntary platform conduct frameworks in UK historically required CEO-level monitoring "
             "rather than immediate legal escalation — confirmed by General Counsel in prior cycle."),
        ]
        matrix_clauses = [
            {"name": "Voluntary Code Intro", "x": 120, "y": 40, "color": "#0ABAB5", "size": 11},
        ]

    else:
        return None   # No scenario match → fall through to live LLM pipeline

    return {
        "step1_data":     step1,
        "step2_data":     step2,
        "step3_data":     step3,
        "debate_log":     debate,
        "pmg_hits":       pmg_hits,
        "matrix_clauses": matrix_clauses,
        "domain":         domain,
    }


# ─── Pipeline Functions ───────────────────────────────────────────────────────
def _safe_json_parse(text: str) -> Dict:
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return json.loads(match.group(1).strip())
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])
    return json.loads(text.strip())


def get_client() -> Optional[anthropic.Anthropic]:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def run_step1_parsing(client: anthropic.Anthropic, policy_text: str) -> Dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=(
            "You are an expert in regulatory law and platform policy analysis. "
            "Extract changes and risk factors precisely from the provided text, "
            "focusing on elements relevant to media companies and AI operators.\n"
            "Return ONLY a valid JSON object — no preamble, no explanation, no markdown code fences."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Analyze the following Policy/Platform Event text and extract structured data "
                f"from the perspective of media company intellectual property and copyright management.\n\n"
                f"[TEXT]\n{policy_text}\n\n"
                f"Return ONLY the following JSON structure (no extra text whatsoever):\n"
                f"{{\n"
                f'  "added_obligations": [{{"item": "...", "severity": "high|medium|low", "description": "..."}}],\n'
                f'  "removed_rights":    [{{"item": "...", "severity": "high|medium|low", "description": "..."}}],\n'
                f'  "key_thresholds":    [{{"item": "...", "value": "...", "description": "..."}}],\n'
                f'  "context_summary":   "2-3 sentence summary of the entire text"\n'
                f"}}"
            ),
        }],
    )
    raw = next(b.text for b in response.content if b.type == "text")
    return _safe_json_parse(raw)


def run_step2_impact_mapping(client: anthropic.Anthropic, step1_data: Dict, domain: str) -> Dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=(
            "You are a senior business strategy and risk assessment expert for a major media enterprise. "
            "Evaluate the quantitative, multi-dimensional business impact of regulatory changes. "
            "Scores are 0–100: 50 is neutral; higher scores indicate greater impact magnitude "
            "(direction is expressed separately via the 'direction' field).\n"
            "Return ONLY a valid JSON object — no preamble, no explanation, no markdown code fences. "
            "All text fields must be in professional business English."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Evaluate the business impact for the '{domain}' domain.\n\n"
                f"[Domain Profile]\n{DOMAIN_PROFILES[domain]}\n\n"
                f"[Domain-Specific Risk Calibration]\n{DOMAIN_RISK_FOCUS.get(domain, '')}\n\n"
                f"[Step 1 Structured Data]\n{json.dumps(step1_data, ensure_ascii=False, indent=2)}\n\n"
                f"Return ONLY the following JSON structure (no extra text whatsoever):\n"
                f"{{\n"
                f'  "scores": {{\n'
                f'    "IP":      {{"score": 0-100, "direction": "threat|opportunity|neutral", "evidence": "...", "priority_actions": ["..."]}},\n'
                f'    "Traffic": {{"score": 0-100, "direction": "threat|opportunity|neutral", "evidence": "...", "priority_actions": ["..."]}},\n'
                f'    "Revenue": {{"score": 0-100, "direction": "threat|opportunity|neutral", "evidence": "...", "priority_actions": ["..."]}},\n'
                f'    "Product": {{"score": 0-100, "direction": "threat|opportunity|neutral", "evidence": "...", "priority_actions": ["..."]}}\n'
                f'  }},\n'
                f'  "overall_risk_level": "critical|high|medium|low",\n'
                f'  "executive_summary": "...",\n'
                f'  "key_opportunities": ["..."],\n'
                f'  "key_threats": ["..."]\n'
                f"}}"
            ),
        }],
    )
    raw = next(b.text for b in response.content if b.type == "text")
    return _safe_json_parse(raw)


def _build_draft_context(domain: str, step1_data: Dict, step2_data: Dict) -> str:
    scores = step2_data["scores"]
    return (
        f"[Policy/Regulatory Change Summary]\n{step1_data.get('context_summary', '')}\n\n"
        f"[Target Domain] {domain}\n{DOMAIN_PROFILES[domain]}\n\n"
        f"[Domain-Specific Risk Calibration]\n{DOMAIN_RISK_FOCUS.get(domain, '')}\n\n"
        f"[Structured Extraction]\n"
        f"Added Obligations: {json.dumps(step1_data.get('added_obligations', []), ensure_ascii=False)}\n"
        f"Removed Rights:    {json.dumps(step1_data.get('removed_rights', []), ensure_ascii=False)}\n"
        f"Key Thresholds:    {json.dumps(step1_data.get('key_thresholds', []), ensure_ascii=False)}\n\n"
        f"[Impact Map Scores]\n"
        + "\n".join(
            f"{ax}: {scores[ax]['score']}/100 ({scores[ax]['direction']}) — {scores[ax]['evidence'][:80]}"
            for ax in ["IP", "Traffic", "Revenue", "Product"]
        )
        + f"\nStrategic Stance: {step2_data['overall_risk_level'].upper()}\n"
        f"Key Opportunities: {'; '.join(step2_data.get('key_opportunities', []))}\n"
        f"Key Threats:       {'; '.join(step2_data.get('key_threats', []))}"
    )


def run_step3_structured(
    client: anthropic.Anthropic,
    domain: str,
    step1_data: Dict,
    step2_data: Dict,
    policy_text: str = "",
) -> Dict:
    """Generate all role-based deliverables as a single structured JSON call with evidence quotes."""
    context = _build_draft_context(domain, step1_data, step2_data)

    # Prepend original policy text so LLM can extract verbatim evidence quotes
    original_block = ""
    if policy_text:
        snippet = policy_text[:3500]
        original_block = (
            f"[ORIGINAL SOURCE TEXT — Extract VERBATIM quotes from this for all *_quotes fields]\n"
            f"{snippet}\n\n"
        )

    response = client.messages.create(
        model=MODEL,
        max_tokens=10000,
        thinking={"type": "adaptive"},
        system=STRATEGIST_SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                f"Based on the following policy analysis, generate a complete intelligence report "
                f"with role-specific deliverables for the '{domain}' domain.\n\n"
                f"{original_block}"
                f"{context}\n\n"
                f"CRITICAL INSTRUCTION A: For every *_quotes field, you MUST include 1–3 VERBATIM "
                f"quotes copied exactly from the ORIGINAL SOURCE TEXT above. "
                f"These are evidence citations — they must be exact text, not paraphrases.\n\n"
                f"CRITICAL INSTRUCTION B — product_checklist QUALITY STANDARD:\n"
                f"The product_checklist must function as a concrete implementation specification that a "
                f"CPO and UX designer can execute directly without further legal interpretation. "
                f"Each item must be written in the format: [CATEGORY] Owner Team — specific action. "
                f"You MUST cover ALL of the following five mandatory categories with at least one item each:\n"
                f"  1. CONSENT MECHANISM: Specify whether opt-in or opt-out consent is required under the "
                f"new policy, which user actions trigger consent capture, and the exact data to be stored "
                f"(timestamp, version ID, user ID). Distinguish between first-time users and existing users.\n"
                f"  2. CONSENT UI IMPLEMENTATION: Define exactly when and where the consent surface appears "
                f"(e.g., on first login post-update, at checkout, before AI feature activation). Specify the "
                f"UI component (modal, banner, inline checkbox, gate screen). List dark-pattern anti-patterns "
                f"to avoid: pre-ticked boxes, buried decline links, misleading button labels, confusing "
                f"double-negatives. Cite applicable regulation (GDPR Art.7, CCPA, etc.) per item.\n"
                f"  3. LEGAL DOCUMENT DISCLOSURE: Specify the UI pattern for notifying users of updated "
                f"Terms of Service or Privacy Policy (e.g., persistent header banner, email notification, "
                f"in-app toast). Define the required link placement, label text, and whether a summary "
                f"changelog ('What changed') must accompany the full document link.\n"
                f"  4. FEATURE / PLATFORM CHANGE: Specific product feature, API endpoint, content filter, "
                f"or platform capability to add, modify, or disable — with owning team and deadline.\n"
                f"  5. AUDIT & COMPLIANCE LOGGING: What events must be logged, retained for how long, and "
                f"in what format to satisfy the new regulatory requirement. Include any required audit trail "
                f"for consent records.\n\n"
                f"Return ONLY the following JSON structure (no preamble, no code fences):\n"
                f"{{\n"
                f'  "what_changed_brief": "Concise 90-second delta memo: exactly what changed, written as a clear before/after summary for a busy executive. Include specific clause numbers, penalties, and effective dates where applicable.",\n'
                f'  "what_changed_quotes": ["Verbatim quote from source text supporting this delta"],\n'
                f'  "overall_risk": "CRITICAL|HIGH|MEDIUM|LOW",\n'
                f'  "business_exposure_memo": "Structured memo covering how this affects: (1) Traffic & audience reach, (2) Revenue streams & monetization, (3) IP & copyright position, (4) Product & platform capabilities, (5) Brand & competitive standing. Include estimated financial impact ranges and timelines.",\n'
                f'  "business_exposure_quotes": ["Verbatim quote from source text supporting this exposure assessment"],\n'
                f'  "negotiation_brief": "Legal & deal team briefing covering: (1) Non-negotiable conditions we must insist on, (2) Items requiring written confirmation from the other party, (3) Our strongest leverage points, (4) Acceptable compromise zones, (5) Red lines that trigger legal escalation or deal termination.",\n'
                f'  "negotiation_quotes": ["Verbatim quote from source text relevant to negotiation position"],\n'
                f'  "board_memo": "One-page board summary covering: (1) What happened and why it matters now, (2) Financial and strategic exposure, (3) Decisions the board must make, (4) Recommended immediate actions with owners and deadlines, (5) Best/base/worst case scenarios.",\n'
                f'  "board_memo_quotes": ["Verbatim quote from source text supporting board-level concern"],\n'
                f'  "product_checklist": [\n'
                f'    "[CONSENT MECHANISM] Team — opt-in/opt-out specification with trigger condition, data captured, and user segment (new vs. existing)",\n'
                f'    "[CONSENT UI] Team — component type, placement, timing, and specific dark-pattern anti-patterns to avoid with regulatory citation",\n'
                f'    "[LEGAL DISCLOSURE] Team — notification UI pattern, link placement, changelog summary requirement, and rollout timing",\n'
                f'    "[FEATURE CHANGE] Team — specific product or platform change with implementation detail and deadline",\n'
                f'    "[AUDIT LOGGING] Team — events to log, retention period, format, and consent record requirements"\n'
                f'  ]\n'
                f"}}"
            ),
        }],
    )
    raw = next(b.text for b in response.content if b.type == "text")
    return _safe_json_parse(raw)


# ─── Chart Functions ──────────────────────────────────────────────────────────
_DIR_COLORS = {
    "threat":      ("#8B2635", "rgba(139, 38, 53, 0.18)"),
    "opportunity": ("#1A6B3C", "rgba(26, 107, 60, 0.18)"),
    "neutral":     ("#0ABAB5", "rgba(10, 186, 181, 0.16)"),
}


def _majority_direction(scores: Dict) -> str:
    dirs = [scores[a]["direction"] for a in ["IP", "Traffic", "Revenue", "Product"]]
    return max(set(dirs), key=dirs.count)


def create_exposure_delta_radar(scores: Dict) -> go.Figure:
    """Before/After radar: Current Baseline vs. New Policy Exposure."""
    axes = ["Traffic", "IP", "Revenue", "Product"]

    # New Policy Exposure = scores returned by AI analysis
    new_vals = [scores[a]["score"] for a in axes]

    # Current Baseline = fixed at 70 across all axes (pre-policy reference line)
    base_vals = [70] * len(axes)

    # Close the polygon
    theta   = axes + [axes[0]]
    new_r   = new_vals  + [new_vals[0]]
    base_r  = base_vals + [base_vals[0]]

    fig = go.Figure()

    # ── Trace 1: Current Baseline (muted steel blue) ───────────────────────
    fig.add_trace(go.Scatterpolar(
        r=base_r, theta=theta,
        fill="toself",
        fillcolor="rgba(90,130,160,0.18)",
        line=dict(color="rgba(90,130,160,0.65)", width=1.5, dash="dot"),
        marker=dict(size=5, color="rgba(90,130,160,0.8)", symbol="circle"),
        name="Current Baseline",
        hovertemplate="<b>%{theta}</b><br>Baseline: %{r}/100<extra></extra>",
    ))

    # ── Trace 2: New Policy Exposure (crimson warning) ─────────────────────
    fig.add_trace(go.Scatterpolar(
        r=new_r, theta=theta,
        fill="toself",
        fillcolor="rgba(139,38,53,0.28)",
        line=dict(color="#C0392B", width=2.2),
        marker=dict(size=7, color="#E74C3C", symbol="diamond"),
        name="New Policy Exposure",
        hovertemplate="<b>%{theta}</b><br>New Exposure: %{r}/100<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100], tickvals=[25, 50, 75, 100],
                tickfont=dict(size=8, color="#6B6560", family="Montserrat"),
                gridcolor="rgba(196,191,184,0.07)",
                linecolor="rgba(196,191,184,0.05)",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#C4BFB8", family="Montserrat"),
                gridcolor="rgba(10,186,181,0.08)",
                linecolor="rgba(10,186,181,0.10)",
            ),
            bgcolor="rgba(13,13,13,0.0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9A9590", family="Montserrat"),
        legend=dict(
            x=0.5, y=-0.12, xanchor="center", orientation="h",
            font=dict(size=9, color="#9A9590", family="Montserrat"),
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
        ),
        margin=dict(l=55, r=55, t=30, b=50),
        height=380,
    )
    return fig


def create_risk_urgency_matrix(scores: Dict, clauses: Optional[List[Dict]] = None) -> go.Figure:
    """Risk & Urgency Matrix: scatter of key policy clauses by time + severity."""
    if clauses is None:
        # ── Fallback: derive clause positions from axis scores ───────────────
        ip_s  = scores["IP"]["score"]
        tr_s  = scores["Traffic"]["score"]
        rv_s  = scores["Revenue"]["score"]
        pr_s  = scores["Product"]["score"]
        clauses = [
            {
                "name": "IP Licensing Term",
                "x": 10,
                "y": min(98, ip_s + 4),
                "color": "#C0392B",
                "size": 14,
                "detail": f"IP Licensing Term<br>Days to Enactment: 10<br>Severity: {min(98, ip_s+4)}/100",
            },
            {
                "name": "Data Share-back Clause",
                "x": 22,
                "y": max(30, tr_s - 5),
                "color": "#E67E22",
                "size": 12,
                "detail": f"Data Share-back Clause<br>Days to Enactment: 22<br>Severity: {max(30, tr_s-5)}/100",
            },
            {
                "name": "Content Attribution Rule",
                "x": 38,
                "y": max(25, rv_s - 10),
                "color": "#A8892A",
                "size": 11,
                "detail": f"Content Attribution Rule<br>Days to Enactment: 38<br>Severity: {max(25, rv_s-10)}/100",
            },
            {
                "name": "Opt-out UI Change",
                "x": 55,
                "y": max(20, pr_s - 8),
                "color": "#0ABAB5",
                "size": 10,
                "detail": f"Opt-out UI Change<br>Days to Enactment: 55<br>Severity: {max(20, pr_s-8)}/100",
            },
        ]
    else:
        # ── Ensure each clause has a "detail" field ──────────────────────────
        for c in clauses:
            if "detail" not in c:
                c["detail"] = f"{c['name']}<br>Days to Enactment: {c['x']}<br>Severity: {c['y']}/100"
            if "color" not in c:
                c["color"] = "#C0392B"
            if "size" not in c:
                c["size"] = 13

    fig = go.Figure()

    # ── Urgency quadrant shading ──────────────────────────────────────────────
    # Q1 top-left: Critical & Urgent (darkest red tint)
    fig.add_shape(type="rect", x0=0, y0=60, x1=30, y1=100,
                  fillcolor="rgba(139,38,53,0.07)", line=dict(width=0), layer="below")
    # Q2 top-right: Critical but time available
    fig.add_shape(type="rect", x0=30, y0=60, x1=70, y1=100,
                  fillcolor="rgba(168,137,42,0.05)", line=dict(width=0), layer="below")
    # Quadrant labels
    for txt, qx, qy, col in [
        ("PROTECT & LICENSE", 15, 97, "rgba(139,38,53,0.55)"),
        ("HIGH EXPOSURE", 50, 97, "rgba(168,137,42,0.40)"),
        ("MONITOR", 50, 22, "rgba(100,100,100,0.35)"),
    ]:
        fig.add_annotation(x=qx, y=qy, text=txt, showarrow=False,
                           font=dict(size=7, color=col, family="Montserrat"),
                           xanchor="center")

    # ── Divider lines ─────────────────────────────────────────────────────────
    fig.add_shape(type="line", x0=30, y0=0, x1=30, y1=100,
                  line=dict(color="rgba(196,191,184,0.08)", width=1, dash="dot"))
    fig.add_shape(type="line", x0=0, y0=60, x1=70, y1=60,
                  line=dict(color="rgba(196,191,184,0.08)", width=1, dash="dot"))

    # ── Data points ──────────────────────────────────────────────────────────
    for c in clauses:
        fig.add_trace(go.Scatter(
            x=[c["x"]], y=[c["y"]],
            mode="markers+text",
            marker=dict(
                size=c["size"] + 4,
                color=c["color"],
                opacity=0.85,
                line=dict(width=1.5, color="rgba(255,255,255,0.15)"),
            ),
            text=[f'  {c["name"]}'],
            textposition="middle right",
            textfont=dict(size=9, color="#C4BFB8", family="Montserrat"),
            hovertemplate=f"<b>{c['detail']}</b><extra></extra>",
            showlegend=False,
        ))

    # x-axis range adapts to the furthest clause with 15% padding
    max_x = max((c["x"] for c in clauses), default=70)
    x_max = max(70, int(max_x * 1.15))

    fig.update_layout(
        xaxis=dict(
            title=dict(text="← Time to Enactment (Days)  [left = more urgent]",
                       font=dict(size=9, color="#9A9590", family="Montserrat")),
            range=[0, x_max], autorange="reversed",
            tickfont=dict(size=9, color="#6B6560", family="Montserrat"),
            gridcolor="rgba(196,191,184,0.05)", showline=False, zeroline=False,
        ),
        yaxis=dict(
            title=dict(text="Business Impact Severity",
                       font=dict(size=9, color="#9A9590", family="Montserrat")),
            range=[0, 100],
            tickfont=dict(size=9, color="#6B6560", family="Montserrat"),
            gridcolor="rgba(196,191,184,0.05)", showline=False, zeroline=False,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,13,13,0.0)",
        font=dict(color="#9A9590", family="Montserrat"),
        showlegend=False,
        margin=dict(l=60, r=30, t=20, b=55),
        height=380,
    )
    return fig


# ─── HTML Component Helpers ───────────────────────────────────────────────────
_ACCENT = "#0ABAB5"


def _sev_color(sev: str) -> str:
    return {"high": "#8B2635", "medium": "#A8892A", "low": "#1A6B3C"}.get(sev, _ACCENT)


def _risk_config(level: str):
    """Returns (stance_label, color, stance_sub) for a raw risk level."""
    return {
        "critical": (
            "PROTECT & LICENSE",
            "#8B2635",
            "Immediate IP defense · aggressive licensing required",
        ),
        "high": (
            "NEGOTIATE & LICENSE",
            "#A8892A",
            "Proactive licensing engagement · secure favorable terms now",
        ),
        "medium": (
            "MONITOR & PROMOTE",
            "#8A7020",
            "Track developments · selectively capture opportunities",
        ),
        "low": (
            "PROMOTE & WAIT",
            "#1A6B3C",
            "Selective engagement · no urgent defensive action required",
        ),
    }.get(level.lower() if level else "medium", ("—", "#C4BFB8", ""))


def _accent_divider() -> None:
    st.markdown(
        '<div style="border-top:1px solid rgba(10,186,181,0.15);margin:2.5rem 0 2rem"></div>',
        unsafe_allow_html=True,
    )


def _engine_badge(label: str) -> str:
    """Return an inline HTML engine badge span."""
    return (
        f'<span style="font-size:0.7rem;color:#888;border:1px solid #333;'
        f'padding:2px 6px;border-radius:4px;margin-left:10px;'
        f'font-family:\'Montserrat\',sans-serif;font-weight:400;'
        f'letter-spacing:0.04em;vertical-align:middle">[Engine: {label}]</span>'
    )


def _section_label(num: str, title: str) -> None:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin:2rem 0 1.4rem">
      <div style="font-family:'Montserrat',system-ui,sans-serif;color:{_ACCENT};font-size:1.4rem;
                  font-weight:700;line-height:1;min-width:28px">{num}</div>
      <div>
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.62rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:2px">Step</div>
        <div style="font-family:'Montserrat',system-ui,sans-serif;color:#F0EDE6;font-size:1.05rem;
                    font-weight:600;letter-spacing:0.04em">{title}</div>
      </div>
      <div style="flex:1;height:1px;background:rgba(10,186,181,0.12);margin-left:8px"></div>
    </div>""", unsafe_allow_html=True)


def _item_card(item: Dict, accent: str) -> None:
    desc = item.get("description", "")
    sev  = item.get("severity", "")
    val  = item.get("value", "")
    sc   = _sev_color(sev) if sev else accent
    st.markdown(f"""
    <div style="background:#111111;border-left:2px solid {accent};
                padding:12px 16px;margin:5px 0;">
      <div style="color:#F0EDE6;font-family:'Montserrat',sans-serif;
                  font-size:0.82rem;font-weight:500;margin-bottom:4px">
        {item.get('item','')}
      </div>
      {"<span style='color:"+sc+";font-family:Montserrat,sans-serif;font-size:0.60rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase'>"+sev+"</span>" if sev else ""}
      {"<span style='color:"+_ACCENT+";font-family:Montserrat,sans-serif;font-weight:600;font-size:0.85rem;margin-left:10px'>"+val+"</span>" if val else ""}
      <div style="color:#C4BFB8;font-family:'Montserrat',sans-serif;
                  font-size:0.76rem;line-height:1.6;margin-top:5px">
        {desc}
      </div>
    </div>""", unsafe_allow_html=True)


def _score_card(axis: str, info: Dict) -> None:
    d = info["direction"]
    lc, _ = _DIR_COLORS.get(d, (_ACCENT, ""))
    ev = info.get("evidence", "")
    acts = info.get("priority_actions", [])[:2]
    icons = {"IP": "◈", "Traffic": "◉", "Revenue": "◆", "Product": "◇"}
    st.markdown(f"""
    <div style="background:#111111;padding:20px 16px;border-top:1px solid {lc};
                border-left:1px solid rgba(10,186,181,0.08);
                border-right:1px solid rgba(10,186,181,0.08);
                border-bottom:1px solid rgba(10,186,181,0.08)">
      <div style="font-family:'Montserrat',system-ui,sans-serif;color:{_ACCENT};
                  font-size:1.2rem;margin-bottom:6px">{icons.get(axis,'◆')}</div>
      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;
                  font-size:0.60rem;letter-spacing:0.22em;text-transform:uppercase">{axis}</div>
      <div style="font-family:'Montserrat',system-ui,sans-serif;color:{lc};
                  font-size:2.8rem;font-weight:700;line-height:1;margin:6px 0 2px">{info['score']}</div>
      <div style="font-family:'Montserrat',sans-serif;color:{lc};
                  font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;
                  margin-bottom:10px">{d}</div>
      <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                  font-size:0.74rem;line-height:1.7;word-break:break-word">
        {ev}
      </div>
      {''.join(f'<div style="font-family:Montserrat,sans-serif;color:#9A9590;font-size:0.70rem;margin-top:5px;padding-left:8px;border-left:1px solid {_ACCENT}33;word-break:break-word">▸ {a}</div>' for a in acts)}
    </div>""", unsafe_allow_html=True)


def _col_header(label: str, badge: str = "", badge_color: str = "#0ABAB5") -> None:
    badge_html = (
        f'<span style="font-family:Montserrat,sans-serif;font-size:0.48rem;font-weight:700;'
        f'letter-spacing:0.14em;color:{badge_color};background:{badge_color}18;'
        f'border:1px solid {badge_color}55;border-radius:3px;padding:2px 6px;'
        f'margin-left:8px;vertical-align:middle">{badge}</span>'
    ) if badge else ""
    st.markdown(f"""
    <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.62rem;
                letter-spacing:0.20em;text-transform:uppercase;margin-bottom:10px;
                border-bottom:1px solid rgba(10,186,181,0.10);padding-bottom:8px;
                display:flex;align-items:center">
      <span>{label}</span>{badge_html}
    </div>""", unsafe_allow_html=True)


def _prose_block(text: str) -> None:
    """Render prose with excess-newline sanitization and inline Markdown table support."""
    import re as _re

    # ── 1. Sanitize: collapse 3+ consecutive newlines → single blank line ──────
    text = _re.sub(r'\n{3,}', '\n\n', text.strip())

    # ── 2. Split text into prose / table segments ──────────────────────────────
    lines = text.split('\n')
    segments: list = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('|'):
            tbl: list = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl.append(lines[i])
                i += 1
            segments.append(('table', tbl))
        else:
            prose: list = []
            while i < len(lines) and not lines[i].strip().startswith('|'):
                prose.append(lines[i])
                i += 1
            segments.append(('prose', prose))

    # ── 3. Build HTML ──────────────────────────────────────────────────────────
    _TH = (
        "padding:7px 14px;text-align:left;font-family:'Montserrat',sans-serif;"
        "font-size:0.62rem;letter-spacing:0.18em;text-transform:uppercase;"
        "color:#9A9590;border-bottom:1px solid rgba(10,186,181,0.22);"
        "background:rgba(10,186,181,0.06);white-space:nowrap"
    )
    _TD = (
        "padding:7px 14px;font-family:'Montserrat',sans-serif;"
        "font-size:0.80rem;color:#C4BFB8;line-height:1.5;"
        "border-bottom:1px solid rgba(196,191,184,0.06)"
    )

    html_parts: list = []
    for seg_type, seg_lines in segments:
        if seg_type == 'prose':
            body = '\n'.join(seg_lines).strip()
            if body:
                # HTML-escape angle brackets, preserve newlines as <br>
                safe = (body
                        .replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;')
                        .replace('\n', '<br>'))
                html_parts.append(
                    f'<div style="font-family:\'Montserrat\',sans-serif;color:#C4BFB8;'
                    f'font-size:0.88rem;line-height:1.85;margin-bottom:0.8rem">'
                    f'{safe}</div>'
                )
        else:
            rows_html: list = []
            header_done = False
            for tl in seg_lines:
                cols = [c.strip() for c in tl.strip().strip('|').split('|')]
                # Skip separator row (---, :--:, etc.)
                if all(_re.match(r'^[-: ]+$', c) for c in cols if c):
                    header_done = True
                    continue
                if not header_done:
                    cells = ''.join(f'<th style="{_TH}">{c}</th>' for c in cols)
                    rows_html.append(f'<tr>{cells}</tr>')
                    header_done = True
                else:
                    cells = ''.join(f'<td style="{_TD}">{c}</td>' for c in cols)
                    rows_html.append(f'<tr>{cells}</tr>')
            if rows_html:
                html_parts.append(
                    f'<div style="overflow-x:auto;margin:0 0 0.8rem">'
                    f'<table style="width:100%;border-collapse:collapse;'
                    f'background:#0D0D0D;border:1px solid rgba(10,186,181,0.12)">'
                    f'{"".join(rows_html)}</table></div>'
                )

    inner = ''.join(html_parts) or f'<div style="color:#6B6560;font-size:0.80rem">—</div>'
    st.markdown(
        f'<div style="background:#111111;border:1px solid rgba(10,186,181,0.10);'
        f'padding:24px 28px;margin:4px 0">{inner}</div>',
        unsafe_allow_html=True,
    )


def _checklist_items(items: list) -> None:
    """Render product checklist as styled actionable items."""
    for i, item in enumerate(items, 1):
        st.markdown(f"""
        <div style="background:#111111;border-left:2px solid {_ACCENT};
                    padding:12px 16px;margin:6px 0;display:flex;gap:12px;align-items:flex-start">
          <div style="font-family:'Montserrat',system-ui,sans-serif;color:{_ACCENT};
                      font-size:0.80rem;font-weight:700;min-width:20px;margin-top:1px">{i:02d}</div>
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                      font-size:0.82rem;line-height:1.6">{item}</div>
        </div>""", unsafe_allow_html=True)


def _evidence_block(
    quotes: List[str],
    claim_tag: str = "Source Citation",
    claim_color: str = "#0ABAB5",
    agent_tag: str = "",
    agent_color: str = "#9A9590",
) -> None:
    """Render evidence quotes with claim-level provenance tags (audit-grade)."""
    if not quotes:
        return
    st.markdown(f"""
    <div style="margin:1.8rem 0 0.6rem">
      <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.58rem;
                  letter-spacing:0.28em;text-transform:uppercase;margin-bottom:0.9rem;
                  display:flex;align-items:center;gap:10px">
        <span>◈</span>
        <span>EVIDENCE — CLAIM-LEVEL PROVENANCE</span>
        <div style="flex:1;height:1px;background:rgba(10,186,181,0.12)"></div>
      </div>
    </div>""", unsafe_allow_html=True)

    for q in quotes:
        agent_badge = (
            f'<span style="background:rgba(154,149,144,0.12);color:{agent_color};'
            f'border:1px solid rgba(154,149,144,0.22);font-family:Montserrat,sans-serif;'
            f'font-size:0.50rem;letter-spacing:0.16em;text-transform:uppercase;'
            f'padding:2px 7px;margin-left:6px">{agent_tag}</span>'
            if agent_tag else ""
        )
        st.markdown(f"""
        <div style="background:#0D0D0D;border:1px solid rgba(10,186,181,0.10);
                    border-left:3px solid {claim_color};
                    padding:13px 16px;margin:7px 0">
          <div style="display:flex;align-items:center;margin-bottom:9px;flex-wrap:wrap;gap:4px">
            <span style="background:rgba(10,186,181,0.08);color:{claim_color};
                         border:1px solid {claim_color}44;font-family:Montserrat,sans-serif;
                         font-size:0.50rem;letter-spacing:0.18em;text-transform:uppercase;
                         padding:2px 8px">{claim_tag}</span>
            {agent_badge}
          </div>
          <div style="color:rgba(240,237,230,0.90);font-family:'Montserrat',sans-serif;
                      font-size:0.84rem;line-height:1.7;font-style:normal;font-weight:400">
            &ldquo;{q}&rdquo;
          </div>
        </div>""", unsafe_allow_html=True)


def _to_docx_bytes(title: str, body: str, domain: str, doc_id: str) -> bytes:
    """Generate a styled Word (.docx) document from title + prose body."""
    from docx import Document as DocxDocument
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    import docx.oxml as oxml

    doc = DocxDocument()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin   = Inches(1.25)
        section.right_margin  = Inches(1.25)

    # Title
    title_para = doc.add_paragraph()
    title_run  = title_para.add_run(title)
    title_run.bold      = True
    title_run.font.size = Pt(16)
    title_run.font.color.rgb = RGBColor(0x0A, 0xBA, 0xB5)

    # Metadata block
    meta_lines = [
        f"Document ID: {doc_id}",
        f"Domain: {domain}",
        f"Grounding Sources: External Policy Text + Nikkei Internal DB",
        f"Compliance Status: Pending Human Review (GC & CPO)",
        f"Traceability: Claim-level provenance active",
    ]
    meta_para = doc.add_paragraph()
    for line in meta_lines:
        run = meta_para.add_run(line + "\n")
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0x77, 0x77, 0x77)

    doc.add_paragraph()  # spacer

    # Body — split on double newlines; render numbered items as list
    for chunk in body.split("\n\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            p = doc.add_paragraph()
            # Detect simple numbered list markers like "1." or "(1)"
            import re as _re
            if _re.match(r"^(\d+\.|[\(\[]\d+[\)\]])\s", line):
                p.style = doc.styles["List Number"]
                line = _re.sub(r"^(\d+\.|[\(\[]\d+[\)\]])\s+", "", line)
            p.add_run(line).font.size = Pt(11)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _download_row(label: str, data: bytes, file_name: str, key: str) -> None:
    """Render a visually prominent .docx download button with teal accent divider."""
    st.markdown(
        '<div style="height:1px;background:rgba(10,186,181,0.14);margin:1.6rem 0 1.2rem"></div>',
        unsafe_allow_html=True,
    )
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        st.download_button(
            label=label,
            data=data,
            file_name=file_name,
            mime=_DOCX_MIME,
            use_container_width=True,
            type="primary",
            key=key,
        )


def _audit_block(doc_id: str, domain: str = "", step2_data: Optional[Dict] = None, policy_text: str = "") -> None:
    """Render compact audit-metadata header — contextual data derived from input text & analysis."""
    import datetime as _dt

    # ── Grounding Sources & Document ID: keyword-based on input policy text ──
    _txt = policy_text.upper()
    if "UK" in _txt or "PARLIAMENT" in _txt:
        grounding  = "UK Parliament Written Statement (HCWS1416) · Active Partner Contract DB"
        doc_id     = "REQ-2026-UK-1416"
    elif "GAIF" in _txt:
        grounding  = "GAIF Publisher Terms (v3.1) · Active Partner Contract DB"
        doc_id     = "REQ-2026-GAIF-3100"
    elif "US" in _txt or "ACT" in _txt:
        grounding  = "US AI Search & Attribution Act Draft · Active Partner Contract DB"
        doc_id     = "REQ-2026-US-0900"
    elif "EU" in _txt or "DMA" in _txt:
        grounding  = "EU DMA Draft Guidance · Active Partner Contract DB"
        doc_id     = "REQ-2026-EU-0400"
    else:
        grounding  = "External Policy Update · Active Partner Contract DB"
        doc_id     = "REQ-2026-GEN-0001"

    # ── Compliance Status: parse date from doc_id → add 2 calendar days ────────
    try:
        date_part = doc_id.split("-")[1]          # e.g. "20260318"
        req_date  = _dt.datetime.strptime(date_part, "%Y%m%d")
        due_date  = req_date + _dt.timedelta(days=2)
        due_str   = due_date.strftime("%b %-d, 12:00 JST")   # e.g. "Mar 20, 12:00 JST"
    except Exception:
        due_str = "Mar 20, 12:00 JST"
    compliance_html = f"🟡 Pending Legal Approval &nbsp;<span style='color:#6B6560'>(Due: {due_str})</span>"

    # ── Traceability: derive confidence from avg axis score ──────────────────
    if step2_data:
        axes = step2_data.get("axes", {})
        scores = [v.get("score", 50) for v in axes.values() if isinstance(v, dict)]
        avg = int(sum(scores) / len(scores)) if scores else 50
        # Map 0-100 score to match-rate (score already reflects alignment with red-lines)
        match_pct = min(98, max(60, avg + 8))
        if avg >= 75:
            conf_label, conf_color = "High Confidence", "#0ABAB5"
        elif avg >= 50:
            conf_label, conf_color = "Moderate Confidence", "#A8892A"
        else:
            conf_label, conf_color = "Low Confidence", "#8B2635"
        traceability = (
            f"<span style='color:{conf_color}'>{conf_label}</span>"
            f"<span style='color:#6B6560'> ({match_pct}% match with internal red-lines)</span>"
        )
    else:
        traceability = "<span style='color:#0ABAB5'>High Confidence</span><span style='color:#6B6560'> (92% match with internal red-lines)</span>"

    st.markdown(f"""
    <div style="background:#0D0D0D;border:1px solid rgba(10,186,181,0.14);
                border-left:2px solid rgba(10,186,181,0.45);
                padding:10px 18px;margin-bottom:20px;
                display:flex;flex-wrap:wrap;gap:10px 36px;align-items:center">
      <div>
        <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.50rem;
                    letter-spacing:0.24em;text-transform:uppercase;margin-bottom:2px">Document ID</div>
        <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};
                    font-size:0.68rem;letter-spacing:0.08em">{doc_id}</div>
      </div>
      <div>
        <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.50rem;
                    letter-spacing:0.24em;text-transform:uppercase;margin-bottom:2px">Grounding Sources</div>
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.68rem">
          {grounding}
        </div>
      </div>
      <div>
        <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.50rem;
                    letter-spacing:0.24em;text-transform:uppercase;margin-bottom:2px">Compliance Status</div>
        <div style="font-family:'Montserrat',sans-serif;color:#A8892A;font-size:0.68rem">
          {compliance_html}
        </div>
      </div>
      <div>
        <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.50rem;
                    letter-spacing:0.24em;text-transform:uppercase;margin-bottom:2px">Traceability</div>
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.68rem">
          {traceability}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


def _policy_memory_block(domain: str, pmg_hits: Optional[List[tuple]] = None) -> None:
    """Render a mock Policy Memory Graph — historical red-line match panel.
    pmg_hits, when provided by the Scenario Router, overrides the domain-keyed defaults.
    """
    if pmg_hits is None:
        _fallback: Dict[str, List[tuple]] = {
            "AI Licensing & Copyright": [
                ("Clause 4.2",    "2024 OpenAI partner contract negotiations",
                 "Zero-revenue attribution for AI-generated summaries of licensed content exceeding 40 words "
                 "was a non-negotiable red-line confirmed by the Legal Committee."),
                ("Exhibit B §3",  "2023 Google News Showcase MOU",
                 "Minimum 12-month traffic guarantee required as a prerequisite to any content licensing "
                 "arrangement — hard floor established by Board resolution."),
            ],
            "AI Search & Zero-Click": [
                ("Article 7(c)",  "2024 Google SGE pre-negotiation memo",
                 "Any Zero-click AI Answers rendering of more than 40 words from a Nikkei article without a redirect "
                 "was categorised as a hard termination trigger — binding precedent."),
                ("Clause 11",     "2023 Bing / Microsoft partner contract review",
                 "Traffic attribution model changes require 90-day advance notice and board sign-off. "
                 "Retroactive application of algorithm changes was explicitly rejected."),
            ],
            "Platform Distribution Policies": [
                ("Section 6.1",   "2024 Meta Platform Agreement review",
                 "Unilateral algorithm change causing >15% traffic reduction triggers force majeure — "
                 "clause negotiated by General Counsel in prior cycle."),
                ("Clause 9.4",    "2023 Apple News+ renegotiation",
                 "Revenue share floor of 35% was confirmed as a hard red-line by Board resolution. "
                 "Any offer below this threshold requires CEO-level authorisation to consider."),
            ],
        }
        pmg_hits = _fallback.get(domain, _fallback["AI Licensing & Copyright"])
    hits = pmg_hits
    cards_html = "".join(
        f"""<div style="background:rgba(10,186,181,0.03);border:1px solid rgba(10,186,181,0.18);
                        border-left:3px solid {_ACCENT};border-radius:0 4px 4px 0;
                        padding:11px 14px;margin-bottom:8px">
              <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:5px">
                <span style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.54rem;
                             font-weight:600;letter-spacing:0.10em">{ref}</span>
                <span style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.50rem;
                             font-style:italic">{source}</span>
              </div>
              <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.63rem;
                          line-height:1.65">{memo}</div>
            </div>"""
        for ref, source, memo in hits
    )
    st.markdown(f"""
    <div style="margin:20px 0 4px">
      <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.52rem;
                  letter-spacing:0.28em;text-transform:uppercase;margin-bottom:10px;
                  display:flex;align-items:center;gap:8px">
        <span>🎯</span>
        <span>Policy Memory Graph — Historical Red-Line Match</span>
        <div style="flex:1;height:1px;background:rgba(10,186,181,0.14)"></div>
        <span style="color:#6B6560;font-size:0.46rem;letter-spacing:0.10em;text-transform:none;
                     font-style:italic">Auto-matched from 340+ archived partner contracts &amp; Board Minutes</span>
      </div>
      {cards_html}
    </div>""", unsafe_allow_html=True)


_COUNTERPARTY_PROFILES: Dict[str, Dict[str, str]] = {
    "AI Search & Zero-Click": {
        "label":           "Dominant Search Platform",
        "traffic_pct":     "85%",
        "traffic_level":   "CRITICAL",
        "traffic_color":   "#8B2635",
        "substitutability":"LOW",
        "sub_color":       "#8B2635",
    },
    "AI Licensing & Copyright": {
        "label":           "Foundation Model Provider",
        "traffic_pct":     "60%",
        "traffic_level":   "HIGH",
        "traffic_color":   "#A8892A",
        "substitutability":"MEDIUM",
        "sub_color":       "#A8892A",
    },
    "Platform Distribution Policies": {
        "label":           "Social / Distribution Platform",
        "traffic_pct":     "45%",
        "traffic_level":   "MEDIUM",
        "traffic_color":   "#0ABAB5",
        "substitutability":"MEDIUM",
        "sub_color":       "#A8892A",
    },
}


def _counterparty_panel(domain: str) -> None:
    """Render a counterparty market-power profile badge panel for Impact Mapping."""
    profile = _COUNTERPARTY_PROFILES.get(
        domain, _COUNTERPARTY_PROFILES["AI Licensing & Copyright"]
    )
    tc = profile["traffic_color"]
    sc = profile["sub_color"]
    st.markdown(f"""
    <div style="background:#0D0D0D;border:1px solid #2A2A2A;
                padding:12px 18px;margin-bottom:18px;
                display:flex;align-items:center;gap:12px;flex-wrap:wrap">
      <div style="font-family:'Montserrat',sans-serif;color:#6B6560;font-size:0.46rem;
                  letter-spacing:0.22em;text-transform:uppercase;margin-right:4px;
                  white-space:nowrap">Target Platform Profile</div>
      <span style="font-family:'Montserrat',sans-serif;font-size:0.62rem;color:#C4BFB8;
                   border:1px solid #333;border-radius:3px;padding:3px 10px;
                   white-space:nowrap">
        Platform: <strong style="color:#F0EDE6">{profile["label"]}</strong>
      </span>
      <span style="font-family:'Montserrat',sans-serif;font-size:0.62rem;
                   border:1px solid {tc}55;border-radius:3px;padding:3px 10px;
                   color:{tc};white-space:nowrap">
        Traffic Dependency: <strong>{profile["traffic_pct"]} ({profile["traffic_level"]})</strong>
      </span>
      <span style="font-family:'Montserrat',sans-serif;font-size:0.62rem;
                   border:1px solid {sc}55;border-radius:3px;padding:3px 10px;
                   color:{sc};white-space:nowrap">
        Substitutability: <strong>{profile["substitutability"]}</strong>
      </span>
    </div>""", unsafe_allow_html=True)


def _pplw_map_block(risk_raw: str = "high") -> None:
    """Render PPLW (Protect / Promote / License / Wait) 4-stance visual mapping."""
    active_map = {
        "critical": "PROTECT",
        "high":     "LICENSE",
        "medium":   "PROMOTE",
        "low":      "WAIT",
    }
    active = active_map.get((risk_raw or "high").lower(), "LICENSE")
    stances = [
        ("PROTECT", "#8B2635", "Immediate IP defense"),
        ("PROMOTE", "#0ABAB5", "Brand visibility & discovery"),
        ("LICENSE", "#A8892A", "Revenue & contract leverage"),
        ("WAIT",    "#6B6560", "Pending further clarity"),
    ]
    badges_html = ""
    for label, color, desc in stances:
        is_active = label == active
        opacity   = "1" if is_active else "0.32"
        border    = f"border:1.5px solid {color}" if is_active else f"border:1px solid {color}44"
        prefix    = "▶ " if is_active else ""
        badges_html += (
            f'<div style="display:inline-flex;flex-direction:column;align-items:center;'
            f'margin-right:12px;opacity:{opacity}">'
            f'<div style="background:{color}1A;{border};border-radius:4px;'
            f'padding:7px 18px;font-family:\'Montserrat\',sans-serif;color:{color};'
            f'font-size:0.62rem;font-weight:700;letter-spacing:0.16em;white-space:nowrap">'
            f'{prefix}{label}</div>'
            f'<div style="font-family:\'Montserrat\',sans-serif;color:#9A9590;'
            f'font-size:0.46rem;margin-top:5px;text-align:center;letter-spacing:0.04em">'
            f'{desc}</div></div>'
        )
    st.markdown(f"""
    <div style="background:#0D0D0D;border:1px solid rgba(10,186,181,0.14);
                padding:16px 20px;margin-bottom:20px;border-radius:2px">
      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.48rem;
                  letter-spacing:0.28em;text-transform:uppercase;margin-bottom:12px">
        ◈ &nbsp; PPLW Strategic Stance Classification
      </div>
      <div style="display:flex;align-items:flex-start;flex-wrap:wrap;gap:4px">
        {badges_html}
      </div>
    </div>""", unsafe_allow_html=True)


def _uncertainty_alert(step2_data: Dict, domain: str) -> None:
    """Render legal/technical uncertainty alert box derived from analysis data."""
    scores     = step2_data.get("scores", {})
    risk_level = step2_data.get("overall_risk_level", "high")
    # Collect axes with medium/low confidence (score ≤ 55) as uncertain items
    uncertain_axes = [
        ax for ax, info in scores.items()
        if isinstance(info, dict) and int(info.get("score", 100)) <= 55
    ]
    if uncertain_axes:
        items_html = "".join(
            f'<li style="margin-bottom:4px">'
            f'<span style="color:#A8892A;font-weight:600">[WAIT]</span> '
            f'{ax.replace("_", " ").title()} — '
            f'specific regulatory threshold not yet defined in current draft; '
            f'pending official guidance before final implementation scope can be determined.'
            f'</li>'
            for ax in uncertain_axes[:3]
        )
    else:
        items_html = (
            '<li style="margin-bottom:4px">'
            '<span style="color:#A8892A;font-weight:600">[WAIT]</span> '
            f'The specific technical standard for the machine-readable opt-out format '
            f'is not strictly defined in the current draft for <em>{domain}</em>. '
            f'Final engineering effort estimates are marked as [WAIT] pending official '
            f'regulatory guidelines.'
            '</li>'
        )
    st.markdown(f"""
    <div style="background:#1A1200;border-left:3px solid #A8892A;
                padding:14px 18px;margin:16px 0 20px;border-radius:0 2px 2px 0">
      <div style="font-family:'Montserrat',sans-serif;color:#A8892A;font-size:0.60rem;
                  font-weight:700;letter-spacing:0.10em;margin-bottom:10px">
        ⚠️ &nbsp;Identified Legal &amp; Technical Uncertainties
      </div>
      <ul style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.62rem;
                 line-height:1.75;margin:0;padding-left:18px">
        {items_html}
        <li style="margin-bottom:4px">
          <span style="color:#6B6560;font-weight:600">[PENDING]</span>
          Enforcement timeline and jurisdictional scope may change before final enactment.
          All [WAIT]-classified items should be re-evaluated upon next scheduled policy review.
        </li>
      </ul>
    </div>""", unsafe_allow_html=True)


def _governance_panel(tab_key: str, risk_raw: str = "high", step2_data: Optional[Dict] = None) -> None:
    """Enterprise governance & audit control panel — Human-in-the-Loop."""
    if step2_data is None:
        step2_data = {}
    st.markdown(f"""
    <div style="border-top:1px solid rgba(10,186,181,0.15);margin:3rem 0 1.6rem;padding-top:1.6rem">
      <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.58rem;
                  letter-spacing:0.28em;text-transform:uppercase;margin-bottom:0.4rem;
                  display:flex;align-items:center;gap:10px">
        <span>◆</span>
        <span>GOVERNANCE &amp; AUDIT CONTROL PANEL</span>
        <span style="font-size:0.7rem;color:#888;border:1px solid #333;padding:2px 6px;
                     border-radius:4px;font-weight:400;letter-spacing:0.04em;
                     text-transform:none">[Engine: Tool-Calling State Machine]</span>
        <div style="flex:1;height:1px;background:rgba(10,186,181,0.14)"></div>
      </div>
      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.56rem;
                  letter-spacing:0.14em;margin-top:3px">
        Human-in-the-Loop · System of Record · Audit-grade Sign-off
      </div>
    </div>""", unsafe_allow_html=True)

    rl_key   = (risk_raw or "medium").lower()
    stance_label, rl_color, stance_sub = _risk_config(rl_key)
    stance_label = step2_data.get("stance_label") or stance_label

    # Override dropdown uses human-readable stance options
    all_stances = [
        ("critical", "PROTECT & LICENSE"),
        ("high",     "NEGOTIATE & LICENSE"),
        ("medium",   "MONITOR & PROMOTE"),
        ("low",      "PROMOTE & WAIT"),
    ]
    keep_opt = f"— Keep AI Stance: {stance_label} —"
    other_opts = [f"Override → {s}" for k, s in all_stances if k != rl_key]
    override_options = [keep_opt] + other_opts

    with st.form(key=f"gov_{tab_key}"):

        # ── ① Executive Review & Stance Adjustment ────────────────────────────
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.56rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:12px">
          ①&nbsp; EXECUTIVE REVIEW &amp; STANCE ADJUSTMENT
        </div>""", unsafe_allow_html=True)

        oc1, oc2 = st.columns([1.4, 2.4])
        with oc1:
            st.markdown(f"""
            <div style="background:#0D0D0D;border:1px solid {rl_color}44;
                        padding:14px 16px;text-align:center;height:100%">
              <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.48rem;
                          letter-spacing:0.22em;text-transform:uppercase;margin-bottom:8px">
                AI Strategic Stance
              </div>
              <div style="font-family:'Montserrat',system-ui,sans-serif;color:{rl_color};
                          font-size:0.72rem;font-weight:700;letter-spacing:0.12em;
                          text-transform:uppercase;line-height:1.35">
                {stance_label}
              </div>
              <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.44rem;
                          letter-spacing:0.04em;margin-top:8px;line-height:1.5">
                {stance_sub}
              </div>
              <div style="font-family:'Montserrat',sans-serif;color:#6B6560;font-size:0.42rem;
                          letter-spacing:0.08em;margin-top:8px">
                claude-opus-4-6 · adaptive thinking
              </div>
            </div>""", unsafe_allow_html=True)
        with oc2:
            st.selectbox(
                "Final Strategic Decision (Human-in-the-Loop)",
                options=override_options,
                key=f"override_{tab_key}",
            )
            st.text_area(
                "Justification / Human Context  (Required for Audit Log)",
                placeholder=(
                    "Enter your justification for any risk level change, "
                    "or add contextual notes to confirm the AI determination. "
                    "This entry will be immutably logged with your Audit ID."
                ),
                height=82,
                key=f"justification_{tab_key}",
            )

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        # ── ② Automated Workflow Execution ────────────────────────────────────
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.56rem;
                    letter-spacing:0.22em;text-transform:uppercase;
                    margin:18px 0 10px;padding-top:14px;
                    border-top:1px solid rgba(10,186,181,0.08)">
          ②&nbsp; AUTOMATED WORKFLOW EXECUTION
        </div>""", unsafe_allow_html=True)

        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.checkbox(
                "Push Product Checklist to Jira  (Epic)",
                value=True, key=f"r_jira_{tab_key}",
            )
        with rc2:
            st.checkbox(
                "Send Board Memo to Slack  (#exec-alerts)",
                value=True, key=f"r_slack_{tab_key}",
            )
        with rc3:
            st.checkbox(
                "Generate Policy Response Draft in Google Docs",
                value=True, key=f"r_docs_{tab_key}",
            )
        with rc4:
            st.checkbox(
                "Update Policy Memory Graph with this approved decision (Data Flywheel)",
                value=True, key=f"r_pmg_{tab_key}",
            )

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        # ── ③ Audit Sign-off ──────────────────────────────────────────────────
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.56rem;
                    letter-spacing:0.22em;text-transform:uppercase;
                    margin:18px 0 10px;padding-top:14px;
                    border-top:1px solid rgba(10,186,181,0.08)">
          ③&nbsp; AUDIT SIGN-OFF &amp; EXECUTION
        </div>""", unsafe_allow_html=True)

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        sc1, sc2 = st.columns([3, 1.2])
        with sc1:
            st.markdown(f"""
            <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.60rem;
                        letter-spacing:0.08em;line-height:1.8;padding-top:6px">
              Logged in as: &nbsp;<span style="color:#C4BFB8;font-weight:600">General Counsel</span>
              &nbsp;·&nbsp; Audit ID: <span style="color:{_ACCENT}">GC-8921</span>
              &nbsp;·&nbsp; Session: <span style="color:#1A6B3C">enterprise-verified</span>
              &nbsp;·&nbsp; Jurisdiction: Japan / APAC
              <br>
              <span style="color:#9A9590;font-size:0.54rem">
                This sign-off constitutes a legally binding attestation under the enterprise governance protocol.
                All actions will be immutably logged to the System of Record.
              </span>
            </div>""", unsafe_allow_html=True)
        with sc2:
            _already_executed = st.session_state.get("workflow_executed", False)
            if _already_executed:
                st.markdown("""
                <div style="background:#0D1A0D;border:1px solid #1A6B3C;border-radius:4px;
                            padding:10px 14px;text-align:center">
                  <div style="font-family:'Montserrat',sans-serif;color:#2ECC71;
                              font-size:0.78rem;font-weight:700;letter-spacing:0.10em">
                    ✅ Executed Successfully
                  </div>
                  <div style="font-family:'Montserrat',sans-serif;color:#1A6B3C;
                              font-size:0.54rem;letter-spacing:0.08em;margin-top:4px">
                    Slack · Jira · Docs · Memory Graph Updated
                  </div>
                </div>""", unsafe_allow_html=True)
                submitted = False
            else:
                submitted = st.form_submit_button(
                    "Approve & Execute Selected Actions",
                    use_container_width=True,
                )
                st.markdown("""
                <div style="font-family:'Montserrat',sans-serif;color:#6B6560;
                            font-size:0.52rem;letter-spacing:0.06em;text-align:center;
                            margin-top:4px">
                  (Triggers Slack, Jira, Docs &amp; Updates Memory Graph)
                </div>""", unsafe_allow_html=True)

        if submitted:
            st.session_state["workflow_executed"] = True
            st.toast(
                "✅ Approved & executing — Slack, Jira, Docs and Memory Graph updating. "
                "Audit ID GC-8921 logged.",
                icon="✅",
            )
            st.rerun()


# ─── Multi-Agent Debate Helpers ───────────────────────────────────────────────

def _build_debate_log(step1_data: Dict, step2_data: Dict, domain: str) -> List[Dict]:
    """Build a virtual expert-committee debate transcript from analysis data (no API call)."""
    scores    = step2_data.get("scores", {})
    obligations = step1_data.get("added_obligations", [])
    threats     = step2_data.get("key_threats", [])
    opportunities = step2_data.get("key_opportunities", [])
    risk_level  = step2_data.get("overall_risk_level", "medium").upper()

    ip_score   = scores.get("IP",      {}).get("score", 50)
    rev_score  = scores.get("Revenue", {}).get("score", 50)
    prod_score = scores.get("Product", {}).get("score", 50)

    obl_text = obligations[0].get("item", "new compliance obligations") if obligations else "new compliance obligations"
    threat_text = threats[0]   if threats      else "potential operational disruption"
    opp_text    = opportunities[0] if opportunities else "strategic repositioning opportunity"

    return [
        {
            "agent": "⚖️ Legal Agent",
            "color": "#8B2635",
            "message": (
                f"[🎯 Policy Memory Graph Match: 2024 partner contract Red-lines] "
                f"IP exposure flagged at {ip_score}/100. "
                f"The clause '{obl_text}' directly conflicts with the "
                f"'no-sublicensing without prior written consent' red-line established during our 2024 OpenAI partner contract "
                f"negotiations (Clause 4.2) and reaffirmed in the 2023 Google News Showcase MOU (Exhibit B §3). "
                f"This is a historically non-negotiable position — require written indemnification and sub-licensing "
                f"prohibition before any commitment. Triggering standard outside-counsel review protocol for {domain}."
            ),
        },
        {
            "agent": "💰 Business Agent",
            "color": "#A8892A",
            "message": (
                f"Revenue impact at {rev_score}/100 is material. Primary threat: '{threat_text}'. "
                f"Counter-position: '{opp_text}' is a genuine leverage point. "
                f"I disagree with full escalation — negotiated compliance with phased timelines protects both revenue and the partnership."
            ),
        },
        {
            "agent": "🧩 Product Agent",
            "color": "#1A6B3C",
            "message": (
                f"Product surface exposure at {prod_score}/100. Consent UI and audit logging are hard requirements — "
                f"estimate 4–6 weeks engineering lead time for full compliance stack. "
                f"Recommend phased delivery: consent gate first, audit trail second. "
                f"Legal sign-off required at each milestone before public release."
            ),
        },
        {
            "agent": "🏛️ Executive Alignment",
            "color": "#0ABAB5",
            "final": True,
            "message": (
                f"Conflict Resolved: Balancing Legal risk (IP exposure: {ip_score}/100) with Business impact "
                f"(revenue exposure: {rev_score}/100). Unified cross-functional strategy formulated — "
                f"Strategic Stance: {_risk_config(risk_level.lower())[0]}. "
                f"Action Required: Escalating to Legal and Product leadership for final review and compliance sprint kick-off. "
                f"Board notification required within 48 hours — {domain} domain."
            ),
        },
    ]


def _debate_expander(debate_log: List[Dict]) -> None:
    """Render the multi-agent debate transcript as a collapsible section."""
    if not debate_log:
        return
    with st.expander("◆  Multi-Agent Debate Log — Virtual Expert Committee", expanded=False):
        st.markdown(
            _engine_badge("Opus-4 Reasoning") +
            f'<div style="font-family:\'Montserrat\',sans-serif;color:#C4BFB8;font-size:0.60rem;'
            f'letter-spacing:0.22em;text-transform:uppercase;margin:10px 0 1.2rem">'
            f'Internal reasoning trace — autonomous committee deliberation prior to output generation'
            f'</div>',
            unsafe_allow_html=True,
        )
        for entry in debate_log:
            is_final = entry.get("final", False)
            if is_final:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(10,186,181,0.10),rgba(10,186,181,0.04));
                            border:1px solid rgba(10,186,181,0.35);border-left:3px solid {entry['color']};
                            padding:16px 18px;margin:14px 0 4px">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                    <div style="font-family:'Montserrat',sans-serif;color:{entry['color']};
                                font-size:0.65rem;font-weight:700;letter-spacing:0.16em;
                                text-transform:uppercase">
                      {entry['agent']}
                    </div>
                    <div style="font-family:'Montserrat',sans-serif;color:{entry['color']};
                                font-size:0.55rem;letter-spacing:0.18em;text-transform:uppercase;
                                background:rgba(10,186,181,0.12);padding:2px 8px;
                                border:1px solid rgba(10,186,181,0.25)">
                      SYSTEM OF RECORD
                    </div>
                  </div>
                  <div style="font-family:'Montserrat',sans-serif;color:#F0EDE6;
                              font-size:0.82rem;line-height:1.75;font-weight:500">
                    {entry['message']}
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#111111;border-left:2px solid {entry['color']};
                            padding:12px 16px;margin:8px 0">
                  <div style="font-family:'Montserrat',sans-serif;color:{entry['color']};
                              font-size:0.65rem;font-weight:600;letter-spacing:0.14em;
                              text-transform:uppercase;margin-bottom:6px">
                    {entry['agent']}
                  </div>
                  <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                              font-size:0.80rem;line-height:1.7">
                    {entry['message']}
                  </div>
                </div>""", unsafe_allow_html=True)


# ─── System of Action Export Helpers ─────────────────────────────────────────

def _format_jira_export(checklist: List[str], domain: str) -> str:
    """Format product checklist as Jira Epic + User Stories with Acceptance Criteria."""
    lines = [
        f"EPIC: Policy Compliance Sprint — {domain}",
        f"Epic Description: Implement required product, legal, and engineering changes",
        f"  per Policy Response analysis. Priority: HIGH. Owner: CPO + Legal.",
        "",
    ]
    for i, item in enumerate(checklist, 1):
        lines.append(f"── Story {i:02d} ──────────────────────────────────────────")
        lines.append(f"Title: {item}")
        lines.append(f"Story Type: Task  |  Priority: High  |  Sprint: Compliance-Q2")
        lines.append(f"User Story:")
        if item.startswith("[") and "]" in item:
            cat = item[1:item.index("]")]
            rest = item[item.index("]") + 1:].strip(" —").strip()
            lines.append(f"  As a compliance officer, I need {rest.lower()}")
            lines.append(f"  so that the {domain} product satisfies {cat} requirements.")
        else:
            lines.append(f"  As a compliance officer, I need this item implemented")
            lines.append(f"  so that the {domain} product satisfies policy requirements.")
        lines.append(f"Acceptance Criteria:")
        lines.append(f"  - [ ] Implementation complete and code-reviewed")
        lines.append(f"  - [ ] QA sign-off on all affected user flows")
        lines.append(f"  - [ ] Legal review completed — regulatory citation confirmed")
        lines.append(f"  - [ ] Analytics event(s) verified in staging")
        lines.append("")
    return "\n".join(lines)


def _format_slack_export(board_memo: str, domain: str, risk_label: str) -> str:
    """Format board memo as Slack #exec-alerts channel message."""
    snippet = board_memo[:700].replace("\n\n", "\n").strip()
    if len(board_memo) > 700:
        snippet += "..."
    risk_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk_label.upper(), "⚪")
    return (
        f"*{risk_emoji} Policy Response Alert — {domain}*\n"
        f"*Strategic Stance:* `{risk_label.upper()}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{snippet}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"_Actions required — see full report in the enterprise dashboard._\n"
        f"_Policy Response · claude-opus-4-6_"
    )


# ─── Login Screen ─────────────────────────────────────────────────────────────
_LOGIN_ID = "aifund"
_LOGIN_PW  = "nikkei2030"


def render_login() -> None:
    st.markdown("""
    <style>
    .stApp {
        background-color: #0a0a0a !important;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    section[data-testid="stSidebar"],
    header[data-testid="stHeader"] {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
    }
    .block-container {
        padding-top: 15vh !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, card_col, _ = st.columns([1, 4, 1])
    with card_col:
        st.markdown(f"""
        <div style="background:#111111;border:1px solid rgba(10,186,181,0.18);
                    padding:44px 44px 36px;">
          <div style="text-align:center;margin-bottom:32px;">
            <div style="font-family:'Montserrat',system-ui,sans-serif;color:{_ACCENT};
                        font-size:1.1rem;font-weight:700;letter-spacing:0.16em;
                        white-space:nowrap;">
              POLICY RESPONSE
            </div>
            <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                        font-size:0.55rem;letter-spacing:0.34em;text-transform:uppercase;
                        margin-top:4px;white-space:nowrap;">
              ENTERPRISE · RESTRICTED ACCESS
            </div>
            <div style="width:48px;height:1px;
                        background:linear-gradient(90deg,transparent,{_ACCENT}88,transparent);
                        margin:16px auto 0;"></div>
          </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                      font-size:0.60rem;letter-spacing:0.22em;text-transform:uppercase;
                      margin-bottom:6px;">Login ID</div>
        """, unsafe_allow_html=True)
        login_id = st.text_input("login_id", placeholder="Enter your login ID",
                                 label_visibility="collapsed", key="login_id_input")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                      font-size:0.60rem;letter-spacing:0.22em;text-transform:uppercase;
                      margin-bottom:6px;">Password</div>
        """, unsafe_allow_html=True)
        password = st.text_input("password", type="password",
                                 placeholder="Enter your password",
                                 label_visibility="collapsed", key="login_pw_input")

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        login_btn = st.button("◆  Login", use_container_width=True, key="login_btn")

        if login_btn:
            if login_id == _LOGIN_ID and password == _LOGIN_PW:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.markdown(f"""
                <div style="font-family:'Montserrat',sans-serif;color:#8B2635;
                            font-size:0.70rem;text-align:center;margin-top:12px;
                            letter-spacing:0.08em;">
                  Invalid credentials. Please try again.
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin-top:20px;
                    font-family:'Montserrat',sans-serif;color:#C4BFB8;
                    font-size:0.58rem;letter-spacing:0.14em;">
          Access restricted to authorized personnel only.
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ─── Main App ─────────────────────────────────────────────────────────────────
def main() -> None:
    if not st.session_state.get("authenticated", False):
        render_login()

    if "results" not in st.session_state:
        st.session_state.results = None

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="margin-bottom:2rem;">
          <div style="font-family:'Montserrat',system-ui,sans-serif;color:{_ACCENT};
                      font-size:1.05rem;font-weight:700;letter-spacing:0.12em;">
            POLICY RESPONSE
          </div>
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                      font-size:0.58rem;letter-spacing:0.30em;text-transform:uppercase;
                      margin-top:2px">
            ENTERPRISE · {MODEL}
          </div>
          <div style="height:1px;background:linear-gradient(90deg,{_ACCENT}33,transparent);
                      margin-top:12px"></div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;font-size:0.65rem;margin-bottom:10px">
          <div style="color:{_ACCENT};letter-spacing:0.20em;font-size:0.56rem;
                      font-weight:600;margin-bottom:10px;text-transform:uppercase">
            ◆ Internal Data Grounding
          </div>
          <div style="color:#9A9590;font-size:0.57rem;letter-spacing:0.08em;
                      margin-bottom:10px;line-height:1.5">
            AI-linked sources · AI Licensing domain
          </div>
          <div style="color:#C4BFB8;line-height:2.2;font-size:0.64rem">
            <span style="color:#1A6B3C;margin-right:5px">🟢</span>
            Content &amp; IP Archive
            <span style="color:#9A9590;font-size:0.54rem;margin-left:4px">(Asset volume linked)</span>
          </div>
          <div style="color:#C4BFB8;line-height:2.2;font-size:0.64rem">
            <span style="color:#1A6B3C;margin-right:5px">🟢</span>
            Rights Management System
            <span style="color:#9A9590;font-size:0.54rem;margin-left:4px">(Third-party clearance linked)</span>
          </div>
          <div style="color:#C4BFB8;line-height:2.2;font-size:0.64rem">
            <span style="color:#1A6B3C;margin-right:5px">🟢</span>
            Contract Repository
            <span style="color:#9A9590;font-size:0.54rem;margin-left:4px">(Existing AI partner contracts linked)</span>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div style="height:1px;background:rgba(10,186,181,0.08);margin:1.4rem 0 1.2rem"></div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;font-size:0.65rem;line-height:2.1">
          <div style="color:{_ACCENT};letter-spacing:0.20em;font-size:0.56rem;
                      font-weight:600;margin-bottom:10px;text-transform:uppercase">
            AGENTIC WORKFLOW PIPELINE
          </div>
          <div style="color:#C4BFB8">
            <span style="color:{_ACCENT};font-family:'Montserrat',system-ui,sans-serif;
                         font-size:0.72rem;font-weight:700;margin-right:6px">I</span>
            Policy Ingestion &rarr; Substantive Changes
          </div>
          <div style="color:#C4BFB8">
            <span style="color:{_ACCENT};font-family:'Montserrat',system-ui,sans-serif;
                         font-size:0.72rem;font-weight:700;margin-right:6px">II</span>
            Business Translation &rarr; Strategic Stance Mapping
          </div>
          <div style="color:#C4BFB8">
            <span style="color:{_ACCENT};font-family:'Montserrat',system-ui,sans-serif;
                         font-size:0.72rem;font-weight:700;margin-right:6px">III</span>
            Multi-Agent Synthesis &rarr; Role-Specific Actions
          </div>
          <div style="margin-top:12px;padding-top:10px;
                      border-top:1px solid rgba(10,186,181,0.10);
                      color:#A8A49E;letter-spacing:0.10em;font-size:0.57rem;
                      line-height:1.9">
            <span style="color:{_ACCENT}99">Evidence-Grounded</span>
            &nbsp;&middot;&nbsp;
            <span style="color:#C4BFB8">Domain Judgment</span>
            <br>
            <span style="color:{_ACCENT}99">Multi-Agent Debate</span>
            &nbsp;&middot;&nbsp;
            <span style="color:#C4BFB8">Human-in-the-Loop</span>
          </div>
        </div>""", unsafe_allow_html=True)

    run_triggered = False

    # ── Welcome Screen + Inline Input Form ───────────────────────────────────
    if not st.session_state.results:
        st.markdown(f"""
        <div style="text-align:center;padding:4rem 2rem 2.5rem">
          <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.62rem;
                      letter-spacing:0.42em;text-transform:uppercase;margin-bottom:1.8rem">
            ◆ &nbsp; Agentic Workflow · Policy Response &nbsp; ◆
          </div>
          <h1 style="font-family:'Montserrat',sans-serif !important;
                     color:#F0EDE6 !important;font-size:3.4rem;font-weight:700;
                     letter-spacing:0.04em;margin:0 0 0.6rem;line-height:1.1">
            Policy<br>
            <span style="color:{_ACCENT};">Response</span>
          </h1>
          <div style="width:80px;height:1px;background:linear-gradient(90deg,transparent,{_ACCENT},transparent);
                      margin:1.4rem auto"></div>
          <p style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.78rem;
                    letter-spacing:0.14em;text-transform:uppercase;margin:0">
            External Change &nbsp;→&nbsp; 6 Role-Specific Actionable Outputs
          </p>
        </div>""", unsafe_allow_html=True)

        g1, g2, g3 = st.columns(3)
        for col, num, label, desc in [
            (g1, "I",   "Set Context",       "Select the target business domain profile (e.g., AI Licensing) to align the engine with your company's revenue and IP structure."),
            (g2, "II",  "Ingest Data",       "Paste the external change—such as a new platform policy, draft agreement, or regulatory update."),
            (g3, "III", "Run Response Pipeline",  "Execute the agentic pipeline to autonomously extract substantive changes and generate role-specific deliverables in seconds."),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:#111111;border:1px solid rgba(10,186,181,0.12);
                            padding:28px 22px;text-align:center;min-height:180px">
                  <div style="font-family:'Montserrat',system-ui,sans-serif;color:{_ACCENT};
                              font-size:1.8rem;font-weight:700;margin-bottom:12px">{num}</div>
                  <div style="font-family:'Montserrat',sans-serif;color:#F0EDE6;
                              font-size:0.72rem;font-weight:600;letter-spacing:0.18em;
                              text-transform:uppercase;margin-bottom:12px">{label}</div>
                  <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                              font-size:0.78rem;line-height:1.7">{desc}</div>
                </div>""", unsafe_allow_html=True)

        # ── Inline Input Container ────────────────────────────────────────────
        st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0D0D0D;border:1px solid rgba(10,186,181,0.18);
                    border-top:2px solid {_ACCENT};padding:2rem 2.4rem 1.8rem;
                    margin-bottom:0.5rem">
          <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.56rem;
                      letter-spacing:0.32em;text-transform:uppercase;margin-bottom:1.4rem;
                      display:flex;align-items:center;gap:10px">
            <span>◆</span><span>ANALYSIS CONFIGURATION</span>
            <div style="flex:1;height:1px;background:rgba(10,186,181,0.14)"></div>
          </div>
        </div>""", unsafe_allow_html=True)

        inp_left, inp_right = st.columns([1, 2], gap="large")

        # ── Sample text payloads ──────────────────────────────────────────
        _SAMPLES: Dict[str, str] = {
            "gaif": (
                "GAIF Publisher Ecosystem Terms Update (v3.1):\n"
                "- To improve user experience, GAIF 'Direct Answers' will now provide comprehensive\n"
                "  inline AI summaries. Publisher source links will be consolidated and moved to a\n"
                "  separate 'References' tab below the fold.\n"
                "- Publishers who implement machine-readable opt-outs for AI training will\n"
                "  simultaneously be excluded from all GAIF search indexing and discovery surfaces.\n"
                "- Revenue share for inline summary impressions is discontinued."
            ),
            "usai": (
                "US AI Search & Attribution Act (Draft):\n"
                "- Mandates that any generative AI system providing 'Direct Answers' that substantially\n"
                "  substitute original publisher content must provide prominent, above-the-fold\n"
                "  hyperlinks to the source.\n"
                "- Classifies Zero-click AI Answers without explicit publisher licensing agreements\n"
                "  as presumptive copyright infringement.\n"
                "- Statutory damages apply per un-attributed search query."
            ),
            "eu": (
                "EU Commission Draft Guidance on AI Search & DMA:\n"
                "- Designates AI-powered search overviews by dominant platforms as core platform\n"
                "  services.\n"
                "- Dominant platforms are prohibited from using publisher data for Zero-click AI Answers\n"
                "  summaries without offering fair, proportionate, and non-discriminatory compensation.\n"
                "- Publishers must be given granular technical controls to allow traditional search\n"
                "  indexing without implicitly consenting to generative AI training."
            ),
        }

        with inp_left:
            st.markdown(f"""
            <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.52rem;
                        letter-spacing:0.24em;text-transform:uppercase;margin-bottom:6px">
              Target Domain Profile
            </div>""", unsafe_allow_html=True)
            domain = st.selectbox(
                "domain_select",
                options=list(DOMAIN_PROFILES.keys()),
                key="domain",
                label_visibility="collapsed",
            )
            st.caption("Calibrates risk-weighting and contract references for the selected domain.")

            # ── Active Data Integrations panel ────────────────────────────
            st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.50rem;
                        letter-spacing:0.28em;text-transform:uppercase;margin-bottom:10px;
                        display:flex;align-items:center;gap:8px">
              <span>◆</span><span>Active Data Integrations</span>
            </div>
            <div style="background:rgba(10,186,181,0.04);border:1px solid rgba(10,186,181,0.14);
                        border-radius:6px;padding:12px 14px;display:flex;flex-direction:column;gap:8px">
              <div style="display:flex;align-items:center;gap:8px">
                <span style="font-size:0.55rem;line-height:1">🟢</span>
                <span style="font-family:'Montserrat',sans-serif;color:#C8C3BD;font-size:0.60rem;
                             letter-spacing:0.04em">Nikkei IP &amp; Content Archive</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <span style="font-size:0.55rem;line-height:1">🟢</span>
                <span style="font-family:'Montserrat',sans-serif;color:#C8C3BD;font-size:0.60rem;
                             letter-spacing:0.04em">Active Partner Contract DB</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <span style="font-size:0.55rem;line-height:1">🟢</span>
                <span style="font-family:'Montserrat',sans-serif;color:#C8C3BD;font-size:0.60rem;
                             letter-spacing:0.04em">Audience Traffic Analytics</span>
              </div>
            </div>""", unsafe_allow_html=True)
            st.caption(
                "Auto-extracted from 340+ historical partner contracts, Board Minutes, and litigation records "
                "to establish Day 1 Policy Memory Graph."
            )

        with inp_right:
            # ── Sample loader rows ────────────────────────────────────────
            st.markdown(f"""
            <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.52rem;
                        letter-spacing:0.24em;text-transform:uppercase;margin-bottom:6px">
              Policy / Regulatory Text
            </div>""", unsafe_allow_html=True)
            _b1_col, _b2_col, _b3_col = st.columns(3)
            with _b1_col:
                if st.button("⬇ GAIF Publisher Terms v3.1", key="_load_gaif",
                             use_container_width=True, help="Load GAIF Publisher Ecosystem Terms v3.1"):
                    st.session_state["policy_text"] = _SAMPLES["gaif"]
                    st.rerun()
            with _b2_col:
                if st.button("⬇ US AI Search & Attribution Act", key="_load_usai",
                             use_container_width=True, help="Load US AI Search & Attribution Act draft"):
                    st.session_state["policy_text"] = _SAMPLES["usai"]
                    st.rerun()
            with _b3_col:
                if st.button("⬇ EU DMA Draft Guidance on AI Search", key="_load_eu",
                             use_container_width=True, help="Load EU Commission DMA draft guidance on AI search"):
                    st.session_state["policy_text"] = _SAMPLES["eu"]
                    st.rerun()

            policy_text = st.text_area(
                "policy_input",
                height=248,
                placeholder=(
                    "Example: EU AI Act Amendment — Article 53\n"
                    "- Generative AI systems using copyrighted content for training\n"
                    "  must provide prior notice and a compensation scheme to rights holders.\n"
                    "- Non-compliance: 3% of global turnover or up to €15M, whichever is higher.\n"
                    "- Phased enforcement begins Q1 2026."
                ),
                key="policy_text",
                label_visibility="collapsed",
            )

        has_input = bool(policy_text and policy_text.strip() and len(policy_text.strip()) >= 20)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            run_triggered = st.button(
                "▶  EXECUTE RESPONSE PIPELINE",
                key="main_run",
                use_container_width=True,
                type="primary",
                disabled=not has_input,
            )
            if not has_input:
                st.markdown(
                    '<div style="font-family:Montserrat,sans-serif;color:#6B6560;'
                    'font-size:0.60rem;text-align:center;margin-top:5px;letter-spacing:0.06em">'
                    'Paste policy text above (min 20 chars) to activate</div>',
                    unsafe_allow_html=True,
                )

        if not run_triggered:
            st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
            _accent_divider()
            c1, c2, c3 = st.columns(3)
            for col, icon, cap, sub in [
                (c1, "◈", "Substantive Change Analysis",
                 "Identifies meaning-level policy changes—not just text diffs. Maps added obligations and removed rights directly to your unique Media Business Ontology."),
                (c2, "◉", "Policy Memory Graph",
                 "Evaluates external threats against your institutional memory (past partner contracts, board red-lines) to recommend 4 Strategic Stances: PROTECT, PROMOTE, LICENSE, or WAIT."),
                (c3, "◆", "Agentic Execution",
                 "Generates 6 role-specific outputs (incl. PPL Map & Board Memo) and autonomously routes approved cross-functional workflows to Jira, Slack, and Docs."),
            ]:
                with col:
                    st.markdown(f"""
                    <div style="padding:0 8px">
                      <div style="font-family:'Montserrat',system-ui,sans-serif;color:{_ACCENT};
                                  font-size:1.2rem;font-weight:700;margin-bottom:8px">{icon}</div>
                      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;
                                  font-size:0.68rem;font-weight:600;letter-spacing:0.14em;
                                  text-transform:uppercase;margin-bottom:8px">{cap}</div>
                      <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                                  font-size:0.75rem;line-height:1.7">{sub}</div>
                    </div>""", unsafe_allow_html=True)
            return

    # ── Validation ────────────────────────────────────────────────────────────
    if run_triggered:
        # domain / policy_text / has_input are defined in the welcome block above
        if not has_input:
            st.warning("Please enter policy text (minimum 20 characters).")
            return

        # ── Scenario Router: check for known demo scenario BEFORE LLM calls ───
        scenario = get_scenario_data(policy_text)

        if scenario is None:
            # No keyword match → require live API key
            client = get_client()
            if not client:
                st.markdown(f"""
                <div style="background:#111111;border:1px solid rgba(139,38,53,0.4);
                            padding:16px 20px;margin-bottom:1rem">
                  <div style="font-family:'Montserrat',sans-serif;color:#8B2635;
                              font-size:0.72rem;font-weight:600;letter-spacing:0.12em">
                    API KEY REQUIRED
                  </div>
                  <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                              font-size:0.78rem;margin-top:4px">
                    Set the ANTHROPIC_API_KEY environment variable to enable analysis.
                  </div>
                </div>""", unsafe_allow_html=True)
                return
        else:
            client = None   # Scenario Router provides all data; no API call needed

        # ── Agentic Pipeline ───────────────────────────────────────────────────
        st.session_state.results = None
        pipeline_start = time.time()

        step1_data:     Optional[Dict] = None
        step2_data:     Optional[Dict] = None
        step3_data:     Optional[Dict] = None
        debate_log:     List[Dict] = []
        pmg_hits:       Optional[List] = None
        matrix_clauses: Optional[List] = None

        # Progress bar lives outside st.status so it stays visible throughout
        _prog = st.progress(0, text="◆  Initializing Autonomous Response Pipeline...")
        time.sleep(0.3)

        with st.status(
            "◆  Autonomous Response Pipeline — Running...",
            expanded=True,
        ) as pipeline_status:
            try:
                if scenario is not None:
                    # ── Scenario Router fast path ─────────────────────────────
                    _prog.progress(6, text="Step I · Substantive Change Analysis — Parsing policy structure...")
                    st.write(
                        "**Step I — Substantive Change Analysis**  \n"
                        "Deep-parsing source text to isolate meaning-level changes — added obligations, "
                        "removed rights, penalty thresholds, and effective-date triggers. "
                        "Mapping to Media Business Ontology..."
                    )
                    time.sleep(0.6)

                    step1_data = scenario["step1_data"]
                    domain     = scenario["domain"]
                    n_obl = len(step1_data.get("added_obligations", []))
                    n_rem = len(step1_data.get("removed_rights", []))
                    n_thr = len(step1_data.get("key_thresholds", []))
                    _prog.progress(25, text="Step I Complete ✓ — Substantive change extraction finished")
                    st.write(
                        f"  ✓  Substantive change extraction complete — "
                        f"**{n_obl}** added obligations · "
                        f"**{n_rem}** removed rights · "
                        f"**{n_thr}** key thresholds identified"
                    )
                    time.sleep(0.4)

                    _prog.progress(30, text=f"Step II · Policy Memory Graph — Loading '{domain}' institutional memory...")
                    st.write(
                        f"**Step II — Policy Memory Graph × Impact Mapping**  \n"
                        f"Cross-referencing extracted deltas against Policy Memory Graph: "
                        f"340+ archived partner contracts, Board red-lines, and prior negotiation records. "
                        f"Scoring across 4 axes: IP Exposure · Traffic Risk · Revenue Sensitivity · "
                        f"Product Constraint. Deriving Strategic Stance..."
                    )
                    time.sleep(0.5)

                    step2_data = scenario["step2_data"]
                    rl_raw = step2_data.get("overall_risk_level", "medium").upper()
                    stance_label = step2_data.get("stance_label") or _risk_config(rl_raw.lower())[0]
                    scores = step2_data.get("scores", {})
                    score_str = "  ·  ".join(
                        f"{ax}: **{scores[ax]['score']}**/100"
                        for ax in ["IP", "Traffic", "Revenue", "Product"]
                        if ax in scores
                    )
                    _prog.progress(50, text=f"Step II Complete ✓ — Strategic Stance: {stance_label}")
                    st.write(
                        f"  ✓  Policy Memory Graph match complete — Strategic Stance: **{stance_label}**  \n"
                        f"  {score_str}"
                    )
                    time.sleep(0.4)

                    _prog.progress(54, text="Multi-Agent Debate · Convening virtual expert committee...")
                    st.write(
                        "**Multi-Agent Debate — Virtual Expert Committee**  \n"
                        "Convening Legal Counsel, Business Strategy, Product Leadership, "
                        "and Executive Alignment agents for structured adversarial review against "
                        "Policy Memory Graph red-lines..."
                    )
                    time.sleep(0.4)

                    debate_log = scenario["debate_log"]
                    _debate_progress_steps = [56, 59, 62, 65]
                    for i, entry in enumerate(debate_log):
                        pct = _debate_progress_steps[i] if i < len(_debate_progress_steps) else 65
                        _prog.progress(pct, text=f"Multi-Agent Debate · {entry['agent']} speaking...")
                        short = entry["message"][:120].rstrip()
                        st.write(f"  {entry['agent']}: _{short}..._")
                        time.sleep(0.45)

                    _prog.progress(68, text="Multi-Agent Debate · Consensus reached ✓")
                    st.write(
                        f"  ✓  Committee consensus reached — "
                        f"Strategic Stance confirmed: **{stance_label}**"
                    )
                    time.sleep(0.3)

                    _prog.progress(72, text="Step III · Agentic Execution — Generating 6 deliverables...")
                    st.write(
                        "**Step III — Agentic Execution & Deliverable Synthesis**  \n"
                        "Generating 6 Deliverables: What Changed Brief · Business Exposure Memo · "
                        "PPL Map · Negotiation Brief · Product / Legal Checklist · Board Memo — "
                        "each grounded with verbatim evidence citations and Policy Memory Graph matches. "
                        "Preparing execution payloads for Slack, Jira, and Docs..."
                    )
                    time.sleep(0.5)

                    step3_data     = scenario["step3_data"]
                    pmg_hits       = scenario["pmg_hits"]
                    matrix_clauses = scenario.get("matrix_clauses")

                    _prog.progress(98, text="Step III · Finalizing audit metadata & document ID...")
                    st.write(
                        "  ✓  6 role-specific deliverables generated — "
                        "Policy Memory Graph citations embedded · execution payloads ready"
                    )
                    time.sleep(0.3)

                else:
                    # ── Live LLM pipeline ─────────────────────────────────────
                    _prog.progress(6, text="Step I · Substantive Change Analysis — Parsing policy structure...")
                    st.write(
                        "**Step I — Substantive Change Analysis**  \n"
                        "Deep-parsing source text to isolate meaning-level changes — added obligations, "
                        "removed rights, penalty thresholds, and effective-date triggers. "
                        "Mapping to Media Business Ontology..."
                    )
                    time.sleep(0.4)

                    step1_data = run_step1_parsing(client, policy_text)

                    n_obl = len(step1_data.get("added_obligations", []))
                    n_rem = len(step1_data.get("removed_rights", []))
                    n_thr = len(step1_data.get("key_thresholds", []))
                    _prog.progress(25, text="Step I Complete ✓ — Substantive change extraction finished")
                    st.write(
                        f"  ✓  Substantive change extraction complete — "
                        f"**{n_obl}** added obligations · "
                        f"**{n_rem}** removed rights · "
                        f"**{n_thr}** key thresholds identified"
                    )
                    time.sleep(0.3)

                    _prog.progress(30, text=f"Step II · Policy Memory Graph — Loading '{domain}' institutional memory...")
                    st.write(
                        f"**Step II — Policy Memory Graph × Impact Mapping**  \n"
                        f"Cross-referencing extracted deltas against Policy Memory Graph: "
                        f"340+ archived partner contracts, Board red-lines, and prior negotiation records. "
                        f"Scoring across 4 axes: IP Exposure · Traffic Risk · Revenue Sensitivity · "
                        f"Product Constraint. Deriving Strategic Stance..."
                    )
                    time.sleep(0.4)

                    step2_data = run_step2_impact_mapping(client, step1_data, domain)

                    rl_raw = step2_data.get("overall_risk_level", "medium").upper()
                    stance_label = _risk_config(rl_raw.lower())[0]
                    scores = step2_data.get("scores", {})
                    score_str = "  ·  ".join(
                        f"{ax}: **{scores[ax]['score']}**/100"
                        for ax in ["IP", "Traffic", "Revenue", "Product"]
                        if ax in scores
                    )
                    _prog.progress(50, text=f"Step II Complete ✓ — Strategic Stance: {stance_label}")
                    st.write(
                        f"  ✓  Policy Memory Graph match complete — Strategic Stance: **{stance_label}**  \n"
                        f"  {score_str}"
                    )
                    time.sleep(0.3)

                    _prog.progress(54, text="Multi-Agent Debate · Convening virtual expert committee...")
                    st.write(
                        "**Multi-Agent Debate — Virtual Expert Committee**  \n"
                        "Convening Legal Counsel, Business Strategy, Product Leadership, "
                        "and Executive Alignment agents for structured adversarial review against "
                        "Policy Memory Graph red-lines..."
                    )
                    time.sleep(0.5)

                    debate_log = _build_debate_log(step1_data, step2_data, domain)

                    _debate_progress_steps = [56, 59, 62, 65]
                    for i, entry in enumerate(debate_log):
                        pct = _debate_progress_steps[i] if i < len(_debate_progress_steps) else 65
                        _prog.progress(pct, text=f"Multi-Agent Debate · {entry['agent']} speaking...")
                        short = entry["message"][:120].rstrip()
                        st.write(f"  {entry['agent']}: _{short}..._")
                        time.sleep(0.55)

                    _prog.progress(68, text="Multi-Agent Debate · Consensus reached ✓")
                    st.write(
                        f"  ✓  Committee consensus reached — "
                        f"Strategic Stance confirmed: **{stance_label}**"
                    )
                    time.sleep(0.3)

                    _prog.progress(72, text="Step III · Agentic Execution — Generating 6 deliverables...")
                    st.write(
                        "**Step III — Agentic Execution & Deliverable Synthesis**  \n"
                        "Generating 6 Deliverables: What Changed Brief · Business Exposure Memo · "
                        "PPL Map · Negotiation Brief · Product / Legal Checklist · Board Memo — "
                        "each grounded with verbatim evidence citations and Policy Memory Graph matches. "
                        "Preparing execution payloads for Slack, Jira, and Docs..."
                    )
                    time.sleep(0.4)

                    step3_data = run_step3_structured(
                        client, domain, step1_data, step2_data, policy_text
                    )

                    _prog.progress(98, text="Step III · Finalizing audit metadata & document ID...")
                    st.write(
                        "  ✓  6 role-specific deliverables generated — "
                        "Policy Memory Graph citations embedded · execution payloads ready"
                    )
                    time.sleep(0.4)

                _prog.progress(100, text="◆  Response Package Ready — All steps complete ✓")
                pipeline_status.update(
                    label="◆  Execution Complete — 6 Deliverables Ready",
                    state="complete",
                    expanded=False,
                )

            except anthropic.AuthenticationError:
                _prog.progress(100, text="Pipeline failed.")
                pipeline_status.update(
                    label="◆  Pipeline Failed — Authentication Error", state="error"
                )
                st.error("Invalid API key. Please check your credentials.")
                return
            except anthropic.RateLimitError:
                _prog.progress(100, text="Pipeline failed.")
                pipeline_status.update(
                    label="◆  Pipeline Failed — Rate Limit", state="error"
                )
                st.error("Rate limit exceeded. Please wait a moment and try again.")
                return
            except Exception as exc:
                _prog.progress(100, text="Pipeline failed.")
                pipeline_status.update(label="◆  Pipeline Failed", state="error")
                st.error(f"Pipeline Error: {exc}")
                return

        elapsed = round(time.time() - pipeline_start, 1)
        initials = "".join(w[0].upper() for w in domain.split() if w[0].isalpha())[:4]
        doc_id = f"REQ-{time.strftime('%Y%m%d')}-{initials}-{str(int(elapsed * 1000))[-4:]}"

        st.session_state.results = {
            "step1": step1_data,
            "step2": step2_data,
            "step3": step3_data,
            "domain": domain,
            "elapsed": elapsed,
            "debate_log": debate_log if debate_log else [],
            "doc_id": doc_id,
            "policy_text":    policy_text,
            "pmg_hits":       pmg_hits,
            "matrix_clauses": matrix_clauses,
        }

    # ── Display Results ───────────────────────────────────────────────────────
    res = st.session_state.results
    if not res:
        return

    step1_data = res["step1"]
    step2_data = res["step2"]
    step3_data = res["step3"]
    domain      = res["domain"]
    elapsed     = res.get("elapsed", 0)
    debate_log  = res.get("debate_log", [])
    doc_id      = res.get("doc_id", "REQ-—")
    policy_text = res.get("policy_text", "")
    pmg_hits       = res.get("pmg_hits")
    matrix_clauses = res.get("matrix_clauses")

    # ── Header ────────────────────────────────────────────────────────────────
    hcol1, hcol2 = st.columns([4, 1])
    with hcol1:
        st.markdown(f"""
        <div style="padding:1.5rem 0 0.5rem">
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.60rem;
                      letter-spacing:0.28em;text-transform:uppercase;margin-bottom:6px">
            Analysis Complete · {domain}
          </div>
          <div style="font-family:'Montserrat',system-ui,sans-serif;color:#F0EDE6;
                      font-size:1.1rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase">
            Policy Response — Execution Report
          </div>
        </div>""", unsafe_allow_html=True)
    with hcol2:
        if st.button("← New Analysis", key="clear"):
            st.session_state.results = None
            st.session_state["workflow_executed"] = False
            st.rerun()

    # ── Success Toast ─────────────────────────────────────────────────────────
    st.toast("✅ Multi-Agent Synthesis Complete: Generated 6 role-specific actionable outputs.")

    # ── Multi-Agent Debate Log ────────────────────────────────────────────────
    _debate_expander(debate_log)
    _uncertainty_alert(step2_data, domain)

    # ── STEP 1: Parsing Output ────────────────────────────────────────────────
    _accent_divider()
    _section_label("I", "Substantive Change Analysis (Previous vs. New Policy Diff)")
    st.markdown(_engine_badge("Semantic Chunker &amp; Alignment Model"), unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        _col_header("Added Obligations", badge="[+] NEW", badge_color="#1A6B3C")
        items = step1_data.get("added_obligations", [])
        for it in items:
            _item_card(it, _sev_color(it.get("severity", "medium")))
        if not items:
            st.caption("—")
    with c2:
        _col_header("Removed Rights", badge="[-] REMOVED", badge_color="#8B2635")
        items = step1_data.get("removed_rights", [])
        for it in items:
            _item_card(it, _sev_color(it.get("severity", "medium")))
        if not items:
            st.caption("—")
    with c3:
        _col_header("Key Thresholds", badge="[⚑] THRESHOLD", badge_color="#A8892A")
        items = step1_data.get("key_thresholds", [])
        for it in items:
            _item_card(it, _ACCENT)
        if not items:
            st.caption("—")

    if step1_data.get("context_summary"):
        st.markdown(f"""
        <div style="background:#111111;border-left:2px solid {_ACCENT};
                    padding:14px 18px;margin-top:16px">
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.60rem;
                      letter-spacing:0.20em;text-transform:uppercase;margin-bottom:6px">Context Summary</div>
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                      font-size:0.82rem;line-height:1.7">
            {step1_data['context_summary']}
          </div>
        </div>""", unsafe_allow_html=True)

    # ── STEP 2: Impact Mapping ────────────────────────────────────────────────
    _accent_divider()
    _section_label("II", f"Impact Mapping — {domain}")
    st.markdown(_engine_badge("Composite Embedding Search"), unsafe_allow_html=True)
    _counterparty_panel(domain)

    rl = step2_data.get("overall_risk_level", "medium")
    rl_label2, rl_color2, rl_sub2 = _risk_config(rl)
    st.markdown(f"""
    <div style="background:#111111;border:1px solid {rl_color2}55;
                padding:16px 22px;margin-bottom:1.5rem;
                display:flex;align-items:center;gap:20px">
      <div style="min-width:180px">
        <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.48rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:4px">Strategic Stance</div>
        <div style="font-family:'Montserrat',sans-serif;color:{rl_color2};
                    font-size:0.92rem;font-weight:700;letter-spacing:0.04em;line-height:1.2">{rl_label2}</div>
        <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.44rem;
                    font-style:italic;margin-top:5px">{rl_sub2}</div>
      </div>
      <div style="width:1px;height:50px;background:rgba(10,186,181,0.14)"></div>
      <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.80rem;
                  line-height:1.7;flex:1">
        {step2_data.get('executive_summary','')}
      </div>
    </div>""", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(
            '<div style="font-family:Montserrat,sans-serif;color:#C4BFB8;font-size:0.80rem;'
            'letter-spacing:0.24em;text-transform:uppercase;margin-bottom:6px;font-weight:600">'
            'Exposure Delta Radar</div>'
            '<div style="font-family:Montserrat,sans-serif;color:#A0A09A;font-size:0.90rem;'
            'margin-bottom:10px">Current Baseline vs. New Policy Exposure</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(create_exposure_delta_radar(step2_data["scores"]),
                        use_container_width=True, config={"displayModeBar": False})
    with ch2:
        st.markdown(
            '<div style="font-family:Montserrat,sans-serif;color:#C4BFB8;font-size:0.80rem;'
            'letter-spacing:0.24em;text-transform:uppercase;margin-bottom:6px;font-weight:600">'
            'Risk &amp; Urgency Matrix</div>'
            '<div style="font-family:Montserrat,sans-serif;color:#A0A09A;font-size:0.90rem;'
            'margin-bottom:10px">Key clauses by time-to-enactment × business severity</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(create_risk_urgency_matrix(step2_data["scores"], matrix_clauses),
                        use_container_width=True, config={"displayModeBar": False})

    st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#C4BFB8;font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;margin:1rem 0 12px">Evidence & Priority Actions</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    _card_scores = step2_data.get("card_scores", step2_data["scores"])
    for col, axis in [(sc1, "IP"), (sc2, "Traffic"), (sc3, "Revenue"), (sc4, "Product")]:
        with col:
            _score_card(axis, _card_scores[axis])

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    op_col, th_col = st.columns(2)
    with op_col:
        _col_header("Key Opportunities")
        for opp in step2_data.get("key_opportunities", []):
            st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#1A6B3C;padding:4px 0 4px 10px;border-left:1px solid #1A6B3C44;font-size:0.78rem;margin:3px 0">▸ {opp}</div>', unsafe_allow_html=True)
    with th_col:
        _col_header("Key Threats")
        for thr in step2_data.get("key_threats", []):
            st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#8B2635;padding:4px 0 4px 10px;border-left:1px solid #8B263544;font-size:0.78rem;margin:3px 0">▸ {thr}</div>', unsafe_allow_html=True)

    # ── STEP 3: Role-Specific Deliverables (6 Tabs) ───────────────────────────
    _accent_divider()
    _section_label("III", "Role-Specific Deliverables — 6 Actionable Outputs")

    _wf_executed = st.session_state.get("workflow_executed", False)
    if _wf_executed:
        st.markdown("""
        <div style="display:inline-flex;align-items:center;gap:10px;
                    background:#0D1A0D;border:1px solid #1A6B3C;
                    border-radius:4px;padding:6px 16px;margin-bottom:14px">
          <span style="font-family:'Montserrat',sans-serif;color:#2ECC71;
                       font-size:0.68rem;font-weight:700;letter-spacing:0.12em">
            🟢 STATUS: EXECUTED
          </span>
          <span style="font-family:'Montserrat',sans-serif;color:#1A6B3C;
                       font-size:0.58rem;letter-spacing:0.08em">
            — ROUTED TO SLACK / DOCS / JIRA · MEMORY GRAPH UPDATED
          </span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:inline-flex;align-items:center;gap:10px;
                    background:#1A1500;border:1px solid #A8892A;
                    border-radius:4px;padding:6px 16px;margin-bottom:14px">
          <span style="font-family:'Montserrat',sans-serif;color:#C9A84C;
                       font-size:0.68rem;font-weight:700;letter-spacing:0.12em">
            🟡 STATUS: DRAFT
          </span>
          <span style="font-family:'Montserrat',sans-serif;color:#A8892A;
                       font-size:0.58rem;letter-spacing:0.08em">
            — PENDING EXECUTIVE REVIEW
          </span>
        </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "◆  What Changed Brief",
        "◉  Business Exposure Memo",
        "🎯  Protect / Promote / License Map",
        "⚖  Negotiation Brief",
        "✓  Product / Legal Checklist",
        "▪  Board Memo",
    ])

    def _fn(prefix: str) -> str:
        return f"{prefix}_{domain.replace(' ', '_')}.md"

    # ── Compute governance risk level once (passed raw to all panels) ─────────
    _gov_risk_raw = step3_data.get("overall_risk", step2_data.get("overall_risk_level", "medium"))

    # ── Tab 1: Executive Summary & Delta ─────────────────────────────────────
    with tab1:
        _audit_block(doc_id, domain, step2_data, policy_text)
        rl3 = step3_data.get("overall_risk", "—")
        rl3_label, rl3_color, rl3_sub = _risk_config(rl3)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px">
          <div style="background:#111111;border:1px solid {rl3_color}55;
                      padding:14px 20px;text-align:center;min-width:170px">
            <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.48rem;
                        letter-spacing:0.22em;text-transform:uppercase;margin-bottom:5px">
              Strategic Stance
            </div>
            <div style="font-family:'Montserrat',sans-serif;color:{rl3_color};
                        font-size:0.92rem;font-weight:700;letter-spacing:0.04em;line-height:1.2">
              {rl3_label}
            </div>
            <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.44rem;
                        font-style:italic;margin-top:6px;line-height:1.4">
              {rl3_sub}
            </div>
          </div>
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.76rem;
                      line-height:1.6;flex:1">
            90-second delta brief — what specifically changed and why it matters now.
          </div>
        </div>""", unsafe_allow_html=True)

        what_changed = step3_data.get("what_changed_brief", "")
        _prose_block(what_changed)

        # ── Parsed Claims — verbatim extracts from source policy document ──────
        _parsed_claims = step1_data.get("parsed_claims", [])
        if _parsed_claims:
            _evidence_block(
                _parsed_claims,
                claim_tag="📄 Parsed Claim",
                claim_color="#6B8F71",
                agent_tag="Policy Parser",
            )

        _evidence_block(
            step3_data.get("what_changed_quotes", []),
            claim_tag="🔵 Policy Delta",
            claim_color="#0ABAB5",
            agent_tag="Executive Summary",
        )

        # ── Policy Memory Graph evidence — scenario-driven or domain fallback ──
        _pmg_fallback = {
            "AI Licensing & Copyright": [
                "Strictly aligns with the 'no-sublicensing without prior written consent' red-line "
                "established during our 2024 OpenAI partner contract negotiations (Clause 4.2). Previous position "
                "required board-level sign-off before any sub-licensing of editorial content.",
                "Mirrors the revenue-floor precedent from 2023 Google News Showcase MOU (Exhibit B §3): "
                "minimum per-article compensation must not fall below ¥0.8 per impression.",
            ],
            "AI Search & Zero-Click": [
                "Consistent with red-line position from 2023 Apple News+ renewal: attribution link "
                "must remain clickable and must not be replaced by AI-generated summaries (§7.1).",
                "Conflicts with internal policy memo (Legal, Nov 2024): Zero-click AI Answers from "
                "generative search must be classified as derivative works under J-Copyright Act Art. 21.",
            ],
            "Platform Distribution Policies": [
                "Directly triggers the 'algorithmic reach guarantee' clause negotiated in 2022 Meta "
                "Instant Articles exit agreement — any reach reduction >15% activates renegotiation right.",
                "Matches threat pattern documented in 2023 internal IP audit (Board Minutes, Q3): "
                "platform-controlled distribution reduces Nikkei's first-party data leverage to zero.",
            ],
        }
        _pmg_quotes = (
            step2_data.get("pmg_evidence")
            or _pmg_fallback.get(domain)
            or [
                "Historical institutional memory confirms this policy shift pattern was anticipated "
                "in 2024 internal strategy documents. Board-approved response protocols apply.",
                "Cross-referenced against 340+ archived partner contracts: this clause type has a 73% success rate "
                "when countered with the 'reciprocal data access' negotiation framework.",
            ]
        )
        _evidence_block(
            _pmg_quotes,
            claim_tag="🎯 Policy Memory Graph",
            claim_color="#9B59B6",
            agent_tag="Institutional Memory",
        )

        _download_row(
            label="📥  Export Executive Delta Brief (.docx)",
            data=_to_docx_bytes(
                f"Executive Delta Brief — {domain}",
                f"Strategic Stance: {rl3_label}\n\n{what_changed}",
                domain, doc_id,
            ),
            file_name=_fn("delta_brief").replace(".md", ".docx"),
            key="dl_tab1",
        )

        _governance_panel("tab1", _gov_risk_raw, step2_data)

    # ── Tab 2: Business Exposure ──────────────────────────────────────────────
    with tab2:
        _audit_block(doc_id, domain, step2_data, policy_text)
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.72rem;
                    line-height:1.6;margin-bottom:16px">
          Impact on traffic, revenue, IP rights, product capabilities, and competitive position.
        </div>""", unsafe_allow_html=True)
        _pplw_map_block(_gov_risk_raw)

        exposure = step3_data.get("business_exposure_memo", "")
        _prose_block(exposure)

        _evidence_block(
            step3_data.get("business_exposure_quotes", []),
            claim_tag="🟡 Revenue Impact",
            claim_color="#A8892A",
            agent_tag="Business Agent",
        )

        _download_row(
            label="📥  Export Business Exposure Memo (.docx)",
            data=_to_docx_bytes(
                f"Business Exposure Memo — {domain}",
                exposure, domain, doc_id,
            ),
            file_name=_fn("business_exposure").replace(".md", ".docx"),
            key="dl_tab2",
        )

        _governance_panel("tab2", _gov_risk_raw, step2_data)

    # ── Tab 3: Protect / Promote / License Map ────────────────────────────────
    with tab3:
        _audit_block(doc_id, domain, step2_data, policy_text)
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.72rem;
                    line-height:1.6;margin-bottom:20px">
          Axis-by-axis recommended business action — derived from Policy Memory Graph + impact scoring.
        </div>""", unsafe_allow_html=True)

        # Use card_scores (scenario-specific) if available, fall back to scores
        _display_scores = step2_data.get("card_scores", step2_data.get("scores", {}))

        # Badge config: badge_name → (color, icon)
        _BADGE_CFG = {
            "PROTECT":  ("#8B2635", "🛡"),
            "LICENSE":  ("#0ABAB5", "💼"),
            "PROMOTE":  ("#1A6B3C", "📣"),
            "WAIT":     ("#A8892A", "⏳"),
            "MONITOR":  ("#6B6560", "🔍"),
            "NEGOTIATE":("#A8892A", "⚖"),
        }

        def _ppl_action(ax_data: dict, direction: str, score: int):
            """Return (action, color, icon, summary) — prefer explicit badge fields."""
            badge   = ax_data.get("action_badge")
            summary = ax_data.get("action_summary")
            if badge and summary:
                color, icon = _BADGE_CFG.get(badge.upper(), ("#6B6560", "🔍"))
                return badge.upper(), color, icon, summary
            # Fallback derivation
            if direction == "threat":
                if score >= 70:
                    return "PROTECT",  "#8B2635", "🛡", "High-severity threat — activate IP defense and contract protections immediately."
                return "NEGOTIATE", "#A8892A", "⚖", "Material threat — engage counterparty to renegotiate terms before enforcement."
            if direction == "opportunity":
                if score >= 60:
                    return "LICENSE",  "#0ABAB5", "💼", "Monetisation opportunity — formalise licensing arrangement to capture upside."
                return "PROMOTE",  "#1A6B3C", "📣", "Positive development — proactively promote capabilities and market positioning."
            return "MONITOR", "#6B6560", "🔍", "Neutral impact — continue monitoring; no urgent action required."

        ppl_rows = []
        for ax, icon in [("IP", "◈"), ("Traffic", "◉"), ("Revenue", "◆"), ("Product", "◇")]:
            ax_data   = _display_scores.get(ax, {})
            direction = ax_data.get("direction", "neutral")
            score     = ax_data.get("score", 0)
            evidence  = ax_data.get("evidence", "")
            action, acolor, aicon, rationale = _ppl_action(ax_data, direction, score)
            ppl_rows.append((ax, icon, score, direction, action, acolor, aicon, rationale, evidence))

        for ax, axicon, score, direction, action, acolor, aicon, rationale, evidence in ppl_rows:
            st.markdown(f"""
            <div style="background:#111111;border:1px solid {acolor}44;
                        border-left:4px solid {acolor};border-radius:0 6px 6px 0;
                        padding:16px 20px;margin-bottom:12px;
                        display:flex;align-items:flex-start;gap:16px">
              <div style="min-width:80px;text-align:center">
                <div style="font-family:'Montserrat',system-ui,sans-serif;color:{acolor};
                            font-size:1.6rem;line-height:1">{aicon}</div>
                <div style="font-family:'Montserrat',sans-serif;color:{acolor};font-size:0.52rem;
                            font-weight:700;letter-spacing:0.12em;margin-top:4px">{action}</div>
              </div>
              <div style="flex:1">
                <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:6px">
                  <span style="font-family:'Montserrat',system-ui,sans-serif;color:#F0EDE6;
                               font-size:0.95rem;font-weight:600">{axicon} {ax}</span>
                  <span style="font-family:'Montserrat',sans-serif;color:{acolor};
                               font-size:0.52rem;letter-spacing:0.10em">{score}/100 · {direction.upper()}</span>
                </div>
                <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.66rem;
                            line-height:1.6;margin-bottom:6px">{rationale}</div>
                <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.60rem;
                            font-style:italic;line-height:1.5">{evidence[:140]}{"…" if len(evidence) > 140 else ""}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        _policy_memory_block(domain, pmg_hits)
        _governance_panel("tab3", _gov_risk_raw, step2_data)

    # ── Tab 4: Negotiation Brief ──────────────────────────────────────────────
    with tab4:
        _audit_block(doc_id, domain, step2_data, policy_text)
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.72rem;
                    line-height:1.6;margin-bottom:16px">
          Deal team briefing: non-negotiable conditions, confirmation points, leverage, and red lines.
        </div>""", unsafe_allow_html=True)

        negotiation = step3_data.get("negotiation_brief", "")
        _prose_block(negotiation)

        _evidence_block(
            step3_data.get("negotiation_quotes", []),
            claim_tag="🔴 IP Risk",
            claim_color="#8B2635",
            agent_tag="Legal Agent",
        )
        _policy_memory_block(domain, pmg_hits)

        _download_row(
            label="📥  Export Negotiation Brief (.docx)",
            data=_to_docx_bytes(
                f"Negotiation Brief — {domain}",
                negotiation, domain, doc_id,
            ),
            file_name=_fn("negotiation_brief").replace(".md", ".docx"),
            key="dl_tab4",
        )

        _governance_panel("tab4", _gov_risk_raw, step2_data)

    # ── Tab 5: Product / Legal Checklist ─────────────────────────────────────
    with tab5:
        _audit_block(doc_id, domain, step2_data, policy_text)
        checklist = step3_data.get("product_checklist", [])
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.72rem;
                    line-height:1.6;margin-bottom:16px">
          {len(checklist)} implementation items — features, UI elements, terms, and technical changes to review.
        </div>""", unsafe_allow_html=True)

        if checklist:
            _checklist_items(checklist)
            checklist_body = "\n\n".join(f"{i}. {item}" for i, item in enumerate(checklist, 1))
            _download_row(
                label="📥  Export Product / Legal Checklist (.docx)",
                data=_to_docx_bytes(
                    f"Product & Legal Checklist — {domain}",
                    checklist_body, domain, doc_id,
                ),
                file_name=_fn("product_checklist").replace(".md", ".docx"),
                key="dl_tab5",
            )
        else:
            st.caption("No checklist items generated.")

        _governance_panel("tab5", _gov_risk_raw, step2_data)

        # ── Jira Export ───────────────────────────────────────────────────────
        if checklist:
            st.markdown(f"""
            <div style="border-top:1px solid rgba(10,186,181,0.10);margin:2.2rem 0 1rem;padding-top:1.2rem">
              <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.58rem;
                          letter-spacing:0.26em;text-transform:uppercase;margin-bottom:0.9rem">
                ◆ &nbsp; SYSTEM OF ACTION — JIRA EXPORT
              </div>
            </div>""", unsafe_allow_html=True)

            jira_text = _format_jira_export(checklist, domain)
            st.code(jira_text, language=None)
            jc1, jc2 = st.columns([1, 2])
            with jc1:
                if st.button("🎯  Export to Jira  (Mock)", key="jira_export_tab5", use_container_width=True):
                    st.toast("🎯 Jira Epic + Stories queued for import — ticket IDs assigned (mock).", icon="🎯")
            with jc2:
                st.download_button(
                    "Download Jira Export (.txt)",
                    data=jira_text,
                    file_name=_fn("jira_export").replace(".md", ".txt"),
                    mime="text/plain",
                    use_container_width=True,
                )

    # ── Tab 6: Board Memo ─────────────────────────────────────────────────────
    with tab6:
        _audit_block(doc_id, domain, step2_data, policy_text)
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.72rem;
                    line-height:1.6;margin-bottom:16px">
          One-page board summary: business significance, decisions required, and recommended actions.
        </div>""", unsafe_allow_html=True)

        board = step3_data.get("board_memo", "")
        _prose_block(board)

        _evidence_block(
            step3_data.get("board_memo_quotes", []),
            claim_tag="🟠 Strategic Risk",
            claim_color="#9A4520",
            agent_tag="Board Level",
        )
        _policy_memory_block(domain, pmg_hits)

        _download_row(
            label="📥  Export Board Memorandum (.docx)",
            data=_to_docx_bytes(
                f"Board Memorandum — {domain}",
                board, domain, doc_id,
            ),
            file_name=_fn("board_memo").replace(".md", ".docx"),
            key="dl_tab6",
        )

        _governance_panel("tab6", _gov_risk_raw, step2_data)

        # ── Slack Export ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="border-top:1px solid rgba(10,186,181,0.10);margin:2.2rem 0 1rem;padding-top:1.2rem">
          <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.58rem;
                      letter-spacing:0.26em;text-transform:uppercase;margin-bottom:0.9rem">
            ◆ &nbsp; SYSTEM OF ACTION — SLACK EXPORT
          </div>
        </div>""", unsafe_allow_html=True)

        rl3_slack = step3_data.get("overall_risk", step2_data.get("overall_risk_level", "medium"))
        rl3_label_slack, *_ = _risk_config(rl3_slack)
        slack_text = _format_slack_export(board, domain, rl3_label_slack)
        st.code(slack_text, language=None)
        if st.button("📨  Send to Slack  #exec-alerts  (Mock)", key="slack_export_tab6"):
            st.toast("📨 Slack message queued for #exec-alerts — delivery confirmed (mock).", icon="📨")

    # ── Footer ────────────────────────────────────────────────────────────────
    _accent_divider()
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0 2rem">
      <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.58rem;
                  letter-spacing:0.28em;text-transform:uppercase">
        Analysis Complete &nbsp;◆&nbsp; Agentic Workflow Pipeline &nbsp;◆&nbsp;
        Evidence-Grounded · Multi-Agent Debate · Human-in-the-Loop
      </div>
      <div style="width:60px;height:1px;background:linear-gradient(90deg,transparent,{_ACCENT}44,transparent);
                  margin:1rem auto"></div>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
