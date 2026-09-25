from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'
    verbose_name = 'Library Management'

    def ready(self):
        # Import signal handlers so they get registered when the app starts.
        import library.signals  # noqa: F401
