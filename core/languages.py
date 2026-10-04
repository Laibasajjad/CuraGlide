"""Multi-language support for CuraGlide.

- language_selector(): sidebar dropdown (+ "Other" free-text for any language)
- t(text): translate a UI string into the selected language (cached, falls back to English)
- prefetch(list): translate many strings in ONE API call so pages load fast
- apply_rtl(): right-to-left layout (and an Urdu font) for Arabic, Urdu, Persian, Hebrew...

Numbers (helplines) are NEVER translated by the model - only labels.
"""
import os
import json
import streamlit as st

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# (label shown in dropdown, language name sent to the model)
LANGS = [
    ("English", "English"),
    ("Urdu — اردو", "Urdu"),
    ("Roman Urdu (Urdu in English letters)", "Roman Urdu (Urdu written in English/Latin letters)"),
    ("Arabic — العربية", "Arabic"),
    ("Turkish — Türkçe", "Turkish"),
    ("German — Deutsch", "German"),
    ("French — Français", "French"),
    ("Spanish — Español", "Spanish"),
    ("Portuguese — Português", "Portuguese"),
    ("Italian — Italiano", "Italian"),
    ("Dutch — Nederlands", "Dutch"),
    ("Russian — Русский", "Russian"),
    ("Hindi — हिन्दी", "Hindi"),
    ("Bengali — বাংলা", "Bengali"),
    ("Persian — فارسی", "Persian"),
    ("Chinese — 中文", "Chinese (Simplified)"),
    ("Japanese — 日本語", "Japanese"),
    ("Korean — 한국어", "Korean"),
    ("Indonesian — Bahasa Indonesia", "Indonesian"),
]
OTHER = "Other… (type your language)"
RTL_WORDS = ("urdu", "arabic", "persian", "farsi", "hebrew", "pashto", "sindhi", "kurdish", "dari", "uyghur")


def language_selector():
    labels = [l for l, _ in LANGS] + [OTHER]
    choice = st.selectbox("🌐 Language / زبان / Sprache", labels, key="lang_choice")
    if choice == OTHER:
        custom = st.text_input("Your language", key="lang_custom",
                               placeholder="e.g. Pashto, Punjabi, Swahili, Greek")
        name = custom.strip() or "English"
    else:
        name = dict(LANGS)[choice]
    st.session_state.language = name
    return name


def current_language():
    return st.session_state.get("language", "English")


def is_english():
    return current_language() == "English"


def is_rtl():
    lang = current_language().lower()
    if "roman" in lang:  # Roman Urdu is written left-to-right
        return False
    return any(w in lang for w in RTL_WORDS)


def apply_rtl():
    if not is_rtl():
        return
    font = ""
    if "urdu" in current_language().lower():
        font = ("@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');"
                "[data-testid='stMain'] *{font-family:'Noto Nastaliq Urdu',serif !important;line-height:2.1;}")
    st.markdown(f"""<style>{font}
[data-testid="stMain"] .stMarkdown, [data-testid="stMain"] .stAlert,
[data-testid="stMain"] textarea, [data-testid="stMain"] input,
[data-testid="stMain"] .stCaption {{ direction: rtl; text-align: right; }}
</style>""", unsafe_allow_html=True)


# ---------------------------------------------------------------- translation
@st.cache_resource
def _store():
    return {}


def _call_translate(texts, language):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    try:
        from groq import Groq
        prompt = (
            f"Translate each string of this JSON array into {language}. Keep emojis, arrows, numbers and "
            "markdown (##, **) exactly as they are. Natural, simple wording; this is a health app. "
            'Return ONLY JSON: {"translations": [...]} with the same number of items in the same order.\n'
            + json.dumps(texts, ensure_ascii=False)
        )
        r = Groq(api_key=key).chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": "You are a precise UI translator. Return valid JSON only."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}, temperature=0, max_completion_tokens=4000)
        out = json.loads(r.choices[0].message.content).get("translations")
        if isinstance(out, list) and len(out) == len(texts):
            return [str(x) for x in out]
    except Exception:
        pass
    return None


def prefetch(texts):
    """Translate many strings in a few API calls and cache them."""
    lang = current_language()
    if lang == "English":
        return
    store = _store()
    missing = [x for x in dict.fromkeys(texts) if x and (lang, x) not in store]
    for i in range(0, len(missing), 40):
        batch = missing[i:i + 40]
        res = _call_translate(batch, lang)
        if res:
            for a, b in zip(batch, res):
                store[(lang, a)] = b


def t(text):
    """Translated text, or the original English if translation is unavailable."""
    lang = current_language()
    if lang == "English" or not text:
        return text
    store = _store()
    k = (lang, text)
    if k not in store:
        res = _call_translate([text], lang)
        if not res:
            return text
        store[k] = res[0]
    return store[k]


def lang_instruction(language):
    """Extra prompt text that makes the AI answer in the chosen language."""
    if not language or language == "English":
        return ""
    return (f"\n\nLANGUAGE: Write all human-readable text in {language}, using simple natural wording. "
            "Keep JSON keys (if JSON is requested) exactly as specified, in English.")


def select_en(label, options, **kw):
    """Selectbox that SHOWS translated options but RETURNS the original English option."""
    shown = [t(o) for o in options]
    choice = st.selectbox(label, shown, **kw)
    return options[shown.index(choice)] if choice in shown else options[0]
