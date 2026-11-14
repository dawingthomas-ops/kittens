import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from core.models import ContactMessage, Post, WaitlistEntry
from kittens.models import Kitten
from reservations.forms import ReservationAdminForm
from reservations.models import Reservation
from reviews.forms import TestimonialAdminForm
from reviews.models import Testimonial
from .forms import KittenForm, KittenImageFormSet, PostForm
from .models import PageView


def _is_admin(user):
    return user.is_active and user.is_superuser


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "accounts:login"

    def test_func(self):
        return _is_admin(self.request.user)


class AdminPostMixin(AdminRequiredMixin):
    """Admin-only, POST-only actions (state changes never happen on GET)."""

    http_method_names = ["post"]


class ReviewModeratorRequiredMixin(AdminRequiredMixin):
    """Only an administrator may moderate reviews."""

    def test_func(self):
        user = self.request.user
        return _is_admin(user) and user.has_perm("reviews.change_testimonial")


class OverviewView(AdminRequiredMixin, TemplateView):
    """KPIs plus the data the Chart.js graphs consume."""

    template_name = "dashboard/overview.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        thirty_days_ago = timezone.now() - timedelta(days=30)

        ctx["total_kittens_available"] = Kitten.objects.filter(status=Kitten.Status.AVAILABLE).count()
        ctx["total_reservations_30d"] = Reservation.objects.filter(created_at__gte=thirty_days_ago).count()
        ctx["pending_testimonials"] = Testimonial.objects.filter(is_approved=False).count()
        ctx["page_views_30d"] = PageView.objects.filter(created_at__gte=thirty_days_ago).count()
        ctx["unhandled_messages"] = ContactMessage.objects.filter(is_handled=False).count()
        ctx["waitlist_waiting"] = WaitlistEntry.objects.filter(is_contacted=False).count()
        ctx["published_posts"] = Post.objects.filter(is_published=True).count()
        ctx["draft_posts"] = Post.objects.filter(is_published=False).count()
        ctx["pipeline_value"] = Reservation.objects.filter(
            status__in=[Reservation.Status.NEW, Reservation.Status.CONTACTED, Reservation.Status.DEPOSIT_RECEIVED]
        ).aggregate(total=Sum("kitten__price"))["total"] or 0
        ctx["recent_reservations"] = Reservation.objects.select_related("kitten").order_by("-created_at")[:8]
        ctx["top_kittens"] = Kitten.objects.exclude(status=Kitten.Status.ADOPTED).order_by("-view_count")[:5]
        return ctx


# ---------------------------------------------------------------- reservations
class ReservationQueueView(AdminRequiredMixin, ListView):
    template_name = "dashboard/reservations.html"
    context_object_name = "reservations"
    paginate_by = 25

    def get_queryset(self):
        qs = Reservation.objects.select_related("kitten").order_by("-created_at")
        status = self.request.GET.get("status")
        if status in dict(Reservation.Status.choices):
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Reservation.Status.choices
        ctx["current_status"] = self.request.GET.get("status", "")
        return ctx


