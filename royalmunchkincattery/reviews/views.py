from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from .forms import TestimonialForm
from .models import Testimonial


class TestimonialListView(ListView):
    """Public reviews page. Only ever shows admin-approved testimonials."""

    template_name = "reviews/list.html"
    context_object_name = "testimonials"
    paginate_by = 12

    def get_queryset(self):
        return Testimonial.objects.filter(is_approved=True).select_related("kitten")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        approved = Testimonial.objects.filter(is_approved=True)
        count = approved.count()
        ctx["review_count"] = count
        ctx["average_rating"] = (sum(t.rating for t in approved) / count) if count else 0
        ctx["meta_title"] = "Munchkin Kitten Reviews | American Munchkin House"
        ctx["meta_description"] = "Read verified reviews from families who adopted a Munchkin kitten from American Munchkin House."
        ctx["breadcrumbs"] = [("Home", "/"), ("Reviews", "/reviews/")]
        return ctx


class TestimonialSubmitView(View):
    template_name = "reviews/submit.html"

    def get(self, request):
        return render(request, self.template_name, {"form": TestimonialForm()})

    def post(self, request):
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            if not form.is_spam:
                # is_approved is False at the model level, so nothing here can
                # publish directly: an admin must approve first.
                form.save()
            return redirect(reverse("reviews:thank_you"))
        return render(request, self.template_name, {"form": form}, status=422)


class TestimonialThankYouView(View):
    def get(self, request):
        return render(request, "reviews/thank_you.html")
