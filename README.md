# Willovate AI Automation Engine & Sample CRM

An AI-powered business automation engine that converts natural-language instructions into validated browser workflows and executes them on a sample CRM application.

Instead of manually navigating the CRM interface, users can issue natural-language commands to manage business operations, update products and customers, or redesign storefront branding:

> *"Change the homepage heading to Mega Summer Sale with summer vibes like beaches, shells, sun, and ocean waves."*

The engine understands the instruction, synthesizes visual banner themes, generates executable Playwright browser actions, checks for operational risk, and updates the CRM UI seamlessly.

---

## Key Features

- **Natural-Language Storefront Customization**: Redesign storefront layout, headings, and promotional banners using natural-language instructions.
- **Dynamic Prompt-Based Banner Themes**: Automatically translates prompt keywords into CSS background gradients and color schemes for themes including:
  - *Summer, beaches, ocean, sun, and tropical vibes*
  - *Independence Day, patriotic, saffron & green tricolor themes*
  - *Festivals, Diwali, celebrations, and festive sparkle*
  - *Christmas, winter, snow, and holiday presets*
- **AI-Generated Sale Descriptions**: Dynamically generates contextual promotional subheadings based on the sale heading (e.g. *"Mega Summer Sale"*, *"Independence Day Sale"*), replacing generic boilerplate text.
- **Live Active-Offer Marquee**: Displays a continuously scrolling marquee ticker of active promotional offers on the Dashboard, updated in real time.
- **Synchronized Previews & Shared State**: Single-source-of-truth state architecture ensuring instant synchronization between the Homepage Customization page and the main Dashboard hero banner.
- **Store Branding & Media Uploads**: Support for custom logo and banner image uploads, dynamically rendered in the sidebar brand mark and storefront hero banner.
- **Customer & Product Automation**: Natural-language commands to add, search, update, or delete customers and products.
- **Risk Classification & Confirmation**: Identifies destructive actions (e.g., deletions) and requests user confirmation prior to execution.
- **Playwright Automation & Visual OCR**: Headless browser automation combined with Tesseract OCR screenshot verification to confirm page state updates visually.

---

## Architecture & Workflow

```text
Natural-Language Instruction
           │
           ▼
   Intent Detection & Entity Extraction
           │
           ▼
 Dynamic Theme & Sale Description Generator
           │
           ▼
   Required Information & Risk Check
           │
           ▼
 Structured Workflow Generation & Validation
           │
           ▼
     Playwright Browser Runner
           │
           ▼
 Sample CRM State Update (homepage_settings / offers_list)
           │
           ▼
 Visual OCR Verification & Synchronized UI Preview
```

---

## State Architecture: Single Source of Truth

The sample CRM uses centralized in-memory repositories in `sample_crm/app.py` made available globally to all Jinja2 templates via Flask `@app.context_processor`:

- **`homepage_settings`**: Stores the active storefront configuration (heading, dynamic sale description, special announcement, contact number, uploaded logo/banner paths, and CSS gradient styles). Any change on `/homepage` or via natural-language automation immediately updates the Dashboard (`/`) banner preview.
- **`offers_list`**: Stores active promotional campaigns (offer name, discount percentage, category, valid end date, description). Active offers automatically render in the Offers list and in the live Dashboard marquee ticker without hardcoded values or duplicated percentages.

---

## Technologies Used

- **Python 3.10+** — Core engine logic, intent detection, and entity extraction
- **Flask & Jinja2** — CRM web application backend and template rendering engine
- **Playwright for Python** — Headless browser automation execution
- **Tesseract OCR / Pytesseract** — Visual verification of rendered browser screenshots
- **Vanilla CSS & Flexbox/Grid** — Modern responsive UI styling, glassmorphism card panels, and dynamic banner gradients

---

## Supported Operations

| Category | Description | Examples |
| :--- | :--- | :--- |
| **Homepage Customization** | Update heading, subtitle, announcement, contact, logo, and visual banner themes | *"Change homepage heading to Independence Day Sale with patriotic vibes"* |
| **Offers & Campaigns** | Add and display active promotional offers in marquee ticker | *"Add offer Summer Special with 20% discount on software"* |
| **Customer Management** | Add, delete, list, and verify customer records | *"Add Amit Sharma as active customer with phone 7873543100"* |
| **Product Management** | Add, update price/stock, and list products | *"Add CRM Pro software for 4999 in stock 120"* |
| **Reports & Files** | Download reports, upload store logos, and export data | *"Upload brand logo image to homepage"* |

---

## Project Structure

```text
Willovate AI Automation Engine/
│
├── src/
│   └── willovate/
│       ├── intent_detector.py      # Natural-language intent classifier
│       ├── banner_theme.py         # Dynamic theme & sale description generator
│       ├── workflow_generator.py   # Executable step generator
│       ├── workflow_validator.py   # Workflow schema & safety validator
│       ├── automation_runner.py    # Playwright browser executor
│       ├── risk_classifier.py     # Destructive action classifier
│       └── tesseract_ocr.py        # Visual OCR verification
│
├── sample_crm/
│   ├── app.py                      # Flask backend & global context processors
│   ├── templates/
│   │   ├── base.html               # Main layout & sidebar with dynamic logo
│   │   ├── dashboard.html          # Main dashboard with banner & offer marquee
│   │   ├── homepage.html           # Storefront customization panel
│   │   ├── offers.html             # Offer campaign management
│   │   └── components/
│   │       └── hero_banner.html    # Unified reusable storefront banner
│   └── static/
│       ├── css/style.css           # Responsive design system
│       └── uploads/                # Custom logo and banner media files
│
├── run_willovate.py                # Command-line entry point for automation engine
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

---

## Installation & Setup

### 1. Prerequisites

- Python 3.10+
- Tesseract OCR (installed on system path for visual verification)

### 2. Clone & Install Dependencies

```bash
git clone <repository-url>
cd "Willovate AI Automation Engine"

python -m venv venv
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

---

## Running the Application

### Step 1: Start the Sample CRM Application

In your primary terminal:

```powershell
python sample_crm/app.py
```

The sample CRM will start at:
```text
http://127.0.0.1:5000
```

### Step 2: Run the AI Automation Engine

In a second terminal:

```powershell
.\venv\Scripts\activate
python run_willovate.py
```

Enter a natural-language instruction when prompted:

```text
What should Willovate do?
> Change the homepage heading to Mega Summer Sale with summer vibes like beaches, sun, and ocean waves
```

The engine will classify the intent, synthesize the banner theme, generate the workflow, execute Playwright browser steps, and update the CRM dashboard in real time.
