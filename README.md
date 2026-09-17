# Mortgage Rate — Smart National Rate Scanner

An interactive Python tool for comparing **mortgage interest rates across the United States** using publicly available mortgage-rate data from the **Consumer Financial Protection Bureau (CFPB)**.

The scanner evaluates mortgage-rate availability across all **50 states plus Washington, D.C.**, automatically handles conforming and jumbo loan scenarios, ranks regions by their lowest available rate, and visualizes the most competitive results.

> **Disclaimer:** This project is for research and educational purposes only. Results are based on publicly available rate data and are not mortgage offers, loan estimates, or financial advice. Actual rates depend on the lender, borrower profile, property, loan structure, points, fees, and market conditions.

---

## Overview

Mortgage rates can vary based on:

* Property location
* Credit score
* Loan amount
* Down payment
* Loan term
* Fixed vs. adjustable-rate structure
* Conforming vs. jumbo loan classification

This project provides an interactive way to explore those differences nationally.

The user selects a mortgage profile:

```text
Home Price
    +
Down Payment
    +
Credit Score
    +
Mortgage Product
    │
    ▼
CFPB Mortgage Rate Data
    │
    ▼
Scan 50 States + Washington, D.C.
    │
    ▼
Conforming / Jumbo Auto-Fallback
    │
    ▼
Rank Lowest Available Rates
    │
    ▼
Table + Visualization
```

---

## Features

### National Mortgage Rate Scan

The application scans mortgage-rate data for:

* All 50 U.S. states
* Washington, D.C.

For each region, the program records:

* Lowest observed interest rate
* Number of lenders represented in the returned rate distribution
* Loan type used
* Data date
* State

Results are ranked from the lowest rate upward.

---

## Interactive Mortgage Inputs

The application uses Jupyter widgets to let users configure their mortgage scenario.

### Home Price

Enter the estimated property purchase price.

Example:

```text
$1,000,000
```

### Down Payment

Specify the down payment as a percentage of the purchase price.

Example:

```text
20%
```

The loan amount is calculated automatically:

```text
Loan Amount = Home Price - Down Payment
```

### Credit Score

Select a credit score between:

```text
600 — 850
```

The scanner maps the selected score into the credit-score range expected by the rate API.

For example, a selected score around `800` is evaluated using the corresponding score bucket.

### Mortgage Product

The current interface supports:

* 30-Year Fixed
* 15-Year Fixed
* 7/1 ARM
* 5/1 ARM
* 5/3 ARM

---

## Conforming / Jumbo Auto-Fallback

Mortgage data availability can differ depending on whether a loan is categorized as conforming or jumbo.

The scanner therefore implements an automatic fallback strategy.

```text
Loan Scenario
     │
     ▼
Select likely loan type
     │
     ├── Conforming
     │
     └── Jumbo
     │
     ▼
Query CFPB
     │
     ▼
Data available?
   /       \
 Yes        No
  │          │
  ▼          ▼
Use      Try alternate
data       loan type
```

The current implementation uses the loan amount to choose which loan type to try first and then automatically tries the alternative if no data are returned.

This improves geographic coverage when rate data are unavailable for the first loan classification.

---

## Data Source

Mortgage-rate data are retrieved from the **Consumer Financial Protection Bureau (CFPB)** rate-checker service.

The application sends mortgage characteristics including:

* Property price
* Loan amount
* Down payment
* Credit-score range
* State
* Loan type
* Loan term
* Rate structure
* ARM structure when applicable

No API key is required by the current implementation.

Because the project depends on an external CFPB service, data availability and endpoint behavior may change over time.

---

## Rate Selection

For each state, the CFPB response contains a distribution of available mortgage rates.

The scanner identifies:

```text
Lowest Rate = minimum rate returned for the state
```

It also calculates the total number of lender observations represented by the returned distribution.

The final ranking is sorted by:

1. Lowest mortgage rate
2. Number of lenders when rates are tied

---

## Example Workflow

Suppose a user selects:

```text
Home Price:       $1,000,000
Down Payment:     20%
Loan Amount:      $800,000
Credit Score:     800
Product:          30-Year Fixed
```

The scanner then:

1. Calculates the loan amount.
2. Determines the appropriate credit-score bucket.
3. Builds the CFPB query.
4. Scans each state and Washington, D.C.
5. Attempts the primary loan classification.
6. Falls back to the alternative classification when necessary.
7. Extracts each region's lowest available rate.
8. Ranks the results.
9. Displays the top 10 regions.
10. Generates a comparison chart.

---

## Output

After completing the national scan, the application displays a table similar to:

```text
TOP 10 STATES WITH LOWEST RATES

   State   Lowest Rate (%)   Total Lenders   Loan Type Used   Date
1  XX          6.xxx              xxx             CONF        YYYY-MM-DD
2  XX          6.xxx              xxx             JUMBO       YYYY-MM-DD
3  XX          6.xxx              xxx             CONF        YYYY-MM-DD
...
```

