# Sales CRM Application

A full-stack Customer Relationship Management (CRM) application built using Django REST Framework and React to manage leads, customers, deals, and activities.

## Features

- **Lead Management** — Create, view, and manage sales leads.
- **Customer Management** — Manage customer information.
- **Deal Management** — Track sales opportunities and deal stages.
- **Activity Management** — Organize and track sales-related activities.
- **Authentication** — Secure access to application features.
- **Dashboard** — View sales-related information in one place.

## Tech Stack

**Frontend**
- React
- JavaScript
- HTML
- CSS

**Backend**
- Python
- Django
- Django REST Framework

**Database**
- SQLite or the database configured in Django settings

## Project Structure

```text
sales-crm/
├── accounts/
├── activities/
├── authentication/
├── config/
├── customers/
├── dashboard/
├── deals/
├── frontend/
├── leads/
├── manage.py
└── README.md
```

## Getting Started

### Prerequisites

- Python
- Node.js and npm
- Git

### Backend Setup

1. Clone the repository:

   ```bash
   https://github.com/durga-prasad-thalapala/sales-crm.git
   cd sales-crm
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   On Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the backend server:

   ```bash
   python manage.py runserver
   ```

### Frontend Setup

Open another terminal and run:

```bash
cd frontend
npm install
npm run dev
```

## Project Status

This project is under development. More features and improvements may be added over time.
