from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Book, Category, Issue, UserProfile


class RegisterForm(UserCreationForm):
    """Registration form for new library members (not librarians)."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(
        max_length=255, required=False, widget=forms.Textarea(attrs={'rows': 2})
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'phone': self.cleaned_data.get('phone', ''),
                    'address': self.cleaned_data.get('address', ''),
                },
            )
        return user


class LoginForm(AuthenticationForm):
    """Simple styled login form built on Django's AuthenticationForm."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class BookForm(forms.ModelForm):
    """Used for both adding and editing a book (librarian only)."""

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'category', 'publisher',
            'publication_date', 'total_copies', 'available_copies',
            'description', 'image',
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_copies')
        available = cleaned_data.get('available_copies')
        if total is not None and available is not None and available > total:
            raise forms.ValidationError(
                'Available copies cannot be greater than total copies.'
            )
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class IssueBookForm(forms.ModelForm):
    """Used by a librarian to manually issue a book to any registered user."""

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        help_text='Select the member borrowing the book.',
    )

    class Meta:
        model = Issue
        fields = ['user', 'book']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)

    def clean_book(self):
        book = self.cleaned_data['book']
        if book.available_copies < 1:
            raise forms.ValidationError('No copies of this book are currently available.')
        return book


class ProfileForm(forms.ModelForm):
    """Lets a user update their own contact details."""

    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['phone', 'address']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class BookSearchForm(forms.Form):
    """A small non-model form used to search/filter the book catalogue."""

    q = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Search by title, author or ISBN...'}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
    )
