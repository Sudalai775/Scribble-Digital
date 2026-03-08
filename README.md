# Scribble Digital

A Streamlit app that converts handwritten notes (images) into clean, structured digital summaries and action items using EasyOCR + Google Gemini (GenAI).

## ✅ Features

- 📸 Upload a handwriting image (JPG/PNG)
- 🧠 OCR extraction using EasyOCR
- 🧩 Clean and structure content using Google Gemini (GenAI)
- 📝 Output: clean notes + action item checklist
- 📦 Downloadable JSON export

## 🚀 Getting started

### 1) Clone / open the project

```bash
cd "<path-to>/NM PROJECT"
```

### 2) Install dependencies

The project uses a Python virtual environment. If you don’t already have one, create it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then install requirements:

```bash
python -m pip install -U pip
python -m pip install streamlit opencv-python numpy pillow easyocr google-genai python-dotenv
```

### 3) Configure the API key

Create a `.env` file with your Gemini API key:

```bash
cat > .env <<'EOF'
GEMINI_API_KEY=YOUR_API_KEY_HERE
EOF
```

If you don't set a key, the app uses a hardcoded fallback key (not recommended for production).

### 4) Run the app

```bash
python -m streamlit run new.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

## 🛠️ Notes

- If you hit quota limits, the Gemini API will return a `RESOURCE_EXHAUSTED` error.
- Models supported in the app are:
  - `gemini-1.5-flash`
  - `gemini-1.5-pro`
  - `gemini-2.0-flash`

## ❤️ Improvements

Want additional features? Some ideas:

- Add a "Try sample note" button to avoid API calls during testing
- Cache recent results for faster iteration
- Add dark/light mode toggle
- Use a custom prompt template file for easier modifications

---

Made with ❤️ using Streamlit + EasyOCR + Google Gemini
