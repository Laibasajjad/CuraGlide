import urllib.parse
import streamlit as st

from core.case_lab import (
    answer_student_question,
    generate_case,
    review_reasoning,
)
from core.hospital_finder import find_hospitals
from core.patient_mode import render_patient_mode
from core.helplines import lookup_helplines, helplines_for, country_options
from core.ui_strings import PAGE_STRINGS
from core.languages import select_en, language_selector, apply_rtl, current_language, is_english, prefetch, t


# =================================================
# PAGE CONFIG
# =================================================

st.set_page_config(
    page_title="CuraGlide",
    page_icon="🏥",
    layout="wide",
)


# =================================================
# CURAGLIDE GLOBAL THEME
# =================================================

st.markdown("""
<style>

/* =========================
   MAIN BACKGROUND
   ========================= */

.stApp {
    background:
        linear-gradient(
            135deg,
            #061A2B 0%,
            #073B4C 45%,
            #075E54 100%
        );
    color: #F5FFFF;
}

.main {
    background: transparent;
}


/* =========================
   SIDEBAR
   ========================= */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #041725 0%,
            #063B45 55%,
            #075E54 100%
        );
}

section[data-testid="stSidebar"] * {
    color: #F5FFFF !important;
}


/* =========================
   HEADINGS
   ========================= */

h1, h2, h3 {
    color: #F5FFFF !important;
    font-weight: 700;
}

p, label, span {
    color: #E8FFFF;
}


/* =========================
   BUTTONS
   ========================= */

.stButton > button {
    background:
        linear-gradient(
            135deg,
            #D62828,
            #B91C1C
        ) !important;

    color: #FFFFFF !important;

    border: 2px solid #FF6B6B !important;

    border-radius: 12px !important;

    font-weight: 700 !important;

    padding: 0.65rem 1rem;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease,
        background 0.15s ease;
}

.stButton > button:hover {
    background:
        linear-gradient(
            135deg,
            #EF4444,
            #C81E1E
        ) !important;

    color: #FFFFFF !important;

    transform: translateY(-2px);

    box-shadow:
        0 8px 20px rgba(255, 80, 80, 0.35);
}

.stButton > button:active {
    transform: translateY(0);
}


/* =========================
   HOSPITAL DIRECTIONS BUTTON
   ========================= */

.stLinkButton > a {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: 2px solid #5EEAD4 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

.stLinkButton > a:hover {
    background-color: #111111 !important;
    color: #FFFFFF !important;
}


/* =========================
   INPUT BOXES
   ========================= */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #000000 !important;

    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;

    border:
        1px solid rgba(150, 255, 245, 0.35) !important;

    border-radius: 10px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    background-color: #000000 !important;

    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;

    border: 2px solid #5EEAD4 !important;

    box-shadow:
        0 0 12px rgba(94, 234, 212, 0.25);
}


/* Placeholder */

::placeholder {
    color: #B7D8D8 !important;
    opacity: 0.8 !important;
}


/* =========================
   SELECT BOXES
   ========================= */

div[data-baseweb="select"] > div {
    background-color:
        rgba(255, 255, 255, 0.10) !important;

    border-color:
        rgba(150, 255, 245, 0.35) !important;

    color: #FFFFFF !important;
}


/* =========================
   CARDS / CONTAINERS
   ========================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        rgba(4, 31, 43, 0.55);

    border:
        1px solid rgba(94, 234, 212, 0.20);

    border-radius: 16px;

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.20);
}


/* =========================
   DIVIDERS
   ========================= */

hr {
    border-color:
        rgba(94, 234, 212, 0.25);
}


/* =========================
   PROGRESS BAR
   ========================= */

div[data-testid="stProgress"] > div > div {
    background:
        linear-gradient(
            90deg,
            #14B8A6,
            #5EEAD4
        );
}


/* =========================
   ALERTS
   ========================= */

div[data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: 12px;
}


/* =========================
   LINKS
   ========================= */

a {
    color: #5EEAD4 !important;
}


/* =========================
   CODE / MONOSPACE
   ========================= */

code {
    color: #99F6E4;
}

</style>
""", unsafe_allow_html=True)


