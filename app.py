import streamlit as st
import pandas as pd
import ollama
import json
import re
from io import BytesIO

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Meeting Action Item Agent",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS - PROFESSIONAL DARK BLUE UI
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

h1, h2, h3 {
    color: #60a5fa !important;
}

p, label, li {
    color: #e2e8f0;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.stTextArea textarea {
    background-color: #172033;
    color: #ffffff;
    border: 1px solid #334155;
    border-radius: 10px;
}

.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}

[data-testid="stMetric"] {
    background-color: #172033;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #334155;
}

hr {
    border-color: #334155;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🤖 Meeting Action Item Agent")

st.markdown(
    """
    Transform meeting transcripts into **actionable tasks,
    important decisions, and meeting summaries** using AI.
    """
)

st.divider()


# --------------------------------------------------
# AI ANALYSIS FUNCTION
# --------------------------------------------------

def analyze_meeting(transcript, model_name):

    prompt = f"""
You are an AI meeting assistant.

Analyze the meeting transcript provided below.

Extract:
1. A short meeting summary.
2. All action items.
3. All important decisions.

Return ONLY valid JSON using this exact structure:

{{
    "summary": "Short summary of the meeting",
    "action_items": [
        {{
            "task": "Description of the task",
            "assigned_to": "Person responsible",
            "deadline": "Deadline or Not specified",
            "priority": "High, Medium, or Low"
        }}
    ],
    "decisions": [
        "Important decision 1",
        "Important decision 2"
    ]
}}

Rules:
- Include every action item mentioned in the transcript.
- Do not omit people who have been assigned tasks.
- Keep each task clear and concise.
- Use the actual person's name when available.
- Do not invent deadlines or responsibilities.
- If a deadline is not mentioned, use "Not specified".
- If priority is unclear, use "Medium".
- Include important decisions only once.
- If no action items exist, return an empty action_items list.
- If no decisions exist, return an empty decisions list.
- Do not include markdown or explanations outside the JSON.

Meeting transcript:

{transcript}
"""

    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    content = response["message"]["content"]

    return extract_json(content)


# --------------------------------------------------
# JSON EXTRACTION
# --------------------------------------------------

def extract_json(content):

    content = content.strip()

    # Remove markdown code fences if present
    content = re.sub(
        r"^```(?:json)?\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    )

    data = json.loads(content)

    if not isinstance(data, dict):
        raise ValueError("AI did not return a JSON object.")

    return data


# --------------------------------------------------
# SIDEBAR SETTINGS
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    model_name = st.text_input(
        "Ollama model name",
        value="llama3.2:latest"
    )

    st.caption(
        "Make sure the selected model is installed "
        "and running in Ollama."
    )

    st.divider()

    st.markdown("### 📌 About")

    st.write(
        "This AI application converts meeting "
        "transcripts into structured information."
    )

    st.markdown("**Technology Stack**")

    st.write("• Python")
    st.write("• Streamlit")
    st.write("• Ollama")
    st.write("• Llama 3.2")
    st.write("• Pandas")


# --------------------------------------------------
# MEETING TRANSCRIPT INPUT
# --------------------------------------------------

st.subheader("📝 Meeting Transcript")

transcript = st.text_area(
    "Paste your meeting transcript here",
    height=250,
    placeholder=(
        "Example:\n"
        "Arun will complete the registration by Monday.\n"
        "Priya will prepare the poster by Wednesday.\n"
        "Ravi will contact five colleges by Friday.\n"
        "The team decided to conduct the event in the auditorium."
    )
)

analyze_button = st.button(
    "🚀 Analyze Meeting",
    type="primary",
    use_container_width=True
)


# --------------------------------------------------
# PROCESS MEETING
# --------------------------------------------------

if analyze_button:

    if not transcript.strip():

        st.warning(
            "Please enter a meeting transcript before analyzing."
        )

    elif not model_name.strip():

        st.warning(
            "Please enter your Ollama model name."
        )

    else:

        try:

            with st.spinner(
                "AI is analyzing your meeting... Please wait."
            ):

                result = analyze_meeting(
                    transcript,
                    model_name.strip()
                )

            # Get summary
            summary = result.get(
                "summary",
                "No summary available."
            )

            # Get action items
            action_items = result.get(
                "action_items",
                []
            )

            # Get decisions
            decisions = result.get(
                "decisions",
                []
            )

            # Validate AI output
            if not isinstance(action_items, list):
                action_items = []

            if not isinstance(decisions, list):
                decisions = []

            # Normalize action items
            normalized_items = []

            for item in action_items:

                if isinstance(item, dict):

                    normalized_items.append({
                        "Task": item.get(
                            "task",
                            item.get("action_item", "Not specified")
                        ),
                        "Assigned To": item.get(
                            "assigned_to",
                            item.get("responsible_person", "Not specified")
                        ),
                        "Deadline": item.get(
                            "deadline",
                            "Not specified"
                        ),
                        "Priority": item.get(
                            "priority",
                            "Medium"
                        )
                    })

                elif isinstance(item, str):

                    normalized_items.append({
                        "Task": item,
                        "Assigned To": "Not specified",
                        "Deadline": "Not specified",
                        "Priority": "Medium"
                    })

            # Convert decisions into simple text
            normalized_decisions = []

            for decision in decisions:

                if isinstance(decision, str):

                    normalized_decisions.append(decision)

                elif isinstance(decision, dict):

                    decision_text = (
                        decision.get("decision")
                        or decision.get("description")
                        or decision.get("text")
                    )

                    if decision_text:
                        normalized_decisions.append(
                            str(decision_text)
                        )

            # Store results in session state
            st.session_state["meeting_summary"] = summary

            st.session_state["meeting_actions"] = (
                normalized_items
            )

            st.session_state["meeting_decisions"] = (
                normalized_decisions
            )

            st.success("Meeting analyzed successfully!")

        except json.JSONDecodeError:

            st.error(
                "The AI returned an invalid JSON response. "
                "Please try again."
            )

        except Exception as error:

            st.error(
                "Unable to analyze the meeting. "
                "Please check Ollama and the model name."
            )

            with st.expander("View technical error"):

                st.code(str(error))


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if "meeting_summary" in st.session_state:

    summary = st.session_state["meeting_summary"]

    action_items = st.session_state["meeting_actions"]

    decisions = st.session_state["meeting_decisions"]

    st.divider()

    st.header("📊 Meeting Analysis Results")

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            label="Total Action Items",
            value=len(action_items)
        )

    with col2:

        st.metric(
            label="Important Decisions",
            value=len(decisions)
        )

    with col3:

        st.metric(
            label="Meeting Summary",
            value="Ready"
        )

    # Summary
    st.subheader("📄 Meeting Summary")

    st.info(summary)

    st.divider()

    # Action items
    st.subheader("✅ Action Items")

    if action_items:

        action_df = pd.DataFrame(action_items)

        st.dataframe(
            action_df,
            use_container_width=True,
            hide_index=True
        )

        # Convert DataFrame to CSV
        csv_data = action_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="📥 Download Action Items as CSV",
            data=csv_data,
            file_name="meeting_action_items.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:

        st.info(
            "No action items were identified in this meeting."
        )

    st.divider()

    # Important decisions
    st.subheader("💡 Important Decisions")

    if decisions:

        for index, decision in enumerate(
            decisions,
            start=1
        ):

            st.markdown(
                f"**{index}.** {decision}"
            )

    else:

        st.info(
            "No important decisions were identified."
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Meeting Action Item Agent | "
    "Built with Python, Streamlit and Ollama"
)