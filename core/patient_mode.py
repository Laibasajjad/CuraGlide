import streamlit as st

from core.model import analyze_patient
from core.languages import t, prefetch, current_language


PATIENT_QUESTIONS = [
    {
        "key": "age",
        "question": "Hi there! 👋 Let's get you well and fit! 😊 First off, what's your age? 🎂",
        "placeholder": "Enter your age",
        "type": "number",
        "min_value": 1,
        "max_value": 120,
        "step": 1
    },
    {
        "key": "gender",
        "question": "Thanks! 😊 What is your sex or gender?",
        "placeholder": "For example: Male, Female, Another identity, or Prefer not to say",
        "type": "text"
    },
    {
        "key": "weight",
        "question": "Got it! ⚖️ How much do you weigh?",
        "placeholder": "Enter your weight in kg",
        "type": "number",
        "min_value": 1.0,
        "max_value": 500.0,
        "step": 0.1
    },
    {
        "key": "height",
        "question": "And what's your height? 📏",
        "placeholder": "Enter your height in cm",
        "type": "number",
        "min_value": 30.0,
        "max_value": 300.0,
        "step": 0.1
    },
    {
        "key": "conditions",
        "question": "Do you have any existing medical conditions I should know about? 🏥",
        "placeholder": "For example: asthma, diabetes, high blood pressure, or None",
        "type": "text"
    },
    {
        "key": "medications",
        "question": "Are you currently taking, or have you recently taken, any medications? 💊",
        "placeholder": "Include prescription or over-the-counter medicines, or type None",
        "type": "text"
    },
    {
        "key": "allergies",
        "question": "Do you have any allergies I should know about? ⚠️",
        "placeholder": "For example: medicine allergies, food allergies, or None",
        "type": "text"
    },
    {
        "key": "medical_history",
        "question": "Have you had any important illnesses, hospitalizations, or surgeries before? 🏥",
        "placeholder": "Briefly describe them, or type None",
        "type": "text"
    },
    {
        "key": "symptoms",
        "question": "Now tell me how you're feeling today. 💬 What symptoms, pain, or concerns are you experiencing?",
        "placeholder": "Describe everything you think might be important",
        "type": "text"
    },
    {
        "key": "duration",
        "question": "How long have you been experiencing these symptoms? ⏱️",
        "placeholder": "For example: 2 hours, 3 days, or 2 weeks",
        "type": "text"
    }
]