The exact values depend on current data and the mortgage profile selected by the user.

The scanner also calculates:

```text
National Average of State-Level Lowest Rates
```

This provides a simple benchmark for comparing the most competitive rate observed in each region.

---

## Visualization

The application generates a bar chart showing the:

**Top 10 states/regions with the lowest observed mortgage rates**

The visualization makes geographic differences easier to compare.

```text
Interest
 Rate
   │
   │      ▇
   │  ▇   ▇
   │  ▇ ▇ ▇   ▇
   │  ▇ ▇ ▇ ▇ ▇
   └──────────────────
       States / D.C.
```

The Y-axis automatically adjusts to the range of rates returned by the scan so that relatively small differences remain visible.

---

## Repository Structure

```text
Mortgage-Rate/
│
├── mortgage.py
│   Interactive national mortgage-rate scanner
│
└── README.md
    Project documentation
```

---

## Technologies

The project is implemented in Python using:

* Python
* Requests
* pandas
* Matplotlib
* ipywidgets
* IPython
* REST API integration

---

## Installation

Clone the repository:

```bash
git clone https://github.com/vincent625/Mortgage-Rate.git
cd Mortgage-Rate
```

Install the required Python packages:

```bash
pip install requests pandas matplotlib ipywidgets ipython
```

Because the application uses interactive widgets, it is best run in:

* Jupyter Notebook
* JupyterLab
* Another compatible IPython environment

---

## Running the Scanner

Start Jupyter:

```bash
jupyter notebook
```

Create or open a notebook in the project directory and run:

```python
%run mortgage.py
```

The interactive controls will appear in the notebook.

Configure:

1. Mortgage product
2. Credit score
3. Property price
4. Down payment

Then click:

```text
Start Smart Scan
```

The application displays progress while scanning the country and presents the results when complete.

---

## Example Interface

The interactive interface contains controls for:

```text
Product:       [30-Year Fixed ▼]

Credit Score:  [────────●──────] 800

Price ($):     [1000000]

Down Pymt %:   [20.0]

                [ Start Smart Scan ]
```

A progress indicator tracks the national scan.

---

## Implementation Details

### Credit-Score Bucketing

The selected credit score is converted into a score range before being sent to the CFPB service.

The current implementation uses 20-point score buckets and constrains the API query range to the supported range used by the application.

### Fixed-Rate Mortgages

For fixed-rate products, the application specifies:

```text
rate_structure = fixed
loan_term      = 15 or 30
```

### Adjustable-Rate Mortgages

For ARM products, the application specifies:

```text
rate_structure = arm
loan_term      = 30
arm_type       = selected ARM structure
```

### Rate Limiting

A short delay is added between state requests to reduce request pressure on the external service.

The application also detects HTTP `429` responses and temporarily slows down when rate limiting occurs.

---

## Limitations

Several factors should be considered when interpreting the results.

### Rates Are Not Personalized Loan Offers

The returned rates are market observations based on the selected scenario. They do not represent guaranteed rates from a lender.

### Lowest Rate Does Not Mean Lowest Cost

Mortgage comparison should also consider:

* APR
* Discount points
* Origination fees
* Closing costs
* Mortgage insurance
* Rate-lock terms
* Prepayment conditions

A mortgage with the lowest nominal interest rate may not have the lowest total borrowing cost.

### Geographic Comparison Is Exploratory

The tool compares state-level rate data, but borrowers normally purchase property in a particular location rather than choose a state solely based on mortgage rates.

The geographic scan is therefore primarily useful for exploring how mortgage-rate availability varies across markets.

### External API Dependency

The project relies on the CFPB rate-checker service.

Changes to:

* API endpoints
* Query parameters
* Loan classifications
* Available products
* Data formats

may require updates to the code.

### Conforming Loan Limits Change

The script currently uses a fixed loan-amount threshold when deciding whether to attempt conforming or jumbo data first.

Conforming loan limits change over time and can also differ for designated high-cost areas. The fallback mechanism helps retrieve available data, but the internal threshold should not be treated as an authoritative current conforming-loan-limit calculation.

---

## Possible Future Improvements

Potential extensions include:

* Retrieve current conforming-loan limits dynamically
* Compare APR in addition to nominal interest rates
* Include mortgage points and fees where available
* Track rates historically
* Plot geographic rate distributions on a U.S. map
* Calculate monthly principal-and-interest payments
* Compare total interest over the life of the loan
* Add refinance scenarios
* Export scan results to CSV
* Build a standalone Streamlit or web interface

---

## Skills Demonstrated

This project demonstrates experience with:

* REST API integration
* Financial data analysis
* Interactive Python applications
* Data processing with pandas
* Data visualization
* User-interface development with ipywidgets
* Rate-limit handling
* Automated multi-region data collection
* Ranking and comparison algorithms
* Mortgage and consumer-finance data exploration

---

## Author

**Yan Zhu**

Python · Data Analysis · Financial Analytics · API Integration
