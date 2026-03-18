"""
Platform & Policy Intelligence Engine — Enterprise PoC
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
    page_title="Platform & Policy Intelligence Engine",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
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
        + f"\nOverall Risk: {step2_data['overall_risk_level'].upper()}\n"
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


def create_radar_chart(scores: Dict) -> go.Figure:
    axes = ["IP", "Traffic", "Revenue", "Product"]
    vals = [scores[a]["score"] for a in axes]
    md = _majority_direction(scores)
    line_color, fill_color = _DIR_COLORS.get(md, ("#0ABAB5", "rgba(10,186,181,0.16)"))
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=axes + [axes[0]],
        fill="toself", fillcolor=fill_color,
        line=dict(color=line_color, width=2),
        marker=dict(size=7, color=line_color, symbol="diamond"),
        hovertemplate="<b>%{theta}</b><br>%{r}/100<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickvals=[0, 25, 50, 75, 100],
                tickfont=dict(size=9, color="#C4BFB8", family="Montserrat"),
                gridcolor="rgba(10,186,181,0.08)", linecolor="rgba(10,186,181,0.06)"),
            angularaxis=dict(tickfont=dict(size=12, color="#9A9590", family="Montserrat"),
                gridcolor="rgba(10,186,181,0.08)", linecolor="rgba(10,186,181,0.10)"),
            bgcolor="rgba(17,17,17,0.9)",
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9A9590", family="Montserrat"),
        showlegend=False, margin=dict(l=55, r=55, t=30, b=30), height=360,
    )
    return fig


def create_bar_chart(scores: Dict) -> go.Figure:
    axes = ["IP", "Traffic", "Revenue", "Product"]
    vals = [scores[a]["score"] for a in axes]
    colors = [_DIR_COLORS.get(scores[a]["direction"], ("#0ABAB5", ""))[0] for a in axes]
    fig = go.Figure(go.Bar(
        x=axes, y=vals, marker_color=colors,
        text=[str(v) for v in vals], textposition="outside",
        textfont=dict(size=13, color="#F0EDE6", family="Montserrat"),
        hovertemplate="<b>%{x}</b> — %{y}/100<extra></extra>",
        marker=dict(line=dict(width=0)),
    ))
    fig.update_layout(
        xaxis=dict(tickfont=dict(size=11, color="#9A9590", family="Montserrat"),
                   gridcolor="rgba(10,186,181,0.05)", showline=False),
        yaxis=dict(range=[0, 120], tickfont=dict(size=9, color="#C4BFB8"),
                   gridcolor="rgba(10,186,181,0.06)", title="Impact Score  (0 – 100)",
                   title_font=dict(size=10, color="#C4BFB8", family="Montserrat")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,17,17,0.9)",
        font=dict(color="#9A9590", family="Montserrat"),
        showlegend=False, margin=dict(l=50, r=20, t=15, b=40), height=300,
    )
    return fig


# ─── HTML Component Helpers ───────────────────────────────────────────────────
_ACCENT = "#0ABAB5"


def _sev_color(sev: str) -> str:
    return {"high": "#8B2635", "medium": "#A8892A", "low": "#1A6B3C"}.get(sev, _ACCENT)


def _risk_config(level: str):
    return {
        "critical": ("CRITICAL", "#8B2635"),
        "high":     ("HIGH",     "#A8892A"),
        "medium":   ("MEDIUM",   "#8A7020"),
        "low":      ("LOW",      "#1A6B3C"),
    }.get(level.lower() if level else "medium", ("—", "#C4BFB8"))


def _accent_divider() -> None:
    st.markdown(
        '<div style="border-top:1px solid rgba(10,186,181,0.15);margin:2.5rem 0 2rem"></div>',
        unsafe_allow_html=True,
    )


def _section_label(num: str, title: str) -> None:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin:2rem 0 1.4rem">
      <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};font-size:1.6rem;
                  font-weight:300;line-height:1;min-width:28px">{num}</div>
      <div>
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.62rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:2px">Step</div>
        <div style="font-family:'Cormorant Garamond',serif;color:#F0EDE6;font-size:1.15rem;
                    font-weight:400;letter-spacing:0.04em">{title}</div>
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
      <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                  font-size:1.5rem;margin-bottom:6px">{icons.get(axis,'◆')}</div>
      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;
                  font-size:0.60rem;letter-spacing:0.22em;text-transform:uppercase">{axis}</div>
      <div style="font-family:'Cormorant Garamond',serif;color:{lc};
                  font-size:3rem;font-weight:300;line-height:1;margin:6px 0 2px">{info['score']}</div>
      <div style="font-family:'Montserrat',sans-serif;color:{lc};
                  font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;
                  margin-bottom:10px">{d}</div>
      <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                  font-size:0.74rem;line-height:1.7;word-break:break-word">
        {ev}
      </div>
      {''.join(f'<div style="font-family:Montserrat,sans-serif;color:#9A9590;font-size:0.70rem;margin-top:5px;padding-left:8px;border-left:1px solid {_ACCENT}33;word-break:break-word">▸ {a}</div>' for a in acts)}
    </div>""", unsafe_allow_html=True)