class ReservationEditView(AdminRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationAdminForm
    template_name = "dashboard/reservation_form.html"
    success_url = reverse_lazy("dashboard:reservations")
    context_object_name = "reservation"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Updated reservation for {self.object.full_name}.")
        return response


class ReservationDeleteView(AdminRequiredMixin, DeleteView):
    model = Reservation
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:reservations")
    extra_context = {"what": "reservation", "back_url": reverse_lazy("dashboard:reservations")}

    def form_valid(self, form):
        messages.success(self.request, f"Deleted reservation for {self.object.full_name}.")
        return super().form_valid(form)


class ReservationStatusView(AdminPostMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        new_status = request.POST.get("status")
        if new_status in dict(Reservation.Status.choices):
            reservation.status = new_status
            reservation.save(update_fields=["status", "updated_at"])
            messages.success(request, f"Marked {reservation.full_name} as {reservation.get_status_display().lower()}.")
        return redirect(request.POST.get("next") or reverse("dashboard:reservations"))


def _csv_safe(value):
    """Neutralise spreadsheet formula injection (=, +, -, @ at cell start)."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


class ReservationExportView(AdminRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reservations.csv"'
        writer = csv.writer(response)
        writer.writerow(["Received", "Name", "Email", "Phone", "Prefers", "Message sent via", "Kitten", "Price", "City", "State", "Delivery", "Status", "Message"])
        for r in Reservation.objects.select_related("kitten").order_by("-created_at"):
            writer.writerow([
                _csv_safe(r.created_at.strftime("%Y-%m-%d %H:%M")), _csv_safe(r.full_name), _csv_safe(r.email),
                _csv_safe(r.phone), _csv_safe(r.get_contact_preference_display()), _csv_safe(r.get_message_channel_display()), _csv_safe(r.kitten.name),
                _csv_safe(r.kitten.price), _csv_safe(r.shipping_city), _csv_safe(r.shipping_state),
                _csv_safe(r.get_delivery_method_display()), _csv_safe(r.get_status_display()), _csv_safe(r.message),
            ])
        return response


# ---------------------------------------------------------------- testimonials
class TestimonialModerationView(ReviewModeratorRequiredMixin, ListView):
    template_name = "dashboard/testimonials.html"
    context_object_name = "testimonials"
    paginate_by = 25

    def get_queryset(self):
        return Testimonial.objects.select_related("kitten").order_by("is_approved", "-submitted_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pending_count"] = Testimonial.objects.filter(is_approved=False).count()
        ctx["approved_count"] = Testimonial.objects.filter(is_approved=True).count()
        return ctx


class TestimonialEditView(ReviewModeratorRequiredMixin, UpdateView):
    model = Testimonial
    form_class = TestimonialAdminForm
    template_name = "dashboard/review_form.html"
    success_url = reverse_lazy("dashboard:testimonials")
    context_object_name = "testimonial"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.is_approved and not self.object.approved_at:
            self.object.approve(user=self.request.user)
        elif not self.object.is_approved and (self.object.approved_at or self.object.approved_by):
            self.object.approved_at = None
            self.object.approved_by = None
            self.object.save(update_fields=["approved_at", "approved_by"])
        messages.success(self.request, f"Updated review from {self.object.author_name}.")
        return response


class TestimonialDeleteView(ReviewModeratorRequiredMixin, DeleteView):
    model = Testimonial
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:testimonials")
    extra_context = {"what": "review", "back_url": reverse_lazy("dashboard:testimonials")}

    def form_valid(self, form):
        messages.success(self.request, f"Deleted review from {self.object.author_name}.")
        return super().form_valid(form)


class TestimonialApproveView(ReviewModeratorRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        testimonial = get_object_or_404(Testimonial, pk=pk)
        testimonial.approve(user=request.user)
        messages.success(request, f"Approved review from {testimonial.author_name}.")
        return redirect("dashboard:testimonials")


class TestimonialRejectView(ReviewModeratorRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        testimonial = get_object_or_404(Testimonial, pk=pk)
        testimonial.delete()
        messages.success(request, "Review rejected and removed.")
        return redirect("dashboard:testimonials")


# ---------------------------------------------------------------- kittens
class KittenListView(AdminRequiredMixin, ListView):
    model = Kitten
    template_name = "dashboard/kitten_list.html"
    context_object_name = "kittens"
    paginate_by = 25
    ordering = ["-created_at"]


class KittenFormMixin:
    model = Kitten
    form_class = KittenForm
    template_name = "dashboard/kitten_form.html"
    success_url = reverse_lazy("dashboard:kittens")
    form_title = "Add kitten"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if "image_formset" not in kwargs:
            if self.request.method == "POST":
                ctx["image_formset"] = KittenImageFormSet(self.request.POST, self.request.FILES, instance=getattr(self, "object", None))
            else:
                ctx["image_formset"] = KittenImageFormSet(instance=getattr(self, "object", None))
        ctx["form_title"] = self.form_title
        return ctx

    def form_valid(self, form):
        formset = KittenImageFormSet(self.request.POST, self.request.FILES, instance=form.instance)
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, image_formset=formset))
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        messages.success(self.request, f"Saved {self.object.name}.")
        return redirect(self.success_url)


class KittenCreateView(AdminRequiredMixin, KittenFormMixin, CreateView):
    form_title = "Add kitten"


class KittenUpdateView(AdminRequiredMixin, KittenFormMixin, UpdateView):
    form_title = "Edit kitten"


class KittenDeleteView(AdminRequiredMixin, DeleteView):
    model = Kitten
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:kittens")
    extra_context = {"what": "kitten", "back_url": reverse_lazy("dashboard:kittens")}

    def form_valid(self, form):
        messages.success(self.request, f"Deleted {self.object.name}.")
        return super().form_valid(form)


# ---------------------------------------------------------------- journal posts
class PostListView(AdminRequiredMixin, ListView):
    model = Post
    template_name = "dashboard/post_list.html"
    context_object_name = "posts"
    paginate_by = 25

    def get_queryset(self):
        queryset = Post.objects.all()
        published = self.request.GET.get("published", "")
        if published in {"yes", "no"}:
            queryset = queryset.filter(is_published=(published == "yes"))
        search = self.request.GET.get("q", "").strip()[:100]
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset.order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_published"] = self.request.GET.get("published", "")
        context["search_query"] = self.request.GET.get("q", "").strip()[:100]
        context["querystring"] = self.request.GET.copy()
        context["querystring"].pop("page", None)
        context["querystring"] = context["querystring"].urlencode()
        context["published_count"] = Post.objects.filter(is_published=True).count()
        context["draft_count"] = Post.objects.filter(is_published=False).count()
        return context


class PostFormMixin:
    model = Post
    form_class = PostForm
    template_name = "dashboard/post_form.html"
    success_url = reverse_lazy("dashboard:posts")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Saved “{self.object.title}”.")
        return response


class PostCreateView(AdminRequiredMixin, PostFormMixin, CreateView):
    pass


class PostUpdateView(AdminRequiredMixin, PostFormMixin, UpdateView):
    pass


class PostDeleteView(AdminRequiredMixin, DeleteView):
    model = Post
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:posts")
    extra_context = {"what": "journal post", "back_url": reverse_lazy("dashboard:posts")}

    def form_valid(self, form):
        messages.success(self.request, f"Deleted “{self.object.title}”.")
        return super().form_valid(form)


# ---------------------------------------------------------------- inbox
class InboxView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/inbox.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["messages_list"] = ContactMessage.objects.all()[:50]
        ctx["waitlist"] = WaitlistEntry.objects.all()[:100]
        return ctx


class InboxToggleView(AdminPostMixin, View):
    def post(self, request, kind, pk):
        if kind == "message":
            obj = get_object_or_404(ContactMessage, pk=pk)
            obj.is_handled = not obj.is_handled
            obj.save(update_fields=["is_handled"])
        elif kind == "waitlist":
            obj = get_object_or_404(WaitlistEntry, pk=pk)
            obj.is_contacted = not obj.is_contacted
            obj.save(update_fields=["is_contacted"])
        return redirect("dashboard:inbox")


class AnalyticsJsonView(AdminRequiredMixin, View):
    """Feeds the Chart.js graphs on the overview page."""

    def get(self, request):
        since = timezone.now() - timedelta(days=14)
        daily_views = (
            PageView.objects.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        status_breakdown = Reservation.objects.values("status").annotate(count=Count("id")).order_by("status")
        labels = dict(Reservation.Status.choices)
        return JsonResponse({
            "daily_views": [{"day": row["day"].isoformat(), "count": row["count"]} for row in daily_views],
            "status_breakdown": [
                {"status": row["status"], "label": labels.get(row["status"], row["status"]), "count": row["count"]}
                for row in status_breakdown
            ],
        })
