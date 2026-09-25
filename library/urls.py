from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('books/<int:pk>/request-issue/', views.request_issue_book, name='request_issue_book'),

    # Issuing / returning (librarian)
    path('issue/', views.issue_book, name='issue_book'),
    path('issued/', views.issued_books, name='issued_books'),
    path('issued/<int:pk>/return/', views.return_book, name='return_book'),

    # Member area
    path('my-books/', views.my_books, name='my_books'),
    path('profile/', views.profile, name='profile'),

    # Librarian: registered users
    path('users/', views.registered_users, name='registered_users'),
]
