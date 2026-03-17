"""
Policy Intelligence Engine — Luxury Enterprise UI
Agentic Workflow PoC · Nikkei AI Strategy
"""

import streamlit as st
import anthropic
import json
import re
import os
import concurrent.futures

port = int(os.environ.get("PORT", 8080))
port_number = int(os.environ.get("PORT", 8080))
import plotly.graph_objects as go
from typing import Optional, Dict, Any, Tuple

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Policy Intelligence Engine",
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
    --text-sec:      #9A9590;
    --text-muted:    #504D48;
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
/* Apply sans-serif broadly, but NOT to bare `span` —
   Streamlit status/alert widgets use Material Symbols font
   via ligature text (e.g. "check") inside <span> elements.
   Overriding span globally breaks those icon ligatures. */
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

/* Explicitly restore Material Symbols icon font for status/notification widgets.
   Must come AFTER the broad rule above to win the specificity race. */
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

/* ── BUTTONS ────────────────────────────────── */
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

/* download button — outlined accent */
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
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 0.85rem 2rem !important;
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
/* Status label text (the div/p next to the icon) */
[data-testid="stStatusWidget"] p,
[data-testid="stStatusWidget"] div:not([class*="icon"]) {
    font-family: var(--sans) !important;
    font-size: 0.82rem !important;
    color: var(--text-sec) !important;
}
/* Prevent layout shift: give the icon container a stable width */
[data-testid="stStatusWidget"] > div > div:first-child {
    min-width: 1.5rem !important;
    display: inline-flex !important;
    align-items: center !important;
}

/* ── ALERTS ─────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 0 !important;
    font-family: var(--sans) !important;
    font-size: 0.83rem !important;
    background: var(--bg-card2) !important;
}

/* ── DIVIDER ────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--accent-border) !important;
    margin: 2rem 0 !important;
}

/* ── CAPTION ────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    font-family: var(--sans) !important;
}

/* ── JSON VIEWER ────────────────────────────── */
[data-testid="stJson"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--accent-border) !important;
    font-family: "SF Mono", "Monaco", monospace !important;
    font-size: 0.78rem !important;
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
    "AI Licensing": (
        "Partnership and licensing model development with generative AI operators "
        "(domestic and international LLM providers, AI startups). "
        "Pillars: fair valuation of training data supply with equitable revenue-share design, "
        "and data defense strategy (robots.txt enforcement, technical protection measures, legal defense). "
        "Core objective: licensing revenue maximization and strategic intellectual property protection."
    ),
    "News & Insights": (
        "Japan's leading digital subscription media business with a strong domestic base. "
        "Core strategy centers on combating zero-click search erosion (AI Overviews reducing article impressions), "
        "liquid content transformation (cross-format distribution: video, audio, text), "
        "and copyright enforcement with content licensing revenue optimization."
    ),
    "Decision-making": (
        "Enterprise generative AI agents for data analytics and executive decision support, "
        "regulatory compliance services on disclosure platforms (DPF), "
        "integrated risk management solutions, and ESG data business. "
        "Core strategy: B2B SaaS revenue model with regulatory compliance and risk governance."
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

# ─── JSON Schemas ─────────────────────────────────────────────────────────────
STEP1_SCHEMA = {
    "type": "object",
    "properties": {
        "added_obligations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    "description": {"type": "string"},
                },
                "required": ["item", "severity", "description"],
                "additionalProperties": False,
            },
        },
        "removed_rights": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    "description": {"type": "string"},
                },
                "required": ["item", "severity", "description"],
                "additionalProperties": False,
            },
        },
        "key_thresholds": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "value": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["item", "value", "description"],
                "additionalProperties": False,
            },
        },
        "context_summary": {"type": "string"},
    },
    "required": ["added_obligations", "removed_rights", "key_thresholds", "context_summary"],
    "additionalProperties": False,
}

