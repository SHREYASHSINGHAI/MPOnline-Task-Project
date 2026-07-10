# TaskFlow — Task Management System

A full-stack Task Management application built with **HTML/CSS/JS**, **Flask**, and **MySQL**.

---

## 📁 Project Structure

```
task-manager/
├── backend/
│   ├── app.py              Flask REST API
│   ├── config.py           MySQL connection settings
│   ├── models.py           Database helper functions
│   ├── init_db.sql         DB initialization script
│   └── requirements.txt    Python dependencies
├── frontend/
│   ├── index.html          Single-page UI
│   ├── style.css           Dark glassmorphism styles
│   └── app.js              Fetch API + UI logic
└── README.md
```

---

## ⚡ Quick Setup

### Step 1 — MySQL Database

Open MySQL (Workbench or CLI) and run:

```bash
mysql -u root -p < backend/init_db.sql
```

Or paste the contents of `init_db.sql` into MySQL Workbench and execute.

> Update `backend/config.py` if your MySQL password differs from `root`.

---

### Step 2 — Backend (Flask)

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

Flask runs at: **http://localhost:5000**

---

### Step 3 — Frontend

Simply open `frontend/index.html` in your browser:

```bash
start frontend/index.html    # Windows
```

Or open it directly from File Explorer.

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/tasks` | List all tasks |
| GET    | `/api/tasks?search=Alice` | Search tasks |
| GET    | `/api/tasks?completed=true` | Filter by status |
| GET    | `/api/tasks/<id>` | Get single task |
| POST   | `/api/tasks` | Create task |
| PUT    | `/api/tasks/<id>` | Update task |
| DELETE | `/api/tasks/<id>` | Delete task |
| GET    | `/api/stats` | Dashboard stats |

---

## 🗄️ Database Schema

```sql
CREATE TABLE tasks (
    task_id       INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    task_title    VARCHAR(255) NOT NULL,
    completed     BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```
