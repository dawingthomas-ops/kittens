from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from kittens.models import Kitten
from reviews.models import Testimonial

from .content import DELIVERY_OPTIONS, FAQS, JOURNEY_STEPS
from .emails import confirm_waitlist, notify_admin_of_waitlist, notify_contact_submission
from .forms import ContactForm, WaitlistForm
from .landing_pages import LANDING_PAGES, get_page
from .middleware import client_ip
from .models import ContactMessage, Post


def _open_kittens():
    return Kitten.objects.exclude(status=Kitten.Status.ADOPTED)


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["featured_kittens"] = _open_kittens().filter(is_featured=True)[:6] or _open_kittens()[:6]
        ctx["testimonials"] = Testimonial.objects.filter(is_approved=True).select_related("kitten")[:6]
        ctx["recent_posts"] = Post.objects.filter(is_published=True)[:3]
        ctx["faqs"] = FAQS[:5]
        ctx["journey_steps"] = JOURNEY_STEPS
        ctx["available_count"] = _open_kittens().filter(status=Kitten.Status.AVAILABLE).count()
        ctx["meta_title"] = "Munchkin Kittens for Sale | $800-$1,000 | American Munchkin House"
        ctx["meta_description"] = (
            "Browse Munchkin kittens priced from $800 to $1,000. View each kitten's photos, availability, "
            "and confirmed care details."
        )
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meta_title"] = "About American Munchkin House | Ethical Munchkin Breeder"
        ctx["meta_description"] = (
            "Meet the family behind American Munchkin House: small litters, home-raised Munchkin kittens, "
            "honest health information and fair $800 to $1,000 pricing."
        )
        ctx["breadcrumbs"] = [("Home", "/"), ("About", "/about/")]
        return ctx


class FAQView(TemplateView):
    template_name = "core/faq.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["faqs"] = FAQS
        ctx["meta_title"] = "Munchkin Cat FAQ | Size, Health, Price & Delivery"
        ctx["meta_description"] = (
            "Answers to the questions we hear most about Munchkin kittens: price, size, health, "
            "jumping, guarantees, reservations and delivery."
        )
        ctx["breadcrumbs"] = [("Home", "/"), ("FAQ", "/faq/")]
        return ctx


class DeliveryView(TemplateView):
    template_name = "core/delivery.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["delivery_options"] = DELIVERY_OPTIONS
        ctx["meta_title"] = "Munchkin Kitten Delivery & Pickup | American Munchkin House"
        ctx["meta_description"] = (
            "How Munchkin kitten pickup and delivery works: visits by appointment, ground delivery and "
            "in-cabin flight nanny. Kittens never fly in cargo."
        )
        ctx["breadcrumbs"] = [("Home", "/"), ("Delivery", "/delivery/")]
        return ctx


class BreedGuideView(TemplateView):
    template_name = "core/breed_guide.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meta_title"] = "Munchkin Cat Breed Guide | Size, Temperament, Health & Care"
        ctx["meta_description"] = (
            "A balanced guide to Munchkin cats: origin, size, personality, grooming, health concerns, "
            "registry recognition and what to ask a breeder."
        )
        ctx["meta_keywords"] = "munchkin cat breed, munchkin cat guide, munchkin cat size, munchkin cat health, munchkin cat temperament"
        ctx["breadcrumbs"] = [("Home", "/"), ("Munchkin breed guide", "/munchkin-cat-breed-guide/")]
        ctx["featured_kittens"] = _open_kittens()[:3]
        return ctx


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("core:contact_thanks")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meta_title"] = "Contact American Munchkin House | Ask About Munchkin Kittens"
        ctx["meta_description"] = (
            "Questions about available Munchkin kittens, delivery or the adoption process? "
            "Message American Munchkin House and we reply within one business day."
        )
        ctx["breadcrumbs"] = [("Home", "/"), ("Contact", "/contact/")]
        return ctx

    def form_valid(self, form):
        if not form.is_spam:
            message = form.save(commit=False)
            message.submission_key = form.cleaned_data["submission_key"]
            message.ip_address = client_ip(self.request)
            try:
                with transaction.atomic():
                    message.save()
            except IntegrityError:
                if not ContactMessage.objects.filter(submission_key=message.submission_key).exists():
                    raise
                return super().form_valid(form)
            notify_contact_submission(message)
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=422)


