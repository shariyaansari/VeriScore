# VeriScore ✅

> Verify. Trust. Trade Safely.

![veriscore-badge](https://img.shields.io/badge/VeriScore-v1.0.0-blue) ![python](https://img.shields.io/badge/backend-Flask%20%2F%20Python-blueviolet) ![react](https://img.shields.io/badge/frontend-React%20%2F%20Vite-brightgreen) ![license](https://img.shields.io/badge/license-MIT-lightgrey)

## 📘 Project Summary

VeriScore is a Trading Address Verification System that detects fraudulent business addresses and verifies legitimacy using AI, fuzzy matching, and multiple external data sources. It assigns a fraud risk / confidence score (0–100) for each trading address and exposes a real-time API and web dashboard to help businesses automate address verification and KYB/KYC workflows.

Tagline: "Verify. Trust. Trade Safely."

---

## 🧩 Problem Statement

E-commerce, logistics providers, and B2B networks face an increasing number of frauds stemming from fake trading addresses:

- Rise in fake addresses used for scams, refund fraud, fake suppliers and drop-shipping abuse.
- Manual address verification is slow, costly and error-prone.
- There is no single centralized, trustworthy data source for trading address legitimacy.
- Businesses lose revenue and face reputational and operational risks from fraudulent entities.

VeriScore aims to reduce these risks by automating, scoring, and centralizing address verification.

---

## 🚀 Solution Overview

VeriScore verifies trading addresses by combining heuristic rules, fuzzy matching, and multi-source checks. Key capabilities:

- AI / ML and heuristics compute a confidence score for each address.
- Cross-checks against official and public data: Google Places / Maps, government registries, and web search results.
- Produces a fraud risk score (0–100) and a findings breakdown for auditability.
- Real-time verification API and a simple dashboard to monitor verification activity and trends.
- Supports automation for KYC/KYB, vendor onboarding, and fraud prevention pipelines.

---

## 🧠 Key Features

- 🔍 Smart Address Verification (structured parsing + normalization)
- 🤖 AI-driven Fraud Detection & Scoring (fuzzy matching + heuristics)
- 🌐 Multi-source Cross Validation (Google Places, government search, general web)
- 📊 Real-time Dashboard for Monitoring (API + frontend)
- 🧾 API Integration for Businesses (webhooks, programmatic checks)
- 📱 Scalable Web Interface (React + Vite)
- 🔒 Data Privacy & Secure Storage (MongoDB backend; configurable via env)
- 🧠 Machine learning / anomaly detection building blocks (fuzzy matching, distance checks)

---

## 🏗 System Architecture

A high-level overview (components you have in this repository):

- Frontend: React with Vite (located in `frontend/`) — UI components, pages, and CSV import/export utilities.
- Backend: Python Flask app (app factory in `backend/address_verifier/__init__.py`) — API endpoints, verification logic.
- Database: MongoDB (used by the Flask app for storing verification records).
- External APIs: Google Places / Maps, optional government search (via Google Custom Search), IP geolocation services.
- AI Models: Lightweight ML / heuristics implemented in `backend/address_verifier/verifier.py` (fuzzy matching + rules). Can be extended with trained models (scikit-learn, XGBoost, or more advanced ML).
- Deployment: Can be deployed to cloud providers (AWS / GCP / Render / Vercel for frontend). Backend can run on any host able to run Flask + access to MongoDB.

(You can add an architecture diagram here — e.g., `docs/architecture.png`.)

---

## ⚙ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS (UI components in `frontend/src/components`) |
| Backend | Python, Flask, Flask-CORS, python-dotenv |
| Database | MongoDB (pymongo) |
| ML/Libs | fuzzywuzzy, geopy, googlemaps, google-api-python-client, geocoder, requests |
| APIs | Google Places / Maps APIs, Google Custom Search (for gov/general checks) |
| Packaging / Tools | npm (frontend), pip (backend), Vite dev server |
| Deployment | Any: Render, AWS Elastic Beanstalk / ECS, GCP Cloud Run, Docker-ready |

---

## 🧾 Installation & Setup

These instructions are based on the repository structure and files in the project.

Prereqs:

- Node.js (18+ recommended) and npm
- Python 3.10+ and pip
- MongoDB (local or hosted Atlas)
- Google API Key(s) for Places / Custom Search (optional but recommended)

1) Clone the repository:

```bash
git clone https://github.com/jaedenpereira2/VeriScore.git
cd VeriScore
```

2) Backend setup (Flask):

```bash
cd backend
# create a virtual environment (recommended)
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Install dependencies
pip install -r address_verifier/requirements.txt
```

3) Configure environment variables:

Create a `.env` file at `backend/` (or set env vars in your deployment platform) with at least:

```
MONGO_URI=mongodb://<user>:<pass>@host:port/<dbname>
GOOGLE_API_KEY=your_google_api_key
GENERAL_SEARCH_CX=your_google_custom_search_cx_for_general
GOV_SEARCH_CX=your_google_custom_search_cx_for_gov
```

Notes:
- The Flask app connects to MongoDB using `MONGO_URI` (see `backend/address_verifier/__init__.py`).
- Google API keys are optional for local tests but required for real name/place validation used by `backend/address_verifier/verifier.py`.

4) Run the backend server:

```bash
# from the 'backend' folder (with venv activated)
python run.py
# or
python app.py
```

This starts the Flask API at `http://127.0.0.1:5000` by default.

5) Frontend setup:

