# 🏥 CuraGlide

**Your well-being in every step — accessed from a single touch.**

CuraGlide is a comprehensive health-information and learning platform designed to help users understand their health concerns, find nearby hospitals, and explore clinical-style cases for educational purposes. Built with **Streamlit** and powered by **Groq** AI models.

## ✨ Features

- **👤 Patient Mode:** Input basic health metrics, symptoms, and medical history. The AI acts as a cautious health-information assistant to provide an analysis of your urgency, potential conditions, and actionable advice (What to do now, What to monitor). 
- **🏥 Hospital Finder:** Enter a location (city or area) to discover nearby hospitals using the OpenStreetMap API. Get the distance to the hospital and quick access to Google Maps for navigation.
- **🧪 Case Lab:** Generate clinical-style educational cases (e.g., diagnostic mysteries, emergency presentations) based on specified topics and difficulties. Practice reasoning through symptoms, explanations, warning signs, and more.
- **🆘 Help You Need:** Enter a city or area and get the local emergency helpline numbers (e.g. Rescue 1122 / Edhi in Punjab), with one-tap call buttons and a country picker fallback.
- **🌐 Multi-language:** Pick a language in the sidebar (Urdu, Roman Urdu, Arabic, Turkish, German, and more, or type any other language). AI answers and the main screens are translated; Arabic/Urdu use a right-to-left layout.

## 🛠️ Technologies Used

- **Python** (Backend logic)
- **Streamlit** (Interactive Web UI)
- **Groq API** (LLM inference for Patient Mode and Case Lab)
- **Requests & OpenStreetMap Nominatim API** (Hospital geolocation and search)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd CuraGlide-main
   ```

2. **Install dependencies:**
   Make sure you have Python installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   You need a Groq API key to use the AI features. Set the environment variable in your terminal:
   - On Windows (Command Prompt):
     ```cmd
     set GROQ_API_KEY=your_api_key_here
     ```
   - On Windows (PowerShell):
     ```powershell
     $env:GROQ_API_KEY="your_api_key_here"
     ```
   - On macOS/Linux:
     ```bash
     export GROQ_API_KEY=your_api_key_here
     ```
   *(Optional) You can also set `GROQ_MODEL` to specify a different model. The default is `openai/gpt-oss-20b`.*

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   The app will automatically open in your default web browser at `http://localhost:8501`.

## ⚠️ Disclaimer

**Educational and Informational Use Only.** 

CuraGlide provides educational health information and does not replace a qualified healthcare professional. The generated responses and cases are not clinical advice and should not be used as a substitute for professional medical care, diagnosis, or treatment. Always consult with a doctor for serious or worsening symptoms.