STEP2_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "object",
            "properties": {
                axis: {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer"},
                        "direction": {
                            "type": "string",
                            "enum": ["threat", "opportunity", "neutral"],
                        },
                        "evidence": {"type": "string"},
                        "priority_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["score", "direction", "evidence", "priority_actions"],
                    "additionalProperties": False,
                }
                for axis in ["IP", "Traffic", "Revenue", "Product"]
            },
            "required": ["IP", "Traffic", "Revenue", "Product"],
            "additionalProperties": False,
        },
        "overall_risk_level": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"],
        },
        "executive_summary": {"type": "string"},
        "key_opportunities": {"type": "array", "items": {"type": "string"}},
        "key_threats": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "scores", "overall_risk_level", "executive_summary",
        "key_opportunities", "key_threats",
    ],
    "additionalProperties": False,
}

# ─── Pipeline Functions ───────────────────────────────────────────────────────
def _safe_json_parse(text: str) -> Dict:
    """Safely extract and parse JSON from LLM output.
    Strips ```json ... ``` or ``` ... ``` code fences and surrounding text before parsing.
    """
    # Prefer code fence extraction
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return json.loads(match.group(1).strip())
    # No code fence — extract from first { to last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])
    # Fallback: parse as-is (raises json.JSONDecodeError on failure)
    return json.loads(text.strip())


def get_client() -> Optional[anthropic.Anthropic]:
    api_key = os.environ.get("ANTHROPIC_API_KEY") or st.session_state.get("api_key", "")
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
        messages=[
            {
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
            }
        ],
    )
    raw = next(b.text for b in response.content if b.type == "text")
    return _safe_json_parse(raw)


def run_step2_impact_mapping(
    client: anthropic.Anthropic, step1_data: Dict, domain: str
) -> Dict:
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
        messages=[
            {
                "role": "user",
                "content": (
                    f"Evaluate the business impact for the '{domain}' domain.\n\n"
                    f"[Domain Profile]\n{DOMAIN_PROFILES[domain]}\n\n"
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
            }
        ],
    )
    raw = next(b.text for b in response.content if b.type == "text")
    return _safe_json_parse(raw)