```bash
cd ../frontend
npm install
npm run dev
```

Vite will show the dev URL (commonly `http://localhost:5173`). Open the URL in your browser.

6) Accessing the app

- Frontend: the Vite dev server URL (e.g., `http://localhost:5173`)
- Backend: `http://localhost:5000/api` (sample endpoints below)

---

## 🧪 Usage / Demo

Quick API examples and how to test locally.

1) Verify an address (POST):

- Endpoint: `POST /api/verify`
- Body (JSON):

```json
{
  "company_name": "Acme Pvt Ltd",
  "address": "123 Market Rd, Mumbai, India",
  "webhook_url": "https://example.com/webhook"  // optional
}
```

- Example curl:

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Acme Pvt Ltd","address":"123 Market Rd, Mumbai, India"}'
```

- Sample response (JSON):

```json
{
  "company_name": "Acme Pvt Ltd",
  "address": "123 Market Rd, Mumbai, India",
  "confidence_score": 85,
  "findings": [
    { "source": "Google Places Name Match", "note": "High-confidence name match found." },
    { "source": "Government Domain Search", "note": "Company found on a trusted government source.", "evidence_url": "https://gov.example/..." }
  ],
  "id": "650f2a..."
}
```

2) Dashboard stats (GET):

- Endpoint: `GET /api/dashboard-stats`
- Returns aggregate counts and recent verifications.

3) Download PDF report (GET):

- Endpoint: `GET /api/get-report/<verification_id>`
- Downloads a small PDF summarizing verification findings (implemented in `backend/address_verifier/routes.py`).

Demo notes:
- The frontend includes an `Export` page (`frontend/src/components/pages/ExportPage.jsx`) to upload CSVs and download processed CSVs locally.
- Add screenshots: place images in `docs/` and reference them here. (Placeholder below)

![screenshot-placeholder](docs/screenshot-dashboard.png)

---

## 🧠 AI & ML Components

Current approach implemented in `backend/address_verifier/verifier.py`:

- Fuzzy name matching: `fuzzywuzzy` token set ratio is used to compare the provided company name with the top Google Places candidate. High-similarity matches add a large weight (70 points) to the confidence score.
- Multi-source evidence: hits from government/custom search engines add supporting points (25 and 5 points respectively).
- IP geolocation: a heuristic distance check between business geocode and user IP can add a small bonus (5 points).
- Scoring: Scores are summed and capped at 100. The final status mapping is typically: >=80 => verified, >=40 => suspicious, <40 => rejected.

Inputs used:
- company_name
- raw address string (free-form)
- user IP (optional)
- external search results and place metadata

Outputs:
- confidence_score (0–100)
- findings[] (per-source notes and evidence URLs)
- status label (verified / suspicious / rejected)

Datasets:
- The project currently relies on external APIs (Google Places, public government domains). You can augment it with public datasets (official company registries, GSTIN databases) or synthetic datasets for model training and evaluation.

Extending to ML models:
- Add a supervised classifier (e.g., XGBoost or scikit-learn) trained on labeled verifications to predict fraud probability.
- Add feature extraction: normalized address tokens, TF-IDF from web hits, registration age, phone/email match signals, geospatial distance features.

---

## 📊 Impact & Results

(Values below are illustrative — replace with your measured results after experiments.)

- Expected reduction in manual verification time: 70–90% for routine verifications.
- Faster fraud detection: risk-based routing for manual review reduces false positives sent to investigators.
- Real-world applicability: vendor onboarding, marketplace seller verification, supply chain partner vetting.

Social/economic benefits:
- Reduced chargebacks and refund abuse for e-commerce platforms.
- Faster compliance checks for regulated businesses.

---

## 🧩 Future Scope

Planned or recommended improvements:

- Integrate global address verification providers for better standardization.
- Add blockchain anchoring for immutable proof-of-verification.
- Expand to identity verification and full KYB/KYC flows (document OCR, face-match).
- Replace heuristic scoring with a trained model and continually retrain on labeled data.
- Mobile app for on-the-go verification and field operations.

---

## 🧱 Folder Structure (high level)

```
VeriScore/
│
├── backend/
│   ├── address_verifier/
│   │   ├── __init__.py         # Flask app factory
│   │   ├── routes.py           # API endpoints (verify, dashboard, reports)
│   │   ├── verifier.py         # Main verification logic & scoring
│   │   ├── parser.py           # (address parsing utilities)
│   │   └── requirements.txt
│   ├── run.py
│   └── app.py
│
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── components/         # UI pages & components (Dashboard, Verify, Export)
│   │   └── App.jsx             # Router and navigation
│   └── ...
│
├── README.md
└── package.json
```

---

## ✅ Quick Checklist (to run locally)

- [ ] Python 3.10+, pip, virtualenv
- [ ] Node.js + npm
- [ ] MongoDB (local or Atlas) and `MONGO_URI` in `.env`
- [ ] Google API key(s) for better results (optional but recommended)

---

## Troubleshooting & Tips

- If the Flask app cannot connect to MongoDB, check `MONGO_URI` and network rules (Atlas IP whitelist).
- If Google API calls fail, verify `GOOGLE_API_KEY` and billing is enabled in GCP Console.
- The frontend expects the backend at `http://localhost:5000/api/*` during local development — update fetch URLs in the frontend if you run the API on a different host/port.

---

## Contributing

Contributions, issues and feature requests are welcome. Please open a GitHub issue or submit a pull request.

