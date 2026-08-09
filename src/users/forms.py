# src/users/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm

# Unfold-styled admin forms
from unfold.forms import (
    UserChangeForm as UnfoldUserChangeForm,
    UserCreationForm as UnfoldUserCreationForm,
)

User = get_user_model()


# --- Public (non-admin) registration form you already had --------------------
class RegisterForm(DjangoUserCreationForm):
    """Admin-facing form for creating a learner account.

    No password is collected. RegisterView calls set_unusable_password() on the
    new user, and users/signals.py then emails them a set-password invite - the
    onboarding path Decision D8 specifies.

    password1/password2 are set to None deliberately. Django declares them on
    the UserCreationForm class rather than in Meta.fields, so narrowing fields
    to ("email",) does not remove them; setting the name to None on a subclass
    is Django's documented way to opt out of an inherited declared field.
    Without it the form demands a password it immediately discards.
    """

    # expose role for now (default student)
    role = forms.ChoiceField(choices=User.Roles.choices, initial=User.Roles.STUDENT)

    password1 = None
    password2 = None

    class Meta(DjangoUserCreationForm.Meta):
        model = User
        # our model uses email as USERNAME_FIELD
        fields = ("email",)

    def save(self, commit=True):
        """Skip UserCreationForm.save(), which reads cleaned_data["password1"].

        That key no longer exists, so the parent implementation would raise
        KeyError. The caller decides the password state instead.
        """
        return forms.ModelForm.save(self, commit=commit)


# --- Admin-only forms (Unfold-styled) ---------------------------------------
class AdminUserAddForm(UnfoldUserCreationForm):
    """Used by Django admin Add User page (gives Unfold-styled password1/2)."""

    class Meta(UnfoldUserCreationForm.Meta):
        model = User
        fields = ("email",)  # password1/password2 come from parent form


class AdminUserChangeForm(UnfoldUserChangeForm):
    """Used by Django admin Change User page (Unfold-styled widgets)."""

    class Meta(UnfoldUserChangeForm.Meta):
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
