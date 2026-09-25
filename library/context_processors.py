def librarian_status(request):
    """
    Makes `is_librarian` available in every template, so the navbar and
    other templates can show/hide librarian-only links without repeating
    profile lookups in every view.
    """
    is_librarian = False
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile is not None:
            is_librarian = profile.is_staff_member
        else:
            is_librarian = request.user.is_staff or request.user.is_superuser
    return {'is_librarian': is_librarian}