def initialize_patient_session():

    defaults = {
        "patient_step": 0,
        "patient_answers": {},
        "patient_completed": False,
        "patient_analysis": None,
        "patient_analysis_error": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


def reset_patient_mode():

    st.session_state.patient_step = 0
    st.session_state.patient_answers = {}
    st.session_state.patient_completed = False
    st.session_state.patient_analysis = None
    st.session_state.patient_analysis_error = None


def validate_answer(question, answer):

    if question["type"] == "number":

        if answer is None:
            return False, "Please enter a value."

        if (
            answer < question["min_value"]
            or answer > question["max_value"]
        ):
            return (
                False,
                f"Please enter a value between "
                f"{question['min_value']} and "
                f"{question['max_value']}."
            )

        return True, ""

    if not str(answer).strip():

        return (
            False,
            "Please enter an answer before continuing."
        )

    return True, ""


def get_urgency_level(analysis):

    """
    Detect the urgency level from the AI response.

    This is intentionally flexible so it works with the
    current model output without requiring changes to model.py.
    """

    if not analysis:
        return "UNKNOWN"

    # Language-independent tag written by the model on the first line.
    for line in str(analysis).splitlines()[:3]:
        if line.strip().upper().startswith("URGENCY_LEVEL"):
            tag = line.upper()
            if "EMERGENCY" in tag:
                return "EMERGENCY"
            if "URGENT" in tag:
                return "URGENT"
            if "SOON" in tag:
                return "SOON"
            if "LOWER" in tag or "LOW" in tag:
                return "LOW"

    text = analysis.upper()

    # Highest priority first
    if "EMERGENCY" in text:
        return "EMERGENCY"

    if (
        "URGENT" in text
        or "GET CHECKED SOON" in text
        or "IMMEDIATE MEDICAL" in text
    ):
        return "URGENT"

    if (
        "NEEDS ATTENTION" in text
        or "NEED ATTENTION" in text
        or "CHECK SOON" in text
        or "WORTH CHECKING SOON" in text
    ):
        return "SOON"

    if (
        "LOWER CONCERN" in text
        or "LOW CONCERN" in text
        or "ROUTINE" in text
        or "MILD" in text
    ):
        return "LOW"

    return "UNKNOWN"


BANNERS = {
    "E": '🚨 EMERGENCY\n\nThis information suggests that urgent medical attention may be needed.',
    "U": '🟠 URGENT — GET CHECKED SOON\n\nConsider getting checked by a healthcare professional soon.',
    "S": '🟡 NEEDS ATTENTION\n\nThis may be worth discussing with a healthcare professional.',
    "L": '🟢 LOWER CONCERN — WORTH CHECKING\n\nNothing in the available information suggests an immediate emergency, but professional advice can still be useful.',
    "I": '🔵 HEALTH INFORMATION\n\nReview the information below and consider speaking with a healthcare professional if you are concerned.',
}


def display_urgency_banner(analysis):

    urgency = get_urgency_level(analysis)

    if urgency == "EMERGENCY":

        st.error(
            t(BANNERS['E'])
        )

    elif urgency == "URGENT":

        st.warning(
            t(BANNERS['U'])
        )

    elif urgency == "SOON":

        st.warning(
            t(BANNERS['S'])
        )

    elif urgency == "LOW":

        st.success(
            t(BANNERS['L'])
        )

    else:

        st.info(
            t(BANNERS['I'])
        )


def display_analysis_sections(analysis):

    """
    Adds visual section labels around common sections in the AI output.

    The original AI text is preserved rather than rewritten.
    """

    if not analysis:
        return

    text = str(analysis).strip()

    # Hide the machine-readable urgency tag line.
    lines = [
        ln for ln in text.splitlines()
        if not ln.strip().upper().startswith("URGENCY_LEVEL")
    ]

    cleaned_lines = []

    for line in lines:

        stripped = line.strip()

        if stripped.upper() in [
            "EMERGENCY",
            "URGENT",
            "SOON",
            "LOW",
            "LOWER CONCERN",
            "NEEDS ATTENTION"
        ]:
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines).strip()

    # Section emoji replacements.
    replacements = {
        "WHY THIS URGENCY": "🚨 WHY THIS URGENCY",
        "WHAT MIGHT BE HAPPENING": "🧠 WHAT MIGHT BE HAPPENING",
        "WHAT TO DO": "✅ WHAT TO DO",
        "WHAT YOU SHOULD DO": "✅ WHAT YOU SHOULD DO",
        "WHAT TO MONITOR": "👀 WHAT TO MONITOR",
        "MONITOR": "👀 MONITOR",
        "WHEN TO GET HELP": "🏥 WHEN TO GET HELP",
        "WHEN TO SEEK HELP": "🏥 WHEN TO SEEK HELP",
        "IMPORTANT DISCLAIMER": "⚠️ IMPORTANT DISCLAIMER",
        "DISCLAIMER": "⚠️ DISCLAIMER",
        "NEXT STEPS": "➡️ NEXT STEPS",
        "WARNING SIGNS": "🚨 WARNING SIGNS"
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    st.markdown(text)


def _ui_strings():
    out = ["Question", "Your answer", "← Previous", "Analyze →", "Continue →",
           "✅ CuraGlide analysis complete!", "## 🧠 AI Health Analysis",
           "🔄 Start New Health Check", "🔄 Try Analysis Again",
           "🆘 Get emergency helpline numbers",
           "❌ We couldn't complete the analysis.",
           "✅ Thank you! I've collected your information.",
           "## 🧠 Analyzing your information...",
           "CuraGlide is analyzing your information...",
           "⚠️ CuraGlide provides health information and guidance. It does not replace a qualified healthcare professional or provide a confirmed medical diagnosis.",
           "Your well-being in every step — accessed from a single touch.",
           "Please enter a value.", "Please enter an answer before continuing."]
    out += list(BANNERS.values())
    for q in PATIENT_QUESTIONS:
        out += [q["question"], q["placeholder"]]
    return out


def render_patient_mode():

    prefetch(_ui_strings())

    initialize_patient_session()

    st.title("🏥 CuraGlide")

    st.caption(
        t("Your well-being in every step — accessed from a single touch.")
    )

    st.divider()

    # ---------------------------------------------------------
    # FINAL ANALYSIS SCREEN
    # ---------------------------------------------------------

    if st.session_state.patient_analysis:

        st.success(t("✅ CuraGlide analysis complete!"))

        analysis = st.session_state.patient_analysis

        # Urgency banner
        display_urgency_banner(analysis)

        if get_urgency_level(analysis) in ("EMERGENCY", "URGENT"):

            if st.button(
                t("🆘 Get emergency helpline numbers"),
                type="primary",
                use_container_width=True,
                key="analysis_to_help",
            ):

                st.session_state.page = "Emergency Help"
                st.rerun()

        st.markdown(t("## 🧠 AI Health Analysis"))

        # Display the AI analysis with section emojis
        display_analysis_sections(analysis)

        st.divider()

        st.info(
            t("⚠️ CuraGlide provides health information and guidance. It does not replace a qualified healthcare professional or provide a confirmed medical diagnosis.")
        )

        if st.button(
            t("🔄 Start New Health Check"),
            use_container_width=True
        ):

            reset_patient_mode()
            st.rerun()

        return

    # ---------------------------------------------------------
    # ANALYSIS ERROR
    # ---------------------------------------------------------

    if st.session_state.patient_analysis_error:

        st.error(
            t("❌ We couldn't complete the analysis.")
        )

        st.warning(
            st.session_state.patient_analysis_error
        )

        if st.button(
            t("🔄 Try Analysis Again"),
            use_container_width=True
        ):

            st.session_state.patient_analysis_error = None
            st.rerun()

        return

    # ---------------------------------------------------------
    # START ANALYSIS
    # ---------------------------------------------------------

    if st.session_state.patient_completed:

        st.success(
            t("✅ Thank you! I've collected your information.")
        )

        st.markdown(
            t("## 🧠 Analyzing your information...")
        )

        with st.spinner(
            t("CuraGlide is analyzing your information...")
        ):

            result = analyze_patient(
                st.session_state.patient_answers,
                language=current_language(),
            )

        if result.get("success"):

            st.session_state.patient_analysis = (
                result.get(
                    "analysis",
                    "No analysis returned."
                )
            )

        else:

            st.session_state.patient_analysis_error = (
                result.get(
                    "error",
                    "Unable to analyze your information."
                )
            )

        st.rerun()

        return

    # ---------------------------------------------------------
    # QUESTION SCREEN
    # ---------------------------------------------------------

    step = st.session_state.patient_step

    total_questions = len(PATIENT_QUESTIONS)

    question_data = PATIENT_QUESTIONS[step]

    progress = (step + 1) / total_questions

    st.progress(progress)

    st.caption(
        f"{t('Question')} {step + 1} / {total_questions}"
    )

    st.markdown(
        f"## {t(question_data['question'])}"
    )

    # ---------------------------------------------------------
    # QUESTION FORM
    # ---------------------------------------------------------

    with st.form(
        key=f"patient_form_{step}",
        clear_on_submit=False
    ):

        existing_answer = (
            st.session_state.patient_answers.get(
                question_data["key"]
            )
        )

        if question_data["type"] == "number":

            if existing_answer is None:
                default_value = question_data["min_value"]
            else:
                default_value = existing_answer

            user_answer = st.number_input(
                t("Your answer"),
                min_value=question_data["min_value"],
                max_value=question_data["max_value"],
                value=default_value,
                step=question_data["step"]
            )

        else:

            user_answer = st.text_area(
                t("Your answer"),
                value=existing_answer or "",
                placeholder=t(question_data["placeholder"]),
                height=120
            )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:

            previous_clicked = False

            if step > 0:

                previous_clicked = st.form_submit_button(
                    t("← Previous"),
                    use_container_width=True
                )

        with col2:

            if step == total_questions - 1:

                next_clicked = st.form_submit_button(
                    t("Analyze →"),
                    type="primary",
                    use_container_width=True
                )

            else:

                next_clicked = st.form_submit_button(
                    t("Continue →"),
                    type="primary",
                    use_container_width=True
                )

    # ---------------------------------------------------------
    # PREVIOUS BUTTON
    # ---------------------------------------------------------

    if previous_clicked:

        st.session_state.patient_step -= 1
        st.rerun()

    # ---------------------------------------------------------
    # NEXT BUTTON
    # ---------------------------------------------------------

    if next_clicked:

        valid, message = validate_answer(
            question_data,
            user_answer
        )

        if not valid:

            st.warning(t(message))

        else:

            st.session_state.patient_answers[
                question_data["key"]
            ] = user_answer

            if step == total_questions - 1:

                st.session_state.patient_completed = True

            else:

                st.session_state.patient_step += 1

            st.rerun()

    st.write("")

    # ---------------------------------------------------------
    # RESTART
    # ---------------------------------------------------------

    if st.button(
        "🔄 Restart health check",
        use_container_width=True
    ):

        reset_patient_mode()
        st.rerun()
