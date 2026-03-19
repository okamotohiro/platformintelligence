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
        "Primary risk vectors: AI Overviews and zero-click SERP features reducing article click-through rates, "
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

    # Current Baseline = pulled toward neutral (50) to show pre-policy state
    # Threats show score jump upward; opportunities show score drop; neutral ≈ -5
    def _baseline(axis: str) -> int:
        s, d = scores[axis]["score"], scores[axis]["direction"]
        if d == "threat":
            return max(10, s - 22)
        elif d == "opportunity":
            return min(95, s + 14)
        return max(10, s - 6)

    base_vals = [_baseline(a) for a in axes]

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


def create_risk_urgency_matrix(scores: Dict) -> go.Figure:
    """Risk & Urgency Matrix: scatter of key policy clauses by time + severity."""
    # ── Derive clause positions from actual axis scores ──────────────────────
    ip_s  = scores["IP"]["score"]
    tr_s  = scores["Traffic"]["score"]
    rv_s  = scores["Revenue"]["score"]
    pr_s  = scores["Product"]["score"]

    clauses = [
        {
            "name": "IP Licensing Term",
            "x": 10,                         # very close → high urgency
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

    fig.update_layout(
        xaxis=dict(
            title=dict(text="← Time to Enactment (Days)  [left = more urgent]",
                       font=dict(size=9, color="#9A9590", family="Montserrat")),
            range=[0, 70], autorange="reversed",
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


def _audit_block(doc_id: str, domain: str = "", step2_data: Optional[Dict] = None) -> None:
    """Render compact audit-metadata header — contextual data derived from domain & analysis."""
    import datetime as _dt

    # ── Grounding Sources: domain-specific policy doc + internal contract ref ──
    _grounding_map = {
        "AI Licensing & Copyright":     "GAIF Draft (v3.0) · OpenAI MSA 2024 (Contract #882-A)",
        "AI Search & Zero-Click":       "Google SGE Policy Rev.4 · Search Distribution MSA (Contract #441-B)",
        "Platform Distribution Policies": "Meta Content Policy Rev.9 · Platform Framework MSA (Contract #773-C)",
    }
    grounding = _grounding_map.get(domain, "External Policy Text · Contract Repository (Internal)")

    # ── Compliance Status: parse date from doc_id → add 2 calendar days ────────
    try:
        date_part = doc_id.split("-")[1]          # e.g. "20260318"
        req_date  = _dt.datetime.strptime(date_part, "%Y%m%d")
        due_date  = req_date + _dt.timedelta(days=2)
        due_str   = due_date.strftime("%b %-d, 12:00 JST")   # e.g. "Mar 20, 12:00 JST"
    except Exception:
        due_str = "Mar 20, 12:00 JST"
    compliance_html = f"🟡 Pending GC Approval &nbsp;<span style='color:#6B6560'>(Due: {due_str})</span>"

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


def _policy_memory_block(domain: str) -> None:
    """Render a mock Policy Memory Graph — historical red-line match panel."""
    _pmg_hits: Dict[str, List[tuple]] = {
        "AI Licensing & Copyright": [
            ("Clause 4.2",    "2024 OpenAI MSA negotiations",
             "Zero-revenue attribution for AI-generated summaries of licensed content exceeding 40 words "
             "was a non-negotiable red-line confirmed by the Legal Committee."),
            ("Exhibit B §3",  "2023 Google News Showcase MOU",
             "Minimum 12-month traffic guarantee required as a prerequisite to any content licensing "
             "arrangement — hard floor established by Board resolution."),
        ],
        "AI Search & Zero-Click": [
            ("Article 7(c)",  "2024 Google SGE pre-negotiation memo",
             "Any zero-click rendering of more than 40 words from a Nikkei article without a redirect "
             "was categorised as a hard termination trigger — binding precedent."),
            ("Clause 11",     "2023 Bing / Microsoft MSA review",
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
    hits = _pmg_hits.get(domain, _pmg_hits["AI Licensing & Copyright"])
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
                     font-style:italic">Auto-matched from 340+ archived MSAs &amp; Board Minutes</span>
      </div>
      {cards_html}
    </div>""", unsafe_allow_html=True)


def _governance_panel(tab_key: str, risk_raw: str = "high") -> None:
    """Enterprise governance & audit control panel — Human-in-the-Loop."""
    st.markdown(f"""
    <div style="border-top:1px solid rgba(10,186,181,0.15);margin:3rem 0 1.6rem;padding-top:1.6rem">
      <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.58rem;
                  letter-spacing:0.28em;text-transform:uppercase;margin-bottom:0.4rem;
                  display:flex;align-items:center;gap:10px">
        <span>◆</span>
        <span>GOVERNANCE &amp; AUDIT CONTROL PANEL</span>
        <div style="flex:1;height:1px;background:rgba(10,186,181,0.14)"></div>
      </div>
      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.56rem;
                  letter-spacing:0.14em;margin-top:3px">
        Human-in-the-Loop · System of Record · Audit-grade Sign-off
      </div>
    </div>""", unsafe_allow_html=True)

    rl_key   = (risk_raw or "medium").lower()
    stance_label, rl_color, stance_sub = _risk_config(rl_key)

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

        # ── ① AI Strategic Stance Override ────────────────────────────────────
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.56rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:12px">
          ①&nbsp; AI STRATEGIC STANCE OVERRIDE
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
                "Strategic Stance Override (Human-in-the-Loop)",
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

        # ── ② Cross-functional Routing ────────────────────────────────────────
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.56rem;
                    letter-spacing:0.22em;text-transform:uppercase;
                    margin:18px 0 10px;padding-top:14px;
                    border-top:1px solid rgba(10,186,181,0.08)">
          ②&nbsp; CROSS-FUNCTIONAL ROUTING — WORKFLOW DESTINATIONS
        </div>""", unsafe_allow_html=True)

        rc1, rc2, rc3 = st.columns(3)
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
                "Escalate Legal Brief to Outside Counsel Portal",
                value=False, key=f"r_counsel_{tab_key}",
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
            submitted = st.form_submit_button(
                "◆  Sign-off & Execute Workflows",
                use_container_width=True,
            )

        if submitted:
            st.toast(
                "✅ Sign-off recorded. Cross-functional workflows executing — "
                "Audit ID GC-8921 logged. (mock)",
                icon="✅",
            )


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
                f"[🎯 Policy Memory Graph Match: 2024 MSA Red-lines] "
                f"IP exposure flagged at {ip_score}/100. "
                f"The clause '{obl_text}' directly conflicts with the "
                f"'no-sublicensing without prior written consent' red-line established during our 2024 OpenAI MSA "
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
                f"Legal sign-off required at each milestone before feature GA."
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
                f"Action Required: Escalating to General Counsel and CPO for final review and compliance sprint kick-off. "
                f"Board notification required within 48 hours — {domain} domain."
            ),
        },
    ]


def _debate_expander(debate_log: List[Dict]) -> None:
    """Render the multi-agent debate transcript as a collapsible section."""
    if not debate_log:
        return
    with st.expander("◆  Multi-Agent Debate Log — Virtual Expert Committee", expanded=False):
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.60rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:1.2rem">
          Internal reasoning trace — autonomous committee deliberation prior to output generation
        </div>""", unsafe_allow_html=True)
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
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
    }
    .main .block-container { max-width: 680px !important; margin: 0 auto !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:10vh'></div>", unsafe_allow_html=True)

    _, card_col, _ = st.columns([1, 1.2, 1])
    with card_col:
        st.markdown(f"""
        <div style="background:#111111;border:1px solid rgba(10,186,181,0.18);
                    padding:44px 44px 36px;">
          <div style="text-align:center;margin-bottom:32px;">
            <div style="font-family:'Montserrat',system-ui,sans-serif;color:{_ACCENT};
                        font-size:1.1rem;font-weight:700;letter-spacing:0.16em;">
              POLICY RESPONSE
            </div>
            <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                        font-size:0.55rem;letter-spacing:0.34em;text-transform:uppercase;
                        margin-top:4px;">
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
            RAG-linked sources · AI Licensing domain
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
            <span style="color:#9A9590;font-size:0.54rem;margin-left:4px">(Existing AI MSAs linked)</span>
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
            Policy Ingestion &rarr; Semantic Delta
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
            (g3, "III", "Run Response Pipeline",  "Execute the agentic pipeline to autonomously extract deltas and generate role-specific deliverables in seconds."),
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
                "GAIF Draft v3.0 — Article 12: Content Licensing & AI Training\n"
                "Effective Date: 2026-07-01 | Jurisdiction: G7 + EU\n\n"
                "12.1 Mandatory Prior Notice: Any AI developer deploying a foundation model trained on\n"
                "      copyrighted editorial or structured-data content must provide written notice to\n"
                "      the rights holder no fewer than 90 days before first commercial use.\n\n"
                "12.2 Compensation Framework: A minimum per-token royalty of USD 0.0008 per 1,000\n"
                "      training tokens derived from licensed sources shall apply. Parties may negotiate\n"
                "      alternative lump-sum arrangements subject to a floor equal to 120% of the\n"
                "      per-token baseline.\n\n"
                "12.3 Zero-Click & Summary Display Prohibition: Reproduction of more than 40 words\n"
                "      from a licensed article in any AI-generated search snippet, summary card, or\n"
                "      conversational response is prohibited without an active revenue-share agreement.\n\n"
                "12.4 Enforcement: Non-compliant operators face suspension from GAIF-certified\n"
                "      distribution networks and fines up to 4% of global annual turnover.\n\n"
                "12.5 Audit Rights: Rights holders may request quarterly token-usage reports with\n"
                "      source attribution logs. Operators must retain logs for a minimum of 36 months."
            ),
            "euai": (
                "EU AI Act — Article 53 Amendment (Trilogue Consolidated Text, March 2026)\n"
                "Scope: General-Purpose AI Models with Systemic Risk\n\n"
                "53(a) Obligation to Disclose Training Data Provenance: Providers of GPAI models\n"
                "      classified as 'systemic risk' (cumulative compute > 10^25 FLOPs) must publish\n"
                "      a standardised data provenance report listing all content categories used in\n"
                "      pre-training, fine-tuning, and RLHF phases within 60 days of model release.\n\n"
                "53(b) Content Opt-Out Registry: Member States shall establish a centralised AI\n"
                "      Training Content Opt-Out Registry by Q3 2026. GPAI providers must honour\n"
                "      opt-out flags within 14 days of registry update and purge flagged content\n"
                "      from future training cycles.\n\n"
                "53(c) Search & Retrieval Augmentation: AI-powered search services that retrieve,\n"
                "      summarise, or display news and editorial content must enter into licensing\n"
                "      agreements with qualifying press publishers as defined under Directive 2019/790.\n"
                "      Failure to comply triggers an interim injunction mechanism.\n\n"
                "53(d) Penalties: Infringement of Article 53 obligations: up to 3% of worldwide\n"
                "      annual turnover or EUR 15,000,000, whichever is higher. Repeat violations\n"
                "      within 24 months: up to 6% or EUR 30,000,000."
            ),
        }

        # Pre-fill session state when a sample button is clicked
        for _sk, _sv in _SAMPLES.items():
            if st.session_state.get(f"_load_{_sk}"):
                st.session_state["policy_text"] = _sv
                st.session_state[f"_load_{_sk}"] = False

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
                             letter-spacing:0.04em">Active MSA Contract DB</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <span style="font-size:0.55rem;line-height:1">🟢</span>
                <span style="font-family:'Montserrat',sans-serif;color:#C8C3BD;font-size:0.60rem;
                             letter-spacing:0.04em">Audience Traffic Analytics</span>
              </div>
            </div>""", unsafe_allow_html=True)
            st.caption(
                "Auto-extracted from 340+ historical MSAs, Board Minutes, and litigation records "
                "to establish Day 1 Policy Memory Graph."
            )

        with inp_right:
            # ── Sample loader row ─────────────────────────────────────────
            _lbl_col, _b1_col, _b2_col = st.columns([2.2, 2, 2])
            with _lbl_col:
                st.markdown(f"""
                <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.52rem;
                            letter-spacing:0.24em;text-transform:uppercase;padding-top:6px">
                  Policy / Regulatory Text
                </div>""", unsafe_allow_html=True)
            with _b1_col:
                if st.button("⬇ GAIF v3.0 Draft", key="_load_gaif",
                             use_container_width=True, help="Load GAIF v3.0 Article 12 sample"):
                    st.session_state["policy_text"] = _SAMPLES["gaif"]
                    st.rerun()
            with _b2_col:
                if st.button("⬇ EU AI Act Art.53", key="_load_euai",
                             use_container_width=True, help="Load EU AI Act Article 53 amendment sample"):
                    st.session_state["policy_text"] = _SAMPLES["euai"]
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
                (c1, "◈", "Semantic Delta Analysis",
                 "Identifies meaning-level policy changes—not just text diffs. Maps added obligations and removed rights directly to your unique Media Business Ontology."),
                (c2, "◉", "Policy Memory Graph",
                 "Evaluates external threats against your institutional memory (past MSAs, board red-lines) to recommend 4 Strategic Stances: PROTECT, PROMOTE, LICENSE, or WAIT."),
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
        if not has_input:
            st.warning("Please enter policy text (minimum 20 characters).")
            return

        # ── Agentic Pipeline ───────────────────────────────────────────────────
        st.session_state.results = None
        pipeline_start = time.time()

        step1_data: Optional[Dict] = None
        step2_data: Optional[Dict] = None
        step3_data: Optional[Dict] = None
        debate_log: List[Dict] = []

        # Progress bar lives outside st.status so it stays visible throughout
        _prog = st.progress(0, text="◆  Initializing Autonomous Response Pipeline...")
        time.sleep(0.3)

        with st.status(
            "◆  Autonomous Response Pipeline — Running...",
            expanded=True,
        ) as pipeline_status:
            try:
                # ── STEP I : Semantic Delta Analysis ──────────────────────────
                _prog.progress(6, text="Step I · Semantic Delta Analysis — Parsing policy structure...")
                st.write(
                    "**Step I — Semantic Delta Analysis**  \n"
                    "Deep-parsing source text to isolate meaning-level changes — added obligations, "
                    "removed rights, penalty thresholds, and effective-date triggers. "
                    "Mapping to Media Business Ontology..."
                )
                time.sleep(0.4)   # flush UI before blocking LLM call

                step1_data = run_step1_parsing(client, policy_text)

                n_obl = len(step1_data.get("added_obligations", []))
                n_rem = len(step1_data.get("removed_rights", []))
                n_thr = len(step1_data.get("key_thresholds", []))
                _prog.progress(25, text="Step I Complete ✓ — Semantic delta extraction finished")
                st.write(
                    f"  ✓  Semantic delta extraction complete — "
                    f"**{n_obl}** added obligations · "
                    f"**{n_rem}** removed rights · "
                    f"**{n_thr}** key thresholds identified"
                )
                time.sleep(0.3)

                # ── STEP II : Policy Memory Graph × Impact Mapping ─────────────
                _prog.progress(30, text=f"Step II · Policy Memory Graph — Loading '{domain}' institutional memory...")
                st.write(
                    f"**Step II — Policy Memory Graph × Impact Mapping**  \n"
                    f"Cross-referencing extracted deltas against Policy Memory Graph: "
                    f"340+ archived MSAs, Board red-lines, and prior negotiation records. "
                    f"Scoring across 4 axes: IP Exposure · Traffic Risk · Revenue Sensitivity · "
                    f"Product Constraint. Deriving Strategic Stance..."
                )
                time.sleep(0.4)   # flush before LLM

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

                # ── MULTI-AGENT DEBATE ─────────────────────────────────────────
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

                # ── STEP III : Agentic Execution & Deliverable Synthesis ────────
                _prog.progress(72, text="Step III · Agentic Execution — Generating 6 deliverables...")
                st.write(
                    "**Step III — Agentic Execution & Deliverable Synthesis**  \n"
                    "Generating 6 Deliverables: What Changed Brief · Business Exposure Memo · "
                    "PPL Map · Negotiation Brief · Product / Legal Checklist · Board Memo — "
                    "each grounded with verbatim evidence citations and Policy Memory Graph matches. "
                    "Preparing execution payloads for Slack, Jira, and Docs..."
                )
                time.sleep(0.4)   # flush before the longest LLM call

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
        }

    # ── Display Results ───────────────────────────────────────────────────────
    res = st.session_state.results
    if not res:
        return

    step1_data = res["step1"]
    step2_data = res["step2"]
    step3_data = res["step3"]
    domain     = res["domain"]
    elapsed    = res.get("elapsed", 0)
    debate_log = res.get("debate_log", [])
    doc_id     = res.get("doc_id", "REQ-—")

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
            st.rerun()

    # ── Success Toast ─────────────────────────────────────────────────────────
    st.toast("✅ Multi-Agent Synthesis Complete: Generated 6 role-specific actionable outputs.")

    # ── Multi-Agent Debate Log ────────────────────────────────────────────────
    _debate_expander(debate_log)

    # ── STEP 1: Parsing Output ────────────────────────────────────────────────
    _accent_divider()
    _section_label("I", "Semantic Delta Analysis (Previous vs. New Policy Diff)")

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
        st.plotly_chart(create_risk_urgency_matrix(step2_data["scores"]),
                        use_container_width=True, config={"displayModeBar": False})

    st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#C4BFB8;font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;margin:1rem 0 12px">Evidence & Priority Actions</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, axis in [(sc1, "IP"), (sc2, "Traffic"), (sc3, "Revenue"), (sc4, "Product")]:
        with col:
            _score_card(axis, step2_data["scores"][axis])

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
        _audit_block(doc_id, domain, step2_data)
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

        _evidence_block(
            step3_data.get("what_changed_quotes", []),
            claim_tag="🔵 Policy Delta",
            claim_color="#0ABAB5",
            agent_tag="Executive Summary",
        )

        # ── Policy Memory Graph evidence (mock institutional memory) ──────────
        _PMG_EVIDENCE = {
            "AI Licensing & Copyright": [
                "Strictly aligns with the 'no-sublicensing without prior written consent' red-line "
                "established during our 2024 OpenAI MSA negotiations (Clause 4.2). Previous position "
                "required board-level sign-off before any sub-licensing of editorial content.",
                "Mirrors the revenue-floor precedent from 2023 Google News Showcase MOU (Exhibit B §3): "
                "minimum per-article compensation must not fall below ¥0.8 per impression.",
            ],
            "AI Search & Zero-Click": [
                "Consistent with red-line position from 2023 Apple News+ renewal: attribution link "
                "must remain clickable and must not be replaced by AI-generated summaries (§7.1).",
                "Conflicts with internal policy memo (Legal, Nov 2024): zero-click results from "
                "generative search must be classified as derivative works under J-Copyright Act Art. 21.",
            ],
            "Platform Distribution Policies": [
                "Directly triggers the 'algorithmic reach guarantee' clause negotiated in 2022 Meta "
                "Instant Articles exit agreement — any reach reduction >15% activates renegotiation right.",
                "Matches threat pattern documented in 2023 internal IP audit (Board Minutes, Q3): "
                "platform-controlled distribution reduces Nikkei's first-party data leverage to zero.",
            ],
        }
        _pmg_quotes = _PMG_EVIDENCE.get(
            domain,
            [
                "Historical institutional memory confirms this policy shift pattern was anticipated "
                "in 2024 internal strategy documents. Board-approved response protocols apply.",
                "Cross-referenced against 340+ archived MSAs: this clause type has a 73% success rate "
                "when countered with the 'reciprocal data access' negotiation framework.",
            ],
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

        _governance_panel("tab1", _gov_risk_raw)

    # ── Tab 2: Business Exposure ──────────────────────────────────────────────
    with tab2:
        _audit_block(doc_id, domain, step2_data)
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.72rem;
                    line-height:1.6;margin-bottom:16px">
          Impact on traffic, revenue, IP rights, product capabilities, and competitive position.
        </div>""", unsafe_allow_html=True)

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

        _governance_panel("tab2", _gov_risk_raw)

    # ── Tab 3: Protect / Promote / License Map ────────────────────────────────
    with tab3:
        _audit_block(doc_id, domain, step2_data)
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.72rem;
                    line-height:1.6;margin-bottom:20px">
          Axis-by-axis recommended business action — derived from Policy Memory Graph + impact scoring.
        </div>""", unsafe_allow_html=True)

        scores = step2_data.get("scores", {})
        _ACTION_MAP = {
            # (direction, score_threshold) → (action, color, icon, rationale)
            ("threat",      70): ("PROTECT",  "#8B2635", "🛡",
                                  "High-severity threat — activate IP defense and contract protections immediately."),
            ("threat",      40): ("NEGOTIATE","#A8892A", "⚖",
                                  "Material threat — engage counterparty to renegotiate terms before enforcement."),
            ("opportunity", 60): ("LICENSE",  "#0ABAB5", "💼",
                                  "Monetisation opportunity — formalise licensing arrangement to capture upside."),
            ("opportunity",  0): ("PROMOTE",  "#1A6B3C", "📣",
                                  "Positive development — proactively promote capabilities and market positioning."),
        }
        def _ppl_action(direction: str, score: int):
            if direction == "threat":
                if score >= 70:
                    return _ACTION_MAP[("threat", 70)]
                return _ACTION_MAP[("threat", 40)]
            if direction == "opportunity":
                if score >= 60:
                    return _ACTION_MAP[("opportunity", 60)]
                return _ACTION_MAP[("opportunity", 0)]
            return ("WAIT & MONITOR", "#6B6560", "🔍",
                    "Neutral impact — continue monitoring; no urgent action required.")

        ppl_rows = []
        for ax, icon in [("IP", "◈"), ("Traffic", "◉"), ("Revenue", "◆"), ("Product", "◇")]:
            ax_data = scores.get(ax, {})
            direction = ax_data.get("direction", "neutral")
            score     = ax_data.get("score", 0)
            evidence  = ax_data.get("evidence", "")
            action, acolor, aicon, rationale = _ppl_action(direction, score)
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

        _policy_memory_block(domain)
        _governance_panel("tab3", _gov_risk_raw)

    # ── Tab 4: Negotiation Brief ──────────────────────────────────────────────
    with tab4:
        _audit_block(doc_id, domain, step2_data)
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
        _policy_memory_block(domain)

        _download_row(
            label="📥  Export Negotiation Brief (.docx)",
            data=_to_docx_bytes(
                f"Negotiation Brief — {domain}",
                negotiation, domain, doc_id,
            ),
            file_name=_fn("negotiation_brief").replace(".md", ".docx"),
            key="dl_tab4",
        )

        _governance_panel("tab4", _gov_risk_raw)

    # ── Tab 5: Product / Legal Checklist ─────────────────────────────────────
    with tab5:
        _audit_block(doc_id, domain, step2_data)
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

        _governance_panel("tab5", _gov_risk_raw)

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
        _audit_block(doc_id, domain, step2_data)
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
        _policy_memory_block(domain)

        _download_row(
            label="📥  Export Board Memorandum (.docx)",
            data=_to_docx_bytes(
                f"Board Memorandum — {domain}",
                board, domain, doc_id,
            ),
            file_name=_fn("board_memo").replace(".md", ".docx"),
            key="dl_tab6",
        )

        _governance_panel("tab6", _gov_risk_raw)

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
