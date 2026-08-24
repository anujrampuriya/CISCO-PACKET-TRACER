import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

from src.engine import load_cases, diagnose_with_ai
from src import checker


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NetSage AI",
    page_icon="🌐",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
AUDIT_LOG = BASE_DIR / "docs" / "model_audit_log.md"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def run_rule_checker(show_output):
    """
    Run the deterministic checker.

    This wrapper supports the checker function used in the
    project without requiring changes to checker.py.
    """

    possible_functions = [
        "check_case",
        "check_output",
        "check_show_output",
        "run_checks",
        "check_config"
    ]

    for function_name in possible_functions:
        function = getattr(checker, function_name, None)

        if callable(function):
            try:
                return function({"show_outputs": show_output})
            except TypeError:
                continue

    return {
        "status": "NO_ERRORS_DETECTED",
        "findings": []
    }

def append_audit_record(
    case_id,
    ai_result,
    decision,
    reviewer_reason="",
    edited_fix_steps=None
):
    """
    Append one human-review record to model_audit_log.md
    and update the Agreement Summary.
    """

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    root_cause = ai_result.get("root_cause", "")
    confidence = ai_result.get("confidence", "")
    next_command = ai_result.get("next_command", "")

    fix_steps = edited_fix_steps

    if fix_steps is None:
        fix_steps = ai_result.get("fix_steps", [])

    if not isinstance(fix_steps, list):
        fix_steps = [str(fix_steps)]

    evidence = ai_result.get("evidence", [])

    if not isinstance(evidence, list):
        evidence = [str(evidence)]

    with open(AUDIT_LOG, "a", encoding="utf-8") as file:

        file.write("\n\n---\n\n")

        file.write(f"## Review: {case_id}\n\n")

        file.write(f"- **Timestamp:** {timestamp}\n")
        file.write(f"- **Decision:** {decision}\n")
        file.write(f"- **Reviewer:** Human reviewer\n")
        file.write(
            f"- **Reason:** "
            f"{reviewer_reason or 'No additional reason provided.'}\n\n"
        )

        file.write("### AI Diagnosis\n\n")

        file.write(f"**Root Cause:** {root_cause}\n\n")
        file.write(
            f"**OSI Layer:** "
            f"{ai_result.get('osi_layer', '')}\n\n"
        )
        file.write(f"**Confidence:** {confidence}\n\n")

        file.write("### Evidence\n\n")

        for item in evidence:
            file.write(f"- {item}\n")

        file.write("\n")

        file.write(
            f"**Verification Command:** "
            f"`{next_command}`\n\n"
        )

        file.write("### Final Fix Steps\n\n")

        for index, step in enumerate(fix_steps, start=1):
            file.write(f"{index}. {step}\n")

    # ----------------------------------------------------
    # UPDATE AUDIT SUMMARY
    # ----------------------------------------------------

    text = AUDIT_LOG.read_text(encoding="utf-8")

    accepted = text.count("- **Decision:** Accepted")
    edited = text.count("- **Decision:** Edited")
    rejected = text.count("- **Decision:** Rejected")

    total = accepted + edited + rejected

    agreement = 0.0

    if total > 0:
        agreement = (accepted / total) * 100

    summary = (
        "## Agreement Summary\n\n"
        f"- Total reviewed: {total}\n"
        f"- Accepted: {accepted}\n"
        f"- Edited: {edited}\n"
        f"- Rejected: {rejected}\n"
        f"- AI-Human agreement rate: {agreement:.1f}%\n"
    )

    start_marker = "## Agreement Summary\n"
    end_marker = "## Responsible AI Notes\n"

    if start_marker in text and end_marker in text:

        start = text.index(start_marker)
        end = text.index(end_marker)

        text = (
            text[:start]
            + summary
            + "\n"
            + text[end:]
        )

        AUDIT_LOG.write_text(
            text,
            encoding="utf-8"
        )


def read_audit_statistics():
    """
    Read the audit log and calculate review statistics.
    """

    if not AUDIT_LOG.exists():
        return {
            "total": 0,
            "accepted": 0,
            "edited": 0,
            "rejected": 0,
            "agreement": 0.0
        }

    text = AUDIT_LOG.read_text(encoding="utf-8")

    accepted = text.count("- **Decision:** Accepted")
    edited = text.count("- **Decision:** Edited")
    rejected = text.count("- **Decision:** Rejected")

    total = accepted + edited + rejected

    agreement = 0.0

    if total > 0:
        agreement = (accepted / total) * 100

    return {
        "total": total,
        "accepted": accepted,
        "edited": edited,
        "rejected": rejected,
        "agreement": agreement
    }


