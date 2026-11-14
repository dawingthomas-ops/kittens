from django.contrib.admin import AdminSite

from accounts.forms import AdministratorAuthenticationForm


class SuperuserOnlyAdminSite(AdminSite):
    login_form = AdministratorAuthenticationForm

    def has_permission(self, request):
        user = request.user
        return user.is_active and user.is_superuser
