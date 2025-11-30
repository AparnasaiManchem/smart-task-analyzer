A simple Django backend + static frontend assignment that ranks tasks using urgency, importance, effort and dependencies.

Project Structure

smart-task-analyzer/

backend/ (Django project)

tasks/ (Django app with scoring algorithm)

frontend/ (index.html, script.js, styles.css)

manage.py

venv/ (ignored)

Features

Score tasks using:

Due date (urgency)

Importance

Estimated hours (effort)

Dependency impact

Detect circular dependencies

Sort tasks by total score

API endpoints:

POST /api/tasks/analyze/

GET /api/tasks/suggest/