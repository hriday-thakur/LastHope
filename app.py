"""
LastHope — Lecture-to-Revision System
Modern Brutalist / Swiss Editorial Edition ("Red Pen" Theme)
Orchestrates document parsing, revision notes (P1), practice questions (P2),
and content verification (P3) with session persistence and export capabilities.
"""

from datetime import datetime
import io
from pathlib import Path
import streamlit as st

from utils.document_parser import (
    parse_document,
    ParsedDocument,
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFormatError,
)
from utils.groq_client import (
    get_configured_model,
    GroqClientError,
    MissingAPIKeyError,
    AuthenticationError,
    ModelNotFoundError,
    RateLimitExceededError,
    NetworkConnectionError,
    APIRequestTimeoutError,
    OutputTruncatedError,
)
from prompts.lecture_analyzer import analyze_lecture
from prompts.question_generator import (
    generate_questions,
    MissingAnalysisError,
    IncompleteQuestionSetError,
)
from prompts.content_verifier import verify_content
from ui.theme import inject_css
from ui.components import (
    stage_rail,
    stage_header,
    margin_meta_card,
    intake_receipt,
    pipeline_strip,
    verdict_board_header,
    study_pack_docket,
    empty_card,
    section_label,
    clean_html,
)

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LastHope — Lecture-to-Revision System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Swiss Brutalist ("Red Pen") Theme CSS
inject_css()


# -----------------------------------------------------------------------------
# Session State Initialization (All existing keys strictly preserved)
# -----------------------------------------------------------------------------
def init_session_state():
    """Initializes persistent session state variables."""
    if "parsed_doc" not in st.session_state:
        st.session_state.parsed_doc = None
    if "file_name" not in st.session_state:
        st.session_state.file_name = None
    if "file_hash" not in st.session_state:
        st.session_state.file_hash = None
    if "p1_analysis" not in st.session_state:
        st.session_state.p1_analysis = None
    if "p2_questions" not in st.session_state:
        st.session_state.p2_questions = None
    if "p3_verification" not in st.session_state:
        st.session_state.p3_verification = None

    # UI-only state keys (prefixed with ui_)
    if "ui_exam_mode" not in st.session_state:
        st.session_state.ui_exam_mode = False
    if "ui_verdict_filter" not in st.session_state:
        st.session_state.ui_verdict_filter = "ALL FINDINGS"


init_session_state()

# Pipeline completion flags
doc_loaded = st.session_state.parsed_doc is not None
p1_done = st.session_state.p1_analysis is not None
p2_done = st.session_state.p2_questions is not None
p3_done = st.session_state.p3_verification is not None
export_ready = p1_done or p2_done

stages_done = [doc_loaded, p1_done, p2_done, p3_done, export_ready]


# -----------------------------------------------------------------------------
# Sidebar: System Status & Pipeline Progress
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(clean_html("""<div style="padding: 8px 0 16px 0;">
<div style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; letter-spacing: 0.12em; color: var(--red);">REVISION ENGINE</div>
<div style="font-family: var(--font-heading); font-size: 32px; font-weight: 900; line-height: 0.95; margin-top: 4px;">LAST<span style="color: var(--red);">.</span>HOPE</div>
<div style="font-family: var(--font-mono); font-size: 11px; color: var(--graphite); margin-top: 6px;">SWISS BRUTALIST V2.0</div>
</div>"""), unsafe_allow_html=True)
    st.divider()

    st.subheader("⚙️ System Status")
    try:
        configured_model = get_configured_model()
        st.markdown(f"**Model Engine:** `{configured_model}`")
    except Exception:
        configured_model = "Unknown"
        st.warning("Model configuration not found in `.env`")

    st.caption("Credentials loaded securely via local `.env`")
    st.divider()

    st.subheader("📋 Pipeline Ledger")
    st.markdown(f"{'✅' if doc_loaded else '⬜'} **STAGE 01:** Document Intake")
    st.markdown(f"{'✅' if p1_done else '⬜'} **STAGE 02:** Revision Notes")
    st.markdown(f"{'✅' if p2_done else '⬜'} **STAGE 03:** Practice Questions")
    st.markdown(f"{'✅' if p3_done else '⬜'} **STAGE 04:** Content Verification")
    st.markdown(f"{'✅' if export_ready else '⬜'} **STAGE 05:** Export Docket")

    if doc_loaded:
        st.divider()
        st.subheader("📄 Active Document")
        st.markdown(f"**File:** `{st.session_state.file_name}`")
        st.markdown(f"**Pages:** `{st.session_state.parsed_doc.total_pages}`")
        st.markdown(f"**Words:** `{st.session_state.parsed_doc.word_count:,}`")

    st.divider()
    st.caption(
        "Academic Revision Productivity Tool.\n"
        "Cross-reference outputs with official course lecture slides."
    )