def _build_draft_context(domain: str, step1_data: Dict, step2_data: Dict) -> str:
    scores = step2_data["scores"]
    return (
        f"[Policy/Regulatory Change Summary]\n{step1_data.get('context_summary', '')}\n\n"
        f"[Target Domain] {domain}\n{DOMAIN_PROFILES[domain]}\n\n"
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


_DOC_PROMPTS = {
    "board_memo": (
        "Draft a Board Memorandum for executive leadership.\n\n{context}\n\n"
        "[Required Sections]\n"
        "1. Executive Summary (3–5 lines)\n"
        "2. Impact on Business Objectives (with quantified figures and deadlines)\n"
        "3. Board-Level Decisions Required (in priority order)\n"
        "4. Recommended Actions (Immediate / Within 30 days / Within 90 days)\n"
        "5. Risk Scenarios (Worst Case / Base Case / Best Case)\n"
        "Format in Markdown. All content in professional business English."
    ),
    "strategic_actions": (
        "Draft a Strategic Action Plan for operational teams and partner organizations.\n\n{context}\n\n"
        "[Required Sections]\n"
        "1. Domain-Specific Priority Strategy (concrete measures tailored to the {domain} profile)\n"
        "2. Department-Level Action Plan (Editorial / Technology / Legal / Sales / AI Business)\n"
        "3. Partner Collaboration Strategy (specific Co-Build initiatives with AI Fund partners)\n"
        "4. KPIs and Success Metrics (quantitative targets)\n"
        "5. Timeline (Phase 1 → Phase 2 → Phase 3)\n"
        "6. Required Resources and Estimated Budget\n"
        "Format in Markdown. All content in professional business English."
    ),
    "legal_defense": (
        "Draft a Legal Defense and Negotiation Strategy document for engagement with AI operators and platform owners.\n\n{context}\n\n"
        "[Required Sections]\n"
        "1. Data Defense Framework (three-layer defense: technical / legal / contractual measures)\n"
        "2. Non-Negotiable Terms (absolute conditions listed as a numbered list)\n"
        "3. Acceptable Conditions (permissible terms with defined limits)\n"
        "4. Monitoring Framework (early detection of policy changes and violations)\n"
        "5. Legal Red Lines (conditions that justify litigation or breakdown of negotiations)\n"
        "6. Negotiation Scenario Playbook (Hardline / Compromise / Exit strategies)\n"
        "Format in Markdown. All content in professional business English."
    ),
}


def _generate_single_doc(
    client: anthropic.Anthropic, doc_type: str, domain: str,
    step1_data: Dict, step2_data: Dict,
) -> str:
    context = _build_draft_context(domain, step1_data, step2_data)
    prompt = _DOC_PROMPTS[doc_type].format(context=context, domain=domain)
    with client.messages.stream(
        model=MODEL, max_tokens=8192, system=STRATEGIST_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        final = stream.get_final_message()
    return next(b.text for b in final.content if b.type == "text")


def run_step3_parallel(
    client: anthropic.Anthropic, domain: str,
    step1_data: Dict, step2_data: Dict,
) -> Tuple[str, str, str]:
    results: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    def _gen(dt: str) -> None:
        try:
            results[dt] = _generate_single_doc(client, dt, domain, step1_data, step2_data)
        except Exception as exc:
            errors[dt] = str(exc)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        concurrent.futures.wait([ex.submit(_gen, dt) for dt in ["board_memo", "strategic_actions", "legal_defense"]])

    if errors:
        raise RuntimeError(f"Document generation errors: {errors}")
    return results["board_memo"], results["strategic_actions"], results["legal_defense"]


# ─── Chart Functions (Tiffany Blue palette) ───────────────────────────────────
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
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                tickfont=dict(size=9, color="#504D48", family="Montserrat"),
                gridcolor="rgba(10,186,181,0.08)",
                linecolor="rgba(10,186,181,0.06)",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#9A9590", family="Montserrat"),
                gridcolor="rgba(10,186,181,0.08)",
                linecolor="rgba(10,186,181,0.10)",
            ),
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
        yaxis=dict(range=[0, 120], tickfont=dict(size=9, color="#504D48"),
                   gridcolor="rgba(10,186,181,0.06)",
                   title="Impact Score  (0 – 100)",
                   title_font=dict(size=10, color="#504D48", family="Montserrat")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,17,17,0.9)",
        font=dict(color="#9A9590", family="Montserrat"),
        showlegend=False, margin=dict(l=50, r=20, t=15, b=40), height=300,
    )
    return fig


# ─── HTML Component Helpers ───────────────────────────────────────────────────
_ACCENT = "#0ABAB5"
_ACCENT_DARK = "#089590"

def _sev_color(sev: str) -> str:
    return {"high": "#8B2635", "medium": "#A8892A", "low": "#1A6B3C"}.get(sev, _ACCENT)


