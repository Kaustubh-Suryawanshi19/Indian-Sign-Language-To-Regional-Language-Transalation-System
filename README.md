<div align="center">

# 🤟 MudraTranslate

### Real-Time Indian Sign Language → Multilingual Communication

**Signs Beyond Barriers**

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/YOLOv8-Computer%20Vision-111111?style=for-the-badge" alt="YOLOv8">
  <img src="https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google" alt="Gemini AI">
  <img src="https://img.shields.io/badge/OpenCV-Real--Time-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/MIT-License-2EA44F?style=for-the-badge" alt="MIT License">
</p>

<p>
  <strong>Capture → Detect → Understand → Translate</strong>
</p>

</div>

---

## 🎯 What is MudraTranslate?

**MudraTranslate** is an AI-powered computer-vision system designed to recognize Indian Sign Language (ISL) gestures from a live camera feed and convert recognized gestures into meaningful language.

The system combines a custom-trained **YOLOv8** object-detection model with a temporal/translation layer and an **LLM-powered language-generation stage** to move beyond isolated gesture labels toward readable, context-aware sentences.

The project is designed around a simple goal:

> **Make communication more accessible by turning visual sign-language gestures into understandable language in real time.**

---

## ✨ Key Features

- 🎥 **Real-time camera input** for live gesture recognition
- 🤟 **Custom-trained YOLOv8 model** for ISL gesture detection
- 🧠 **AI-assisted sentence generation** using Google Gemini
- 🌐 **Multilingual output** across supported Indian languages
- 🔄 **Frame-to-frame prediction handling** to reduce noisy detections
- 📊 **Confidence-aware detection** for model predictions
- 🖥️ **Interactive application interface**
- 🌍 **Web-accessible detection workflow** through Flask
- 🧩 Modular design that can be extended with additional gestures and languages

### Current demonstrated coverage

| Capability | Coverage |
|---|---:|
| Supported output languages | **5+** |
| ISL gesture vocabulary | **14+** |
| Detection | **Real-time** |
| AI sentence generation | **Yes** |
| Computer vision model | **YOLOv8** |

> The gesture vocabulary is intentionally constrained to the classes included in the project's trained dataset/model.

---

# 📸 Product Experience

## Home / Product Landing Page

MudraTranslate presents the project as an accessibility-focused AI product, explaining the problem, the gesture-to-language pipeline, supported languages and real-world impact areas.

## Live Detection

The detection workflow takes camera/video input and passes frames through the trained YOLOv8 model.

A simplified interaction looks like:

```text
Camera / Video
      ↓
Frame Capture
      ↓
YOLOv8 Detection
      ↓
Confidence Filtering
      ↓
Gesture Sequence
      ↓
Temporal Processing
      ↓
Context / Sentence Generation
      ↓
Language Translation
      ↓
Readable Output
```

---

# 🧠 How It Works

MudraTranslate is organized as a multi-stage pipeline.

### 1. Capture

A webcam or video source provides frames to the application.

```text
Camera
  ↓
Live Video Frames
```

### 2. Detect

Each relevant frame is processed by the custom-trained **YOLOv8** model.

```text
Frame
  ↓
YOLOv8
  ↓
Bounding Box + Class + Confidence
```

The detector is responsible for answering:

> **"Which known ISL gesture is present in this frame?"**

### 3. Stabilize / Process Predictions

Real-time detection can produce frame-to-frame variation. Predictions are therefore filtered and processed before being passed to the language layer.

This helps reduce unstable output caused by individual-frame noise.

### 4. Understand

Detected gestures are converted into a sequence that can be interpreted as a meaningful expression.

The language-generation layer uses **Google Gemini** to help transform the detected gesture information into a more natural sentence.

```text
Detected Gesture Sequence
          ↓
      Context Layer
          ↓
      Gemini / LLM
          ↓
   Meaningful Sentence
```

### 5. Translate

The resulting meaning can be presented in supported Indian languages.

Current project presentation includes:

- 🇬🇧 English
- 🇮🇳 Hindi
- 🟠 Marathi
- 🟣 Punjabi
- 🟣 Tamil

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │   Webcam / Video     │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │   Frame Processing   │
                         │       OpenCV         │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │   Custom YOLOv8      │
                         │      Detector        │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ Confidence Filtering │
                         │  + Prediction Logic  │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ Gesture Sequence /   │
                         │ Temporal Processing  │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │  Gemini / LLM Layer  │
                         │ Sentence Generation  │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ Multilingual Output  │
                         └──────────┬───────────┘
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
             Desktop / UI                    Flask Web App
