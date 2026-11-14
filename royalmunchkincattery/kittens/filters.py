import django_filters as filters
from django.db.models import Q

from .models import MAX_PRICE, MIN_PRICE, Kitten


class KittenFilter(filters.FilterSet):
    """Backs the public search UI and the DRF API. Every field maps 1:1 to a
    control in templates/kittens/list.html."""

    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte", min_value=MIN_PRICE, max_value=MAX_PRICE)
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte", min_value=MIN_PRICE, max_value=MAX_PRICE)
    gender = filters.ChoiceFilter(choices=Kitten.Gender.choices)
    coat_length = filters.ChoiceFilter(choices=Kitten.CoatLength.choices)
    leg_length = filters.ChoiceFilter(choices=Kitten.LegLength.choices)
    coat_color = filters.ChoiceFilter(choices=Kitten.CoatColor.choices)
    pattern = filters.ChoiceFilter(choices=Kitten.Pattern.choices)
    status = filters.ChoiceFilter(choices=Kitten.Status.choices)
    energy = filters.ChoiceFilter(choices=Kitten.Energy.choices)
    search = filters.CharFilter(method="filter_search")
    slugs = filters.CharFilter(method="filter_slugs")
    ordering = filters.OrderingFilter(
        fields=(("price", "price"), ("created_at", "newest"), ("date_of_birth", "age")),
        field_labels={"price": "Price", "created_at": "Newest", "date_of_birth": "Age"},
    )

    class Meta:
        model = Kitten
        fields = ["gender", "coat_length", "leg_length", "coat_color", "pattern", "status", "energy", "min_price", "max_price"]

    def filter_search(self, queryset, name, value):
        value = value.strip()[:80]
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(headline__icontains=value) | Q(description__icontains=value)
            | Q(personality_tags__icontains=value)
        )

    def filter_slugs(self, queryset, name, value):
        slugs = [s.strip() for s in value.split(",") if s.strip()][:40]
        return queryset.filter(slug__in=slugs) if slugs else queryset.none()
