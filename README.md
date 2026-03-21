# 🌉 SkillBridge — AI-Driven Adaptive Learning Engine

> An intelligent system that parses resumes and job descriptions to identify skill gaps and generate personalized, time-optimized training pathways for corporate onboarding.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Features

### 1. Intelligent Parsing
- **Resume Parsing**: Supports PDF, DOCX, and TXT formats
- **Skill Extraction**: NLP-based extraction using a 270+ skill taxonomy derived from O*NET
- **Experience Detection**: Automatic inference of years of experience, education level, and certifications
- **JD Analysis**: Extracts required skills, seniority level, and experience requirements from job descriptions

### 2. Dynamic Gap Analysis
- **Proficiency Estimation**: Context-based proficiency scoring (0-100) for each skill
- **Gap Classification**: Three severity levels — Critical, Important, Nice-to-Have
- **Transferable Skills**: Recognizes related skills that reduce learning time (e.g., React → Vue.js)
- **Category-Level Insights**: Aggregated gap analysis by skill domain

### 3. Adaptive Learning Pathway (Original Algorithm)
Our custom **Weighted Adaptive Scoring Algorithm** considers:

| Factor | Weight | Description |
|--------|--------|-------------|
| Gap Severity | 35% | How large the proficiency gap is |
| Prerequisite Depth | 20% | How many other skills depend on this one |
| Transferable Bonus | 20% | Quick wins from related skills already known |
| Role Priority | 25% | Positional importance in the job description |

The algorithm:
1. Scores each gap using the weighted formula
2. Maps gaps to learning modules from a 40+ course catalog
3. Resolves prerequisite dependencies (topological ordering)
4. Applies transferable skill time reductions (up to 25%)
5. Organizes modules into phased pathways (Foundation → Core → Advanced → Mastery)

### 4. Functional Web Interface
- Dark, premium UI with glassmorphism and gradient accents
- Drag-and-drop resume upload
- Interactive radar chart for gap visualization
- Phased pathway roadmap with module details
- Real-time metrics dashboard

---

## 📊 Datasets Used

| Dataset | Source | Usage |
|---------|--------|-------|
| **O*NET Skills & Knowledge** | [onetcenter.org](https://www.onetcenter.org/db_releases.html) | Skill taxonomy foundation, proficiency scales, and occupational skill relationships |
| **Kaggle Resume Dataset** | [kaggle.com](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data) | Validation and testing of skill extraction accuracy |
| **Kaggle Jobs & JD Dataset** | [kaggle.com](https://www.kaggle.com/datasets/kshitizregmi/jobs-and-job-description) | Reference for JD parsing patterns |

---

## 🤖 Models & Libraries

| Model/Library | Type | Usage |
|---------------|------|-------|
| **spaCy** | Open-source NLP | Text processing and tokenization |
| **pdfplumber** | Open-source | PDF text extraction |
| **python-docx** | Open-source | DOCX text extraction |
| **Custom NLP Pipeline** | Original | Taxonomy-based skill extraction with confidence scoring |
| **Adaptive Scoring Algorithm** | Original | Weighted gap scoring and pathway optimization |

> **Note**: All adaptive logic (gap scoring, pathway generation, transferable skill bonuses) is our **original implementation**.

---

## 📈 Validation Metrics

1. **Skill Extraction Accuracy**: Taxonomy-based matching with confidence scoring (0.6–1.0 range), validated against manually annotated resumes
2. **Gap Coverage Score**: Percentage of required skills correctly identified and assessed
3. **Pathway Efficiency Index**: Ratio of personalized pathway hours to generic curriculum hours (lower = more efficient)
4. **Personalization Ratio**: Fraction of total course catalog selected for the pathway (lower = more targeted)

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- pip

### Install Dependencies

```bash
cd Resume_Filter_Hackathon
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

The app will be available at **http://localhost:5000**.

---

## 📁 Project Structure

```
Resume_Filter_Hackathon/
├── app.py                          # Flask entry point
├── config.py                       # Configuration constants
├── requirements.txt                # Python dependencies
├── data/
│   ├── onet_skills.json           # O*NET-based skill taxonomy (270+ skills)
│   ├── skill_prerequisites.json   # Dependency graph & transferable skills
│   └── course_catalog.json        # 40+ learning modules
├── parsers/
│   ├── resume_parser.py           # PDF/DOCX/TXT parsing
│   └── jd_parser.py               # Job description parsing
├── engine/
│   ├── skill_extractor.py         # NLP skill extraction
│   ├── gap_analyzer.py            # Skill gap analysis
│   └── pathway_generator.py       # Adaptive pathway generation
├── static/
│   ├── css/styles.css             # Premium dark UI
│   └── js/app.js                  # Frontend application
├── templates/
│   └── index.html                 # Main HTML template
└── README.md                      # This file
```

---

## 🏗️ Architecture

```
Resume (PDF/DOCX/TXT) ─┐
                        ├──► Skill Extraction ──► Gap Analysis ──► Adaptive Pathway
Job Description (Text) ─┘        (NLP)            (Comparison)     (Weighted Algorithm)
                                  │                     │                    │
                           O*NET Taxonomy        Proficiency          Course Catalog
                           (270+ skills)          Estimation          (40+ modules)
                                                       │                    │
                                                  Transferable          Phased
                                                  Skill Bonus          Roadmap
```

---

## 📝 License

MIT License

---

*All datasets and models are explicitly cited above. The adaptive learning logic is our original implementation.*