def _risk_config(level: str):
    return {
        "critical": ("CRITICAL", "#8B2635"),
        "high":     ("HIGH",     "#A8892A"),
        "medium":   ("MEDIUM",   "#8A7020"),
        "low":      ("LOW",      "#1A6B3C"),
    }.get(level, ("—", "#504D48"))


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
        <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.62rem;
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
      <div style="color:#504D48;font-family:'Montserrat',sans-serif;
                  font-size:0.76rem;line-height:1.6;margin-top:5px">
        {desc[:130]}{'…' if len(desc)>130 else ''}
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
                border-bottom:1px solid rgba(10,186,181,0.08);min-height:230px">
      <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                  font-size:1.5rem;margin-bottom:6px">{icons.get(axis,'◆')}</div>
      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;
                  font-size:0.60rem;letter-spacing:0.22em;text-transform:uppercase">{axis}</div>
      <div style="font-family:'Cormorant Garamond',serif;color:{lc};
                  font-size:3rem;font-weight:300;line-height:1;margin:6px 0 2px">{info['score']}</div>
      <div style="font-family:'Montserrat',sans-serif;color:{lc};
                  font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;
                  margin-bottom:10px">{d}</div>
      <div style="font-family:'Montserrat',sans-serif;color:#504D48;
                  font-size:0.74rem;line-height:1.6">
        {ev[:100]}{'…' if len(ev)>100 else ''}
      </div>
      {''.join(f'<div style="font-family:Montserrat,sans-serif;color:#9A9590;font-size:0.70rem;margin-top:5px;padding-left:8px;border-left:1px solid {_ACCENT}33">▸ {a[:55]}</div>' for a in acts)}
    </div>""", unsafe_allow_html=True)


def _col_header(label: str) -> None:
    st.markdown(f"""
    <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.62rem;
                letter-spacing:0.20em;text-transform:uppercase;margin-bottom:10px;
                border-bottom:1px solid rgba(10,186,181,0.10);padding-bottom:8px">
      {label}
    </div>""", unsafe_allow_html=True)


# ─── Login Screen ─────────────────────────────────────────────────────────────
_LOGIN_ID = "aifund"
_LOGIN_PW  = "nikkei2030"


def render_login() -> None:
    """Render the full-screen login gate. Returns only after st.stop()."""
    # Hide sidebar and its toggle completely while on the login screen
    st.markdown("""
    <style>
    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Vertical centering via top spacer
    st.markdown("<div style='height:10vh'></div>", unsafe_allow_html=True)

    _, card_col, _ = st.columns([1, 1.2, 1])
    with card_col:
        # ── Card header ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="background:#111111;border:1px solid rgba(10,186,181,0.18);
                    padding:44px 44px 36px;">

          <!-- wordmark -->
          <div style="text-align:center;margin-bottom:32px;">
            <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                        font-size:1.1rem;font-weight:300;letter-spacing:0.16em;">
              POLICY INTELLIGENCE
            </div>
            <div style="font-family:'Montserrat',sans-serif;color:#504D48;
                        font-size:0.55rem;letter-spacing:0.34em;text-transform:uppercase;
                        margin-top:4px;">
              ENTERPRISE · RESTRICTED ACCESS
            </div>
            <div style="width:48px;height:1px;
                        background:linear-gradient(90deg,transparent,{_ACCENT}88,transparent);
                        margin:16px auto 0;"></div>
          </div>
        """, unsafe_allow_html=True)

        # ── Form fields ───────────────────────────────────────────────────────
        # Custom labels (styled)
        st.markdown(f"""
          <div style="font-family:'Montserrat',sans-serif;color:#504D48;
                      font-size:0.60rem;letter-spacing:0.22em;text-transform:uppercase;
                      margin-bottom:6px;">Login ID</div>
        """, unsafe_allow_html=True)
        login_id = st.text_input(
            "login_id",
            placeholder="Enter your login ID",
            label_visibility="collapsed",
            key="login_id_input",
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
          <div style="font-family:'Montserrat',sans-serif;color:#504D48;
                      font-size:0.60rem;letter-spacing:0.22em;text-transform:uppercase;
                      margin-bottom:6px;">Password</div>
        """, unsafe_allow_html=True)
        password = st.text_input(
            "password",
            type="password",
            placeholder="Enter your password",
            label_visibility="collapsed",
            key="login_pw_input",
        )

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # ── Login button ──────────────────────────────────────────────────────
        login_btn = st.button(
            "◆  Login",
            use_container_width=True,
            key="login_btn",
        )

        # ── Auth logic ────────────────────────────────────────────────────────
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

        # Close card div
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Footer note ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;margin-top:20px;
                    font-family:'Montserrat',sans-serif;color:#504D48;
                    font-size:0.58rem;letter-spacing:0.14em;">
          Access restricted to authorized personnel only.
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ─── Main App ─────────────────────────────────────────────────────────────────
def main() -> None:
    # ── Authentication gate ───────────────────────────────────────────────────
    if not st.session_state.get("authenticated", False):
        render_login()
        # render_login() always calls st.stop(), so execution never reaches here

    # ── Session state init ────────────────────────────────────────────────────
    if "results" not in st.session_state:
        st.session_state.results = None

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # Wordmark
        st.markdown(f"""
        <div style="margin-bottom:2rem;">
          <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                      font-size:1.05rem;font-weight:300;letter-spacing:0.12em;">
            POLICY INTELLIGENCE
          </div>
          <div style="font-family:'Montserrat',sans-serif;color:#504D48;
                      font-size:0.58rem;letter-spacing:0.30em;text-transform:uppercase;
                      margin-top:2px">
            ENTERPRISE · CLAUDE claude-opus-4-6
          </div>
          <div style="height:1px;background:linear-gradient(90deg,{_ACCENT}33,transparent);
                      margin-top:12px"></div>
        </div>""", unsafe_allow_html=True)

        # API Key section
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.60rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:10px">
          ◆ Claude API Key
        </div>""", unsafe_allow_html=True)

        env_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if env_key:
            st.markdown(f"""
            <div style="background:#111111;border:1px solid rgba(26,107,60,0.35);
                        padding:10px 14px;margin-bottom:1rem;">
              <div style="font-family:'Montserrat',sans-serif;color:#1A6B3C;
                          font-size:0.60rem;letter-spacing:0.18em;text-transform:uppercase;
                          margin-bottom:3px">✓  Auto-configured from environment</div>
              <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.72rem;">
                sk-ant-···{env_key[-6:]}</div>
            </div>""", unsafe_allow_html=True)
        else:
            api_input = st.text_input(
                "API Key",
                type="password",
                placeholder="sk-ant-api03-...",
                help="Your API key from console.anthropic.com",
                label_visibility="collapsed",
            )
            if api_input:
                st.session_state["api_key"] = api_input
            if not st.session_state.get("api_key"):
                st.markdown(f"""
                <div style="font-family:'Montserrat',sans-serif;color:#8B2635;
                            font-size:0.68rem;margin-top:-6px;margin-bottom:8px">
                  Please enter your API key
                </div>""", unsafe_allow_html=True)

        st.markdown('<div style="height:1px;background:rgba(10,186,181,0.10);margin:1.4rem 0"></div>',
                    unsafe_allow_html=True)

        # Policy text
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.60rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:10px">
          ◆ Policy / Platform Event
        </div>""", unsafe_allow_html=True)

        policy_text = st.text_area(
            "policy_input",
            height=210,
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

        # Domain
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.60rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:10px">
          ◆ Target Domain Profile
        </div>""", unsafe_allow_html=True)

        domain = st.radio(
            "domain",
            options=list(DOMAIN_PROFILES.keys()),
            label_visibility="collapsed",
        )

        st.markdown('<div style="height:1px;background:rgba(10,186,181,0.10);margin:1.4rem 0"></div>',
                    unsafe_allow_html=True)

        has_input = bool(policy_text and policy_text.strip() and len(policy_text.strip()) >= 20)
        sidebar_btn = st.button(
            "◆  Run Translation Engine",
            use_container_width=True,
            disabled=not has_input,
        )
        if not has_input:
            st.markdown(f"""
            <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.65rem;
                        text-align:center;margin-top:4px;letter-spacing:0.06em">
              Enter policy text to enable analysis
            </div>""", unsafe_allow_html=True)

        # Pipeline info
        st.markdown('<div style="height:1px;background:rgba(10,186,181,0.08);margin:1.8rem 0 1.2rem"></div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.65rem;
                    line-height:2.0">
          <div style="color:{_ACCENT}55;letter-spacing:0.16em;font-size:0.58rem;margin-bottom:6px">
            AGENTIC PIPELINE
          </div>
          <div>I &nbsp; Parsing → Structured JSON</div>
          <div>II &nbsp; Impact Mapping → 4-Axis Score</div>
          <div>III &nbsp; Drafting → 3 Docs (parallel)</div>
          <div style="margin-top:10px;color:{_ACCENT}44;letter-spacing:0.12em;font-size:0.58rem">
            JSON Schema · Adaptive Thinking<br>Streaming · Prompt Chain
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Determine run trigger ─────────────────────────────────────────────────
    if not st.session_state.results:
        main_btn_clicked = False
    else:
        main_btn_clicked = False

    run_triggered = sidebar_btn

    # ── Welcome Screen ────────────────────────────────────────────────────────
    if not st.session_state.results and not run_triggered:
        # Hero
        st.markdown(f"""
        <div style="text-align:center;padding:4rem 2rem 2.5rem">
          <div style="font-family:'Montserrat',sans-serif;color:{_ACCENT};font-size:0.62rem;
                      letter-spacing:0.42em;text-transform:uppercase;margin-bottom:1.8rem">
            ◆ &nbsp; Agentic Workflow · Policy Intelligence &nbsp; ◆
          </div>
          <h1 style="font-family:'Cormorant Garamond',serif !important;
                     color:#F0EDE6 !important;font-size:3.4rem;font-weight:300;
                     letter-spacing:0.06em;margin:0 0 0.6rem;line-height:1.1">
            Policy Intelligence<br>
            <span style="color:{_ACCENT};font-style:italic">Engine</span>
          </h1>
          <div style="width:80px;height:1px;background:linear-gradient(90deg,transparent,{_ACCENT},transparent);
                      margin:1.4rem auto"></div>
          <p style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.78rem;
                    letter-spacing:0.14em;text-transform:uppercase;margin:0">
            External Change &nbsp;→&nbsp; Strategic Clarity
          </p>
        </div>""", unsafe_allow_html=True)

        # 3-Step Guide
        g1, g2, g3 = st.columns(3)
        for col, num, label, desc in [
            (g1, "I",   "Configure",  "Enter or confirm your Anthropic API key in the sidebar."),
            (g2, "II",  "Input",      "Paste the policy or platform update text and select your target business domain."),
            (g3, "III", "Execute",    "Click 'Run Translation Engine' to launch the 3-step agentic pipeline."),
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
                  <div style="font-family:'Montserrat',sans-serif;color:#504D48;
                              font-size:0.78rem;line-height:1.7">{desc}</div>
                </div>""", unsafe_allow_html=True)

        # Centered CTA button
        st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)
        _, center, _ = st.columns([1.5, 2, 1.5])
        with center:
            main_btn_clicked = st.button(
                "◆  Run Translation Engine",
                key="main_run",
                use_container_width=True,
                disabled=not has_input,
            )
            if not has_input:
                st.markdown(f"""
                <div style="font-family:'Montserrat',sans-serif;color:#504D48;
                            font-size:0.65rem;text-align:center;margin-top:6px;
                            letter-spacing:0.06em">
                  Enter policy text in the sidebar to begin
                </div>""", unsafe_allow_html=True)

        run_triggered = run_triggered or main_btn_clicked

        if not run_triggered:
            # Capability strip
            st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
            _accent_divider()
            c1, c2, c3 = st.columns(3)
            for col, icon, cap, sub in [
                (c1, "◈", "Structured Parsing",
                 "Decomposes policy text into Added Obligations · Removed Rights · Key Thresholds via JSON Schema mode"),
                (c2, "◉", "Quantified Impact",
                 "Scores IP · Traffic · Revenue · Product impact 0–100 with Adaptive Thinking"),
                (c3, "◆", "Parallel Drafting",
                 "Generates Board Memo · Strategic Actions · Legal & Defense in parallel (ThreadPoolExecutor + Streaming)"),
            ]:
                with col:
                    st.markdown(f"""
                    <div style="padding:0 8px">
                      <div style="font-family:'Cormorant Garamond',serif;color:{_ACCENT};
                                  font-size:1.4rem;margin-bottom:8px">{icon}</div>
                      <div style="font-family:'Montserrat',sans-serif;color:#9A9590;
                                  font-size:0.68rem;font-weight:600;letter-spacing:0.14em;
                                  text-transform:uppercase;margin-bottom:8px">{cap}</div>
                      <div style="font-family:'Montserrat',sans-serif;color:#504D48;
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
              <div style="font-family:'Montserrat',sans-serif;color:#504D48;
                          font-size:0.78rem;margin-top:4px">
                Please enter your Anthropic API key in the sidebar.
              </div>
            </div>""", unsafe_allow_html=True)
            return
        if not has_input:
            st.warning("Please enter policy text (minimum 20 characters).")
            return

        # ── Pipeline ─────────────────────────────────────────────────────────
        st.session_state.results = None

        step1_data: Optional[Dict] = None
        step2_data: Optional[Dict] = None

        # Step 1
        with st.status("I  ·  Parsing — Structured Data Extraction", expanded=True) as s1:
            st.write("Extracting obligations, removed rights, and key thresholds as structured JSON…")
            try:
                step1_data = run_step1_parsing(client, policy_text)
                s1.update(label="I  ·  Parsing  ✓  Complete", state="complete", expanded=False)
            except anthropic.AuthenticationError:
                s1.update(label="I  ·  Parsing  ✗  Authentication Error", state="error")
                st.error("Invalid API key. Please check your credentials.")
                return
            except anthropic.RateLimitError:
                s1.update(label="I  ·  Parsing  ✗  Rate Limit", state="error")
                st.error("Rate limit exceeded. Please wait a moment and try again.")
                return
            except Exception as exc:
                s1.update(label="I  ·  Parsing  ✗  Error", state="error")
                st.error(f"Step 1 Error: {exc}")
                return

        # Step 2
        with st.status(f"II  ·  Impact Mapping — {domain}", expanded=True) as s2:
            st.write(f"Scoring IP / Traffic / Revenue / Product impact against the '{domain}' domain profile…")
            try:
                step2_data = run_step2_impact_mapping(client, step1_data, domain)
                s2.update(label="II  ·  Impact Mapping  ✓  Complete", state="complete", expanded=False)
            except anthropic.AuthenticationError:
                s2.update(label="II  ·  Impact Mapping  ✗  Authentication Error", state="error")
                st.error("Invalid API key. Please check your credentials.")
                return
            except Exception as exc:
                s2.update(label="II  ·  Impact Mapping  ✗  Error", state="error")
                st.error(f"Step 2 Error: {exc}")
                return

        # Step 3
        with st.status("III  ·  Drafting — 3 Documents in Parallel", expanded=True) as s3:
            st.write("Generating Board Memo · Strategic Actions · Legal & Defense in parallel…")
            st.caption("Long-form document generation may take 1–3 minutes.")
            try:
                board_memo, strategic_actions, legal_defense = run_step3_parallel(
                    client, domain, step1_data, step2_data
                )
                s3.update(label="III  ·  Drafting  ✓  Complete", state="complete", expanded=False)
            except anthropic.AuthenticationError:
                s3.update(label="III  ·  Drafting  ✗  Authentication Error", state="error")
                st.error("Invalid API key. Please check your credentials.")
                return
            except Exception as exc:
                s3.update(label="III  ·  Drafting  ✗  Error", state="error")
                st.error(f"Step 3 Error: {exc}")
                return

        # Store results
        st.session_state.results = {
            "step1": step1_data,
            "step2": step2_data,
            "step3": {
                "board_memo": board_memo,
                "strategic_actions": strategic_actions,
                "legal_defense": legal_defense,
            },
            "domain": domain,
        }

    # ── Display Results ───────────────────────────────────────────────────────
    res = st.session_state.results
    if not res:
        return

    step1_data  = res["step1"]
    step2_data  = res["step2"]
    board_memo  = res["step3"]["board_memo"]
    strategic_actions = res["step3"]["strategic_actions"]
    legal_defense     = res["step3"]["legal_defense"]
    domain      = res["domain"]

    # Result header + new analysis button
    hcol1, hcol2 = st.columns([4, 1])
    with hcol1:
        st.markdown(f"""
        <div style="padding:1.5rem 0 0.5rem">
          <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.60rem;
                      letter-spacing:0.28em;text-transform:uppercase;margin-bottom:6px">
            Analysis Complete · {domain}
          </div>
          <div style="font-family:'Cormorant Garamond',serif;color:#F0EDE6;
                      font-size:1.6rem;font-weight:300;letter-spacing:0.04em">
            Strategic Intelligence Report
          </div>
        </div>""", unsafe_allow_html=True)
    with hcol2:
        if st.button("← New Analysis", key="clear"):
            st.session_state.results = None
            st.rerun()

    # ── STEP 1 RESULTS ────────────────────────────────────────────────────────
    _accent_divider()
    _section_label("I", "Structured Data Extraction — Parsing Output")

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
          <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.60rem;
                      letter-spacing:0.20em;text-transform:uppercase;margin-bottom:6px">Summary</div>
          <div style="font-family:'Montserrat',sans-serif;color:#9A9590;
                      font-size:0.82rem;line-height:1.7">
            {step1_data['context_summary']}
          </div>
        </div>""", unsafe_allow_html=True)

    # ── STEP 2 RESULTS ────────────────────────────────────────────────────────
    _accent_divider()
    _section_label("II", f"Impact Mapping — {domain}")

    # Risk banner
    rl = step2_data.get("overall_risk_level", "medium")
    rl_label, rl_color = _risk_config(rl)
    st.markdown(f"""
    <div style="background:#111111;border:1px solid {rl_color}55;
                padding:16px 22px;margin-bottom:1.5rem;
                display:flex;align-items:center;gap:20px">
      <div>
        <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.58rem;
                    letter-spacing:0.22em;text-transform:uppercase;margin-bottom:3px">Overall Risk</div>
        <div style="font-family:'Cormorant Garamond',serif;color:{rl_color};
                    font-size:1.6rem;font-weight:300;letter-spacing:0.08em">{rl_label}</div>
      </div>
      <div style="width:1px;height:40px;background:rgba(10,186,181,0.14)"></div>
      <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.80rem;
                  line-height:1.7;flex:1">
        {step2_data.get('executive_summary','')}
      </div>
    </div>""", unsafe_allow_html=True)

    # Charts
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#504D48;font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;margin-bottom:8px">Radar — Impact Map</div>', unsafe_allow_html=True)
        st.plotly_chart(create_radar_chart(step2_data["scores"]), use_container_width=True)
    with ch2:
        st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#504D48;font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;margin-bottom:8px">Bar — Score by Axis</div>', unsafe_allow_html=True)
        st.plotly_chart(create_bar_chart(step2_data["scores"]), use_container_width=True)

    # Score cards
    st.markdown(f'<div style="font-family:Montserrat,sans-serif;color:#504D48;font-size:0.60rem;letter-spacing:0.20em;text-transform:uppercase;margin:1rem 0 12px">Evidence & Priority Actions</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, axis in [(sc1, "IP"), (sc2, "Traffic"), (sc3, "Revenue"), (sc4, "Product")]:
        with col:
            _score_card(axis, step2_data["scores"][axis])

    # Opportunities / Threats
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

    # ── STEP 3 RESULTS ────────────────────────────────────────────────────────
    _accent_divider()
    _section_label("III", "Strategic Documents — Board Memo · Strategic Actions · Legal & Defense")

    tab1, tab2, tab3 = st.tabs([
        "Board Memo", "Strategic Actions", "Legal & Defense"
    ])

    def _fn(prefix: str) -> str:
        return f"{prefix}_{domain.replace(' ','_').replace('·','_')}.md"

    with tab1:
        st.markdown(board_memo)
        st.download_button("Download Board Memo (.md)", data=board_memo,
                           file_name=_fn("board_memo"), mime="text/markdown")

    with tab2:
        st.markdown(strategic_actions)
        st.download_button("Download Strategic Actions (.md)", data=strategic_actions,
                           file_name=_fn("strategic_actions"), mime="text/markdown")

    with tab3:
        st.markdown(legal_defense)
        st.download_button("Download Legal & Defense (.md)", data=legal_defense,
                           file_name=_fn("legal_defense"), mime="text/markdown")

    # Footer
    _accent_divider()
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0 2rem">
      <div style="font-family:'Montserrat',sans-serif;color:#504D48;font-size:0.58rem;
                  letter-spacing:0.28em;text-transform:uppercase">
        Analysis Complete &nbsp;◆&nbsp; 3-Step Prompt Chain &nbsp;◆&nbsp;
        JSON Schema Mode · Adaptive Thinking · Parallel Streaming
      </div>
      <div style="width:60px;height:1px;background:linear-gradient(90deg,transparent,{_ACCENT}44,transparent);
                  margin:1rem auto"></div>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