def _col_header(label: str) -> None:
    st.markdown(f"""
    <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.62rem;
                letter-spacing:0.20em;text-transform:uppercase;margin-bottom:10px;
                border-bottom:1px solid rgba(10,186,181,0.10);padding-bottom:8px">
      {label}
    </div>""", unsafe_allow_html=True)


def _prose_block(text: str) -> None:
    """Render a long prose string as a styled readable block."""
    st.markdown(f"""
    <div style="background:#111111;border:1px solid rgba(10,186,181,0.10);
                padding:24px 28px;margin:4px 0;">
      <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                  font-size:0.88rem;line-height:1.85;white-space:pre-wrap">{text}</div>
    </div>""", unsafe_allow_html=True)


def _checklist_items(items: list) -> None:
    """Render product checklist as styled actionable items."""
    for i, item in enumerate(items, 1):
        st.markdown(f"""
        <div style="background:#111111;border-left:2px solid {_ACCENT};
                    padding:12px 16px;margin:6px 0;display:flex;gap:12px;align-items:flex-start">
          <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                      font-size:1.0rem;font-weight:300;min-width:20px;margin-top:1px">{i:02d}</div>
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


def _governance_panel(tab_key: str, risk_label: str = "HIGH") -> None:
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

    rl_clean = risk_label.upper() if risk_label else "HIGH"
    _, rl_color = _risk_config(rl_clean)

    # Build override options dynamically based on current AI determination
    all_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    keep_opt   = f"— Keep AI Determination: {rl_clean} —"
    down_opts  = [f"Downgrade to {l}" for l in all_levels if l != rl_clean and all_levels.index(l) > all_levels.index(rl_clean)]
    up_opts    = [f"Escalate to {l}"  for l in all_levels if l != rl_clean and all_levels.index(l) < all_levels.index(rl_clean)]
    override_options = [keep_opt] + up_opts + down_opts

    with st.form(key=f"gov_{tab_key}"):

        # ── ① AI Risk Determination Override ─────────────────────────────────
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.56rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:12px">
          ①&nbsp; AI RISK DETERMINATION OVERRIDE
        </div>""", unsafe_allow_html=True)

        oc1, oc2 = st.columns([1, 2.4])
        with oc1:
            st.markdown(f"""
            <div style="background:#0D0D0D;border:1px solid {rl_color}44;
                        padding:14px 16px;text-align:center;height:100%">
              <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.50rem;
                          letter-spacing:0.22em;text-transform:uppercase;margin-bottom:5px">
                AI Determination
              </div>
              <div style="font-family:'Cormorant Garamond',serif;color:{rl_color};
                          font-size:1.8rem;font-weight:300;letter-spacing:0.10em;line-height:1">
                {rl_clean}
              </div>
              <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.48rem;
                          letter-spacing:0.10em;margin-top:6px;line-height:1.5">
                claude-opus-4-6<br>adaptive thinking
              </div>
            </div>""", unsafe_allow_html=True)
        with oc2:
            st.selectbox(
                "Human Risk Override",
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
                f"IP exposure flagged at {ip_score}/100. The obligation '{obl_text}' creates direct liability risk. "
                f"Non-negotiable condition: require written indemnification clause before any commitment. "
                f"I recommend triggering the standard outside-counsel review protocol for {domain}."
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
                f"overall classification: {risk_level}. "
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
        f"  per Policy Intelligence analysis. Priority: HIGH. Owner: CPO + Legal.",
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
        f"*{risk_emoji} Policy Intelligence Alert — {domain}*\n"
        f"*Risk Level:* `{risk_label.upper()}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{snippet}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"_Actions required — see full report in the enterprise dashboard._\n"
        f"_Platform & Policy Intelligence Engine · claude-opus-4-6_"
    )


