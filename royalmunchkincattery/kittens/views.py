from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db.models import F
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from dashboard.models import PageView

from .filters import KittenFilter
from .matching import best_matches
from .models import Kitten


def _is_fetch(request):
    return request.headers.get("X-Requested-With") == "fetch"


class KittenListView(ListView):
    """Server-rendered search/browse page. The same view answers the
    progressive-enhancement fetch() calls with just the results partial, so
    the markup lives in one place and the page works and indexes with no JS."""

    model = Kitten
    context_object_name = "kittens"
    paginate_by = 12

    def get_template_names(self):
        return ["kittens/_results.html"] if _is_fetch(self.request) else ["kittens/list.html"]

    def get_queryset(self):
        qs = Kitten.objects.exclude(status=Kitten.Status.ADOPTED)
        self.filter = KittenFilter(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.filter
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["querystring"] = params.urlencode()
        ctx["has_filters"] = any(v for k, v in params.items() if k != "ordering")
        ctx["total_count"] = self.filter.qs.count()
        ctx["meta_title"] = "Available Munchkin Kittens | $800-$1,000 | Royal Munchkin Cattery"
        ctx["meta_description"] = (
            "Browse available Munchkin kittens priced from $800 to $1,000. View each kitten's photos, "
            "availability, and confirmed care details."
        )
        # Faceted URLs (?gender=...) are canonicalised to /kittens/ in the template
        # and marked noindex so filter combinations never compete with real pages.
        ctx["noindex"] = bool(ctx["has_filters"] or self.request.GET.get("page"))
        return ctx


class KittenDetailView(DetailView):
    model = Kitten
    template_name = "kittens/detail.html"
    context_object_name = "kitten"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Kitten.objects.select_related("litter").prefetch_related("gallery_images", "testimonials")

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        if not any(bot in user_agent for bot in ("bot", "spider", "crawl", "slurp", "preview")):
            Kitten.objects.filter(pk=self.object.pk).update(view_count=F("view_count") + 1)
            PageView.objects.create(
                path=request.path[:255], kitten=self.object, referrer=request.META.get("HTTP_REFERER", "")[:255]
            )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        kitten = self.object
        testimonials = list(kitten.testimonials.filter(is_approved=True))
        review_count = len(testimonials)
        ctx["approved_testimonials"] = testimonials
        ctx["review_count"] = review_count
        ctx["average_rating"] = (sum(t.rating for t in testimonials) / review_count) if review_count else 0
        ctx["gallery"] = list(kitten.gallery_images.all())
        ctx["health_items"] = [
            (kitten.vet_checked, "Vet-checked"),
            (kitten.vaccinations_up_to_date, "Vaccinations up to date for age"),
            (kitten.dewormed, "Dewormed"),
            (kitten.microchipped, "Microchipped"),
            (kitten.litter_trained, "Litter-trained"),
            (kitten.spay_neuter_agreement, "Sold under a spay/neuter agreement"),
            (True, f"{kitten.health_guarantee_years}-year written health guarantee"),
            (kitten.good_with_kids, "Good with children" if kitten.good_with_kids else "Best in a calm, adult home"),
        ]
        ctx["similar_kittens"] = (
            Kitten.objects.exclude(pk=kitten.pk)
            .exclude(status=Kitten.Status.ADOPTED)
            .order_by("-is_featured", "-created_at")[:3]
        )
        ctx["litter_mates"] = (
            Kitten.objects.filter(litter=kitten.litter).exclude(pk=kitten.pk).exclude(status=Kitten.Status.ADOPTED)
            if kitten.litter_id
            else Kitten.objects.none()
        )
        ctx["meta_title"] = f"{kitten.name}, {kitten.listing_title} | Royal Munchkin"
        ctx["meta_description"] = (
            f"Meet {kitten.name}, a {kitten.look.lower()} {kitten.get_coat_length_display().lower()} Munchkin kitten, "
            f"priced at ${kitten.price:,.0f}. View photos, availability, and confirmed details."
        )
        ctx["meta_keywords"] = (
            f"{kitten.look.lower()} munchkin kitten, munchkin kitten for sale, "
            f"{kitten.get_coat_length_display().lower()} munchkin kitten, munchkin kittens for sale, {kitten.name} munchkin"
        )
        ctx["og_image"] = kitten.cover_photo.url if kitten.cover_photo else ""
        ctx["breadcrumbs"] = [("Home", "/"), ("Kittens", "/kittens/"), (kitten.name, kitten.get_absolute_url())]
        return ctx


class KittenMatchView(View):
    """A six-question quiz. Answers travel in the query string so a result is
    shareable and bookmarkable, and the page works without JavaScript."""

    template_name = "kittens/match.html"

    def get(self, request):
        answers = None
        matches = []
        if request.GET.get("go"):
            try:
                budget = Decimal(request.GET.get("budget", settings.KITTEN_MAX_PRICE))
            except (InvalidOperation, ValueError):
                budget = Decimal(settings.KITTEN_MAX_PRICE)
            budget = min(max(budget, Decimal(settings.KITTEN_MIN_PRICE)), Decimal(settings.KITTEN_MAX_PRICE))
            answers = {
                "coat": request.GET.get("coat", ""),
                "energy": request.GET.get("energy", ""),
                "kids": request.GET.get("kids", ""),
                "pets": request.GET.get("pets", ""),
                "gender": request.GET.get("gender", ""),
                "budget": budget,
            }
            pool = Kitten.objects.filter(status__in=[Kitten.Status.AVAILABLE, Kitten.Status.COMING_SOON])
            matches = best_matches(pool, answers)
        return render(request, self.template_name, {
            "answers": answers,
            "matches": matches,
            "searched": answers is not None,
            "meta_title": "Kitten Match Quiz | Find Your Munchkin Kitten | Royal Munchkin",
            "meta_description": "Answer six quick questions and we will match you with the Munchkin kitten whose personality, coat and price fit your home.",
            "breadcrumbs": [("Home", "/"), ("Kitten match", "/kitten-match/")],
        })


class FavoritesView(TemplateView):
    template_name = "kittens/favorites.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meta_title"] = "Your Saved Kittens | Royal Munchkin Cattery"
        ctx["meta_description"] = "The Munchkin kittens you saved, kept on this device."
        ctx["noindex"] = True
        return ctx


class FavoritesResultsView(View):
    """Returns card markup for the kittens a visitor saved in localStorage."""

    def get(self, request):
        slugs = [s for s in request.GET.get("slugs", "").split(",") if s][:40]
        kittens = Kitten.objects.filter(slug__in=slugs).exclude(status=Kitten.Status.ADOPTED)
        return render(request, "kittens/_cards.html", {"kittens": kittens})