def clean_ai_result(result):
    """
    Convert AI response into a Python dictionary.
    """

    if isinstance(result, dict):
        return result

    if not isinstance(result, str):
        return {
            "root_cause": str(result),
            "osi_layer": "",
            "confidence": "",
            "evidence": [],
            "next_command": "",
            "fix_steps": []
        }

    text = result.strip()

    # Remove Markdown code fences if Gemini returns them.
    if text.startswith("```"):
        lines = text.splitlines()

        if len(lines) >= 3:
            lines = lines[1:]

            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        return {
            "root_cause": text,
            "osi_layer": "",
            "confidence": "Unknown",
            "evidence": [],
            "next_command": "",
            "fix_steps": []
        }


# ============================================================
# LOAD DATA
# ============================================================

try:
    cases_df = load_cases()

except Exception:
    cases_df = pd.read_csv(
        BASE_DIR / "data" / "cases.csv"
    )


# ============================================================
# SESSION STATE
# ============================================================

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "diagnosed_case_id" not in st.session_state:
    st.session_state.diagnosed_case_id = None

if "review_completed" not in st.session_state:
    st.session_state.review_completed = False

if "edited_fix_steps" not in st.session_state:
    st.session_state.edited_fix_steps = None


# ============================================================
# HEADER
# ============================================================

st.title("🌐 NetSage AI")

st.subheader(
    "AI-Powered Cisco Network Troubleshooting Assistant"
)

st.write(
    "Analyze networking symptoms, Cisco show outputs, "
    "and deterministic rule-checker findings."
)


# ============================================================
# SIDEBAR — AUDIT SUMMARY
# ============================================================

stats = read_audit_statistics()

with st.sidebar:

    st.header("📊 Human Review Summary")

    st.metric(
        "Cases Reviewed",
        stats["total"]
    )

    st.metric(
        "Accepted",
        stats["accepted"]
    )

    st.metric(
        "Edited",
        stats["edited"]
    )

    st.metric(
        "Rejected",
        stats["rejected"]
    )

    st.metric(
        "AI-Human Agreement",
        f"{stats['agreement']:.1f}%"
    )

    st.divider()

    st.caption(
        "AI recommendations must be reviewed by a human "
        "before remediation is accepted."
    )


# ============================================================
# CASE SELECTION
# ============================================================

case_ids = cases_df["case_id"].tolist()

selected_case_id = st.selectbox(
    "Select a Network Case",
    case_ids
)


# ============================================================
# GET SELECTED CASE
# ============================================================

case_row = cases_df[
    cases_df["case_id"] == selected_case_id
].iloc[0]

case = case_row.to_dict()


# Reset diagnosis when case changes.
if st.session_state.diagnosed_case_id != selected_case_id:

    st.session_state.ai_result = None
    st.session_state.review_completed = False
    st.session_state.edited_fix_steps = None


# ============================================================
# CASE INFORMATION
# ============================================================

st.header("Case Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Case ID")
    st.write(case["case_id"])

with col2:
    st.subheader("OSI Layer")
    st.write(case["osi_layer"])

with col3:
    st.subheader("Severity")
    st.write(case["severity"])


# ============================================================
# SYMPTOM
# ============================================================

st.subheader("Symptom")

st.info(case["symptom"])


# ============================================================
# TOPOLOGY
# ============================================================

st.subheader("Topology")

st.code(
    case["topology_note"],
    language="text"
)


# ============================================================
# CISCO SHOW OUTPUT
# ============================================================

st.subheader("Cisco Show Output")

st.code(
    case["show_outputs"],
    language="text"
)


# ============================================================
# DETERMINISTIC RULE CHECKER
# ============================================================

st.subheader("Deterministic Rule Checker")

try:

    rule_result = run_rule_checker(
        case["show_outputs"]
    )

except Exception as error:

    rule_result = {
        "status": "CHECKER_ERROR",
        "findings": [
            {
                "rule_id": "CHECKER",
                "issue": "CHECKER_ERROR",
                "message": str(error)
            }
        ]
    }


if rule_result.get("status") == "ERRORS_DETECTED":

    st.error("Network fault detected")

    findings = rule_result.get("findings", [])

    for finding in findings:

        st.write(
            f"**Rule:** {finding.get('rule_id', '')}"
        )

        st.write(
            f"**Issue:** {finding.get('issue', '')}"
        )

        st.write(
            f"**Message:** {finding.get('message', '')}"
        )

        st.divider()

