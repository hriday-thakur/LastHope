"""
HTML Component helpers for LastHope's modern brutalist Swiss editorial UI.
All dynamic text is safely escaped using html.escape.
All HTML is stripped of leading indentation to prevent Streamlit from rendering code blocks.
"""

import html
from typing import List, Optional


def clean_html(s: str) -> str:
    """Minifies HTML into a single continuous string so Streamlit markdown parser never treats HTML as code blocks."""
    return "".join(line.strip() for line in s.splitlines())


def tag(text: str, variant: str = "ink") -> str:
    """
    Renders a square, brutalist status tag.
    Variants: 'ink', 'green', 'ochre', 'red', 'pencil', 'running'
    """
    safe_text = html.escape(str(text).upper())
    return clean_html(f'<span class="brutalist-tag tag-{variant}">{safe_text}</span>')


def stage_rail(current_stage: int, stages_done: List[bool]) -> str:
    """
    Renders a 5-cell bordered rail across the top reflecting pipeline status.
    current_stage: 1 to 5
    stages_done: list of 5 booleans [done1, done2, done3, done4, done5]
    """
    stages = [
        ("01", "INTAKE"),
        ("02", "NOTES"),
        ("03", "QUESTIONS"),
        ("04", "AUDIT"),
        ("05", "EXPORT"),
    ]

    cells_html = []
    for idx, (num, label) in enumerate(stages):
        stage_idx = idx + 1
        is_current = (stage_idx == current_stage)
        is_done = stages_done[idx] if idx < len(stages_done) else False

        if is_current:
            cell_class = "rail-cell current"
            status_badge = '<span class="rail-badge current">ACTIVE</span>'
        elif is_done:
            cell_class = "rail-cell done"
            status_badge = '<span class="rail-badge done">DONE</span>'
        else:
            cell_class = "rail-cell upcoming"
            status_badge = '<span class="rail-badge upcoming">PENDING</span>'

        cells_html.append(f"""<div class="{cell_class}"><div class="rail-num">{num}</div><div class="rail-meta"><span class="rail-label">{label}</span>{status_badge}</div></div>""")

    return clean_html(f'<div class="stage-rail">{"".join(cells_html)}</div>')


def stage_header(stage_num: str, kicker: str, title: str, purpose: str) -> str:
    """
    Renders the modern brutalist stage header with a giant numeral, kicker, and purpose line.
    """
    safe_num = html.escape(stage_num)
    safe_kicker = html.escape(kicker)
    safe_title = html.escape(title)
    safe_purpose = html.escape(purpose)

    return clean_html(f"""
<div class="stage-header">
<div class="stage-header-left">
<div class="stage-kicker">{safe_kicker}</div>
<h1 class="stage-title">{safe_title}</h1>
<p class="stage-purpose">{safe_purpose}</p>
</div>
<div class="stage-giant-numeral">{safe_num}</div>
</div>
""")


def margin_meta_card(items: List[tuple]) -> str:
    """
    Renders a narrow margin column meta card with key-value entries.
    items: list of (label, value) tuples
    """
    rows = []
    for label, val in items:
        safe_label = html.escape(str(label).upper())
        safe_val = html.escape(str(val))
        rows.append(f"""<div class="margin-meta-row"><span class="margin-meta-label">{safe_label}</span><span class="margin-meta-value">{safe_val}</span></div>""")
    return clean_html(f'<div class="margin-meta-card">{"".join(rows)}</div>')


def intake_receipt(filename: str, pages: int, words: int, chars: int) -> str:
    """
    Renders an intake receipt slip with dotted leaders.
    """
    safe_file = html.escape(filename)
    return clean_html(f"""
<div class="intake-receipt">
<div class="receipt-header">INTAKE RECEIPT — DOCUMENT VERIFIED</div>
<div class="receipt-row"><span class="receipt-label">SOURCE FILE</span><span class="receipt-dots"></span><span class="receipt-val">{safe_file}</span></div>
<div class="receipt-row"><span class="receipt-label">TOTAL PAGES</span><span class="receipt-dots"></span><span class="receipt-val">{pages}</span></div>
<div class="receipt-row"><span class="receipt-label">WORD COUNT</span><span class="receipt-dots"></span><span class="receipt-val">{words:,}</span></div>
<div class="receipt-row"><span class="receipt-label">CHARACTER COUNT</span><span class="receipt-dots"></span><span class="receipt-val">{chars:,}</span></div>
<div class="receipt-footer">STATUS: PARSED &amp; INDEXED WITH PAGE MARKERS</div>
</div>
""")


