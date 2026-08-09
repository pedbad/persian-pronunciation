from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
import pytest

from users.forms import RegisterForm

User = get_user_model()


@pytest.mark.django_db
def test_register_requires_staff_or_redirects_to_login(client):
    """
    Anonymous visitors cannot access /users/register/.
    They are redirected to login by AdminRequiredMixin.
    """
    url = reverse("users:register")
    resp = client.get(url)
    assert resp.status_code in (302, 303)
    assert reverse("users:login") in resp.headers.get("Location", "")


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_staff_can_register_user_and_invite_is_sent(client, django_capture_on_commit_callbacks):
    """
    GIVEN a logged-in staff/admin user
    WHEN they submit the register form
    THEN a new user is created with an unusable password,
         an invite email is sent (via post_save signal on_commit),
         and we redirect to the new user's role landing page.
    """
    # Log in as staff/admin
    admin = User.objects.create_user(
        email="admin@example.com",
        password="adminpass",
        is_active=True,
        is_staff=True,
        role="admin",
    )
    client.force_login(admin)

    url = reverse("users:register")
    # No password is posted. RegisterForm drops password1/password2 so the admin
    # is never asked for a credential the invite flow immediately discards (D8).
    form_data = {
        "email": "newstudent@example.com",
        "role": "student",
    }

    # Execute on_commit callbacks that the signal registers
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        resp = client.post(url, data=form_data, follow=True)

    # We now keep the creator (admin) on their own dashboard
    assert resp.redirect_chain
    assert resp.resolver_match.view_name == "users:admin_home"

    # New user exists and has an unusable password (invite flow)
    new_user = User.objects.get(email="newstudent@example.com")
    assert not new_user.has_usable_password()

    # The form must not collect a password at all. Django ignores unrecognised
    # POST keys, so a passwordless POST succeeding does not by itself prove the
    # fields are gone - assert on the form's own fields. password1/password2 are
    # declared on UserCreationForm, so they are easy to reintroduce by accident.
    form = RegisterForm()
    assert "password1" not in form.fields
    assert "password2" not in form.fields

    # Exactly one invite email was sent by the signal
    assert len(callbacks) >= 1  # at least one callback was scheduled
    assert len(mail.outbox) == 1
    body = (
        mail.outbox[0].alternatives[0][0] if mail.outbox[0].alternatives else mail.outbox[0].body
    ).lower()
    assert "/users/reset/" in body
