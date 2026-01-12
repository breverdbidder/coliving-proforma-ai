# 🏠 BidDeed.AI Co-Living Proforma Analyzer

AI-Powered Co-Living Real Estate Investment Analysis Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-green.svg)](https://github.com/langchain-ai/langgraph)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Overview

BidDeed.AI Co-Living Proforma Analyzer is an enterprise-grade LangGraph-orchestrated AI agent that provides comprehensive financial analysis for co-living real estate investments in Brevard County, Florida.

**Key Features:**
- 🤖 **12-Stage LangGraph Pipeline** - Automated analysis workflow
- 💬 **NLP-Powered Chatbot** - Natural language query interface
- 📊 **Multi-Format Outputs** - Excel, PDF, and Interactive Dashboards
- 🎯 **Custom Scenarios** - User-defined assumptions and stress testing
- 📈 **Bank-Grade Calculations** - Precision financial metrics
- 🌐 **Brevard County Optimized** - Market-specific benchmarks

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [12-Stage Pipeline](#12-stage-pipeline)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Output Formats](#output-formats)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Co-Living AI Platform                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │   React UI  │ ───▶ │  LangGraph   │ ───▶ │  Claude    │ │
│  │  Chatbot    │      │ Orchestrator │      │  Sonnet 4  │ │
│  └─────────────┘      └──────────────┘      └────────────┘ │
│         │                     │                     │        │
│         ▼                     ▼                     ▼        │
│  ┌─────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │   User      │      │  12-Stage    │      │  Report    │ │
│  │  Inputs     │      │  Pipeline    │      │ Generators │ │
│  └─────────────┘      └──────────────┘      └────────────┘ │
│                                                               │
│         Excel Templates (Base64) ───▶ Analysis ───▶ Outputs  │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Outputs: Excel (.xlsx) | PDF (.pdf) | Dashboard (.json)
```

### Technology Stack

**Backend:**
- Python 3.10+
- LangGraph (Orchestration)
- LangChain + Anthropic Claude Sonnet 4
- OpenPyXL (Excel generation)
- ReportLab (PDF generation)
- **Supabase** (Database & Data Persistence)
- **FastAPI** (REST API)

**Frontend:**
- React 18+
- Lucide Icons
- Modern CSS with gradients

**Infrastructure:**
- GitHub Actions (CI/CD)
- Cloudflare Pages (Frontend hosting)
- **Supabase** (PostgreSQL database)
- Railway / Render / Cloudflare Workers (API hosting)

---

## 🔄 12-Stage Pipeline

The LangGraph orchestration runs through a comprehensive 12-stage analysis:

```python
Stage 01: Discovery            → Parse user query and extract intent
Stage 02: Data Extraction      → Load Excel template and user inputs
Stage 03: Assumptions Validation → Verify financial assumptions
Stage 04: Unit Mix Analysis    → Analyze bedroom configurations
Stage 05: Revenue Projection   → Calculate income streams
Stage 06: Expense Analysis     → Detailed operating expenses
Stage 07: Cash Flow Calculation → NOI and debt service analysis
Stage 08: Returns Metrics      → IRR, ROI, Cash-on-Cash
Stage 09: Sensitivity Analysis → Stress testing scenarios
Stage 10: Risk Assessment      → Market and operational risks
Stage 11: Report Generation    → Create multi-format outputs
Stage 12: Recommendations      → AI-powered investment advice
```

Each stage is a separate LangGraph node with state management and error handling.

---

## 🗄️ Supabase Integration

### Database Schema

Co-Living Proforma AI uses Supabase PostgreSQL for data persistence:

**5 Core Tables:**
1. **coliving_properties** - Property records with assumptions
2. **coliving_analyses** - Financial analysis results
3. **coliving_reports** - Generated reports (Excel, PDF, Dashboard)
4. **coliving_conversations** - Chatbot message history
5. **coliving_scenarios** - Scenario comparison data

### Setup Instructions

1. **Execute SQL Schema**:
   ```bash
   # Copy SQL from supabase_schema.sql
   # Run in Supabase SQL Editor:
   # https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Add your Supabase credentials
   ```

3. **Test Connection**:
   ```bash
   python3 coliving_supabase.py
   ```

### API Endpoints

FastAPI backend with full CRUD operations:

- `POST /api/analyze` - Run analysis and save to database
- `GET /api/properties` - List all properties
- `GET /api/analyses/{id}` - Get analysis results
- `GET /api/analyses/{id}/reports/excel` - Generate Excel
- `GET /api/analyses/{id}/reports/pdf` - Generate PDF
- `GET /api/analytics` - Platform analytics

**Full Documentation**: See [SUPABASE_DEPLOYMENT.md](SUPABASE_DEPLOYMENT.md)

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ (for React frontend)
- Anthropic API key

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/breverdbidder/coliving-proforma-ai.git
cd coliving-proforma-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-api-key-here"

# Run the orchestrator
python coliving_orchestrator.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## 💻 Usage

### Command Line Interface

```python
from coliving_orchestrator import CoLivingChatbot

# Initialize chatbot
chatbot = CoLivingChatbot()

# Analyze property
query = "Analyze a 20-unit property with $900/bedroom rent in Brevard County"
results = chatbot.process_query(query)

# Access results
print(results['chatbot_response'])
print(results['dashboard_data'])
```

### Web Interface

1. Start the backend API server
2. Launch the React frontend
3. Upload Excel template or use default
4. Enter natural language queries
5. Download Excel, PDF, or view dashboard

### Example Queries

**Basic Analysis:**
```
"Analyze a 20-unit co-living property with average rent of $900 per bedroom"
```

**Scenario Comparison:**
```
"Compare scenario A: 93% occupancy vs scenario B: 88% occupancy"
```

**Sensitivity Analysis:**
```
"Show me how NOI changes with occupancy rates from 80% to 95%"
```

**Custom Assumptions:**
```
"Calculate returns assuming $800/bedroom rent, 50% OpEx ratio, 6.5% interest rate"
```

---

## 📊 Output Formats

### 1. Excel Proforma (`.xlsx`)

Comprehensive multi-sheet workbook:
- **Executive Summary** - Key metrics and recommendations
- **Assumptions** - All financial inputs
- **Revenue Analysis** - Income projections
- **Expense Analysis** - Operating cost breakdown
- **Cash Flow** - NOI and debt service
- **Returns** - Cap Rate, CoC, IRR
- **Sensitivity** - Scenario testing
- **Risk Assessment** - Risk factors
- **Charts & Dashboard** - Visual analytics

### 2. PDF Executive Summary (`.pdf`)

Professional investor-ready report:
- Property information
- Key financial metrics
- Investment recommendation
- Risk assessment
- Market positioning

### 3. Interactive Dashboard (`.json`)

JSON configuration for dashboard rendering:
```json
{
  "key_metrics": {
    "noi": {...},
    "cap_rate": {...}
  },
  "charts": {
    "revenue_breakdown": {...},
    "expense_breakdown": {...},
    "sensitivity_analysis": {...}
  }
}
```

---

## 🎯 API Reference

### CoLivingProformaAgent

Main LangGraph orchestration class.

```python
agent = CoLivingProformaAgent(anthropic_api_key="sk-...")

# Run full analysis
results = agent.analyze(user_query="Your query here")

# Access stage results
noi = results['cash_flow']['noi']
cap_rate = results['returns_metrics']['cap_rate']
```

### CoLivingChatbot

Natural language processing interface.

```python
chatbot = CoLivingChatbot()

# Process query
response = chatbot.process_query("Analyze property...")

# Get formatted response
print(response['chatbot_response'])

# Get raw analysis
analysis = response['full_analysis']
```

### CoLivingReportGenerator

Multi-format report generation.

```python
from coliving_report_generators import CoLivingReportGenerator

generator = CoLivingReportGenerator(analysis_results)

# Generate reports
excel_bytes = generator.generate_excel_report()
pdf_bytes = generator.generate_pdf_report()
dashboard_json = generator.generate_dashboard_json()
```

---

## 🚀 Deployment

### GitHub Actions CI/CD

Automated deployment on push to `main`:

```yaml
# .github/workflows/deploy.yml
name: Deploy Co-Living AI
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Cloudflare Pages
        run: npm run deploy
```

### Manual Deployment

```bash
# Backend (Python API)
gunicorn coliving_api:app --bind 0.0.0.0:8000

# Frontend (React)
npm run build
# Deploy build/ to Cloudflare Pages
```

---

## 📈 Financial Metrics Calculated

### Revenue Metrics
- Gross Potential Income (GPI)
- Vacancy & Credit Loss
- Effective Gross Income (EGI)
- Other Income

### Expense Metrics
- Property Management (8-12%)
- Utilities (12% for co-living)
- Maintenance & Repairs (6-8%)
- Insurance, Taxes, Marketing
- Co-Living Specific: Cleaning, WiFi, Amenities

### Cash Flow Metrics
- Net Operating Income (NOI)
- Annual Debt Service
- Cash Flow After Debt
- Debt Service Coverage Ratio (DSCR)

### Returns Metrics
- Capitalization Rate (Cap Rate)
- Cash-on-Cash Return
- Internal Rate of Return (IRR)
- Equity Multiple
- Return on Investment (ROI)

---

## 🏘️ Brevard County Market Benchmarks

Industry standards used for validation:

| Metric | Benchmark | Source |
|--------|-----------|---------|
| Occupancy Rate | 90-95% | Market Data |
| Rent/Bedroom | $700-$1,200/mo | Brevard County Avg |
| OpEx Ratio | 45-55% | Co-Living Industry |
| Cap Rate | 6-8% | Brevard Market |
| DSCR | >1.25x | Lender Requirements |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/coliving-proforma-ai.git

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** - Claude Sonnet 4 AI
- **LangChain** - LangGraph orchestration framework
- **Brevard County Real Estate Market** - Data and benchmarks

---

## 📞 Support

- **Documentation**: [docs.biddeed.ai](https://docs.biddeed.ai)
- **Issues**: [GitHub Issues](https://github.com/breverdbidder/coliving-proforma-ai/issues)
- **Email**: support@biddeed.ai

---

## 🗺️ Roadmap

- [ ] Supabase integration for data persistence
- [ ] Multi-market support beyond Brevard County
- [ ] Advanced machine learning predictions
- [ ] Real-time market data integration
- [ ] Mobile app (React Native)
- [ ] API rate limiting and authentication
- [ ] Investor portal with saved analyses

---

**Built with ❤️ by BidDeed.AI**

*Transforming co-living investment analysis with AI-powered automation*


<!-- Deployed: 1768178472.6503782 -->