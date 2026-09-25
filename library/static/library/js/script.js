/* ==========================================================================
   BookNest Library Management System — Client-side JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    initMobileNavbar();
    initAutoDismissAlerts();
    initDeleteConfirmations();
    initIssueConfirmation();
    initRegisterFormValidation();
    initBookFormValidation();
});

/* ---------- Mobile navbar toggle ---------- */
function initMobileNavbar() {
    var toggle = document.getElementById('navbarToggle');
    var links = document.getElementById('navbarLinks');
    if (!toggle || !links) return;

    toggle.addEventListener('click', function () {
        links.classList.toggle('open');
    });

    // Close the mobile menu when a link is clicked
    links.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            links.classList.remove('open');
        });
    });
}

/* ---------- Auto-dismiss Django messages after a few seconds ---------- */
function initAutoDismissAlerts() {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.4s ease';
            alert.style.opacity = '0';
            setTimeout(function () { alert.remove(); }, 400);
        }, 6000);
    });
}

/* ---------- Confirm before deleting a book ---------- */
function initDeleteConfirmations() {
    var deleteForms = document.querySelectorAll('.confirm-delete-form');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            var confirmed = window.confirm('This will permanently delete the book. Are you sure?');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });

    // Also confirm on plain "Delete Book" links that go to the confirm page —
    // no destructive action happens until the confirm page's own form is submitted,
    // so no extra JS confirmation is required there.
}

/* ---------- Confirm before self-issuing a book ---------- */
function initIssueConfirmation() {
    var issueForm = document.getElementById('confirmIssueForm');
    if (!issueForm) return;

    issueForm.addEventListener('submit', function (event) {
        var confirmed = window.confirm('Issue this book to yourself now? It will be due in 14 days.');
        if (!confirmed) {
            event.preventDefault();
        }
    });
}

/* ---------- Registration form: simple client-side checks ---------- */
function initRegisterFormValidation() {
    var form = document.querySelector('.auth-card-wide form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        var password1 = form.querySelector('#id_password1');
        var password2 = form.querySelector('#id_password2');
        var email = form.querySelector('#id_email');

        var errors = [];

        if (password1 && password2 && password1.value !== password2.value) {
            errors.push('Passwords do not match.');
        }
        if (password1 && password1.value.length > 0 && password1.value.length < 6) {
            errors.push('Password must be at least 6 characters long.');
        }
        if (email && email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
            errors.push('Please enter a valid email address.');
        }

        if (errors.length > 0) {
            event.preventDefault();
            showClientAlert(errors.join(' '));
        }
    });
}

/* ---------- Add/Edit book form: available copies cannot exceed total ---------- */
function initBookFormValidation() {
    var totalInput = document.querySelector('#id_total_copies');
    var availableInput = document.querySelector('#id_available_copies');
    if (!totalInput || !availableInput) return;

    var form = totalInput.closest('form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        var total = parseInt(totalInput.value, 10);
        var available = parseInt(availableInput.value, 10);

        if (!isNaN(total) && !isNaN(available) && available > total) {
            event.preventDefault();
            showClientAlert('Available copies cannot be greater than total copies.');
        }
    });
}

/* ---------- Small helper to surface a client-side-only alert ---------- */
function showClientAlert(text) {
    var container = document.querySelector('.messages-container') || createMessagesContainer();
    var alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.innerHTML = '<span>' + text + '</span><button class="alert-close" onclick="this.parentElement.remove()">&times;</button>';
    container.prepend(alert);
}

function createMessagesContainer() {
    var container = document.createElement('div');
    container.className = 'messages-container';
    var main = document.querySelector('.main-content');
    main.insertBefore(container, main.firstChild);
    return container;
}