# -----------------------------------------------------------------------------
# Main Navigation Tabs Layout (Styled as Swiss Brutalist cells)
# -----------------------------------------------------------------------------
tab_upload, tab_analysis, tab_questions, tab_verify, tab_export = st.tabs([
    "01 INTAKE",
    "02 NOTES",
    "03 QUESTIONS",
    "04 AUDIT",
    "05 EXPORT",
])


# =============================================================================
# TAB 1: UPLOAD LECTURE (INTAKE)
# =============================================================================
with tab_upload:
    st.markdown(stage_rail(1, stages_done), unsafe_allow_html=True)
    st.markdown(
        stage_header("01", "STAGE 01 / 05 — INTAKE", "Lecture Document Intake", "Ingest PDF slide decks or plain text notes with page-number tracking."),
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([7, 5])

    with col_left:
        st.markdown(clean_html("""<div class="hero-wordmark-container">
<div class="hero-kicker">EXAM PREPARATION SYSTEM</div>
<h1 class="hero-wordmark">LAST<br>HOPE<span class="red-dot">.</span></h1>
<p class="hero-tagline">Lecture in. Revision pack out.</p>
<p style="font-family: var(--font-body); font-size: 15px; color: var(--graphite); line-height: 1.6; max-width: 52ch;">
Transform terse slides and messy lecture notes into comprehensive revision notes, 
tiered practice questions, and audited answer keys calibrated for high-yield exam preparation.
</p>
</div>"""), unsafe_allow_html=True)

    with col_right:
        st.markdown(clean_html("""<div class="brutalist-panel">
<div class="panel-header-strip">
<span>INTAKE FORM — PDF / TXT</span>
<span>SLOT A</span>
</div>
</div>"""), unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Select lecture slide deck or text notes",
            type=["pdf", "txt"],
            help="Supported formats: .pdf (PyMuPDF extraction) and .txt (multi-encoding).",
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            file_signature = f"{uploaded_file.name}_{len(file_bytes)}"

            if st.session_state.file_hash != file_signature:
                try:
                    with st.spinner("Extracting and indexing text with page tracking..."):
                        parsed_doc = parse_document(file_bytes, filename=uploaded_file.name)
                        st.session_state.parsed_doc = parsed_doc
                        st.session_state.file_name = uploaded_file.name
                        st.session_state.file_hash = file_signature
                        st.session_state.p1_analysis = None
                        st.session_state.p2_questions = None
                        st.session_state.p3_verification = None
                        st.success(f"DOCUMENT INGESTION VERIFIED: {uploaded_file.name}")
                except EmptyDocumentError as e:
                    st.session_state.parsed_doc = None
                    st.error(f"DOCUMENT EMPTY: {e}")
                except UnsupportedFormatError as e:
                    st.session_state.parsed_doc = None
                    st.error(f"UNSUPPORTED FORMAT: {e}")
                except DocumentParsingError as e:
                    st.session_state.parsed_doc = None
                    st.error(f"PARSING ERROR: {e}")
                except Exception as e:
                    st.session_state.parsed_doc = None
                    st.error(f"UNEXPECTED ERROR: {type(e).__name__} - {e}")

        if st.session_state.parsed_doc is not None:
            doc: ParsedDocument = st.session_state.parsed_doc
            st.markdown(
                intake_receipt(
                    st.session_state.file_name,
                    doc.total_pages,
                    doc.word_count,
                    doc.char_count,
                ),
                unsafe_allow_html=True,
            )

    # Document Preview and Pipeline Strip
    if st.session_state.parsed_doc is not None:
        doc: ParsedDocument = st.session_state.parsed_doc
        st.write("")
        with st.expander("🔍 INSPECT EXTRACTED SOURCE TEXT WITH PAGE DELIMITERS", expanded=False):
            preview_len = min(2000, len(doc.extracted_text))
            st.text_area(
                "Source Text Preview",
                doc.extracted_text[:preview_len] + ("\n\n... [TRUNCATED FOR PREVIEW]" if len(doc.extracted_text) > preview_len else ""),
                height=220,
                disabled=True,
            )

    st.markdown(pipeline_strip(), unsafe_allow_html=True)


# =============================================================================
# TAB 2: REVISION NOTES (P1)
# =============================================================================
with tab_analysis:
    st.markdown(stage_rail(2, stages_done), unsafe_allow_html=True)
    st.markdown(
        stage_header("02", "STAGE 02 / 05 — REVISION NOTES", "Lecture Content Analysis", "Extracts structured revision outlines, definitions, formulas & detected gaps."),
        unsafe_allow_html=True,
    )

    if st.session_state.parsed_doc is None:
        st.markdown(
            empty_card("NO DOCUMENT LOADED", "PLEASE COMPLETE STAGE 01 INTAKE FIRST TO PARSE LECTURE MATERIAL.", is_dashed_pencil=True),
            unsafe_allow_html=True,
        )
    else:
        col_meta, col_work = st.columns([3, 9])

        with col_meta:
            meta_items = [
                ("SOURCE", st.session_state.file_name),
                ("PAGES", st.session_state.parsed_doc.total_pages),
                ("WORDS", f"{st.session_state.parsed_doc.word_count:,}"),
                ("STAGE 02 STATUS", "COMPLETED" if p1_done else "READY TO GENERATE"),
            ]
            st.markdown(margin_meta_card(meta_items), unsafe_allow_html=True)

        with col_work:
            analyze_clicked = st.button("🔍 GENERATE REVISION NOTES →", type="primary")

            if analyze_clicked:
                try:
                    with st.spinner("PROCESSING: ANALYZING LECTURE NOTES & EXTRACTING CORE CONCEPTS..."):
                        p1_result = analyze_lecture(
                            st.session_state.parsed_doc.extracted_text,
                            timeout=120.0,
                        )
                        st.session_state.p1_analysis = p1_result
                        st.session_state.p2_questions = None
                        st.session_state.p3_verification = None
                        st.rerun()
                except MissingAPIKeyError as e:
                    st.error(f"CONFIGURATION ERROR: {e}")
                except AuthenticationError as e:
                    st.error(f"AUTHENTICATION ERROR: {e}")
                except RateLimitExceededError as e:
                    st.error(f"RATE LIMIT EXCEEDED: {e}")
                except NetworkConnectionError as e:
                    st.error(f"NETWORK FAILURE: {e}")
                except APIRequestTimeoutError as e:
                    st.error(f"REQUEST TIMEOUT: {e}")
                except GroqClientError as e:
                    st.error(f"API ERROR: {e}")
                except Exception as e:
                    st.error(f"UNEXPECTED ERROR: {type(e).__name__} - {e}")

            if st.session_state.p1_analysis:
                st.markdown(section_label("REVISION MANUSCRIPT — STAGE 02 OUTPUT"), unsafe_allow_html=True)
                with st.container(key="reading_sheet_notes"):
                    st.markdown(st.session_state.p1_analysis)
            else:
                st.markdown(
                    empty_card("NOTES WILL APPEAR HERE", "CLICK 'GENERATE REVISION NOTES' ABOVE TO BEGIN SYNTHESIS.", is_dashed_pencil=False),
                    unsafe_allow_html=True,
                )


# =============================================================================
# TAB 3: PRACTICE QUESTIONS (P2)
# =============================================================================
with tab_questions:
    st.markdown(stage_rail(3, stages_done), unsafe_allow_html=True)
    st.markdown(
        stage_header("03", "STAGE 03 / 05 — PRACTICE QUESTIONS", "Revision Question Suite", "Creates balanced practice questions across difficulty tiers with unspoilered answers."),
        unsafe_allow_html=True,
    )

    if st.session_state.parsed_doc is None or st.session_state.p1_analysis is None:
        st.markdown(
            empty_card("PREREQUISITE REQUIRED", "PLEASE COMPLETE STAGE 02 REVISION NOTES BEFORE GENERATING QUESTIONS.", is_dashed_pencil=True),
            unsafe_allow_html=True,
        )
    else:
        col_meta, col_work = st.columns([3, 9])

        with col_meta:
            meta_items = [
                ("SOURCE", st.session_state.file_name),
                ("NOTES STATE", "READY"),
                ("STAGE 03 STATUS", "COMPLETED" if p2_done else "READY TO GENERATE"),
            ]
            st.markdown(margin_meta_card(meta_items), unsafe_allow_html=True)

            num_questions = st.selectbox(
                "QUESTION VOLUME",
                options=[5, 10, 15],
                index=1,
                help="Choose total quantity of revision practice questions.",
            )

            exam_mode = st.toggle(
                "EXAM MODE",
                key="ui_exam_mode",
                help="Hide inline answer keys to practice test recall without spoilers.",
            )

        with col_work:
            gen_clicked = st.button("📝 GENERATE PRACTICE QUESTIONS →", type="primary")

            if gen_clicked:
                try:
                    with st.spinner(f"PROCESSING: CRAFTING {num_questions} TIERED PRACTICE QUESTIONS & ANSWER KEY..."):
                        p2_result = generate_questions(
                            lecture_text=st.session_state.parsed_doc.extracted_text,
                            analysis_text=st.session_state.p1_analysis,
                            num_questions=num_questions,
                            timeout=150.0,
                        )
                        st.session_state.p2_questions = p2_result
                        st.session_state.p3_verification = None
                        st.rerun()
                except MissingAnalysisError as e:
                    st.error(f"ANALYSIS PREREQUISITE ERROR: {e}")
                except OutputTruncatedError as e:
                    st.warning(
                        "⚠️ GENERATION WAS CUT OFF: The model reached its maximum token allowance before completing "
                        "all questions and explanations. Please select a smaller question volume (e.g., 5 or 10 questions) and try again."
                    )
                except IncompleteQuestionSetError as e:
                    st.warning(
                        f"⚠️ INCOMPLETE OUTPUT: {e} Please select a smaller question volume and try again."
                    )
                except MissingAPIKeyError as e:
                    st.error(f"CONFIGURATION ERROR: {e}")
                except AuthenticationError as e:
                    st.error(f"AUTHENTICATION ERROR: {e}")
                except RateLimitExceededError as e:
                    st.error(f"RATE LIMIT EXCEEDED: {e}")
                except NetworkConnectionError as e:
                    st.error(f"NETWORK FAILURE: {e}")
                except APIRequestTimeoutError as e:
                    st.error(f"REQUEST TIMEOUT: {e}")
                except GroqClientError as e:
                    st.error(f"API ERROR: {e}")
                except Exception as e:
                    st.error(f"UNEXPECTED ERROR: {type(e).__name__} - {e}")

            if st.session_state.p2_questions:
                p2_raw = st.session_state.p2_questions

                # Split questions from answer key
                if "## Part 2" in p2_raw:
                    parts = p2_raw.split("## Part 2", 1)
                    q_part = parts[0].strip()
                    a_part = "## Part 2" + parts[1]
                else:
                    q_part = p2_raw
                    a_part = ""

                st.markdown(section_label("ASSESSMENT SET — STAGE 03 OUTPUT"), unsafe_allow_html=True)

                if st.session_state.ui_exam_mode:
                    # Exam Mode: render questions first, answer key in expander at bottom
                    with st.container(key="reading_sheet_exam_q"):
                        st.markdown(q_part)

                    if a_part:
                        st.write("")
                        with st.container(key="answer_expander"):
                            with st.expander("🔑 [EXAM MODE] REVEAL ANSWER KEY & STEP-BY-STEP EXPLANATIONS", expanded=False):
                                st.markdown(a_part)
                    else:
                        st.warning("⚠️ INCOMPLETE ASSESSMENT: The answer key section (Part 2) is missing. Please regenerate with a smaller question volume.")
                else:
                    # Dual Tabs: Practice vs Answer Key
                    sub_q, sub_a = st.tabs(["✍️ PRACTICE MODE", "🔑 COMPLETE ANSWER KEY & EXPLANATIONS"])
                    with sub_q:
                        with st.container(key="reading_sheet_practice_q"):
                            st.markdown(q_part)
                    with sub_a:
                        if a_part:
                            with st.container(key="answer_expander_sub"):
                                st.markdown(a_part)
                        else:
                            st.warning("⚠️ INCOMPLETE ASSESSMENT: The answer key section (Part 2) is missing. Please regenerate with a smaller question volume.")
            else:
                st.markdown(
                    empty_card("PRACTICE QUESTIONS WILL APPEAR HERE", "CLICK 'GENERATE PRACTICE QUESTIONS' ABOVE TO CREATE ASSESSMENT.", is_dashed_pencil=False),
                    unsafe_allow_html=True,
                )


# =============================================================================
# TAB 4: CONTENT VERIFICATION (P3)
# =============================================================================
with tab_verify:
    st.markdown(stage_rail(4, stages_done), unsafe_allow_html=True)
    st.markdown(
        stage_header("04", "STAGE 04 / 05 — CONTENT AUDIT", "Quality & Grounding Audit", "Audits generated notes and practice questions against the original lecture source text."),
        unsafe_allow_html=True,
    )

    if not (doc_loaded and p1_done and p2_done):
        st.markdown(
            empty_card("PREREQUISITES INCOMPLETE", "PLEASE COMPLETE STAGES 01, 02 AND 03 BEFORE RUNNING THE CONTENT AUDIT.", is_dashed_pencil=True),
            unsafe_allow_html=True,
        )
    else:
        col_meta, col_work = st.columns([3, 9])

        with col_meta:
            meta_items = [
                ("SOURCE", st.session_state.file_name),
                ("NOTES (P1)", "VERIFIED READY"),
                ("QUESTIONS (P2)", "VERIFIED READY"),
                ("STAGE 04 STATUS", "COMPLETED" if p3_done else "READY TO AUDIT"),
            ]
            st.markdown(margin_meta_card(meta_items), unsafe_allow_html=True)

        with col_work:
            verify_clicked = st.button("🛡️ RUN CONTENT VERIFICATION →", type="primary")

            if verify_clicked:
                try:
                    with st.spinner("PROCESSING: CROSS-EXAMINING CLAIMS & VERIFYING ARITHMETIC AGAINST SOURCE SLIDES..."):
                        p3_result = verify_content(
                            lecture_text=st.session_state.parsed_doc.extracted_text,
                            analysis_text=st.session_state.p1_analysis,
                            questions_text=st.session_state.p2_questions,
                            timeout=150.0,
                        )
                        st.session_state.p3_verification = p3_result
                        st.rerun()
                except MissingAPIKeyError as e:
                    st.error(f"CONFIGURATION ERROR: {e}")
                except AuthenticationError as e:
                    st.error(f"AUTHENTICATION ERROR: {e}")
                except RateLimitExceededError as e:
                    st.error(f"RATE LIMIT EXCEEDED: {e}")
                except NetworkConnectionError as e:
                    st.error(f"NETWORK FAILURE: {e}")
                except APIRequestTimeoutError as e:
                    st.error(f"REQUEST TIMEOUT: {e}")
                except GroqClientError as e:
                    st.error(f"API ERROR: {e}")
                except Exception as e:
                    st.error(f"UNEXPECTED ERROR: {type(e).__name__} - {e}")

            if st.session_state.p3_verification:
                report = st.session_state.p3_verification

                # Parse status & approximate counts
                verdict_str = "PASS WITH WARNINGS"
                if "NEEDS REVISION" in report:
                    verdict_str = "NEEDS REVISION"
                elif "PASS WITH WARNINGS" in report:
                    verdict_str = "PASS WITH WARNINGS"
                elif "PASS" in report:
                    verdict_str = "PASS"

                # Count occurrences of checkmarks and crosses
                sup_count = max(4, report.count("✅") + report.count("Correct") + report.count("Verified"))
                warn_count = max(1, report.count("⚠️") + report.count("Warning") + report.count("Gap"))
                err_count = max(1, report.count("❌") + report.count("Error") + report.count("Unsupported"))

                st.markdown(
                    verdict_board_header(verdict_str, sup_count, warn_count, err_count),
                    unsafe_allow_html=True,
                )

                st.markdown(section_label("AUDIT MANUSCRIPT — STAGE 04 REPORT"), unsafe_allow_html=True)
                with st.container(key="reading_sheet_audit"):
                    st.markdown(report)
            else:
                st.markdown(
                    empty_card("VERIFICATION AUDIT WILL APPEAR HERE", "CLICK 'RUN CONTENT VERIFICATION' ABOVE TO AUDIT GENERATED MATERIALS.", is_dashed_pencil=False),
                    unsafe_allow_html=True,
                )


# =============================================================================
# TAB 5: EXPORT STUDY PACK (DISPATCH)
# =============================================================================
with tab_export:
    st.markdown(stage_rail(5, stages_done), unsafe_allow_html=True)
    st.markdown(
        stage_header("05", "STAGE 05 / 05 — EXPORT DOCKET", "Study Pack Dispatch", "Download compiled revision materials for offline studying and exam preparation."),
        unsafe_allow_html=True,
    )

    if not export_ready:
        st.markdown(
            empty_card("NO PACK AVAILABLE YET", "COMPLETE REVISION NOTES OR PRACTICE QUESTIONS BEFORE DOWNLOADING.", is_dashed_pencil=True),
            unsafe_allow_html=True,
        )
    else:
        doc_name = Path(st.session_state.file_name or "lecture").stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        # Compile comprehensive study pack (strictly preserving format and data)
        pack_lines = [
            f"# LastHope Study Pack: {doc_name}",
            f"- Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- Source File: {st.session_state.file_name}",
            f"- Model Engine: {configured_model}",
            "\n---\n",
        ]

        if st.session_state.p1_analysis:
            pack_lines.append("## PART I: LECTURE REVISION NOTES (P1)\n")
            pack_lines.append(st.session_state.p1_analysis)
            pack_lines.append("\n---\n")

        if st.session_state.p2_questions:
            pack_lines.append("## PART II: REVISION QUESTIONS & ANSWER KEY (P2)\n")
            pack_lines.append(st.session_state.p2_questions)
            pack_lines.append("\n---\n")

        # Verification report strictly only included if it has been run
        if st.session_state.p3_verification:
            pack_lines.append("## PART III: CONTENT VERIFICATION & AUDIT REPORT (P3)\n")
            pack_lines.append(st.session_state.p3_verification)
            pack_lines.append("\n---\n")

        full_study_pack = "\n".join(pack_lines)

        col_meta, col_work = st.columns([3, 9])

        with col_meta:
            meta_items = [
                ("PACKAGE", doc_name),
                ("TIMESTAMP", timestamp),
                ("STAGE 05 STATUS", "DISPATCH READY"),
            ]
            st.markdown(margin_meta_card(meta_items), unsafe_allow_html=True)

        with col_work:
            st.markdown(
                study_pack_docket(doc_name, p1_done, p2_done, p3_done),
                unsafe_allow_html=True,
            )

            st.write("")
            st.markdown(section_label("COMPLETE REVISION PACK DISPATCH"), unsafe_allow_html=True)

            col_md, col_txt = st.columns(2)
            with col_md:
                st.download_button(
                    label="📥 Download Study Pack (.md)",
                    data=full_study_pack,
                    file_name=f"LastHope_{doc_name}_StudyPack_{timestamp}.md",
                    mime="text/markdown",
                    type="primary",
                )
            with col_txt:
                st.download_button(
                    label="📥 Download Study Pack (.txt)",
                    data=full_study_pack,
                    file_name=f"LastHope_{doc_name}_StudyPack_{timestamp}.txt",
                    mime="text/plain",
                )

            st.divider()

            st.markdown(section_label("INDIVIDUAL SECTION DISPATCH"), unsafe_allow_html=True)

            col_n, col_q, col_v = st.columns(3)

            with col_n:
                if st.session_state.p1_analysis:
                    st.download_button(
                        label="📄 Download Revision Notes Only",
                        data=st.session_state.p1_analysis,
                        file_name=f"LastHope_{doc_name}_Notes_{timestamp}.md",
                        mime="text/markdown",
                    )
                else:
                    st.caption("Revision Notes: Not generated yet.")

            with col_q:
                if st.session_state.p2_questions:
                    st.download_button(
                        label="📝 Download Questions & Answers Only",
                        data=st.session_state.p2_questions,
                        file_name=f"LastHope_{doc_name}_Questions_{timestamp}.md",
                        mime="text/markdown",
                    )
                else:
                    st.caption("Practice Questions: Not generated yet.")

            with col_v:
                if st.session_state.p3_verification:
                    st.download_button(
                        label="🛡️ Download Verification Report Only",
                        data=st.session_state.p3_verification,
                        file_name=f"LastHope_{doc_name}_Verification_{timestamp}.md",
                        mime="text/markdown",
                    )
                else:
                    st.caption("Verification Report: Not run yet.")
