# Satellite Dashboard Backend

This repository contains the backend for the Trinetra Satellite Monitoring Dashboard. It is built with Flask and uses SQLite for data storage. It provides RESTful API endpoints to serve telemetry data to the frontend.

---

## Technologies Used

- Python 3.x
- Flask
- SQLite
- Flask-CORS
- Virtual Environment (venv)

---

## Project Structure

```
backend/
├── app.py
├── telemetry.db  (excluded by .gitignore)
├── requirements.txt
├── static/
└── templates/
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/satellite-dashboard-backend.git
cd satellite-dashboard-backend
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

---

## API Endpoints

| Method | Endpoint    | Description         |
|--------|-------------|---------------------|
| GET    | /api/data   | Retrieve data       |
| POST   | /api/data   | Submit new data     |

(Adjust routes as applicable.)

---

## Environment Variables

You can use a `.env` file for configuration:

```
FLASK_ENV=development
DATABASE_URL=sqlite:///telemetry.db
```

---

## Deployment Notes

- The `telemetry.db` file is excluded from version control.
- If serving the frontend from Flask, place the React `build/` directory inside `static/` and serve it using `send_from_directory`.

---