```

---

# 🔬 Computer Vision Model

## YOLOv8

MudraTranslate uses **YOLOv8** as the core gesture-detection model.

YOLO was selected because the project requires:

- object detection rather than only image classification
- localization of the gesture within the frame
- fast inference suitable for interactive applications
- a practical training/inference workflow
- support for custom datasets

### Detection output

For each detected gesture, the model can provide:

```text
Class
Confidence
Bounding Box
```

Example:

```text
Gesture: I Love You
Confidence: 0.96
Bounding Box: [x1, y1, x2, y2]
```

---

# 🧪 Dataset & Training Concept

The detector is trained on a project-specific ISL gesture dataset.

The general training workflow is:

```text
ISL Images / Video Frames
          ↓
      Annotation
          ↓
    Dataset Split
          ↓
   YOLO Data Format
          ↓
     Model Training
          ↓
    Validation / Test
          ↓
   Best Model Weights
          ↓
    Real-Time Inference
```

For future expansion, additional gesture classes can be added by collecting representative samples, annotating them consistently, retraining the model and evaluating the new model against the existing baseline.

---

# 🤖 AI / Language Layer

YOLOv8 identifies **what gesture is visible**.

That alone does not guarantee a natural sentence.

MudraTranslate therefore separates:

```text
Computer Vision
     ↓
Gesture Recognition
     ↓
Language Understanding
     ↓
Sentence Generation
```

The Gemini API is used as the AI language layer for generating more meaningful, context-aware textual output from the recognized gesture information.

This separation is important because:

- the vision model focuses on recognition
- the language model focuses on interpretation/generation
- each component can be improved independently

---

# 🌐 Application Layer

The project includes a **Flask-based web application** for exposing the detection workflow.

The application layer connects:

```text
Browser / Client
      ↓
Flask
      ↓
Detection Pipeline
      ↓
YOLOv8
      ↓
AI / Translation Layer
      ↓
Result
```

The project also contains an interactive desktop/application interface for demonstrating the computer-vision workflow.

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| Computer Vision | OpenCV |
| Object Detection | YOLOv8 |
| Model Training | Ultralytics |
| AI / LLM | Google Gemini API |
| Web Framework | Flask |
| Desktop UI | PyQt5 |
| Development | Jupyter Notebook / Python |
| Version Control | Git / GitHub |

---

# 📁 Project Structure

```text
MudraTranslate/
│
├── app.py                         # Desktop application entry point
├── src/isl_translator/            # Shared detection, temporal, translation logic
├── web_app/                       # Flask web application
│   ├── templates/                 # Web pages
│   └── static/                    # CSS, JavaScript and web assets
├── scripts/                       # Utility / dataset scripts
├── training/notebooks/            # Model training and experimentation
├── assets/fonts/                  # Multilingual UI fonts
├── models/                        # Trained YOLOv8 model
├── artifacts/                     # Training evaluation artifacts
├── tests/                         # Automated tests
├── requirements.txt               # Full runtime dependencies
├── requirements-web.txt           # Web runtime dependency profile
├── requirements-training.txt      # Training / notebook dependencies
├── .env.example                   # Environment variable template
├── .github/workflows/ci.yml       # GitHub Actions validation
├── SECURITY.md                    # Security guidance
├── LICENSE                        # MIT license
└── README.md                      # Project documentation
```

Generated caches, local environments, secrets, OS metadata and temporary files are excluded from version control.

# 🚀 Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/Kaustubh-Suryawanshi19/Indian-Sign-Language-To-Regional-Language-Transalation-System.git
cd Indian-Sign-Language-To-Regional-Language-Transalation-System
```

## 2. Create a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure environment variables

If the application requires an external AI API key, create a local `.env` file from the project's example configuration:

```bash
cp .env.example .env
```

Add the required credentials locally.

**Never commit real API keys or `.env` files to GitHub.**

## 5. Run the application

Use the project's configured Flask entry point, for example:

```bash
python app.py
```

If the repository uses a different entry file, use the command documented by that file.

---

# 🧪 Testing & Quality

Before publishing a release, the project should be checked through the available automated tests and Python validation tools.

Recommended checks:

```bash
pytest -q
```

```bash
python -m compileall -q src tests web_app app.py scripts/dataset_creation.py
```

If Ruff is configured:

```bash
ruff check .
```

The goal is to keep the repository in a reproducible state and catch:

- syntax errors
- import errors
- broken application modules
- regression issues
- configuration problems
- code-quality issues