# =================================================
# SESSION STATE
# =================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "case" not in st.session_state:
    st.session_state.case = None

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "review" not in st.session_state:
    st.session_state.review = None


# =================================================
# NAVIGATION
# =================================================

def navigate(page_name):
    st.session_state.page = page_name
    st.rerun()


# =================================================
# SIDEBAR
# =================================================

with st.sidebar:

    st.markdown("# 🏥 CuraGlide")

    language_selector()

    prefetch(
        ["🏠 Home", "👤 Patient Mode", "🏥 Hospital Finder", "🧪 Case Lab", "🆘 Help You Need"]
        + PAGE_STRINGS["_all"]
        + PAGE_STRINGS.get(st.session_state.page, [])
    )

    st.divider()

    st.caption(
        t("Your well-being in every step.")
    )

    st.divider()

    if st.button(
        t("🏠 Home"),
        use_container_width=True,
    ):
        navigate("Home")

    if st.button(
        t("👤 Patient Mode"),
        use_container_width=True,
    ):
        navigate("Patient Mode")

    if st.button(
        t("🏥 Hospital Finder"),
        use_container_width=True,
    ):
        navigate("Hospital Finder")

    if st.button(
        t("🧪 Case Lab"),
        use_container_width=True,
    ):
        navigate("Case Lab")

    if st.button(
        t("🆘 Help You Need"),
        use_container_width=True,
        key="sidebar_help",
    ):
        navigate("Emergency Help")

    st.divider()

    st.caption(
        t("Health information and education only — "
        "not a replacement for professional medical care.")
    )


apply_rtl()


# =================================================
# HOME
# =================================================

