# Quickstart & Verification Guide: VoltKart AI Agent

This guide outlines prerequisites, setup instructions, and step-by-step end-to-end verification procedures for VoltKart.

---

## 1. Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 installed.
- **MongoDB**: Local MongoDB community service running on `mongodb://localhost:27017` OR a MongoDB Atlas connection string.
- **Google Gemini API Key**: Valid API key from Google AI Studio.

---

## 2. Environment Setup

1. **Navigate to the workspace**:
   ```bash
   cd c:\Users\SrinivasCharyThimmap\Desktop\hackathon
   ```

2. **Create and activate a Python virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file from `.env.example`:
   ```ini
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=voltkart_db
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```

---

## 3. Running the Application

Launch the Streamlit web application:
```powershell
streamlit run app.py
```
The browser will automatically open at `http://localhost:8501`.

---

## 4. End-to-End Verification Scenarios

### Step A: Administrator Ingestion Check
1. In the Streamlit sidebar, select **"Admin Dashboard"**.
2. Under **"Upload Dataset"**, choose category **"Laptop Catalog"**.
3. Upload `data/sample_products.csv`.
4. Observe the **Column Mapping** preview (verify automatic mapping of `Price`, `RAM`, `Processor`, etc.).
5. Click **"Validate & Ingest"**.
6. **Expected Outcome**: Ingestion summary displays `25 total records, 25 inserted, 0 failed, 0 skipped`. The catalog table below displays the 25 laptops.
7. Repeat for `data/sample_faqs.csv` (15 FAQs) and `data/sample_policies.csv` (policies).

---

### Step B: Customer Recommendation Flow (User Story 1)
1. In the sidebar, select **"AI Customer Support & Chat"**.
2. Submit query:
   ```text
   "Suggest a good laptop for a college student under Rs. 60,000 with good battery life."
   ```
3. **Expected Outcome**:
   - Status spinner indicates intent extraction and database retrieval.
   - Assistant displays 2–3 recommendation cards.
   - Each card displays price $\le$ ₹60,000, RAM, processor, storage, battery life, and a personalized recommendation rationale.
   - All displayed prices and specs match MongoDB records.

---

### Step C: Multi-Turn Comparison Flow (User Story 4)
1. Immediately follow up in the same chat:
   ```text
   "Compare the first two laptops."
   ```
2. **Expected Outcome**:
   - Assistant references the exact 2 models from the previous turn.
   - A structured side-by-side comparison table is rendered comparing Price, Processor, RAM, Storage, Display, Graphics, Weight, and Battery Life.
   - An objective summary notes which laptop excels in specific trade-offs.

---

### Step D: Store Policy & FAQ Flow (User Story 2)
1. Submit query:
   ```text
   "What is your return policy?"
   ```
2. **Expected Outcome**:
   - Assistant retrieves the 7-day return policy from MongoDB.
   - Responds with exact return conditions (original box, invoice, intact seal).

---

### Step E: Zero-Hallucination Negative Test (Strict Grounding)
1. Submit query:
   ```text
   "Do you offer zero-cost EMI with Bajaj Finserv?"
   ```
2. **Expected Outcome**:
   - Since no EMI policy exists in the sample database, the assistant explicitly states that information about zero-cost EMI is currently unavailable and directs the user to accepted payment methods.
   - **MUST NOT** invent EMI terms.

---

### Step F: Out-of-Scope Deflection (User Story 5)
1. Submit query:
   ```text
   "Do you sell Samsung Galaxy S24 phones?"
   ```
2. **Expected Outcome**:
   - Assistant politely clarifies that VoltKart exclusively sells laptops and offers to help with laptop models.

---

## 5. Automated Test Suite Execution

Run automated unit and integration tests:
```powershell
pytest -v tests/
```
All tests for file import, schema validation, retrieval filtering, and Gemini service fallback must pass.