---

# 🔐 Security

MudraTranslate may use an external AI API.

Therefore:

- never hard-code API keys
- keep secrets in environment variables
- keep `.env` ignored by Git
- provide `.env.example` without real credentials
- do not commit private datasets or credentials
- validate uploaded/user-provided files before processing them

---

# 🌍 Real-World Impact

The project is intended to explore how computer vision and AI can reduce communication barriers for people who use sign language.

Potential application areas include:

### 🎓 Education

Supporting communication between students, teachers and institutions.

### 🏥 Healthcare

Helping improve communication between patients, healthcare staff and service providers.

### 🏛️ Public Services

Supporting accessibility in government offices, transportation and public-facing services.

### 🤝 Social Inclusion

Making everyday communication more accessible across hearing and deaf communities.

> This project is a technology prototype and should not be treated as a replacement for professional human interpreters in high-stakes situations.

---

# 📈 Limitations

Real-time sign-language translation is a challenging computer-vision and language-understanding problem.

Important limitations include:

- limited gesture vocabulary compared with full ISL
- sensitivity to lighting and camera quality
- variations in signer appearance and signing style
- occlusion and complex backgrounds
- ambiguity between visually similar gestures
- frame-level detection does not by itself represent complete sign-language grammar
- generated language output can require validation
- performance depends on hardware and model configuration

These limitations are important when interpreting demo results.

---

# 🚀 Future Improvements

The project can be extended toward a more complete sign-language translation system.

### Computer Vision

- [ ] Expand the ISL gesture vocabulary
- [ ] Add more diverse training samples
- [ ] Improve detection under different lighting/background conditions
- [ ] Optimize inference speed
- [ ] Evaluate additional YOLO model variants

### Temporal Understanding

- [ ] Improve gesture-sequence modeling
- [ ] Add stronger temporal smoothing
- [ ] Detect continuous signing
- [ ] Model sign-language grammar and ordering

### AI / NLP

- [ ] Improve context-aware sentence generation
- [ ] Add configurable LLM providers
- [ ] Improve multilingual translation quality
- [ ] Add speech output
- [ ] Add confidence and uncertainty explanations

### Product

- [ ] Mobile application
- [ ] Better accessibility controls
- [ ] User profiles and personalization
- [ ] Offline inference where practical
- [ ] Production deployment
- [ ] Automated CI/CD
- [ ] Model monitoring and evaluation dashboards

---

# 🎓 Why These Technologies?

| Technology | Why it fits the project |
|---|---|
| **YOLOv8** | Fast object detection with bounding-box localization and practical custom training |
| **OpenCV** | Camera capture and real-time frame processing |
| **Python** | Strong ecosystem for computer vision, ML and AI integration |
| **Gemini API** | Adds language-level interpretation and sentence generation after gesture recognition |
| **Flask** | Lightweight way to expose the Python detection pipeline through a web application |
| **PyQt5** | Suitable for an interactive Python desktop demonstration |
| **Git/GitHub** | Version control, collaboration and reproducible project history |

The architecture intentionally separates **vision**, **language understanding**, and **application delivery** so individual components can be improved without redesigning the complete system.

---

# 🔄 End-to-End Pipeline

```text
┌──────────────────┐
│  Webcam / Video  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Frame Acquisition│
└────────┬─────────┘
         ↓
┌──────────────────┐
│ OpenCV Processing│
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Custom YOLOv8    │
│ Gesture Detector │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Confidence /     │
│ Temporal Filter  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Gesture Sequence │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Gemini / LLM     │
│ Understanding    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Sentence /       │
│ Translation      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ User Output      │
└──────────────────┘
```

---

# 📌 Project Status

**Current status:** Working prototype / portfolio project.

The project demonstrates the complete concept from real-time ISL gesture detection through AI-assisted language output. Further dataset expansion, continuous-sign recognition, evaluation and production hardening are planned improvements.

---

# 👨‍💻 Author

## Kaustubh Suryawanshi

**Computer Science Engineering · Data Science · AI/ML**

- GitHub: [Kaustubh-Suryawanshi19](https://github.com/Kaustubh-Suryawanshi19)
- Project: [Indian Sign Language to Regional Language Translation System](https://github.com/Kaustubh-Suryawanshi19/Indian-Sign-Language-To-Regional-Language-Transalation-System)

---

# 📄 License

This project is released under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

---

<div align="center">

### 🤟 MudraTranslate

**Signs Beyond Barriers**

*Turning gestures into meaningful communication with Computer Vision + AI.*

</div>
