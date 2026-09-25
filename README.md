<<<<<<< HEAD
# 📚 BookNest — Library Management System

A full-stack Library Management System built with **Django** (Python), **SQLite**, and vanilla **HTML5 / CSS3 / JavaScript**, using Django's MVT (Model-View-Template) architecture. Designed as a portfolio-ready project for a Full Stack Python Developer fresher.

---

## ✨ Features

### Authentication
- User registration with validation
- Login / logout using Django's built-in authentication system
- Two roles: **Librarian (Admin)** and **Member (regular user)**
- Password hashing handled entirely by Django (never stored manually)
- Protected pages via `@login_required` and a custom `librarian_required` decorator

### Librarian / Admin Dashboard
- Total books, available books, issued books, total registered users
- Recently issued & recently returned books
- Add / edit / delete / search books
- Issue books to any member, accept returns
- View all issued books (filterable by status)
- View all registered users

### Book Management
- Full `Book` model: title, author, ISBN, category, publisher, publication date, total/available copies, description, cover image, created date
- Search by title, author, ISBN, or category
- Category filtering + pagination
- Availability status badges

### Book Issuing & Fines
- Members can self-issue any available book
- Prevents issuing when no copies are available
- Automatic due date (14 days from issue)
- Automatic fine calculation: **₹5 per late day**
- Status tracking: Issued → Overdue → Returned

### Member Dashboard
- Total issued, currently issued, returned, overdue books
- Total fine due
- Full borrowing history ("My Books")

### Frontend
- Fully responsive, mobile-friendly, professional library-themed UI
- Custom CSS (no frontend frameworks) + vanilla JavaScript
- Mobile hamburger navbar, auto-dismissing alerts, delete/issue confirmations, client-side form validation

---

## 🛠️ Technologies Used

| Layer          | Technology                     |
|----------------|---------------------------------|
| Backend        | Python 3, Django 4.2+            |
| Database       | SQLite                          |
| Frontend       | HTML5, CSS3, JavaScript (vanilla)|
| Templating     | Django Templates (DTL)          |
| Architecture   | Django MVT                      |
| Image handling | Pillow                          |

---

## 📁 Project Structure

```
library_management/
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── library_management/          # Project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── library/                     # Main app
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── create_sample_data.py
│   ├── templates/
│   │   └── library/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── dashboard.html
│   │       ├── librarian_dashboard.html
│   │       ├── books.html
│   │       ├── book_detail.html
│   │       ├── add_book.html
│   │       ├── edit_book.html
│   │       ├── delete_book.html
│   │       ├── issue_book.html
│   │       ├── issued_books.html
│   │       ├── return_book.html
│   │       ├── profile.html
│   │       ├── my_books.html
│   │       ├── registered_users.html
│   │       └── _book_form_fields.html
│   ├── static/
│   │   └── library/
│   │       ├── css/style.css
│   │       ├── js/script.js
│   │       └── images/
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── urls.py
│   ├── views.py
│   └── __init__.py
│
├── media/                       # Uploaded book cover images (created at runtime)
└── db.sqlite3                   # Created after migration
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.10+ installed on your machine
- pip (comes with Python)
- (Optional) VS Code with the Python extension

### 2. Extract the project
Unzip the provided file anywhere on your computer, e.g. `C:\Projects\library_management` or `~/Projects/library_management`.

### 3. Create and activate a virtual environment

**Windows (PowerShell / VS Code terminal):**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser (for Django Admin access)
```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email, and password.

### 7. Load sample data (recommended)
This creates sample categories, 12 sample books, a librarian account, and 3 sample members:
```bash
python manage.py create_sample_data
```

Sample login credentials created by this command:
- **Librarian:** `librarian` / `librarian123`
- **Member:** `john_doe` / `member123` (also `jane_smith`, `mike_brown`)

### 8. Run the development server
```bash
python manage.py runserver
```

### 9. Open the site
Visit **http://127.0.0.1:8000/** in your browser.

### 10. Access Django Admin
Visit **http://127.0.0.1:8000/admin/** and log in with the superuser you created in step 6.

---

## 🧪 Testing the Application

1. **Register** a new account at `/register/` and log in.
2. Browse `/books/`, search by title/author/ISBN, and filter by category.
3. Open a book's detail page and click **"Request / Issue This Book"**.
4. Check `/my-books/` and `/dashboard/` to see the issued book, due date, and any fine.
5. Log out, then log in as the **librarian** account (`librarian` / `librarian123`).
6. Visit `/dashboard/` to see the librarian dashboard with statistics.
7. Try **Add Book**, **Edit Book**, **Delete Book**, **Issue Book**, and **Return Book** (`/issued/`).
8. Confirm that available copies decrease on issue and increase on return, and that a fine is calculated for books returned after the 14-day due date.
9. Visit `/users/` to see all registered members.
10. Visit `/admin/` to confirm Book, Issue, Category, and UserProfile are all registered with search/filter/list options.

---

## 📄 Pages Overview

| Page                  | URL                         | Access          |
|------------------------|------------------------------|-----------------|
| Home                   | `/`                          | Public          |
| Register                | `/register/`                | Public          |
| Login                   | `/login/`                   | Public          |
| Dashboard                | `/dashboard/`               | Logged-in       |
| Browse Books            | `/books/`                    | Public          |
| Book Detail              | `/books/<id>/`              | Public          |
| Add Book                | `/books/add/`               | Librarian only  |
| Edit Book                | `/books/<id>/edit/`         | Librarian only  |
| Delete Book              | `/books/<id>/delete/`       | Librarian only  |
| Issue Book (self)        | `/books/<id>/request-issue/`| Members         |
| Issue Book (manual)      | `/issue/`                   | Librarian only  |
| All Issued Books          | `/issued/`                  | Librarian only  |
| Return Book               | `/issued/<id>/return/`      | Librarian only  |
| My Books                | `/my-books/`                 | Members         |
| Profile                  | `/profile/`                  | Logged-in       |
| Registered Users          | `/users/`                    | Librarian only  |
| Django Admin              | `/admin/`                    | Superuser       |

---

## 🔒 Security Notes
- CSRF tokens are included in every form (`{% csrf_token %}`)
- Passwords are hashed and validated using Django's built-in `AUTH_PASSWORD_VALIDATORS`
- Librarian-only views are protected by a custom `librarian_required` decorator
- All state-changing actions (issue, return, delete) require a `POST` request, not just a link

## 💡 Notes
- This project uses **SQLite only**, as required — no external database server needed.
- `DEBUG = True` is set for local development. Set it to `False` and configure `ALLOWED_HOSTS` before any real deployment.
- The `SECRET_KEY` in `settings.py` is a development key — replace it with an environment-variable-based secret for production use.
=======
# library-management-project
A full-stack Library Management System developed using Python, Django, SQLite, HTML, CSS, and JavaScript. The project helps manage books, users, and library records through a simple and user-friendly interface.
>>>>>>> 4a9e14c6125393016bfd2c4fce88b68c0b5b50f3