else:

    st.success("No deterministic errors detected")


# ============================================================
# AI DIAGNOSIS
# ============================================================

st.header("AI Diagnosis")

if st.button(
    "🔍 Diagnose with NetSage AI",
    type="primary"
):

    with st.spinner(
        "Analyzing the network case..."
    ):

        try:

            result = diagnose_with_ai(case)

            if result.get("status") == "AI_UNAVAILABLE":

                st.session_state.ai_result = None
                st.session_state.diagnosed_case_id = selected_case_id
                st.session_state.review_completed = False
                st.session_state.edited_fix_steps = None

                st.warning(
                    "⚠️ AI Diagnostic Engine is unavailable. "
                    "Deterministic Rule Engine results are still available."
                )

            else:

                result = clean_ai_result(result)

                st.session_state.ai_result = result
                st.session_state.diagnosed_case_id = selected_case_id
                st.session_state.review_completed = False
                st.session_state.edited_fix_steps = None

        except Exception as error:

               st.error(
                f"AI diagnosis failed: {error}"
            )


# ============================================================
# DISPLAY AI RESULT
# ============================================================

if (
    st.session_state.ai_result is not None
    and st.session_state.diagnosed_case_id == selected_case_id
):

    ai_result = st.session_state.ai_result

    st.success("Diagnosis completed")


    # --------------------------------------------------------
    # ROOT CAUSE
    # --------------------------------------------------------

    st.header("Root Cause")

    st.write(
        ai_result.get(
            "root_cause",
            "Not provided."
        )
    )


    # --------------------------------------------------------
    # OSI + CONFIDENCE
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("OSI Layer")

        st.write(
            ai_result.get(
                "osi_layer",
                "Not provided."
            )
        )

    with col2:

        st.subheader("Confidence")

        st.write(
            ai_result.get(
                "confidence",
                "Not provided."
            )
        )


    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    st.header("Evidence")

    evidence = ai_result.get(
        "evidence",
        []
    )

    if isinstance(evidence, list):

        for item in evidence:
            st.write(f"• {item}")

    else:

        st.write(evidence)


    # --------------------------------------------------------
    # NEXT COMMAND
    # --------------------------------------------------------

    st.header("Verification Command")

    st.code(
        ai_result.get(
            "next_command",
            "No command provided."
        ),
        language="text"
    )


    # --------------------------------------------------------
    # FIX STEPS
    # --------------------------------------------------------

    st.header("Suggested Fix Steps")

    fix_steps = ai_result.get(
        "fix_steps",
        []
    )

    if not isinstance(fix_steps, list):
        fix_steps = [str(fix_steps)]

    for index, step in enumerate(
        fix_steps,
        start=1
    ):

        st.write(
            f"{index}. {step}"
        )


    st.warning(
        "AI-generated remediation is a recommendation. "
        "Verify the configuration before applying changes."
    )


    # ========================================================
    # HUMAN REVIEW GATE
    # ========================================================

    st.divider()

    st.header("👤 Human Review")

    st.write(
        "Review the AI diagnosis and remediation steps "
        "before accepting the recommendation."
    )


    # --------------------------------------------------------
    # REVIEW DECISION
    # --------------------------------------------------------

    if not st.session_state.review_completed:

        review_col1, review_col2, review_col3 = st.columns(3)


        # ----------------------------------------------------
        # ACCEPT
        # ----------------------------------------------------

        with review_col1:

            if st.button(
                "✅ Accept Diagnosis",
                width="stretch"
            ):  

                append_audit_record(
                    case_id=selected_case_id,
                    ai_result=ai_result,
                    decision="Accepted",
                    reviewer_reason="AI diagnosis accepted without changes."
                )

                st.session_state.review_completed = True

                st.success(
                    "Diagnosis accepted and recorded."
                )

                st.rerun()


        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        with review_col2:

            if st.button(
                "✏️ Edit Diagnosis",
                width="stretch"
            ):

                st.session_state.show_edit_form = True


        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        with review_col3:

            if st.button(
                "❌ Reject Diagnosis",
                width="stretch"
    
            ):

                st.session_state.show_reject_form = True


    # ========================================================
    # EDIT FORM
    # ========================================================

    if st.session_state.get(
        "show_edit_form",
        False
    ):

        st.subheader(
            "Edit AI Diagnosis"
        )

        edited_root_cause = st.text_area(
            "Corrected Root Cause",
            value=ai_result.get(
                "root_cause",
                ""
            )
        )

        edited_command = st.text_input(
            "Corrected Verification Command",
            value=ai_result.get(
                "next_command",
                ""
            )
        )

        edited_steps_text = st.text_area(
            "Corrected Fix Steps — one step per line",
            value="\n".join(
                fix_steps
            )
        )

        edit_reason = st.text_area(
            "Why was the AI response edited?",
            placeholder=(
                "Example: AI identified the correct issue "
                "but suggested an incorrect interface."
            )
        )

        if st.button(
            "💾 Save Human Correction",
            type="primary"
        ):

            corrected_steps = [
                step.strip()
                for step in edited_steps_text.splitlines()
                if step.strip()
            ]

            corrected_result = dict(
                ai_result
            )

            corrected_result[
                "root_cause"
            ] = edited_root_cause

            corrected_result[
                "next_command"
            ] = edited_command

            corrected_result[
                "fix_steps"
            ] = corrected_steps

            append_audit_record(
                case_id=selected_case_id,
                ai_result=corrected_result,
                decision="Edited",
                reviewer_reason=edit_reason,
                edited_fix_steps=corrected_steps
            )

            st.session_state.ai_result = corrected_result
            st.session_state.edited_fix_steps = corrected_steps
            st.session_state.review_completed = True
            st.session_state.show_edit_form = False

            st.success(
                "Human correction saved to the audit log."
            )

            st.rerun()


    # ========================================================
    # REJECT FORM
    # ========================================================

    if st.session_state.get(
        "show_reject_form",
        False
    ):

        st.subheader(
            "Reject AI Diagnosis"
        )

        reject_reason = st.text_area(
            "Reason for rejection",
            placeholder=(
                "Explain why the AI diagnosis is incorrect."
            )
        )

        if st.button(
            "Confirm Rejection",
            type="primary"
        ):

            if not reject_reason.strip():

                st.error(
                    "Please provide a reason for rejection."
                )

            else:

                append_audit_record(
                    case_id=selected_case_id,
                    ai_result=ai_result,
                    decision="Rejected",
                    reviewer_reason=reject_reason
                )

                st.session_state.review_completed = True
                st.session_state.show_reject_form = False

                st.error(
                    "Diagnosis rejected and recorded."
                )

                st.rerun()


    # ========================================================
    # REVIEW COMPLETED
    # ========================================================

    if st.session_state.review_completed:

        st.success(
            "Human review completed. "
            "The decision has been recorded in the audit log."
        )


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

