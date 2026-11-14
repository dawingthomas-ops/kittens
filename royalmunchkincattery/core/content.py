"""Shared copy used by both the visible page and its JSON-LD, so the two can
never drift apart. Policy wording below (guarantee length, deposit handling,
delivery options) is a sensible starting point: edit it to match exactly how
your cattery operates before launch."""

FAQS = [
    ("How much do your Munchkin kittens cost?",
     "Every kitten is priced between $800 and $1,000. The exact price is on the kitten's page and covers the vet exam, vaccinations, deworming, microchip and written health guarantee."),
    ("How big do Munchkin cats get?",
     "Adult Munchkins are small to medium cats. Most females weigh around 5 to 7 pounds and most males around 6 to 9 pounds. Their short legs make them look smaller than their weight suggests."),
    ("Can Munchkin cats run and jump?",
     "Yes. Munchkins are quick, playful and curious. They jump less high than long-legged cats, so low cat trees, ramps and steps help them reach favorite spots comfortably."),
    ("Are Munchkin cats healthy?",
     "Many Munchkins live active, happy lives, but the short-leg gene is controversial and short-legged cats can be prone to spinal and joint problems. We screen our cats, breed only Munchkin to normal-leg cats, keep our kittens lean and give every kitten a written health guarantee. Read our breed guide for a balanced overview."),
    ("What age do kittens go home?",
     "Kittens go home at 12 weeks or older, after they are fully weaned, litter-trained, vaccinated for their age and cleared at a vet check."),
    ("Are your kittens raised in your home?",
     "Yes. Kittens are born and raised in our living space with daily handling, household noise and gentle introductions to new people so they grow into confident companions."),
    ("What does the health guarantee cover?",
     "Each kitten comes with a written guarantee against life-threatening congenital conditions, with the terms and length shown on the kitten's page and in your adoption contract. We walk you through it before you pay a deposit."),
    ("How do I reserve a kitten?",
     "Open an available kitten's page and choose Reserve. Send the short form and we reply within one business day. A deposit holds the kitten while we finish paperwork and plan pickup or delivery."),
    ("Can I see my kitten before I decide?",
     "Yes. Ask for a live video call, extra photos or videos, or a visit by appointment before you reserve."),
    ("Do you deliver kittens?",
     "Yes. Pickup is by appointment, and we arrange ground transport or an in-cabin flight nanny for families farther away. Kittens never travel in cargo and only travel after a vet clears them."),
    ("Do I have to spay or neuter my kitten?",
     "Yes. Our kittens are sold as pets under a spay/neuter agreement. It is better for their health and prevents unplanned litters."),
    ("How are reviews posted?",
     "Every review is submitted by a real customer and approved by our team before it appears. We never write, edit or buy reviews."),
]

DELIVERY_OPTIONS = [
    ("Pickup by appointment",
     "Meet your kitten in our home, ask questions and take your new family member home. Visits are scheduled one family at a time so the kittens stay calm."),
    ("Ground delivery",
     "For families within a day's drive, a trusted driver or one of our team brings your kitten to you. You receive updates and photos along the way."),
    ("In-cabin flight nanny",
     "For longer distances, a flight nanny carries your kitten in the cabin of the plane, never in cargo, and hands the kitten to you at the airport or your door."),
]

JOURNEY_STEPS = [
    ("Pick your kitten", "Browse by coat, color and personality, or take the 2-minute match quiz."),
    ("Meet on video", "Ask for a live call or extra videos. Seeing your kitten move and play is the best introduction."),
    ("Reserve with a deposit", "We send paperwork and the guarantee. A deposit holds your kitten while the vet check is finished."),
    ("Bring them home", "Pick up in person or arrange safe delivery. Your kitten arrives with records, food and a familiar blanket."),
]