def pipeline_strip() -> str:
    """
    Renders the 5-cell informational pipeline strip explaining each stage.
    """
    steps = [
        ("01", "INTAKE", "PDF/TXT extraction with page-number preservation"),
        ("02", "NOTES", "Executive summary, definitions, formulas & gap detection"),
        ("03", "QUESTIONS", "Tiered MCQs, short answers & unspoilered keys"),
        ("04", "AUDIT", "Grounding check, arithmetic audit & verdict"),
        ("05", "EXPORT", "Downloadable complete study pack & individual sections"),
    ]

    cards = []
    for num, title, desc in steps:
        cards.append(f"""<div class="pipeline-card"><div class="pipeline-num">{num}</div><div class="pipeline-title">{title}</div><div class="pipeline-desc">{desc}</div></div>""")

    return clean_html(f'<div class="pipeline-strip">{"".join(cards)}</div>')


def verdict_board_header(verdict: str, supported: int, warnings: int, errors: int) -> str:
    """
    Renders the brutalist verdict board header with counts and proportional bar.
    """
    safe_verdict = html.escape(verdict.upper())

    total = max(1, supported + warnings + errors)
    pct_sup = int((supported / total) * 100)
    pct_warn = int((warnings / total) * 100)
    pct_err = 100 - pct_sup - pct_warn

    badge_class = "verdict-pass"
    if "NEEDS REVISION" in safe_verdict:
        badge_class = "verdict-fail"
    elif "WARNING" in safe_verdict:
        badge_class = "verdict-warn"

    return clean_html(f"""
<div class="verdict-board">
<div class="verdict-top-bar">
<div>
<span class="verdict-kicker">AUDIT ASSESSMENT RESULT</span>
<div class="verdict-title {badge_class}">{safe_verdict}</div>
</div>
<div class="verdict-stamp">OFFICIAL AUDIT</div>
</div>
<div class="verdict-metric-grid">
<div class="verdict-stat-box stat-green"><div class="stat-num">{supported}</div><div class="stat-label">VERIFIED CLAIMS</div></div>
<div class="verdict-stat-box stat-ochre"><div class="stat-num">{warnings}</div><div class="stat-label">WARNINGS / GAPS</div></div>
<div class="verdict-stat-box stat-red"><div class="stat-num">{errors}</div><div class="stat-label">ERRORS / UNSUPPORTED</div></div>
</div>
<div class="verdict-proportional-bar">
<div class="bar-segment bar-green" style="width: {pct_sup}%;"></div>
<div class="bar-segment bar-ochre" style="width: {pct_warn}%;"></div>
<div class="bar-segment bar-red" style="width: {pct_err}%;"></div>
</div>
<div class="verdict-disclaimer">
SYSTEM VERIFICATION. NOT AN INFALLIBLE GUARANTEE. ALWAYS CROSS-CHECK SOURCE SLIDES.
</div>
</div>
""")


def study_pack_docket(doc_name: str, has_notes: bool, has_questions: bool, has_audit: bool) -> str:
    """
    Renders the study pack docket panel with dotted leaders.
    """
    safe_name = html.escape(doc_name)

    def row_html(label: str, is_ready: bool, detail: str) -> str:
        status_tag = tag("READY", "green") if is_ready else tag("MISSING", "pencil")
        return f"""<div class="docket-row"><span class="docket-label">{label}</span><span class="docket-detail">({detail})</span><span class="docket-dots"></span><span class="docket-status">{status_tag}</span></div>"""

    rows = [
        row_html("PART I: REVISION NOTES", has_notes, "P1 Analysis"),
        row_html("PART II: PRACTICE QUESTIONS & ANSWER KEY", has_questions, "P2 Question Suite"),
        row_html("PART III: CONTENT VERIFICATION REPORT", has_audit, "P3 Quality Audit"),
    ]

    return clean_html(f"""
<div class="study-pack-docket">
<div class="docket-header">
<span>STUDY PACK DOCKET — {safe_name}</span>
<span>MANUAL DISPATCH</span>
</div>
<div class="docket-body">
{"".join(rows)}
</div>
<div class="docket-footer">
{'STATUS: COMPLETE BUNDLE READY' if (has_notes and has_questions) else 'STATUS: PARTIAL BUNDLE (COMPLETE PREVIOUS STEPS FOR FULL PACK)'}
</div>
</div>
""")


def empty_card(title: str, subtitle: str, is_dashed_pencil: bool = True) -> str:
    """Renders a brutalist empty-state card with zero code block risk."""
    border_style = "2px dashed var(--pencil)" if is_dashed_pencil else "2px dashed var(--rule)"
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    return clean_html(f"""
<div class="question-card" style="border: {border_style}; text-align: center; padding: 48px 24px; margin-top: 16px;">
<div style="font-family: var(--font-heading); font-size: 24px; color: var(--pencil); margin-bottom: 8px;">{safe_title}</div>
<div style="font-family: var(--font-mono); font-size: 12px; color: var(--graphite);">{safe_subtitle}</div>
</div>
""")


def section_label(text: str) -> str:
    """Renders a small uppercase mono section label."""
    safe_text = html.escape(text.upper())
    return clean_html(f"""
<div style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; letter-spacing: 0.1em; color: var(--graphite); margin-top: 16px; margin-bottom: 8px;">
{safe_text}
</div>
""")