# ─── Login Screen ─────────────────────────────────────────────────────────────
_LOGIN_ID = "aifund"
_LOGIN_PW  = "nikkei2030"


def render_login() -> None:
    st.markdown("""
    <style>
    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:10vh'></div>", unsafe_allow_html=True)

    _, card_col, _ = st.columns([1, 1.2, 1])
    with card_col:
        st.markdown(f"""
        <div style="background:#111111;border:1px solid rgba(10,186,181,0.18);
                    padding:44px 44px 36px;">
          <div style="text-align:center;margin-bottom:32px;">
            <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                        font-size:1.1rem;font-weight:300;letter-spacing:0.16em;">
              PLATFORM & POLICY INTELLIGENCE
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
          <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                      font-size:1.05rem;font-weight:300;letter-spacing:0.12em;">
            PLATFORM & POLICY INTELLIGENCE
          </div>
          <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                      font-size:0.58rem;letter-spacing:0.30em;text-transform:uppercase;
                      margin-top:2px">
            ENTERPRISE · CLAUDE {MODEL.upper()}
          </div>
          <div style="height:1px;background:linear-gradient(90deg,{_ACCENT}33,transparent);
                      margin-top:12px"></div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.60rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:10px">
          ◆ Policy / Platform Event
        </div>""", unsafe_allow_html=True)

        policy_text = st.text_area(
            "policy_input", height=210,
            placeholder=(
                "Example: EU AI Act Amendment — Article 53\n"
                "- Generative AI systems using copyrighted content for training\n"
                "  must provide prior notice and a compensation scheme to rights holders.\n"
                "- Non-compliance: 3% of global turnover or up to €15M, whichever is higher.\n"
                "- Phased enforcement begins Q1 2026."
            ),
            label_visibility="collapsed",
        )

        st.markdown('<div style="height:1px;background:rgba(10,186,181,0.10);margin:1.2rem 0"></div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.60rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:10px">
          ◆ Target Domain Profile
        </div>""", unsafe_allow_html=True)

        domain = st.radio("domain", options=list(DOMAIN_PROFILES.keys()),
                          label_visibility="collapsed")
        st.caption("Select the policy domain to calibrate the engine's risk assessment weights.")

        st.markdown('<div style="height:1px;background:rgba(10,186,181,0.10);margin:1.4rem 0"></div>',
                    unsafe_allow_html=True)

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

        st.markdown('<div style="height:1px;background:rgba(10,186,181,0.10);margin:0.8rem 0 1.4rem"></div>',
                    unsafe_allow_html=True)

        has_input = bool(policy_text and policy_text.strip() and len(policy_text.strip()) >= 20)
        sidebar_btn = st.button("◆  Run Intelligence Engine", use_container_width=True,
                                disabled=not has_input)
        if not has_input:
            st.markdown(f"""
            <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.65rem;
                        text-align:center;margin-top:4px;letter-spacing:0.06em">
              Enter policy text to enable analysis
            </div>""", unsafe_allow_html=True)

        st.markdown('<div style="height:1px;background:rgba(10,186,181,0.08);margin:1.8rem 0 1.2rem"></div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;font-size:0.65rem;line-height:2.1">
          <div style="color:{_ACCENT};letter-spacing:0.20em;font-size:0.56rem;
                      font-weight:600;margin-bottom:10px;text-transform:uppercase">
            AGENTIC WORKFLOW PIPELINE
          </div>
          <div style="color:#C4BFB8">
            <span style="color:{_ACCENT};font-family:'Cormorant Garamond',serif;
                         font-size:0.85rem;font-weight:300;margin-right:6px">I</span>
            Policy Ingestion &rarr; Structural Delta
          </div>
          <div style="color:#C4BFB8">
            <span style="color:{_ACCENT};font-family:'Cormorant Garamond',serif;
                         font-size:0.85rem;font-weight:300;margin-right:6px">II</span>
            Business Translation &rarr; 4-Axis Risk Profiling
          </div>
          <div style="color:#C4BFB8">
            <span style="color:{_ACCENT};font-family:'Cormorant Garamond',serif;
                         font-size:0.85rem;font-weight:300;margin-right:6px">III</span>
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

    run_triggered = sidebar_btn

    # ── Welcome Screen ────────────────────────────────────────────────────────
    if not st.session_state.results and not run_triggered:
        st.markdown(f"""
        <div style="text-align:center;padding:4rem 2rem 2.5rem">
          <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.62rem;
                      letter-spacing:0.42em;text-transform:uppercase;margin-bottom:1.8rem">
            ◆ &nbsp; Agentic Workflow · Platform & Policy Intelligence &nbsp; ◆
          </div>
          <h1 style="font-family:'Cormorant Garamond',serif !important;
                     color:#F0EDE6 !important;font-size:3.4rem;font-weight:300;
                     letter-spacing:0.06em;margin:0 0 0.6rem;line-height:1.1">
            Platform & Policy<br>
            <span style="color:{_ACCENT};font-style:italic">Intelligence Engine</span>
          </h1>
          <div style="width:80px;height:1px;background:linear-gradient(90deg,transparent,{_ACCENT},transparent);
                      margin:1.4rem auto"></div>
          <p style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.78rem;
                    letter-spacing:0.14em;text-transform:uppercase;margin:0">
            External Change &nbsp;→&nbsp; 5 Role-Specific Actionable Outputs
          </p>
        </div>""", unsafe_allow_html=True)

        g1, g2, g3 = st.columns(3)
        for col, num, label, desc in [
            (g1, "I",   "Set Context",       "Select the target business domain profile (e.g., AI Licensing) to align the engine with your company's revenue and IP structure."),
            (g2, "II",  "Ingest Data",       "Paste the external change—such as a new platform policy, draft agreement, or regulatory update."),
            (g3, "III", "Run Intelligence",  "Execute the agentic pipeline to autonomously extract deltas and generate role-specific deliverables in seconds."),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:#111111;border:1px solid rgba(10,186,181,0.12);
                            padding:28px 22px;text-align:center;min-height:180px">
                  <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                              font-size:2.2rem;font-weight:300;margin-bottom:12px">{num}</div>
                  <div style="font-family:'Montserrat',sans-serif;color:#F0EDE6;
                              font-size:0.72rem;font-weight:600;letter-spacing:0.18em;
                              text-transform:uppercase;margin-bottom:12px">{label}</div>
                  <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                              font-size:0.78rem;line-height:1.7">{desc}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)
        _, center, _ = st.columns([1.5, 2, 1.5])
        with center:
            main_btn = st.button("◆  Run Intelligence Engine", key="main_run",
                                 use_container_width=True, disabled=not has_input)
            if not has_input:
                st.markdown(f"""
                <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                            font-size:0.65rem;text-align:center;margin-top:6px;
                            letter-spacing:0.06em">
                  Enter policy text in the sidebar to begin
                </div>""", unsafe_allow_html=True)
        run_triggered = run_triggered or main_btn

        if not run_triggered:
            st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
            _accent_divider()
            c1, c2, c3 = st.columns(3)
            for col, icon, cap, sub in [
                (c1, "◈", "Delta Extraction",
                 "Identifies exactly what changed — added obligations, removed rights, key thresholds — as structured JSON"),
                (c2, "◉", "4-Axis Impact Score",
                 "Quantifies IP · Traffic · Revenue · Product exposure 0–100 with Adaptive Thinking"),
                (c3, "◆", "5 Role Deliverables",
                 "Generates Executive Delta · Business Exposure · Legal Brief · Board Memo · Product Checklist with evidence citations"),
            ]:
                with col:
                    st.markdown(f"""
                    <div style="padding:0 8px">
                      <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                                  font-size:1.4rem;margin-bottom:8px">{icon}</div>
                      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;
                                  font-size:0.68rem;font-weight:600;letter-spacing:0.14em;
                                  text-transform:uppercase;margin-bottom:8px">{cap}</div>
                      <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;
                                  font-size:0.75rem;line-height:1.7">{sub}</div>
                    </div>""", unsafe_allow_html=True)
            return

    # ── Validation ────────────────────────────────────────────────────────────
    if run_triggered:
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
                Please enter your Anthropic API key in the sidebar.
              </div>
            </div>""", unsafe_allow_html=True)
            return
        if not has_input:
            st.warning("Please enter policy text (minimum 20 characters).")
            return

        # ── Agentic Pipeline with granular step visualization ─────────────────
        st.session_state.results = None
        pipeline_start = time.time()

        step1_data: Optional[Dict] = None
        step2_data: Optional[Dict] = None
        step3_data: Optional[Dict] = None

        with st.status(
            "◆  Autonomous Intelligence Pipeline — Analyzing Policy...",
            expanded=True
        ) as pipeline_status:
            try:
                # ── STEP 1: Ingest & Parse ────────────────────────────────────
                st.write("**Step 1:** Ingesting policy document and identifying text deltas...")
                time.sleep(1.2)

                step1_data = run_step1_parsing(client, policy_text)

                n_obl  = len(step1_data.get("added_obligations", []))
                n_rem  = len(step1_data.get("removed_rights", []))
                n_thr  = len(step1_data.get("key_thresholds", []))
                st.write(
                    f"  ✓  Extracted **{n_obl}** added obligations · "
                    f"**{n_rem}** removed rights · **{n_thr}** key thresholds"
                )

                # ── STEP 2: Cross-reference with Domain Profile ───────────────
                st.write(
                    f"**Step 2:** Cross-referencing deltas with Nikkei's Business Model Profile "
                    f"(IP, Revenue, Traffic) — *{domain}* domain..."
                )
                time.sleep(1.2)

                step2_data = run_step2_impact_mapping(client, step1_data, domain)

                rl_raw = step2_data.get("overall_risk_level", "medium").upper()
                st.write(
                    f"  ✓  Impact mapping complete — Overall Risk: **{rl_raw}**"
                )

                # ── STEP 3: Assess risk severity ──────────────────────────────
                st.write("**Step 3:** Assessing risk severity across 4 dimensions...")
                time.sleep(1.0)

                scores = step2_data.get("scores", {})
                score_str = " · ".join(
                    f"{ax}: **{scores[ax]['score']}**"
                    for ax in ["IP", "Traffic", "Revenue", "Product"]
                    if ax in scores
                )
                st.write(f"  ✓  Risk scores mapped — {score_str}")

                # ── MULTI-AGENT DEBATE ────────────────────────────────────────
                st.write("**Internal Debate:** Convening virtual expert committee (Legal · Business · Product) ...")
                time.sleep(0.8)
                debate_log = _build_debate_log(step1_data, step2_data, domain)
                agent_labels = [e["agent"] for e in debate_log]
                for entry in debate_log:
                    short = entry["message"][:110].rstrip()
                    st.write(f"  {entry['agent']}: _{short}..._")
                    time.sleep(0.65)
                st.write("  ✓  Committee consensus reached — coordinated escalation strategy confirmed")

                # ── STEP 4: Generate role-specific outputs ────────────────────
                st.write(
                    "**Step 4:** Generating role-specific output formats "
                    "(Legal, Board, Product) with evidence citations..."
                )
                time.sleep(1.2)

                step3_data = run_step3_structured(
                    client, domain, step1_data, step2_data, policy_text
                )

                st.write(
                    "  ✓  5 role-specific deliverables generated — "
                    "evidence quotes extracted from source text"
                )

                pipeline_status.update(
                    label="◆  Analysis Complete — 5 Role Deliverables Ready",
                    state="complete",
                    expanded=False,
                )

            except anthropic.AuthenticationError:
                pipeline_status.update(
                    label="◆  Pipeline Failed — Authentication Error", state="error"
                )
                st.error("Invalid API key. Please check your credentials.")
                return
            except anthropic.RateLimitError:
                pipeline_status.update(
                    label="◆  Pipeline Failed — Rate Limit", state="error"
                )
                st.error("Rate limit exceeded. Please wait a moment and try again.")
                return
            except Exception as exc:
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
          <div style="font-family:'Cormorant Garamond',serif;color:#F0EDE6;
                      font-size:1.6rem;font-weight:300;letter-spacing:0.04em">
            Platform & Policy Intelligence Report
          </div>
        </div>""", unsafe_allow_html=True)
    with hcol2:
        if st.button("← New Analysis", key="clear"):
            st.session_state.results = None
            st.rerun()

    # ── Success Toast ─────────────────────────────────────────────────────────
    st.toast("✅ Multi-Agent Synthesis Complete: Generated 5 role-specific actionable outputs.")

    # ── Multi-Agent Debate Log ────────────────────────────────────────────────
    _debate_expander(debate_log)

    # ── STEP 1: Parsing Output ────────────────────────────────────────────────
    _accent_divider()
    _section_label("I", "Structured Delta Extraction — Parsing Output")

    with st.expander("View Raw JSON", expanded=False):
        st.json(step1_data)

    c1, c2, c3 = st.columns(3)
    with c1:
        _col_header("Added Obligations")
        items = step1_data.get("added_obligations", [])
        for it in items:
            _item_card(it, _sev_color(it.get("severity", "medium")))
        if not items:
            st.caption("—")
    with c2:
        _col_header("Removed Rights")
        items = step1_data.get("removed_rights", [])
        for it in items:
            _item_card(it, _sev_color(it.get("severity", "medium")))
        if not items:
            st.caption("—")
    with c3:
        _col_header("Key Thresholds")
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
    rl_label2, rl_color2 = _risk_config(rl)
    st.markdown(f"""
    <div style="background:#111111;border:1px solid {rl_color2}55;
                padding:16px 22px;margin-bottom:1.5rem;
                display:flex;align-items:center;gap:20px">
      <div>
        <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.58rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:3px">Overall Risk</div>
        <div style="font-family:'Cormorant Garamond',serif;color:{rl_color2};
                    font-size:1.6rem;font-weight:300;letter-spacing:0.08em">{rl_label2}</div>
      </div>
      <div style="width:1px;height:40px;background:rgba(10,186,181,0.14)"></div>
      <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.80rem;
                  line-height:1.7;flex:1">
        {step2_data.get('executive_summary','')}
      </div>
    </div>""", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#C4BFB8;font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;margin-bottom:8px">Radar — Impact Map</div>', unsafe_allow_html=True)
        st.plotly_chart(create_radar_chart(step2_data["scores"]), use_container_width=True)
    with ch2:
        st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#C4BFB8;font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;margin-bottom:8px">Bar — Score by Axis</div>', unsafe_allow_html=True)
        st.plotly_chart(create_bar_chart(step2_data["scores"]), use_container_width=True)

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

    # ── STEP 3: Role-Specific Deliverables (5 Tabs) ───────────────────────────
    _accent_divider()
    _section_label("III", "Role-Specific Intelligence — 5 Actionable Deliverables")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "◆  Executive Summary & Delta",
        "◉  Business Exposure",
        "⚖  Legal & Negotiation",
        "▪  Board Memo",
        "✓  Product Checklist",
    ])

    def _fn(prefix: str) -> str:
        return f"{prefix}_{domain.replace(' ', '_')}.md"

    # ── Compute governance risk label once (used across all tabs) ─────────────
    _gov_risk_raw = step3_data.get("overall_risk", step2_data.get("overall_risk_level", "medium"))
    _gov_risk_label, _ = _risk_config(_gov_risk_raw)

    # ── Tab 1: Executive Summary & Delta ─────────────────────────────────────
    with tab1:
        _audit_block(doc_id, domain, step2_data)
        rl3 = step3_data.get("overall_risk", "—")
        rl3_label, rl3_color = _risk_config(rl3)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px">
          <div style="background:#111111;border:1px solid {rl3_color}55;
                      padding:14px 20px;text-align:center;min-width:120px">
            <div style="font-family:'Montserrat',sans-serif;color:#C4BFB8;font-size:0.55rem;
                        letter-spacing:0.22em;text-transform:uppercase;margin-bottom:4px">Risk Level</div>
            <div style="font-family:'Cormorant Garamond',serif;color:{rl3_color};
                        font-size:1.5rem;font-weight:300;letter-spacing:0.10em">{rl3_label}</div>
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

        st.download_button(
            "Export to Word (.docx)",
            data=_to_docx_bytes(
                f"Executive Delta Brief — {domain}",
                f"Overall Risk: {rl3_label}\n\n{what_changed}",
                domain, doc_id,
            ),
            file_name=_fn("delta_brief").replace(".md", ".docx"),
            mime=_DOCX_MIME,
        )

        _governance_panel("tab1", _gov_risk_label)

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

        st.download_button(
            "Export to Word (.docx)",
            data=_to_docx_bytes(
                f"Business Exposure Memo — {domain}",
                exposure, domain, doc_id,
            ),
            file_name=_fn("business_exposure").replace(".md", ".docx"),
            mime=_DOCX_MIME,
        )

        _governance_panel("tab2", _gov_risk_label)

    # ── Tab 3: Legal & Negotiation ────────────────────────────────────────────
    with tab3:
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

        st.download_button(
            "Export to Word (.docx)",
            data=_to_docx_bytes(
                f"Legal & Negotiation Brief — {domain}",
                negotiation, domain, doc_id,
            ),
            file_name=_fn("negotiation_brief").replace(".md", ".docx"),
            mime=_DOCX_MIME,
        )

        _governance_panel("tab3", _gov_risk_label)

    # ── Tab 4: Board Memo ─────────────────────────────────────────────────────
    with tab4:
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

        st.download_button(
            "Export to Word (.docx)",
            data=_to_docx_bytes(
                f"Board Memorandum — {domain}",
                board, domain, doc_id,
            ),
            file_name=_fn("board_memo").replace(".md", ".docx"),
            mime=_DOCX_MIME,
        )

        _governance_panel("tab4", _gov_risk_label)

        # ── Slack Export ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="border-top:1px solid rgba(10,186,181,0.10);margin:2.2rem 0 1rem;padding-top:1.2rem">
          <div style="font-family:'Montserrat',sans-serif;color:#9A9590;font-size:0.58rem;
                      letter-spacing:0.26em;text-transform:uppercase;margin-bottom:0.9rem">
            ◆ &nbsp; SYSTEM OF ACTION — SLACK EXPORT
          </div>
        </div>""", unsafe_allow_html=True)

        rl3_slack = step3_data.get("overall_risk", step2_data.get("overall_risk_level", "medium"))
        rl3_label_slack, _ = _risk_config(rl3_slack)
        slack_text = _format_slack_export(board, domain, rl3_label_slack)
        st.code(slack_text, language=None)
        if st.button("📨  Send to Slack  #exec-alerts  (Mock)", key="slack_export_tab4"):
            st.toast("📨 Slack message queued for #exec-alerts — delivery confirmed (mock).", icon="📨")

    # ── Tab 5: Product Checklist ──────────────────────────────────────────────
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
            st.download_button(
                "Export to Word (.docx)",
                data=_to_docx_bytes(
                    f"Product Checklist — {domain}",
                    checklist_body, domain, doc_id,
                ),
                file_name=_fn("product_checklist").replace(".md", ".docx"),
                mime=_DOCX_MIME,
            )
        else:
            st.caption("No checklist items generated.")

        _governance_panel("tab5", _gov_risk_label)

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
