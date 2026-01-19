# 📈 Automated NIFTY50 Sector Analysis & Daily Email Report

This project automatically generates a **daily sector-wise performance analysis of all NIFTY50 stocks** and emails the report using a scheduled GitHub Action.  
The Python script runs entirely in the cloud — **no local system required**.

---

## 🚀 Features

- Fetches the latest **NIFTY50 price data** using `yfinance`
- Performs **sector-wise impact analysis**
- Adds NSE sector stock counts using NSE APIs
- Generates an HTML formatted email report
- Sends the email daily at a scheduled time
- Runs automatically using **GitHub Actions**
- No need to keep your laptop or server running

---


## 📂 Repository Structure
├── stock_mail.py # Main Python script that generates and sends the report
├── requirements.txt # Python dependencies
└── .github/
└── workflows/
└── run-report.yml # GitHub Actions workflow file

---


