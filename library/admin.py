from django.contrib import admin

from .models import Book, Category, Issue, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'isbn', 'category', 'total_copies',
        'available_copies', 'created_date',
    )
    list_filter = ('category', 'publisher')
    search_fields = ('title', 'author', 'isbn')
    ordering = ('-created_date',)
    date_hierarchy = 'created_date'


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'book', 'user', 'issue_date', 'due_date', 'return_date',
        'status', 'fine_amount', 'fine_paid',
    )
    list_filter = ('status', 'fine_paid', 'issue_date')
    search_fields = ('book__title', 'user__username', 'book__isbn')
    ordering = ('-issue_date',)
    date_hierarchy = 'issue_date'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_librarian', 'phone', 'created_date')
    list_filter = ('is_librarian',)
    search_fields = ('user__username', 'user__email', 'phone')
    ordering = ('user__username',)
