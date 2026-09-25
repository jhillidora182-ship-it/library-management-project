import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from library.models import Book, Category, Issue, UserProfile


class Command(BaseCommand):
    help = 'Creates sample categories, books, and users for the Library Management System.'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # --- Categories -----------------------------------------------------
        category_names = [
            'Fiction', 'Science', 'History', 'Technology',
            'Biography', 'Self-Help', 'Fantasy', 'Poetry',
        ]
        categories = {}
        for name in category_names:
            category, _ = Category.objects.get_or_create(name=name)
            categories[name] = category
        self.stdout.write(self.style.SUCCESS(f'  {len(categories)} categories ready.'))

        # --- Users ------------------------------------------------------------
        if not User.objects.filter(username='librarian').exists():
            librarian = User.objects.create_user(
                username='librarian',
                email='librarian@library.com',
                password='librarian123',
                first_name='Lib',
                last_name='Rarian',
                is_staff=True,
            )
            UserProfile.objects.update_or_create(
                user=librarian, defaults={'is_librarian': True}
            )
            self.stdout.write(self.style.SUCCESS('  Librarian account created (librarian / librarian123).'))
        else:
            self.stdout.write('  Librarian account already exists, skipping.')

        sample_members = [
            ('john_doe', 'John', 'Doe', 'john@example.com'),
            ('jane_smith', 'Jane', 'Smith', 'jane@example.com'),
            ('mike_brown', 'Mike', 'Brown', 'mike@example.com'),
        ]
        members = []
        for username, first, last, email in sample_members:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': email},
            )
            if created:
                user.set_password('member123')
                user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'is_librarian': False})
            members.append(user)
        self.stdout.write(self.style.SUCCESS(f'  {len(members)} sample members ready (password: member123).'))

        # --- Books --------------------------------------------------------
        sample_books = [
            ('The Alchemist', 'Paulo Coelho', '9780061122415', 'Fiction', 'HarperOne', '1988-04-15', 5,
             'A shepherd boy travels from Spain to Egypt in search of treasure and discovers his personal legend along the way.'),
            ('A Brief History of Time', 'Stephen Hawking', '9780553380163', 'Science', 'Bantam', '1988-04-01', 4,
             'An accessible exploration of cosmology, covering the Big Bang, black holes, and the nature of time.'),
            ('Sapiens', 'Yuval Noah Harari', '9780062316097', 'History', 'Harper', '2015-02-10', 6,
             'A sweeping look at how Homo sapiens came to dominate the world, from the cognitive revolution to today.'),
            ('Clean Code', 'Robert C. Martin', '9780132350884', 'Technology', 'Prentice Hall', '2008-08-01', 3,
             'A handbook of agile software craftsmanship, teaching principles and practices for writing clean, maintainable code.'),
            ('Steve Jobs', 'Walter Isaacson', '9781451648539', 'Biography', 'Simon & Schuster', '2011-10-24', 4,
             'The definitive biography of Apple co-founder Steve Jobs, based on exclusive interviews.'),
            ('Atomic Habits', 'James Clear', '9780735211292', 'Self-Help', 'Avery', '2018-10-16', 7,
             'A practical guide to building good habits and breaking bad ones through small, incremental changes.'),
            ('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 'Fantasy', 'Houghton Mifflin', '1937-09-21', 5,
             'Bilbo Baggins is swept into an epic quest to reclaim a dwarf kingdom from the dragon Smaug.'),
            ('Leaves of Grass', 'Walt Whitman', '9781613820392', 'Poetry', 'Dover', '1855-07-04', 2,
             'A landmark collection of American poetry celebrating democracy, nature, and the human spirit.'),
            ('The Selfish Gene', 'Richard Dawkins', '9780198788607', 'Science', 'Oxford University Press', '1976-01-01', 3,
             'An influential exploration of evolution from the perspective of the gene as the unit of selection.'),
            ('1984', 'George Orwell', '9780451524935', 'Fiction', 'Signet Classic', '1949-06-08', 6,
             'A dystopian vision of a totalitarian future where the state controls truth, thought, and history.'),
            ('Educated', 'Tara Westover', '9780399590504', 'Biography', 'Random House', '2018-02-20', 4,
             'A memoir about a woman who leaves her survivalist family and eventually earns a PhD from Cambridge.'),
            ('Python Crash Course', 'Eric Matthes', '9781593279288', 'Technology', "No Starch Press", '2019-05-03', 5,
             'A hands-on, project-based introduction to programming with Python for complete beginners.'),
        ]

        created_count = 0
        for title, author, isbn, cat_name, publisher, pub_date, copies, desc in sample_books:
            book, created = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': title,
                    'author': author,
                    'category': categories.get(cat_name),
                    'publisher': publisher,
                    'publication_date': datetime.datetime.strptime(pub_date, '%Y-%m-%d').date(),
                    'total_copies': copies,
                    'available_copies': copies,
                    'description': desc,
                },
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'  {created_count} new sample books created ({len(sample_books)} total in list).'))

        # --- A couple of sample issues, so dashboards aren't empty ------------
        if members and not Issue.objects.exists():
            book_qs = Book.objects.filter(available_copies__gt=0)[:2]
            for member, book in zip(members, book_qs):
                Issue.objects.create(user=member, book=book)
                book.available_copies -= 1
                book.save()
            self.stdout.write(self.style.SUCCESS('  Sample issue records created.'))

        self.stdout.write(self.style.SUCCESS('Sample data setup complete!'))
        self.stdout.write('')
        self.stdout.write('You can now log in with:')
        self.stdout.write('  Librarian -> username: librarian   password: librarian123')
        self.stdout.write('  Member    -> username: john_doe    password: member123')
