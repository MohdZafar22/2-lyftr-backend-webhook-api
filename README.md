# 🚀 Lyftr Backend Webhook API  
**Backend Technical Assignment – Lyftr.ai**

A production-style, containerized **FastAPI** backend service built as part of the **Lyftr.ai Internship Backend Technical Assignment**.  
The system securely ingests WhatsApp-like webhook messages with **HMAC authentication**, ensures **idempotent processing**, and provides **analytics, health checks, logging, and metrics**.

---

## 📌 Features

- 🔐 **Secure Webhook Ingestion**
  - HMAC-SHA256 signature verification using raw request body
  - Invalid signatures rejected with `401 Unauthorized`

- ♻️ **Idempotent Message Handling**
  - Messages stored exactly once using database-level constraints
  - Duplicate webhook calls safely return success without reinsertion

- 📄 **Messages API**
  - Pagination with `limit` and `offset`
  - Filtering by sender (`from`) and timestamp (`since`)
  - Case-insensitive text search (`q`)
  - Deterministic ordering by timestamp and message ID

- 📊 **Analytics**
  - Total messages
  - Unique senders count
  - Messages per sender (top 10)
  - First and last message timestamps

- ❤️ **Health Checks**
  - Liveness and readiness endpoints for container health monitoring

- 📈 **Observability**
  - Structured JSON logs per request
  - Prometheus-style metrics endpoint

- 🐳 **Dockerized Setup**
  - Runs using Docker Compose
  - SQLite database stored in a Docker volume

---

## 🧱 Tech Stack

- **Language:** Python 3.11  
- **Framework:** FastAPI  
- **Database:** SQLite  
- **Containerization:** Docker, Docker Compose  
- **Logging:** Structured JSON logs  
- **Metrics:** Prometheus-compatible exposition  

---

## ⚙️ Setup & Run (Windows)

### Prerequisites
- Docker Desktop (WSL2 enabled)
- PowerShell
- VS Code (recommended)

### Set Environment Variables
```powershell
$env:WEBHOOK_SECRET="testsecret"
$env:DATABASE_URL="sqlite:////data/app.db"


## 📁 Project Structure
├── app
│ ├── main.py # FastAPI app and routes
│ ├── config.py # Environment configuration
│ ├── models.py # Database initialization
│ ├── storage.py # Database operations
│ ├── logging_utils.py # Structured JSON logging
│ └── metrics.py # Metrics helpers
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── send_webhook.ps1 # PowerShell script to test webhook
└── README.md



