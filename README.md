# 📄 DocChat AI — AI-Powered Document Chatbot

An intelligent document assistant that allows users to upload **PDFs, scanned PDFs, images, and text files**, then ask questions in natural language. The application uses **Google Gemini AI** for question answering and **OCR (Optical Character Recognition)** to extract text from scanned documents and images.

---

## 🚀 Live Demo

🔗 **Live App:** https://YOUR-STREAMLIT-APP.streamlit.app

---

## ✨ Features

* 📄 Chat with Text PDFs
* 🖼️ OCR support for Scanned PDFs
* 🖼️ OCR support for Images (PNG, JPG, JPEG, WEBP, TIFF)
* 📝 Read TXT files
* 💬 Multi-turn conversation with document context
* 🤖 Powered by Google Gemini AI
* ⚡ Fast and lightweight Streamlit interface
* 🔒 Answers only from the uploaded document

---

## 📸 Screenshots

> Add screenshots of your application here.

* Home Page
* Upload Document
* OCR Processing
* Chat Interface

---

## 🛠️ Tech Stack

| Layer               | Technology                                                 |
| ------------------- | ---------------------------------------------------------- |
| Frontend            | Streamlit                                                  |
| AI Model            | Google Gemini 2.5 Flash                                    |
| OCR Engine          | Tesseract OCR                                              |
| PDF OCR             | pdf2image + Poppler                                        |
| PDF Text Extraction | PyPDF2                                                     |
| Image Processing    | Pillow                                                     |
| Language            | Python 3                                                   |
| AI Pattern          | Retrieval-Augmented Prompting (Document Context Injection) |

---

## 📂 Supported File Types

| File Type     | Supported |
| ------------- | --------- |
| PDF (Text)    | ✅         |
| PDF (Scanned) | ✅ OCR     |
| PNG           | ✅ OCR     |
| JPG / JPEG    | ✅ OCR     |
| WEBP          | ✅ OCR     |
| TIFF          | ✅ OCR     |
| TXT           | ✅         |

---

# ⚡ Quick Start

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/docchat-ai.git

cd docchat-ai
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Run the Application

```bash
streamlit run app.py
```

---

## 4️⃣ Get a Free Gemini API Key

Visit:

https://aistudio.google.com/apikey

Create a free API key and paste it into the sidebar when the application starts.

---

# 📁 Project Structure

```text
docchat-ai/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── poppler/
│   └── Library/
│       └── bin/
│
└── Tesseract-OCR/
    ├── tesseract.exe
    └── tessdata/
```

---

# 🏗️ System Architecture

```
User Uploads File
        │
        ▼
PDF / Image / TXT
        │
        ▼
───────────────
Text PDF
───────────────
        │
        ▼
PyPDF2

───────────────
Scanned PDF
───────────────
        │
        ▼
pdf2image
        │
        ▼
Tesseract OCR

───────────────
Image
───────────────
        │
        ▼
Tesseract OCR

        ▼
Extracted Text
        │
        ▼
Google Gemini
        │
        ▼
Document-Aware Response
        │
        ▼
Streamlit Chat Interface
```

---

# 📊 Key Highlights

* 📄 Supports multiple document formats
* 🔍 OCR for scanned documents and images
* 💬 Context-aware conversations
* ⚡ Fast response using Gemini AI
* 🎯 Restricts answers to uploaded document content
* 🔄 Supports follow-up questions
* ☁️ Ready for Streamlit Cloud deployment

---

# 📦 Requirements

* Python 3.10+
* Streamlit
* Google Generative AI SDK
* PyPDF2
* Pillow
* pdf2image
* pytesseract

If using OCR locally:

* Tesseract OCR installed
* Poppler installed

---

# 🌐 Deployment

## GitHub

```bash
git init

git add .

git commit -m "Initial Commit"

git branch -M main

git remote add origin https://github.com/YOUR_USERNAME/docchat-ai.git

git push -u origin main
```

## Streamlit Cloud

1. Push the project to GitHub.
2. Open https://share.streamlit.io
3. Connect your GitHub account.
4. Select the repository.
5. Choose **app.py** as the entry point.
6. Deploy the application.

---

# 📈 Future Improvements

* Support DOCX and PPTX files
* Voice-based document chat
* Document summarization
* Citation highlighting
* Multi-document search
* Chat export (PDF/TXT)
* User authentication

---

# 👨‍💻 Author

**Ketan Shaw**

GitHub: https://github.com/YOUR_USERNAME

LinkedIn: https://linkedin.com/in/YOUR_LINKEDIN

---

## ⭐ If you found this project useful, don't forget to star the repository!