if st.session_state.page == "Home":

    st.title("🏥 CuraGlide")

    st.subheader(
        t("Your well-being in every step — accessed from a single touch.")
    )

    st.write(
        t("CuraGlide is a health-information and learning platform "
        "designed to help users understand health concerns, find "
        "nearby hospitals, and explore clinical-style cases.")
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(t("### 👤 Patient Mode"))

        st.write(
            t("Answer simple questions about your health and receive "
            "AI-generated health-information guidance.")
        )

        if st.button(
            t("Open Patient Mode →"),
            use_container_width=True,
        ):
            navigate("Patient Mode")

    with col2:

        st.markdown(t("### 🏥 Hospital Finder"))

        st.write(
            t("Find hospitals based on a location and open directions "
            "through Google Maps.")
        )

        if st.button(
            t("Open Hospital Finder →"),
            use_container_width=True,
        ):
            navigate("Hospital Finder")

    st.write("")

    col3, col4 = st.columns(2)

    with col3:

        st.markdown(t("### 🧪 Case Lab"))

        st.write(
            t("Generate clinical-style educational cases and practice "
            "reasoning through them.")
        )

        if st.button(
            t("Open Case Lab →"),
            use_container_width=True,
        ):
            navigate("Case Lab")

    with col4:

        st.markdown(t("### 💙 About CuraGlide"))

        st.write(
            t("CuraGlide provides educational health information and "
            "does not replace a qualified healthcare professional.")
        )


# =================================================
# PATIENT MODE
# =================================================

elif st.session_state.page == "Patient Mode":

    render_patient_mode()


# =================================================
# HOSPITAL FINDER
# =================================================

elif st.session_state.page == "Hospital Finder":

    st.title(t("🏥 Hospital Finder"))

    st.write(
        t("Enter a location to search for nearby hospitals.")
    )

    location = st.text_input(
        t("Location"),
        placeholder=t("Enter city, area, or location"),
    )

    if st.button(
        t("🔎 Find Hospitals"),
        use_container_width=True,
    ):

        if not location.strip():

            st.warning(
                t("Please enter a location first.")
            )

        else:

            with st.spinner(
                t("Searching for hospitals...")
            ):

                result = find_hospitals(location)

            if result.get("success"):

                hospitals = result.get(
                    "hospitals",
                    [],
                )

                if hospitals:

                    st.success(
                        f"{t('Hospitals found:')} {len(hospitals)}"
                    )

                    for hospital in hospitals:

                        with st.container(border=True):

                            name = hospital.get(
                                "name",
                                "Hospital",
                            )

                            address = hospital.get(
                                "address",
                                "Address unavailable",
                            )

                            latitude = hospital.get(
                                "latitude"
                            )

                            longitude = hospital.get(
                                "longitude"
                            )

                            st.markdown(
                                f"### 🏥 {name}"
                            )

                            st.write(address)

                            if (
                                latitude is not None
                                and longitude is not None
                            ):

                                query = urllib.parse.quote_plus(
                                    f"{latitude},{longitude}"
                                )

                                maps_url = (
                                    "https://www.google.com/maps/"
                                    f"search/?api=1&query={query}"
                                )

                                st.link_button(
                                    t("🧭 Open directions"),
                                    maps_url,
                                    use_container_width=True,
                                )

                else:

                    st.info(
                        t("No hospitals were found for this location.")
                    )

            else:

                st.error(
                    t(
                        result.get(
                            "error",
                            "Unable to find hospitals.",
                        )
                    )
                )


# =================================================
# EMERGENCY HELP (HELP YOU NEED)
# =================================================

elif st.session_state.page == "Emergency Help":

    HELP_STRINGS = [
        "🆘 Help You Need",
        "If someone is in immediate danger, call the emergency number for your area right now. Do not wait for this app.",
        "Tell us where you are and we will show the emergency helpline numbers for that place.",
        "Your city or area",
        "📍 Show helplines",
        "Please enter your city or area first.",
        "Finding helplines for your location...",
        "Could not locate that place. Pick your country instead:",
        "Country",
        "Helplines for:",
        "📞 Call",
        "We do not have verified numbers for this country. 112 works on most mobile networks worldwide, but please confirm the local number.",
        "Numbers can change. Please verify with local authorities.",
        "🏥 Find nearby hospitals",
        "👤 Describe my symptoms",
    ]

    prefetch(HELP_STRINGS)

    st.title(t("🆘 Help You Need"))

    st.error(
        t(
            "If someone is in immediate danger, call the emergency "
            "number for your area right now. Do not wait for this app."
        )
    )

    st.write(
        t(
            "Tell us where you are and we will show the emergency "
            "helpline numbers for that place."
        )
    )

    help_location = st.text_input(
        t("Your city or area"),
        placeholder=t("e.g. Rawalpindi, Lahore, Karachi, London, Dubai"),
        key="help_location",
    )

    if st.button(
        t("📍 Show helplines"),
        use_container_width=True,
        key="show_helplines",
    ):

        if not help_location.strip():

            st.warning(t("Please enter your city or area first."))

        else:

            with st.spinner(t("Finding helplines for your location...")):

                st.session_state.helpline_result = lookup_helplines(
                    help_location
                )

            st.session_state.helpline_failed = (
                st.session_state.helpline_result is None
            )

    result = st.session_state.get("helpline_result")

    # Fallback: manual country picker (works even when offline)

    if st.session_state.get("helpline_failed"):

        st.info(t("Could not locate that place. Pick your country instead:"))

        options = country_options()

        picked = st.selectbox(
            t("Country"),
            list(options.keys()),
            key="helpline_country",
        )

        result = helplines_for(options[picked])

    if result:

        place = result.get("place") or result.get("country")

        st.success(f"{t('Helplines for:')} {place}")

        labels = [label for label, _ in result["numbers"]]

        prefetch(labels)

        for label, number in result["numbers"]:

            with st.container(border=True):

                c1, c2 = st.columns([3, 1])

                with c1:

                    # The number itself is never translated.
                    st.markdown(f"### {number}")

                    st.write(t(label))

                    if not is_english():

                        st.caption(label)

                with c2:

                    tel = "tel:" + "".join(
                        ch for ch in number if ch.isdigit() or ch == "+"
                    )

                    st.link_button(
                        t("📞 Call"),
                        tel,
                        use_container_width=True,
                    )

        if not result.get("exact"):

            st.warning(
                t(
                    "We do not have verified numbers for this country. "
                    "112 works on most mobile networks worldwide, but "
                    "please confirm the local number."
                )
            )

        st.caption(t("Numbers can change. Please verify with local authorities."))

        col_a, col_b = st.columns(2)

        with col_a:

            if st.button(
                t("🏥 Find nearby hospitals"),
                use_container_width=True,
                key="help_to_hospitals",
            ):

                navigate("Hospital Finder")

        with col_b:

            if st.button(
                t("👤 Describe my symptoms"),
                use_container_width=True,
                key="help_to_patient",
            ):

                navigate("Patient Mode")


# =================================================
# CASE LAB
# =================================================

elif st.session_state.page == "Case Lab":

    st.title(t("🧪 Case Lab"))

    st.warning(
        t("⚠️ Educational use only. "
        "Cases are fictional and not clinical advice.")
    )

    # =============================================
    # CREATE CASE
    # =============================================

    if st.session_state.case is None:

        st.subheader(t("Create a Case"))

        col1, col2 = st.columns(2)

        with col1:

            topic = st.text_input(
                t("Topic"),
                placeholder=(
                    t("Neurology, cardiology, respiratory...")
                ),
            )

            difficulty = select_en(
                t("Difficulty"),
                [
                    "Beginner",
                    "Intermediate",
                    "Advanced",
                ],
            )

        with col2:

            case_type = select_en(
                t("Case type"),
                [
                    "Diagnostic mystery",
                    "Emergency presentation",
                    "Patient interview",
                    "Clinical reasoning challenge",
                    "Differential diagnosis",
                ],
            )

            custom_request = st.text_area(
                t("Optional custom request"),
                placeholder=(
                    t("Add any specific scenario or learning goal...")
                ),
            )

        if st.button(
            t("🚀 Generate New Case"),
            type="primary",
            use_container_width=True,
        ):

            if not topic.strip():

                st.warning(
                    t("Please enter a topic.")
                )

            else:

                with st.spinner(
                    t("Generating fictional case...")
                ):

                    result = generate_case(
                        topic,
                        difficulty,
                        case_type,
                        custom_request,
                        language=current_language(),
                    )

                if "error" in result:

                    st.error(
                        result["error"]
                    )

                else:

                    st.session_state.case = result.get(
                        "case"
                    )

                    st.session_state.conversation = []

                    st.session_state.review = None

                    st.rerun()


    # =============================================
    # DISPLAY CASE — CLEAN VERSION
    # =============================================

    else:

        case = st.session_state.case

        st.divider()

        st.subheader(
            case.get(
                "title",
                "Fictional Case",
            )
        )


        # Professor introduction

        professor_intro = case.get(
            "professor_intro",
            "",
        )

        if professor_intro:

            st.info(
                professor_intro
            )


        # Patient

        patient = case.get(
            "patient",
            {},
        )

        if patient:

            st.markdown(
                t("### 👤 Patient")
            )

            description = patient.get(
                "description",
                "",
            )

            if description:

                st.markdown(
                    f"**{t('Patient')}:** {description}"
                )

            opening_presentation = patient.get(
                "opening_presentation",
                "",
            )

            if opening_presentation:

                st.write(
                    opening_presentation
                )


        # Initial information

        initial_information = case.get(
            "initial_information",
            [],
        )

        if initial_information:

            st.markdown(
                t("### 📋 Initial Information")
            )

            for item in initial_information:

                st.write(
                    f"• {item}"
                )


        # Possible explanations

        possible_explanations = case.get(
            "possible_explanations",
            [],
        )

        if possible_explanations:

            st.markdown(
                t("### 🔍 Possible Explanations")
            )

            for item in possible_explanations:

                st.write(
                    f"• {item}"
                )


        # Warning signs

        warning_signs = case.get(
            "warning_signs",
            [],
        )

        if warning_signs:

            st.markdown(
                t("### ⚠️ Important Warning Signs")
            )

            for item in warning_signs:

                st.write(
                    f"• {item}"
                )


        # Professor hints

        professor_hints = case.get(
            "professor_hints",
            [],
        )

        if professor_hints:

            with st.expander(
                t("💡 Professor Hints")
            ):

                for item in professor_hints:

                    st.write(
                        f"• {item}"
                    )


        # =========================================
        # CONVERSATION HISTORY
        # =========================================

        if st.session_state.conversation:

            st.divider()

            st.subheader(
                t("💬 Conversation")
            )

            for item in st.session_state.conversation:

                st.markdown(
                    f"**{t('You')}:** {item.get('q', '')}"
                )

                st.write(
                    f"**{t('Professor')}:** "
                    + item.get(
                        "a",
                        "",
                    )
                )

                teaching_point = item.get(
                    "teaching_point",
                    "",
                )

                if teaching_point:

                    st.info(
                        f"💡 {t('Teaching point')}: {teaching_point}"
                    )

                st.divider()


        # =========================================
        # ASK PROFESSOR
        # =========================================

        st.subheader(
            t("💬 Ask the Professor")
        )

        question = st.text_input(
            t("Ask the professor a question"),
            key="case_question",
        )

        if (
            st.button(
                t("Ask Question"),
                use_container_width=True,
            )
            and question.strip()
        ):

            with st.spinner(
                t("Professor is responding...")
            ):

                answer = answer_student_question(
                    case,
                    question,
                    st.session_state.conversation,
                    language=current_language(),
                )

            if isinstance(answer, dict) and "error" in answer:

                st.error(
                    answer["error"]
                )

            else:

                if isinstance(answer, dict):

                    answer_text = answer.get(
                        "answer",
                        "",
                    )

                    teaching_point = answer.get(
                        "teaching_point",
                        "",
                    )

                else:

                    answer_text = str(answer)

                    teaching_point = ""

                st.session_state.conversation.append(
                    {
                        "q": question,
                        "a": answer_text,
                        "teaching_point": teaching_point,
                    }
                )

                st.rerun()


        # =========================================
        # REASONING REVIEW
        # =========================================

        st.divider()

        st.subheader(
            t("🧠 Review Your Reasoning")
        )

        reasoning = st.text_area(
            t("Your clinical reasoning / final thoughts"),
            placeholder=(
                t("Explain what you think is happening "
                "and why...")
            ),
            key="reasoning_input",
        )

        if st.button(
            t("🎓 Get Professor Review"),
            use_container_width=True,
        ):

            if not reasoning.strip():

                st.warning(
                    t("Please enter your reasoning first.")
                )

            else:

                with st.spinner(
                    t("Reviewing reasoning...")
                ):

                    review_result = review_reasoning(
                        case,
                        reasoning,
                        st.session_state.conversation,
                        language=current_language(),
                    )

                if (
                    isinstance(review_result, dict)
                    and "error" in review_result
                ):

                    st.error(
                        review_result["error"]
                    )

                else:

                    if isinstance(review_result, dict):

                        st.session_state.review = (
                            review_result.get(
                                "review",
                                review_result,
                            )
                        )

                    else:

                        st.session_state.review = (
                            review_result
                        )

                    st.rerun()


        # =========================================
        # DISPLAY REVIEW — CLEAN VERSION
        # =========================================

        if st.session_state.review:

            st.divider()

            st.subheader(
                t("🎓 Professor Review")
            )

            review = st.session_state.review

            if isinstance(review, dict):

                overall_feedback = review.get(
                    "overall_feedback",
                    "",
                )

                if overall_feedback:

                    st.write(
                        overall_feedback
                    )


                sections = [
                    (
                        t("✅ What Went Well"),
                        "what_went_well",
                    ),
                    (
                        t("📝 What Was Missed"),
                        "what_was_missed",
                    ),
                    (
                        t("⚠️ Important Warning Signs"),
                        "important_warning_signs",
                    ),
                ]

                for title, key in sections:

                    items = review.get(
                        key,
                        [],
                    )

                    if items:

                        st.markdown(
                            f"### {title}"
                        )

                        for item in items:

                            st.write(
                                f"• {item}"
                            )


                key_lesson = review.get(
                    "key_lesson",
                    "",
                )

                if key_lesson:

                    st.info(
                        f"💡 {t('Key lesson')}: {key_lesson}"
                    )

            else:

                st.write(
                    str(review)
                )


        # =========================================
        # START NEW CASE
        # =========================================

        st.divider()

        if st.button(
            t("🔄 Start New Case"),
            use_container_width=True,
        ):

            st.session_state.case = None

            st.session_state.conversation = []

            st.session_state.review = None

            st.rerun()
