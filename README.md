# Data Querying Mechanism

A reusable and extensible data querying mechanism.

---

## 📡 API Endpoints

### 1. Get Posts with Filters and Includes

```http
GET /api/posts?status=draft&include=tags,user
```

Fetch posts filtered by status and include related data (tags, user).

### 2. Get a Single Post by ID

```http
GET /api/posts/1?include=tags,user,comments
```

Retrieve a specific post with its associated tags, user, and comments.

### 3. Get a User by ID

```http
GET /api/users/1?include=posts,comments
```

Retrieve user details along with related posts and comments.

---

## Tech Stack

- **Python 3.13**
- **Django**

---

## How to Run the Project

### Create and Activate a Virtual Environment

A **virtual environment (venv)** keeps your dependencies isolated from your global Python setup.

#### 🧩 On macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 🪟 On Windows (PowerShell):

```bash
python -m venv venv
venv\Scripts\activate
```

---

### Install Dependencies

Once the virtual environment is active, install all required packages:

```bash
pip install -r requirements.txt
```

### .env file

Copy .env.example and populate it accordingly.

### Migrations

```bash
python manage.py migrate
```

### Run the Application

Developer server:

```bash
python manage.py runserver --noreload
```

By default, the API will be available at:
👉 **http://127.0.0.1:8000**

Interactive API docs are automatically available at:

- Swagger UI: [http://127.0.0.1:8000/schema/swagger-ui/](http://127.0.0.1:8000/schema/swagger-ui/)
- ReDoc: [http://127.0.0.1:8000/schema/redoc/](http://127.0.0.1:8000/schema/redoc/)
