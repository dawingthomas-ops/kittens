import datetime
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from kittens import placeholder_art as art
from kittens.models import Kitten, KittenImage, Litter

DEMO = [
    # name, gender, length, leg, color, pattern, eye, hair, energy, price, tags, headline
    ("Duchess", "female", "longhair", "standard", "tricolor", "calico", "green", True, "calm", 950,
     "cuddly, gentle, chatty", "A silky calico who purrs the moment you pick her up."),
    ("Biscuit", "male", "shorthair", "standard", "red", "tabby", "gold", False, "playful", 850,
     "goofy, social, curious", "Marmalade tabby with a motor for a purr and zero shyness."),
    ("Midnight", "male", "shorthair", "super_short", "black", "solid", "gold", False, "adventurous", 900,
     "bold, athletic, brave", "A tiny panther with big opinions and a rug-hugger waddle."),
    ("Snowdrop", "female", "longhair", "standard", "white", "bicolor", "blue", True, "calm", 1000,
     "sweet, quiet, snuggly", "Cloud-soft white longhair with ice-blue eyes."),
    ("Pumpkin", "female", "shorthair", "standard", "cream", "colorpoint", "blue", False, "playful", 825,
     "chatty, affectionate, bright", "Cream colorpoint who talks to everyone she meets."),
    ("Mochi", "female", "longhair", "standard", "silver", "tabby", "green", True, "playful", 975,
     "curious, gentle, clever", "Silver tabby with a plumed tail and a taste for feather wands."),
    ("Ziggy", "male", "shorthair", "non_standard", "brown", "tabby", "copper", False, "adventurous", 800,
     "daring, funny, speedy", "Classic brown tabby who treats the hallway as a racetrack."),
    ("Willow", "female", "longhair", "standard", "tricolor", "tortie", "gold", True, "calm", 925,
     "dreamy, loving, soft-spoken", "Tortoiseshell cuddle-bug with a swirl of caramel and cocoa."),
]


class Command(BaseCommand):
    help = (
        "Seeds placeholder kittens with generated illustrations for local development and design "
        "review. NOT for production: replace with real photos via the dashboard. Use --clear to remove."
    )

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete the demo kittens and litter")

    def handle(self, *args, **options):
        if options["clear"]:
            Kitten.objects.filter(litter__name="Demo litter (placeholder)").delete()
            Litter.objects.filter(name="Demo litter (placeholder)").delete()
            self.stdout.write(self.style.SUCCESS("Removed demo kittens."))
            return

        today = timezone.localdate()
        litter, _ = Litter.objects.get_or_create(
            name="Demo litter (placeholder)",
            defaults=dict(
                dam_name="Lady Marmalade", sire_name="King Winston",
                dam_description="Calico longhair, normal legs, 9 lb", sire_description="Red tabby, standard Munchkin, 7 lb",
                birth_date=today - datetime.timedelta(weeks=10),
            ),
        )
        created = 0
        for i, (name, gender, length, leg, color, pattern, eye, hair, energy, price, tags, headline) in enumerate(DEMO):
            if Kitten.objects.filter(name=name, litter=litter).exists():
                continue
            weeks = 9 + (i % 5)
            kitten = Kitten(
                name=name, gender=gender, coat_length=length, leg_length=leg, coat_color=color, pattern=pattern,
                eye_color=eye if eye in ("gold", "green", "copper", "blue") else "gold",
                date_of_birth=today - datetime.timedelta(weeks=weeks), price=price, deposit_amount=200,
                energy=energy, personality_tags=tags, headline=headline,
                description=(
                    f"{name} is a {pattern if pattern != 'solid' else color} {length} Munchkin raised underfoot in our home. "
                    f"{name} is litter-trained, eats well and loves gentle play.\n\n"
                    "This is placeholder demo copy: replace it with your kitten's real story, personality notes and any "
                    "quirks future owners should know."
                ),
                weight_estimate_lb=6 if gender == "female" else 8, registry="TICA registered", litter=litter,
                is_featured=i < 6, status=Kitten.Status.RESERVED if i == 7 else Kitten.Status.AVAILABLE,
                cover_alt=f"Illustration of {name}, a {pattern} Munchkin kitten (demo image)",
            )
            kwargs = dict(color=color, pattern=pattern, eye=eye, longhair=hair, seed=i + 5, bg_index=i)
            kitten.cover_photo.save(f"{name.lower()}-cover.jpg", ContentFile(art.to_jpeg_bytes(art.draw_kitten(900, **kwargs))), save=False)
            kitten.save()
            for order, (label, pose) in enumerate((("Close-up", "close"), ("Sitting pretty", "portrait"))):
                img = art.draw_kitten(900, pose=pose, **{**kwargs, "seed": i + 40 + order, "bg_index": i + order + 1})
                gi = KittenImage(kitten=kitten, caption=f"{name}, {label.lower()}", ordering=order)
                gi.image.save(f"{name.lower()}-{pose}.jpg", ContentFile(art.to_jpeg_bytes(img)), save=False)
                gi.save()
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} demo kittens (generated placeholder art)."))
