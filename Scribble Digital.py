import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import easyocr
import google.genai as genai
from dotenv import load_dotenv
import json

# ────────────────────────────────────────────────
#               CONFIGURATION
# ────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    API_KEY = "AIzaSyB2zz_uWdtvdFwIjhyvtYQi95oRfOe4umU"  # fallback (remove in production!)

st.set_page_config(
    page_title="Scribble Digital",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────
#               CUSTOM CSS - Modern Glassmorphism
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg: #f8f9fc;
        --card-bg: rgba(255, 255, 255, 0.78);
        --card-border: rgba(200, 200, 220, 0.4);
        --accent: #ff4d4f;
        --accent-dark: #d9363e;
        --text: #1a1a2e;
        --text-muted: #6b7280;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.72);
            --card-border: rgba(100, 116, 139, 0.45);
            --text: #e2e8f0;
            --text-muted: #94a3b8;
        }
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
        background-image: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.70));
        font-family: 'Inter', sans-serif;
        color: var(--text);
        min-height: 100vh;
        overflow-x: hidden;
    }

    .stApp > header { display: none; }

    /* Glass cards */
    .glass-card {
        background: var(--card-bg) !important;
        backdrop-filter: blur(14px) saturate(180%);
        -webkit-backdrop-filter: blur(14px) saturate(180%);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 32px rgba(0,0,0,0.10);
        margin-bottom: 28px;
    }

    /* Hero upload area */
    .upload-hero {
        text-align: center;
        padding: 3.5rem 1.5rem;
        background: linear-gradient(135deg, rgba(255,77,79,0.09), rgba(255,143,143,0.06));
        border-radius: 20px;
        border: 2px dashed var(--accent);
        margin: 1.5rem 0 2.5rem 0;
        transition: all 0.3s ease;
    }
    .upload-hero:hover {
        border-color: var(--accent-dark);
        background: linear-gradient(135deg, rgba(255,77,79,0.13), rgba(255,143,143,0.09));
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, var(--accent), #ff7875) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2.2rem !important;
        font-weight: 600 !important;
        font-size: 1.08rem !important;
        transition: all 0.28s ease;
        box-shadow: 0 5px 16px rgba(255,77,79,0.28) !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 28px rgba(255,77,79,0.38) !important;
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Sidebar cleanup */
    section[data-testid="stSidebar"] {
        background: transparent !important;
        border-right: 1px solid var(--card-border) !important;
    }

    /* Better headers & spacing */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
        letter-spacing: -0.4px;
        color: var(--text);
    }

    .stExpander {
        border-radius: 12px !important;
        border: none !important;
        background: rgba(0,0,0,0.04) !important;
    }

    hr {
        border-color: var(--card-border) !important;
    }
    /* Hero styling */
    .hero {
        max-width: 900px;
        margin: 0 auto 2rem auto;
        padding: 2.25rem 2.25rem 2.5rem 2.25rem;
        border-radius: 24px;
        border: 1px solid rgba(200,200,220,0.5);
        background: linear-gradient(135deg, rgba(255,77,79,0.12), rgba(255,143,143,0.08));
        box-shadow: 0 22px 50px rgba(0,0,0,0.12);
        text-align: center;
    }

    .hero h1 {
        margin: 0 0 0.5rem 0;
        font-size: 2.65rem;
        letter-spacing: -0.4px;
        color: var(--text);
    }

    .hero p {
        margin: 0;
        font-size: 1.2rem;
        color: var(--text-muted);
    }

    .hint {
        display: inline-flex;
        gap: 0.4rem;
        padding: 0.65rem 0.85rem;
        border-radius: 14px;
        background: rgba(255,255,255,0.35);
        border: 1px solid rgba(255,255,255,0.45);
        font-size: 0.95rem;
        color: var(--text);
        margin-top: 0.7rem;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 18px;
        margin-top: 1.35rem;
    }

    .feature-card {
        border-radius: 18px;
        padding: 16px 18px;
        background: rgba(255, 255, 255, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.35);
        box-shadow: 0 12px 30px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, background 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        background: rgba(255, 255, 255, 0.50);
    }

    .feature-card h4 {
        margin: 0 0 0.45rem 0;
        font-size: 1.05rem;
        letter-spacing: -0.3px;
    }

    .feature-card p {
        margin: 0;
        font-size: 0.95rem;
        color: rgba(28, 30, 37, 0.9);
    }

    .footer-links {
        display: flex;
        gap: 1.4rem;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 1.1rem;
        font-size: 0.88rem;
        color: rgba(0,0,0,0.55);
    }
    .footer-links a {
        color: rgba(0,0,0,0.65);
        text-decoration: none;
    }
    .footer-links a:hover {
        text-decoration: underline;
        color: rgba(0,0,0,0.85);
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
#               SIDEBAR
# ────────────────────────────────────────────────
with st.sidebar:
    st.title("✍️ Scribble")
    st.caption("v1.3 • Handwriting → Digital")

    st.divider()

    st.markdown("### Model")
    selected_model = st.selectbox(
        "Gemini Model",
        options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("### Quick Tips")
    st.markdown(
        "<div class='hint'>" 
        "<span>💡</span> Upload clear handwriting for best OCR accuracy." 
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='hint'>" 
        "<span>🔁</span> Convert again if results look partial." 
        "</div>",
        unsafe_allow_html=True
    )
st.markdown(
    "<div class='hero'><h1>Scribble Digital</h1><p>Turn messy handwriting into clean notes & actionable tasks — instantly.</p></div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='feature-grid'>"
    "<div class='feature-card'><h4>🧠 Smart OCR + AI</h4><p>Automatically read handwriting, then structure it into notes + action items.</p></div>"
    "<div class='feature-card'><h4>🧩 One-click workflow</h4><p>Upload an image, press convert, and download the JSON output instantly.</p></div>"
    "<div class='feature-card'><h4>🔒 Privacy-first</h4><p>Nothing is stored locally unless you download the export file.</p></div>"
    "</div>",
    unsafe_allow_html=True
)

# Hero upload area
with st.container():
    st.markdown('<div class="upload-hero glass-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your handwritten note here or click to browse",
        type=["jpg", "jpeg", "png"],
        help="Best results with good lighting and straight paper"
    )
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    # Load image
    pil_image = Image.open(uploaded_file)
    opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # ── Two-column layout ────────────────────────────────
    left_col, right_col = st.columns([5, 5], gap="large")

    with left_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📸 Original Photo")
        st.image(pil_image, width="stretch")

        with st.expander("🔍 OCR Preparation Preview", expanded=False):
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.4, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            st.image(enhanced, width="stretch", clamp=True,
                     caption="Contrast-enhanced for better character detection")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("✨ Digital Conversion")

        convert_button = st.button(
            "Convert Handwriting → Structured Digital Notes",
            type="primary",
            width="stretch",
            help="Uses EasyOCR + Gemini to extract notes & tasks"
        )

        if convert_button:
            with st.spinner("Reading handwriting and structuring content..."):
                response = None
                response_text = ""
                try:
                    # OCR
                    reader = easyocr.Reader(['en'], gpu=False)
                    ocr_result = reader.readtext(opencv_image, detail=0, paragraph=True)
                    raw_text = "\n".join(str(line).strip() for line in ocr_result if line)

                    # Gemini / Google GenAI
                    client = genai.Client(api_key=API_KEY)

                    prompt = f"""You are an expert at understanding messy handwritten notes.
Extract and clean the content from the following text.
Return **only valid JSON** with exactly these two keys:

{{
  "notes": "A clean, well-formatted markdown summary of the entire content",
  "todos": ["array", "of", "clear", "actionable", "task", "strings"]
}}

If no tasks are found, return empty array for todos.
Do NOT include any other text outside the JSON.

Handwritten text:
{raw_text}
"""

                    response = client.models.generate_content(
                        model=selected_model,
                        contents=prompt
                    )
                    response_text = str(response.text or "").strip()

                    # Clean possible markdown code fences
                    if response_text.startswith("```json"):
                        response_text = response_text.split("```json")[1].split("```")[0].strip()

                    data = json.loads(response_text)

                    # Show results
                    st.success("Conversion complete!")

                    st.markdown("##### 📝 Cleaned Notes")
                    st.markdown(data.get("notes", "— No summary generated —"))

                    st.markdown("##### ✅ Action Items")
                    todos = data.get("todos", [])
                    if todos:
                        for i, task in enumerate(todos):
                            st.checkbox(task, key=f"task_{i}_{hash(uploaded_file.name)}")
                    else:
                        st.info("No clear action items detected in the note.")

                    # Export
                    st.divider()
                    export_data = json.dumps(data, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download JSON Export",
                        data=export_data,
                        file_name="scribble_digital_export.json",
                        mime="application/json",
                        width="stretch"
                    )

                except json.JSONDecodeError:
                    st.error("AI returned invalid JSON format. Raw response:\n\n" + response_text)
                except Exception as e:
                    err_str = str(e)

                    if "models/" in err_str and "NOT_FOUND" in err_str:
                        st.error(
                            "Model not supported by your API/key. "
                            "Try selecting a different Gemini model from the sidebar."
                        )
                        st.stop()

                    if "RESOURCE_EXHAUSTED" in err_str or "quota exceeded" in err_str.lower():
                        retry_note = ""
                        if "retryDelay" in err_str:
                            # Try to extract a simple delay hint (best-effort)
                            import re
                            m = re.search(r"retryDelay'?:\s*'?(\d+s)" , err_str)
                            if m:
                                retry_note = f" Please try again in {m.group(1)}."

                        st.error(
                            "Quota exhausted for your Gemini key. "
                            "Check your Google Cloud billing/quotas and retry later." + retry_note
                        )
                        st.stop()

                    st.error(f"Processing error: {err_str}")

        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption(
    "Scribble Digital v1.3  •  "
    "EasyOCR + Google Gemini  •  "
    "Made with focus in Chennai"
)

st.markdown(
    "<div class='footer-links'>"
    "<a href='https://ai.google.dev/gemini' target='_blank'>Gemini docs</a>"
    "<a href='https://github.com/JaidedAI/EasyOCR' target='_blank'>EasyOCR</a>"
    "<a href='https://streamlit.io' target='_blank'>Streamlit</a>"
    "</div>",
    unsafe_allow_html=True
)