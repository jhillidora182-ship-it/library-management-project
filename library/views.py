from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (BookForm, BookSearchForm, IssueBookForm, LoginForm,
                     ProfileForm, RegisterForm)
from .models import Book, Category, Issue, UserProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_librarian(user):
    if not user.is_authenticated:
        return False
    profile = getattr(user, 'profile', None)
    if profile is not None:
        return profile.is_staff_member
    return user.is_staff or user.is_superuser


def librarian_required(view_func):
    """Restrict a view to librarian/admin accounts only."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _is_librarian(request.user):
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)

    return _wrapped


def _refresh_overdue_statuses(queryset=None):
    """Flip any issued-but-past-due records to 'overdue' so dashboards are accurate."""
    qs = queryset if queryset is not None else Issue.objects.filter(status=Issue.STATUS_ISSUED)
    today = timezone.localdate()
    qs.filter(due_date__lt=today, status=Issue.STATUS_ISSUED).update(status=Issue.STATUS_OVERDUE)


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

def home(request):
    _refresh_overdue_statuses()
    featured_books = Book.objects.filter(available_copies__gt=0).order_by('-created_date')[:6]
    context = {
        'featured_books': featured_books,
        'total_books': Book.objects.count(),
        'total_categories': Category.objects.count(),
        'total_members': User.objects.filter(is_superuser=False).count(),
        'total_issued': Issue.objects.filter(status__in=[Issue.STATUS_ISSUED, Issue.STATUS_OVERDUE]).count(),
    }
    return render(request, 'library/home.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()

    return render(request, 'library/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url or 'dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'library/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    _refresh_overdue_statuses()
    if _is_librarian(request.user):
        return librarian_dashboard(request)
    return user_dashboard(request)


def librarian_dashboard(request):
    context = {
        'total_books': Book.objects.count(),
        'available_books': sum(b.available_copies for b in Book.objects.all()),
        'issued_books_count': Issue.objects.filter(
            status__in=[Issue.STATUS_ISSUED, Issue.STATUS_OVERDUE]
        ).count(),
        'total_users': User.objects.filter(is_superuser=False).count(),
        'recent_issued': Issue.objects.select_related('book', 'user').order_by('-issue_date')[:5],
        'recent_returned': Issue.objects.select_related('book', 'user')
        .filter(status=Issue.STATUS_RETURNED)
        .order_by('-return_date')[:5],
        'overdue_count': Issue.objects.filter(status=Issue.STATUS_OVERDUE).count(),
    }
    return render(request, 'library/librarian_dashboard.html', context)


def user_dashboard(request):
    issues = Issue.objects.filter(user=request.user).select_related('book')
    currently_issued = issues.filter(status__in=[Issue.STATUS_ISSUED, Issue.STATUS_OVERDUE])
    returned = issues.filter(status=Issue.STATUS_RETURNED)
    overdue = issues.filter(status=Issue.STATUS_OVERDUE)
    total_fine = sum(i.fine_amount for i in issues if not i.fine_paid)

    context = {
        'total_issued': issues.count(),
        'currently_issued': currently_issued,
        'returned_count': returned.count(),
        'overdue_count': overdue.count(),
        'total_fine': total_fine,
    }
    return render(request, 'library/dashboard.html', context)


# ---------------------------------------------------------------------------
# Book catalogue
# ---------------------------------------------------------------------------

def book_list(request):
    form = BookSearchForm(request.GET or None)
    books = Book.objects.select_related('category').all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        if query:
            books = books.filter(
                Q(title__icontains=query)
                | Q(author__icontains=query)
                | Q(isbn__icontains=query)
                | Q(category__name__icontains=query)
            )
        if category:
            books = books.filter(category=category)

    paginator = Paginator(books, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'books': page_obj.object_list,
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'library/books.html', context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    already_issued = False
    if request.user.is_authenticated:
        already_issued = Issue.objects.filter(
            user=request.user, book=book, status__in=[Issue.STATUS_ISSUED, Issue.STATUS_OVERDUE]
        ).exists()
    return render(request, 'library/book_detail.html', {
        'book': book,
        'already_issued': already_issued,
    })


@librarian_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'"{book.title}" was added to the catalogue.')
            return redirect('book_detail', pk=book.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm(initial={'total_copies': 1, 'available_copies': 1})

    return render(request, 'library/add_book.html', {'form': form})


@librarian_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{book.title}" was updated successfully.')
            return redirect('book_detail', pk=book.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm(instance=book)

    return render(request, 'library/edit_book.html', {'form': form, 'book': book})


@librarian_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'"{title}" was deleted from the catalogue.')
        return redirect('book_list')
    return render(request, 'library/delete_book.html', {'book': book})


# ---------------------------------------------------------------------------
# Issuing and returning books
# ---------------------------------------------------------------------------

@login_required
def request_issue_book(request, pk):
    """A logged-in member requests/borrows an available book for themselves."""
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        if book.available_copies < 1:
            messages.error(request, 'Sorry, no copies of this book are currently available.')
            return redirect('book_detail', pk=book.pk)

        already_has = Issue.objects.filter(
            user=request.user, book=book, status__in=[Issue.STATUS_ISSUED, Issue.STATUS_OVERDUE]
        ).exists()
        if already_has:
            messages.warning(request, 'You already have this book issued.')
            return redirect('book_detail', pk=book.pk)

        Issue.objects.create(user=request.user, book=book)
        book.available_copies -= 1
        book.save()
        messages.success(request, f'"{book.title}" has been issued to you. Please return it on time to avoid fines.')
        return redirect('my_books')

    return render(request, 'library/issue_book.html', {'book': book, 'self_service': True})


@librarian_required
def issue_book(request):
    """A librarian manually issues a book to any registered member."""
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.issued_by = request.user
            issue.save()
            book = issue.book
            book.available_copies -= 1
            book.save()
            messages.success(
                request,
                f'"{book.title}" has been issued to {issue.user.username}.'
            )
            return redirect('issued_books')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = IssueBookForm()

    return render(request, 'library/issue_book.html', {'form': form, 'self_service': False})


@librarian_required
def issued_books(request):
    _refresh_overdue_statuses()
    status_filter = request.GET.get('status', '')
    issues = Issue.objects.select_related('book', 'user').all()
    if status_filter:
        issues = issues.filter(status=status_filter)

    paginator = Paginator(issues, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'library/issued_books.html', {
        'page_obj': page_obj,
        'issues': page_obj.object_list,
        'status_filter': status_filter,
        'status_choices': Issue.STATUS_CHOICES,
    })


@librarian_required
def return_book(request, pk):
    issue = get_object_or_404(Issue, pk=pk)

    if issue.status == Issue.STATUS_RETURNED:
        messages.info(request, 'This book has already been returned.')
        return redirect('issued_books')

    if request.method == 'POST':
        issue.mark_returned()
        fine_note = f' A fine of ₹{issue.fine_amount} applies.' if issue.fine_amount else ''
        messages.success(
            request,
            f'"{issue.book.title}" returned by {issue.user.username}.{fine_note}'
        )
        return redirect('issued_books')

    return render(request, 'library/return_book.html', {'issue': issue})


@login_required
def my_books(request):
    issues = Issue.objects.filter(user=request.user).select_related('book').order_by('-issue_date')
    return render(request, 'library/my_books.html', {'issues': issues})


# ---------------------------------------------------------------------------
# Profile & user management
# ---------------------------------------------------------------------------

@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=user_profile, user=request.user)

    return render(request, 'library/profile.html', {'form': form})


@librarian_required
def registered_users(request):
    users = User.objects.filter(is_superuser=False).select_related('profile').order_by('username')
    return render(request, 'library/registered_users.html', {'users': users})
