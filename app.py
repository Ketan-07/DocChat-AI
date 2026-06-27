import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
import os
import sys
import shutil
import platform
import tempfile

import pytesseract

# ── OCR imports (graceful fallback if not installed) ──────────────────────────
try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_bytes

    OCR_AVAILABLE = True

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Portable paths inside project
    LOCAL_TESS = os.path.join(BASE_DIR, "Tesseract-OCR", "tesseract.exe")
    LOCAL_POPPLER = os.path.join(BASE_DIR, "poppler", "Library", "bin")

    if os.path.exists(LOCAL_TESS) and os.path.exists(LOCAL_POPPLER):

        # Use bundled tools from project folder
        pytesseract.pytesseract.tesseract_cmd = LOCAL_TESS
        POPPLER_PATH = LOCAL_POPPLER

    elif platform.system() == "Windows":

        # Use system-installed tools
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"

    else:

        # Streamlit Community Cloud (Linux)
        pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")
        POPPLER_PATH = None

except ImportError:
    OCR_AVAILABLE = False

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="DocChat AI", page_icon="📄", layout="centered")

st.markdown("""
<style>
    .main { max-width: 750px; margin: auto; }
    .stChatMessage { border-radius: 12px; }
    .ocr-badge { background:#fef9c3; border:1px solid #fde047;
                 border-radius:8px; padding:6px 12px; font-size:13px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    st.caption("Free key → aistudio.google.com/apikey")
    st.divider()

    st.markdown("### 🔍 OCR Mode")
    use_ocr = st.toggle("Enable OCR", value=False,
                        help="Use for scanned PDFs or image files that have no selectable text")
    if use_ocr and not OCR_AVAILABLE:
        st.warning("OCR libraries not installed. Run:\n```\npip install pytesseract Pillow pdf2image\n```\nAlso install Tesseract:\nwindows → github.com/UB-Mannheim/tesseract/wiki")
    elif use_ocr and OCR_AVAILABLE:
        st.success("OCR ready ✅")

    st.divider()
    st.markdown("### 📌 Supported files")
    st.markdown("""
| File | Mode |
|------|------|
| PDF | Normal |
| Scanned PDF | OCR |
| PNG / JPG / WEBP / TIFF | OCR |
| TXT | Normal |
""")
    st.divider()
    st.markdown("### 📊 Tech Stack")
    st.markdown("- `Python` + `Streamlit`\n- `Google Gemini 2.5 Flash`\n- `PyPDF2` — text PDFs\n- `Tesseract OCR` — scanned/images\n- `pdf2image` + `Pillow`")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("📄 DocChat AI")
st.caption("Upload any document or image — powered by Gemini + Tesseract OCR")

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("messages", []), ("doc_content", ""), ("doc_name", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Text extraction helpers ───────────────────────────────────────────────────
def extract_normal_pdf(file):
    try:
        reader = PdfReader(file)
    except Exception:
        return ""

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            text += extracted

            text += "\n"

    return text

def extract_with_ocr_pdf(file_bytes):
    """OCR for scanned PDFs"""

    try:
        pages = convert_from_bytes(
            file_bytes,
            dpi=250,
            poppler_path=POPPLER_PATH
        )

    except Exception:
        st.error(
            """
    ❌ OCR failed.

    Possible reasons:

    • Poppler is not installed correctly.

    • The PDF is password protected.

    • The PDF is corrupted.
    """
        )
        return ""

    text = ""

    progress = st.progress(0)

    for i, page in enumerate(pages):
        progress.progress((i + 1) / len(pages))

        text += pytesseract.image_to_string(page)

        text += "\n"

    progress.empty()

    return text

def extract_image_ocr(file):
    """Tesseract directly on image files."""

    img = Image.open(file).convert("RGB")

    text = pytesseract.image_to_string(
        img,
        config="--oem 3 --psm 6"
    )

    if not text.strip():
        st.warning("⚠️ OCR could not detect any text in the image.")

    return text

def extract_text(file, use_ocr):
    """Smart router: pick the right extraction method."""
    ftype = file.type

    # Plain text
    if ftype == "text/plain":
        return file.read().decode("utf-8", errors="ignore")

    # Image files
    if ftype in ("image/png", "image/jpeg", "image/jpg", "image/webp", "image/tiff"):
        if not OCR_AVAILABLE:
            st.error("❌ OCR libraries not installed. See sidebar for instructions.")
            st.stop()
        with st.spinner("Running OCR on image…"):
            return extract_image_ocr(file)

    # PDF
    if ftype == "application/pdf":
        if use_ocr:
            if not OCR_AVAILABLE:
                st.error("❌ OCR libraries not installed. See sidebar for instructions.")
                st.stop()
            file_bytes = file.read()
            with st.spinner("Running OCR on scanned PDF…"):
                return extract_with_ocr_pdf(file_bytes)
        else:
            text = extract_normal_pdf(file)
            # Auto-fallback: if normal extraction gets < 50 chars, suggest OCR
            if len(text.strip()) < 50:
                st.warning("⚠️ Very little text found. This might be a scanned PDF — try enabling **OCR Mode** in the sidebar.")
            return text

    return ""

# ── Gemini call ───────────────────────────────────────────────────────────────
def ask_gemini(api_key, doc_name, doc_content, history):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    system = f"""You are a helpful document assistant.
Answer questions ONLY based on the document content below.
If the answer is not in the document, say: "This information is not in the document."
Be concise and accurate.

DOCUMENT: {doc_name}
---
{doc_content[:50000]}
---"""

    gemini_history = []
    for i, msg in enumerate(history[:-1]):
        role = "user" if msg["role"] == "user" else "model"
        content = (system + "\n\nUser: " + msg["content"]) if i == 0 and role == "user" else msg["content"]
        gemini_history.append({"role": role, "parts": [content]})

    chat = model.start_chat(history=gemini_history)
    last_msg = history[-1]["content"]
    if not gemini_history:
        last_msg = system + "\n\nUser question: " + last_msg

    return chat.send_message(last_msg).text

# ── File uploader ─────────────────────────────────────────────────────────────
accepted_types = ["pdf", "txt", "png", "jpg", "jpeg", "webp", "tiff"]
uploaded_file = st.file_uploader(
    "Upload document or image",
    type=accepted_types,
    help="Text PDF, Scanned PDF, TXT, PNG, JPG, WEBP, TIFF"
)

if uploaded_file:
    file_key = uploaded_file.name + str(use_ocr)   # re-extract if OCR toggled
    if file_key != st.session_state.doc_name:
        with st.spinner("Extracting text…"):
            text = extract_text(uploaded_file, use_ocr)
            if not text.strip():
                st.error("⚠️ No text could be extracted. If this is a scanned file, enable OCR in the sidebar.")
                st.stop()
            st.session_state.doc_content = text
            st.session_state.doc_name    = file_key
            st.session_state.messages    = []

    # Stats
    word_count = len(st.session_state.doc_content.split())
    c1, c2, c3 = st.columns(3)
    c1.metric("📄 File",     uploaded_file.name[:18] + "…")
    c2.metric("📝 Words",    f"{word_count:,}")
    c3.metric("💬 Messages", len(st.session_state.messages))

    # OCR badge
    if use_ocr and OCR_AVAILABLE:
        st.markdown('<div class="ocr-badge">🔍 OCR mode active — scanned text extracted</div>',
                    unsafe_allow_html=True)
        st.write("")

    st.success(f"✅ Ready — **{uploaded_file.name}**")
    st.divider()

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask anything about your document…")
    if user_input:
        if not api_key:
            st.error("⚠️ Enter your Gemini API key in the sidebar first.")
            st.stop()

        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    answer = ask_gemini(api_key, uploaded_file.name,
                                        st.session_state.doc_content,
                                        st.session_state.messages)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:

                    err = str(e)

                    if "API_KEY" in err.upper():

                        st.error("❌ Invalid Gemini API Key.")

                    elif "quota" in err.lower():

                        st.error("❌ Gemini quota exceeded.")

                    elif "PDFInfoNotInstalledError" in err:

                        st.error("❌ Poppler is missing or configured incorrectly.")

                    elif "TesseractNotFoundError" in err:

                        st.error("❌ Tesseract is not installed.")

                    else:

                        st.error(err)

    if st.session_state.messages:
        if st.button("🗑️ Clear chat"):
            st.session_state.messages = []
            st.rerun()

else:
    st.info("👆 Upload a PDF, image (PNG/JPG), or TXT file to get started.")
    st.markdown("""
### 💡 What you can do
- 📄 **Text PDFs** — ask questions instantly
- 🖼️ **Scanned PDFs & Images** — enable OCR in sidebar first
- 📝 **TXT files** — notes, logs, any plain text
- 🔁 **Follow-up questions** — chat remembers context
    """)
    st.markdown("---")
    st.markdown("**🔑 Free API key →** [aistudio.google.com/apikey](https://aistudio.google.com/apikey)")