class WaitlistView(FormView):
    template_name = "core/waitlist.html"
    form_class = WaitlistForm
    success_url = reverse_lazy("core:waitlist_thanks")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meta_title"] = "Munchkin Kitten Waitlist | Be First to Hear About New Litters"
        ctx["meta_description"] = (
            "Join the American Munchkin House waitlist and tell us the coat, color and personality "
            "you want. We contact waitlist families first when a new litter arrives."
        )
        ctx["breadcrumbs"] = [("Home", "/"), ("Waitlist", "/waitlist/")]
        return ctx

    def form_valid(self, form):
        if not form.is_spam:
            entry = form.save(commit=False)
            entry.ip_address = client_ip(self.request)
            entry.save()
            notify_admin_of_waitlist(entry)
            confirm_waitlist(entry)
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=422)


class ThanksView(TemplateView):
    """Generic confirmation page (noindex)."""

    title = "Thank you"
    message = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title": self.title, "message": self.message, "noindex": True, "meta_title": f"{self.title} | American Munchkin House"})
        return ctx

    template_name = "core/thanks.html"


class LandingPageView(TemplateView):
    template_name = "core/landing_page.html"

    def get_context_data(self, slug, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = get_page(slug, settings.KITTEN_MIN_PRICE, settings.KITTEN_MAX_PRICE)
        if page is None:
            raise Http404
        qs = _open_kittens()
        filters = dict(page["filters"])
        ordering = filters.pop("ordering", None)
        if filters:
            qs = qs.filter(**filters)
        if ordering:
            qs = qs.order_by(ordering)
        ctx.update(page)
        ctx["kittens"] = qs[:6]
        ctx["kitten_count"] = qs.count()
        ctx["list_query"] = "&".join(f"{k}={v}" for k, v in filters.items())
        if ordering:
            ctx["list_query"] = (ctx["list_query"] + "&" if ctx["list_query"] else "") + f"ordering={ordering}"
        ctx["meta_title"] = page["meta_title"]
        ctx["meta_description"] = page["meta_description"]
        ctx["meta_keywords"] = page["meta_keywords"]
        ctx["breadcrumbs"] = [("Home", "/"), ("Kittens", "/kittens/"), (page["h1"], f"/{slug}/")]
        return ctx


class JournalListView(ListView):
    template_name = "core/journal_list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meta_title"] = "Munchkin Cat Journal | Care Guides & Breed Advice"
        ctx["meta_description"] = (
            "Practical Munchkin cat care guides: feeding, home setup, grooming, health and what to "
            "expect when your kitten comes home."
        )
        ctx["breadcrumbs"] = [("Home", "/"), ("Journal", "/journal/")]
        return ctx


class JournalDetailView(DetailView):
    template_name = "core/journal_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.object
        ctx["meta_title"] = f"{post.title} | American Munchkin House"
        ctx["meta_description"] = post.seo_description
        ctx["og_image"] = post.featured_image.url if post.featured_image else ""
        ctx["related_posts"] = Post.objects.filter(is_published=True).exclude(pk=post.pk)[:3]
        ctx["featured_kittens"] = _open_kittens()[:3]
        ctx["breadcrumbs"] = [("Home", "/"), ("Journal", "/journal/"), (post.title, post.get_absolute_url())]
        return ctx


class PrivacyView(TemplateView):
    template_name = "core/privacy.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meta_title"] = "Privacy Policy | American Munchkin House"
        ctx["meta_description"] = "How American Munchkin House collects, uses and protects your information."
        ctx["breadcrumbs"] = [("Home", "/"), ("Privacy", "/privacy/")]
        return ctx


class TermsView(TemplateView):
    template_name = "core/terms.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meta_title"] = "Terms of Service | American Munchkin House"
        ctx["meta_description"] = "The terms that apply to using the American Munchkin House website and reserving a kitten."
        ctx["breadcrumbs"] = [("Home", "/"), ("Terms", "/terms/")]
        return ctx


def not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)
