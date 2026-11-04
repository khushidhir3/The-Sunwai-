# 🗞️ The Sunwai (द सुनवाई)
### The e-Portal for Case Management Hearings

> A digital Case Management Hearing (Pre-Trial Conference) platform for courts and legal practitioners, designed in the vintage dignity of a printed broadsheet newspaper gazette.

---

## 🏛️ What is "The Sunwai"?

In contemporary legal systems (such as under Order X-A of the Code of Civil Procedure), **Case Management Hearings (CMH)** are mandatory pre-trial conferences where judicial officers and counsel narrow controversies, frame agreed issues, settle uncontroverted admissions and denials of documents, and set strict, enforceable procedural timetables.

**The Sunwai** transforms this crucial procedural stage into an elegant, broadsheet newspaper gazette interface that combines timeless typography with modern web architecture.

---

## 🌟 Key Features

1. **Newspaper Broadsheet Design System**
   - **Gothic Masthead & Topstrip**: Dynamic Volume & Issue numbering, daily court circular ticker, and official registry notice dispatches.
   - **3-Column Front Page Grid**:
     - *Left Column*: Daily Cause List with sitting times, courtroom tags, and instant attendance links.
     - *Center Column*: Lead Story docket featuring the next scheduled Case Management Hearing with broadsheet drop caps and action controls.
     - *Right Column*: Registry vitals (active matters, roll tally, compliance desks), pending directions with overdue warnings, and recent filings.
   - **Curated Legal Typography**: UnifrakturCook (masthead blackletter), Playfair Display (headlines), and Source Serif 4 (justified broadsheet columns).

2. **Full Virtual Hearing Chamber**
   - Embedded **Jitsi Meet** video-conference room with room identity encryption.
   - **Interactive Pre-Hearing Checklist**: Real-time Order X CPC checklist with HTMX completion toggles.
   - **Confidential Bench Minutes**: In-camera private judicial note-taking panel visible only to the presiding judge.
   - **Live Registry Transcript Log**: Real-time WebSocket messaging powered by Django Channels.

3. **Master Case Register & Digital Bundle Viewer**
   - Gazette register with status and category filters (Commercial, Arbitration, Civil, Writ).
   - Document bundle reader with interactive tabbed pleadings index and certified timestamp headers.

4. **Conflict Detection Scheduling Engine**
   - Automated scheduling algorithm preventing double bookings across **Judges**, **Courtrooms**, and **Appearing Advocates**.
   - HTMX-driven next available free slot recommendation.

5. **Directions & Certified Gazette Order Sheets**
   - Pre-trial direction recording using standardized practice templates (witness affidavits, document discovery, mediation referrals).
   - WeasyPrint / CSS Paged Media court order sheets with digital seal verification.

6. **Immutable Audit Register**
   - Append-only ledger recording every user action, pleading filing, direction issuance, and status change with cryptographic timestamps.

---

## 🛠️ Technology Stack

- **Backend**: Django 5.2 (Python 3.12)
- **Frontend**: Django Templates, [HTMX](https://htmx.org/), [Alpine.js](https://alpinejs.dev/), Vanilla CSS
- **Real-Time WebSockets**: Django Channels (ASGI)
- **PDF Generation**: WeasyPrint / CSS Paged Media
- **Video Conferencing**: Jitsi Meet IFrame API
- **Task Queue & Reminders**: Celery + Redis (T-7, T-2, T-1 automated email notices)
- **Environment Management**: `python-decouple`

---

## 🚀 Quickstart & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/khushidhir3/The-Sunwai-.git
cd The-Sunwai-
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
```

### 4. Apply Database Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_sunwai
```

### 5. Run the Server
```bash
python manage.py runserver 8008
```
Visit **http://127.0.0.1:8008/** in your browser.

---

## 👥 Demo Credentials

The database comes pre-seeded with realistic judicial data. All accounts use password: `sunwai2024`

| Role | Email Address | Notes |
|------|---------------|-------|
| **Presiding Judge** | `judge@thesunwai.court` | Commercial Division Bench |
| **Registrar** | `registrar@thesunwai.court` | Scheduling & Registry Desk |
| **Advocate (Petitioner)** | `advocate@thesunwai.court` | Adv. Meenakshi Sundaram |
| **Advocate (Respondent)** | `counsel2@thesunwai.court` | Adv. Arjun Kapoor |
| **Litigant** | `litigant@thesunwai.court` | Bharat Heavy Infra Ltd. |
| **Administrator** | `admin@thesunwai.court` | System Administrator |

---

## 📄 License
This project is open-source under the MIT License.
