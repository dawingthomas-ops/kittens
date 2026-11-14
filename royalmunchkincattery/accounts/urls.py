from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import AdministratorAuthenticationForm

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=AdministratorAuthenticationForm,
        ),
        name="login",
    ),
    # Django 5 requires POST for logout; the dashboard sidebar renders a form.
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