st.divider()

st.header("📊 NetSage AI Dashboard Summary")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Network Cases",
        len(cases_df)
    )

with col2:

    st.metric(
        "High Severity Cases",
        len(
            cases_df[
                cases_df["severity"]
                .astype(str)
                .str.lower()
                == "high"
            ]
        )
    )

with col3:

    st.metric(
        "Cases Reviewed",
        stats["total"]
    )


# ============================================================
# ISSUE TYPE SUMMARY
# ============================================================

st.subheader("Issue Types")

if "concept_tag" in cases_df.columns:

    issue_counts = (
        cases_df["concept_tag"]
        .value_counts()
        .reset_index()
    )

    issue_counts.columns = [
        "Issue Type",
        "Cases"
    ]

    st.dataframe(
        issue_counts,
        width="stretch",
        hide_index=True
    )


# ============================================================
# SEVERITY SUMMARY
# ============================================================

st.subheader("Severity Distribution")

severity_counts = (
    cases_df["severity"]
    .value_counts()
    .reset_index()
)

severity_counts.columns = [
    "Severity",
    "Cases"
]

st.dataframe(
    severity_counts,
    width="stretch",
    hide_index=True
)


# ============================================================
# RESPONSIBLE AI STATUS
# ============================================================

st.subheader("Responsible AI Review Status")

if stats["edited"] >= 5:

    st.success(
        "Responsible AI requirement satisfied: "
        "at least 5 human-corrected AI responses have been logged."
    )

else:

    remaining = 5 - stats["edited"]

    st.info(
        f"Need {remaining} more human-edited case(s) "
        "to reach the required 5 corrected AI responses."
    )


st.caption(
    "NetSage AI follows a Human-in-the-Loop approach. "
    "AI suggestions are not automatically executed."
)