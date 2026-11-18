"""
Keyword landing pages.

Unlike a single shared template with swapped headings, every page here has its
own copy, sections and FAQ so search engines see distinct, useful documents
(thin/duplicate keyword pages are discounted by Google). Edit freely - the
views, URLs, sitemap, schema and navigation are all generated from this dict.

`{price_range}` is replaced with the live price range from settings.
`filters` pre-selects kittens shown on the page and the "see all" link.
"""

LANDING_PAGES = {
    "munchkin-kittens-for-sale": {
        "nav_label": "Munchkin kittens for sale",
        "meta_title": "Munchkin Kittens for Sale | $800-$1,000 | American Munchkin House",
        "meta_description": "Healthy, home-raised Munchkin kittens for sale at {price_range}. Vet-checked, vaccinated, microchipped, with a written health guarantee. Browse available kittens.",
        "meta_keywords": "munchkin kittens for sale, munchkin kitten for sale, munchkin cat for sale, short leg kittens for sale, munchkin cattery",
        "h1": "Munchkin kittens for sale",
        "intro": "Every kitten at American Munchkin House is born and raised in our home, handled daily from the first week, and priced openly between {price_range}. No bidding, no hidden fees, no surprises.",
        "filters": {},
        "sections": [
            ("What you get with every kitten", [
                "Each kitten leaves with a vet exam, age-appropriate vaccinations, deworming, a microchip, a starter food supply and a written health guarantee. Photos and videos are updated while the kitten is still with us, so you see the same personality that comes home to you.",
                "Because one flat price band covers every kitten, color and coat length never turn into a bidding war. The rarest-looking kitten and the sweetest lap-sitter are both within {price_range}.",
            ]),
            ("How reserving works", [
                "Choose a kitten, send a reservation request, and we reply within one business day. A deposit holds your kitten while we finish paperwork, schedule the vet check and arrange pickup or delivery. You are welcome to ask for a live video visit before you commit.",
            ]),
        ],
        "faqs": [
            ("How much are your Munchkin kittens?", "Our kittens are priced between $800 and $1,000. The exact price is shown on every kitten's page, and it includes the vet exam, first vaccinations, microchip and health guarantee."),
            ("Are your kittens raised in a home?", "Yes. Our kittens are raised underfoot in a living space, not in a separate kennel, so they are used to voices, vacuum cleaners, visitors and gentle handling before they go home."),
            ("Can I see my kitten before I reserve?", "Yes. Ask for a live video call or extra photos and videos of the kitten you are considering."),
        ],
        "related": ["affordable-munchkin-kittens", "munchkin-kittens-near-me", "longhair-munchkin-kittens"],
    },
    "munchkin-kittens-near-me": {
        "nav_label": "Munchkin kittens near me",
        "meta_title": "Munchkin Kittens Near Me | Pickup & Delivery | American Munchkin House",
        "meta_description": "Looking for Munchkin kittens near you? American Munchkin House offers pickup by appointment and safe delivery across the US. See available kittens today.",
        "meta_keywords": "munchkin kittens near me, munchkin cat breeder near me, munchkin kittens local, munchkin kittens delivery",
        "h1": "Munchkin kittens near me",
        "intro": "You do not have to live down the road to bring home a kitten from American Munchkin House. We offer pickup by appointment and carefully arranged delivery to families across the United States.",
        "filters": {},
        "sections": [
            ("Local pickup, by appointment", [
                "If you are within driving distance, we invite you to meet your kitten in person. Visits are scheduled one family at a time so the kittens stay calm and our home stays healthy. Tell us where you are in your reservation request and we will confirm the easiest option.",
            ]),
            ("Delivery when you are farther away", [
                "For families outside driving range we coordinate ground transport or an in-cabin flight nanny, depending on distance and the kitten's age. Every kitten travels only after a vet clears it, and you receive updates from pickup to your front door. Read the full details on our delivery page.",
            ]),
            ("How to judge any breeder near you", [
                "Ask to see the kitten's living space and parents (in person or on video), ask for written vaccination and deworming records, and expect clear answers about Munchkin health. A breeder who rushes you or refuses video visits is a warning sign, wherever they are.",
            ]),
        ],
        "faqs": [
            ("Do you ship Munchkin kittens?", "Kittens never travel in cargo. We arrange ground transport or an in-cabin flight nanny, and each kitten is cleared by a vet before travel."),
            ("Can I pick up my kitten in person?", "Yes. Pickup is by appointment. Mention your location when you reserve and we will confirm availability and timing."),
            ("What age do kittens go home?", "Kittens are ready for their new homes at 12 weeks or older, after their first vaccinations and a vet check."),
        ],
        "related": ["munchkin-kittens-for-sale", "affordable-munchkin-kittens"],
    },
    "affordable-munchkin-kittens": {
        "nav_label": "Affordable Munchkin kittens",
        "meta_title": "Affordable Munchkin Kittens | Fair, Flat $800-$1,000 Pricing",
        "meta_description": "Affordable Munchkin kittens without cutting corners. Every kitten is $800 to $1,000 and includes vet care, vaccinations, microchip and a health guarantee.",
        "meta_keywords": "affordable munchkin kittens, cheap munchkin kittens, munchkin kitten price, how much is a munchkin cat, munchkin kittens under 1000",
        "h1": "Affordable Munchkin kittens, priced fairly",
        "intro": "Munchkin kittens are often listed for several times what ours cost. We keep every kitten between {price_range} because healthy, well-raised kittens should be within reach of ordinary families.",
        "filters": {"ordering": "price"},
        "sections": [
            ("Affordable should not mean cut corners", [
                "A very low price from an unknown seller usually means skipped vet care, no vaccinations or no real health records. Our price band is lower than many catteries, but the essentials are never optional: vet exam, vaccinations, deworming, microchip and a written guarantee are included for every kitten.",
            ]),
            ("What your $800 to $1,000 covers", [
                "Your price covers the kitten, the first round of veterinary care, microchip registration support, a starter kit of food and a familiar blanket, and written care instructions. The only extra cost you may face is optional delivery, which we quote before you commit.",
            ]),
            ("The real cost of a Munchkin", [
                "Plan for a lifetime of ordinary cat costs: quality food, litter, annual vet visits, and spay or neuter surgery. Budgeting about the same as for any cat keeps the adoption price from being the only number you think about.",
            ]),
        ],
        "faqs": [
            ("Why are your Munchkin kittens cheaper than some breeders?", "We keep litters small, price every kitten inside one transparent band and do not charge more for color or coat. Savings never come from skipping vet care."),
            ("Is the deposit part of the price?", "Yes. Your deposit is credited toward the kitten's total price."),
            ("Are there extra fees after I reserve?", "No hidden fees. The only optional extra is delivery, which is quoted up front."),
        ],
        "related": ["munchkin-kittens-for-sale", "munchkin-kittens-near-me"],
    },
    "longhair-munchkin-kittens": {
        "nav_label": "Longhair Munchkin kittens",
        "meta_title": "Longhair Munchkin Kittens for Sale | American Munchkin House",
        "meta_description": "Fluffy longhair Munchkin kittens for sale at $800 to $1,000. Silky coats, short legs and sweet temperaments, raised in our home and vet-checked.",
        "meta_keywords": "longhair munchkin kittens, long hair munchkin kitten, fluffy munchkin kitten for sale, long haired munchkin cat",
        "h1": "Longhair Munchkin kittens",
        "intro": "Short legs and a silky, flowing coat make longhair Munchkins some of the most photographed kittens we raise. Their plumed tails and soft ruffs fill out over the first year.",
        "filters": {"coat_length": "longhair"},
        "sections": [
            ("What to expect from the coat", [
                "Longhair Munchkin kittens are born with soft, fine fur that thickens into a semi-long coat as they mature. Most have a fuller tail and a ruff around the neck. Brush two to three times a week and every day during seasonal shedding to prevent mats.",
            ]),
            ("Grooming a kitten with short legs", [
                "Because the belly and legs sit close to the floor, longer fur can pick up litter. Trim the hair around the back end if it gets messy, choose a low-dust litter, and get your kitten used to the brush early with short, treat-filled sessions.",
            ]),
        ],
        "faqs": [
            ("Do longhair Munchkins shed more?", "They shed about as much as other medium-coated cats, but the hair is more visible. Regular brushing keeps it manageable."),
            ("Are longhair kittens more expensive?", "No. All our kittens, longhair or shorthair, are priced between $800 and $1,000."),
            ("Do longhair Munchkins get matted easily?", "Matting is easy to prevent with regular brushing, especially around the armpits, belly and behind the ears."),
        ],
        "related": ["shorthair-munchkin-kittens", "calico-munchkin-kittens", "munchkin-kittens-for-sale"],
    },
    "shorthair-munchkin-kittens": {
        "nav_label": "Shorthair Munchkin kittens",
        "meta_title": "Shorthair Munchkin Kittens for Sale | Low-Maintenance Coats",
        "meta_description": "Sleek shorthair Munchkin kittens for sale at $800 to $1,000. Easy-care coats, playful short-legged personalities, vet-checked and home-raised.",
        "meta_keywords": "shorthair munchkin kittens, short hair munchkin kitten, short haired munchkin cat for sale, easy care munchkin kitten",
        "h1": "Shorthair Munchkin kittens",
        "intro": "Shorthair Munchkins give you all the short-legged charm with a coat that practically cares for itself. They are a good fit for busy households and first-time cat owners.",
        "filters": {"coat_length": "shorthair"},
        "sections": [
            ("An easy coat for everyday life", [
                "A weekly brushing is usually enough for a shorthair Munchkin. The dense, plush coat feels velvety, shows off tabby and calico patterns clearly and sheds little dirt around the home.",
            ]),
            ("Energy and personality", [
                "Do not mistake short legs for slow. Shorthair Munchkins zoom through hallways, chase feather wands and curl up on laps afterward. Provide low cat trees and ramps so they can climb comfortably at their own pace.",
            ]),
        ],
        "faqs": [
            ("Is a shorthair Munchkin better for first-time owners?", "Many first-time owners prefer them because grooming is minimal, though temperament matters more than coat length. We can help match you with a calm or playful kitten."),
            ("Do shorthair Munchkins shed?", "All cats shed to some degree. A short coat sheds smaller, less noticeable hairs and needs little brushing."),
            ("What colors do shorthair Munchkins come in?", "We raise solids, tabbies, calicos, bicolors and more. Use our filters to browse every available color."),
        ],
        "related": ["longhair-munchkin-kittens", "tabby-munchkin-kittens", "black-munchkin-kittens"],
    },
    "calico-munchkin-kittens": {
        "nav_label": "Calico Munchkin kittens",
        "meta_title": "Calico Munchkin Kittens for Sale | American Munchkin House",
        "meta_description": "Calico Munchkin kittens for sale at $800 to $1,000. Patchwork coats in white, orange and black, short legs, and big personalities. Browse available calicos.",
        "meta_keywords": "calico munchkin kitten, calico munchkin kittens for sale, tricolor munchkin cat, calico short leg cat",
        "h1": "Calico Munchkin kittens",
        "intro": "A calico Munchkin is a patchwork of white, orange and black on a body built low to the ground. No two coats are ever the same, which makes every kitten truly one of a kind.",
        "filters": {"pattern": "calico"},
        "sections": [
            ("Why calicos are almost always girls", [
                "The genes that make orange and black fur sit on the X chromosome, so a calico usually needs two X chromosomes. That is why nearly all calico kittens are female. Rare male calicos exist but are typically infertile and are not something we can promise.",
            ]),
            ("The calico personality", [
                "People often describe calicos as spirited and confident. Coat color does not determine temperament, so we match you with a kitten based on the energy level you want rather than the pattern alone.",
            ]),
        ],
        "faqs": [
            ("Are calico Munchkin kittens rare?", "True calico patterns appear in only some litters, so availability changes often. Join the waitlist if none are currently listed."),
            ("Are all calico kittens female?", "Almost all. The calico pattern requires two X chromosomes, so calico kittens are nearly always female."),
            ("Do calicos cost more?", "Not with us. Every kitten, calico or not, is priced between $800 and $1,000."),
        ],
        "related": ["tabby-munchkin-kittens", "female-munchkin-kittens", "longhair-munchkin-kittens"],
    },
    "tabby-munchkin-kittens": {
        "nav_label": "Tabby Munchkin kittens",
        "meta_title": "Tabby Munchkin Kittens for Sale | Brown, Silver & Red Tabbies",
        "meta_description": "Tabby Munchkin kittens for sale at $800 to $1,000. Classic and mackerel stripes in brown, silver and red with short legs and playful personalities.",
        "meta_keywords": "tabby munchkin kitten, tabby munchkin kittens for sale, brown tabby munchkin, silver tabby munchkin, orange tabby munchkin",
        "h1": "Tabby Munchkin kittens",
        "intro": "Tabby is the most common cat pattern in the world, and on a Munchkin it looks irresistible. Expect the signature M on the forehead, striped legs and a ringed tail.",
        "filters": {"pattern": "tabby"},
        "sections": [
            ("Tabby patterns explained", [
                "Mackerel tabbies carry thin vertical stripes like a tiger. Classic tabbies swirl into a bullseye on the sides. Both come in many colors, from brown and silver to red, often called orange.",
            ]),
            ("Orange tabbies and personality", [
                "Red tabbies are mostly male, and many owners swear they are the most affectionate cats of all. It is a charming reputation but not a guarantee. We describe each kitten's real personality on its page, so you pick the temperament, not the stereotype.",
            ]),
        ],
        "faqs": [
            ("Do tabby Munchkins have different temperaments?", "Pattern does not decide temperament. Each kitten's page describes its actual personality."),
            ("What does the M on a tabby's forehead mean?", "It is a natural marking shared by all tabby cats, with many myths but no special meaning."),
            ("Are tabby Munchkins more affordable?", "All kittens from American Munchkin House are priced between $800 and $1,000 regardless of pattern."),
        ],
        "related": ["calico-munchkin-kittens", "shorthair-munchkin-kittens", "male-munchkin-kittens"],
    },
    "black-munchkin-kittens": {
        "nav_label": "Black Munchkin kittens",
        "meta_title": "Black Munchkin Kittens for Sale | American Munchkin House",
        "meta_description": "Black Munchkin kittens for sale at $800 to $1,000. Glossy coats, golden eyes, short legs and loving temperaments. See available black kittens.",
        "meta_keywords": "black munchkin kitten, black munchkin kittens for sale, black short leg cat, solid black munchkin",
        "h1": "Black Munchkin kittens",
        "intro": "Glossy, inky and impossibly small-legged, black Munchkin kittens look like tiny panthers with a sweet side. Their golden or green eyes stand out against the dark coat.",
        "filters": {"coat_color": "black"},
        "sections": [
            ("A coat that changes with the sun", [
                "Many black kittens show a rusty or smoky tint in direct sunlight, especially while growing. That is normal and often fades as the adult coat settles in. Black cats also look striking in photos when lit softly from the side.",
            ]),
            ("Black cats make wonderful pets", [
                "Black cats are often overlooked in shelters because of old superstitions, yet they are every bit as loving as any other color. A black Munchkin brings that affectionate nature along with a short-legged waddle you will never get tired of.",
            ]),
        ],
        "faqs": [
            ("Do black Munchkin kittens turn brown?", "Some develop a rusty tint in the sun. It is normal and not a health concern."),
            ("Are black kittens harder to photograph?", "A little, so we photograph them in natural light and share extra close-ups on request."),
            ("What eye colors do black kittens have?", "Most have gold or green eyes, depending on the kitten. Each kitten's page lists its eye color."),
        ],
        "related": ["shorthair-munchkin-kittens", "tabby-munchkin-kittens", "munchkin-kittens-for-sale"],
    },
    "male-munchkin-kittens": {
        "nav_label": "Male Munchkin kittens",
        "meta_title": "Male Munchkin Kittens for Sale | American Munchkin House",
        "meta_description": "Male Munchkin kittens for sale at $800 to $1,000. Affectionate, playful and vet-checked, with a written health guarantee and delivery options.",
        "meta_keywords": "male munchkin kitten, male munchkin kittens for sale, boy munchkin cat, male short leg kitten",
        "h1": "Male Munchkin kittens",
        "intro": "Male Munchkins are often bigger-hearted and a little goofier than their sisters. Many stay playful well into adulthood and love to follow their people from room to room.",
        "filters": {"gender": "male"},
        "sections": [
            ("Male or female: which is right for you?", [
                "Individual personality matters far more than gender. Boys tend to grow slightly larger, typically a few pounds heavier than girls, and often stay kittenish longer. Girls are sometimes more independent. We would rather match your home to a specific kitten than to a stereotype.",
            ]),
            ("Neutering and household life", [
                "Neutering is strongly recommended and required by our agreement. It prevents marking, roaming and most unwanted behavior, and helps keep your Munchkin at a healthy weight for his smaller frame.",
            ]),
        ],
        "faqs": [
            ("How big do male Munchkins get?", "Most adult males weigh roughly 6 to 9 pounds, a little more than females, though diet and genetics vary."),
            ("When should I neuter my male kitten?", "Your vet will advise on timing, commonly between 5 and 6 months. Our adoption agreement requires spay or neuter."),
            ("Do males spray?", "Neutered males rarely do. Neutering at the right age greatly reduces marking behavior."),
        ],
        "related": ["female-munchkin-kittens", "tabby-munchkin-kittens", "munchkin-kittens-for-sale"],
    },
    "female-munchkin-kittens": {
        "nav_label": "Female Munchkin kittens",
        "meta_title": "Female Munchkin Kittens for Sale | American Munchkin House",
        "meta_description": "Female Munchkin kittens for sale at $800 to $1,000. Sweet, spirited and home-raised, with vet checks, vaccinations and a written health guarantee.",
        "meta_keywords": "female munchkin kitten, female munchkin kittens for sale, girl munchkin cat, female short leg kitten",
        "h1": "Female Munchkin kittens",
        "intro": "Female Munchkin kittens are petite, quick and wonderfully expressive. If you love a calico or tortoiseshell coat, you will most often find it on a girl.",
        "filters": {"gender": "female"},
        "sections": [
            ("Why many colors come on girls", [
                "Calico and tortoiseshell patterns depend on two X chromosomes, so they appear almost exclusively on females. If those patchwork coats are on your wish list, a female kitten is the way to get one.",
            ]),
            ("Size and personality", [
                "Adult females commonly weigh around 5 to 7 pounds. Many are confident explorers who still make time for cuddles. Tell us what kind of home you have and we will help you choose the personality that fits.",
            ]),
        ],
        "faqs": [
            ("Are female Munchkins smaller than males?", "Usually. Adult females commonly weigh about 5 to 7 pounds, with some variation."),
            ("Do females need to be spayed?", "Yes. Our adoption agreement requires spaying, which prevents heat cycles and several health problems."),
            ("Can I choose a calico?", "Calico kittens are almost always female. Check the calico page or join the waitlist for the next litter."),
        ],
        "related": ["male-munchkin-kittens", "calico-munchkin-kittens", "munchkin-kittens-for-sale"],
    },
    "super-short-leg-munchkin-kittens": {
        "nav_label": "Rug hugger Munchkin kittens",
        "meta_title": "Super Short Leg & Rug Hugger Munchkin Kittens | American Munchkin House",
        "meta_description": "Super short leg ('rug hugger') Munchkin kittens for sale at $800 to $1,000. Learn what the term means, health considerations and how we raise them.",
        "meta_keywords": "rug hugger munchkin, super short leg munchkin kitten, rug hugger kitten for sale, extra short leg cat",
        "h1": "Super short leg ('rug hugger') Munchkin kittens",
        "intro": "'Rug hugger' is the affectionate name for Munchkins with the shortest legs. They are adorable, but they also deserve extra thought from any responsible buyer.",
        "filters": {"leg_length": "super_short"},
        "sections": [
            ("What 'super short' really means", [
                "Munchkin leg length falls along a spectrum: standard short legs, super short ('rug hugger') and non-standard, which means normal-length legs. Not every Munchkin kitten is a rug hugger, and leg length can be hard to judge exactly in a young kitten.",
            ]),
            ("Health and ethics, honestly", [
                "The gene behind short legs has been linked in some cats to spinal and joint concerns, and the breed is controversial in several cat registries. Responsible breeders pair a Munchkin with a normal-leg cat only, screen their cats and are honest with buyers. Ask any breeder, including us, to discuss it openly.",
            ]),
            ("Caring for a rug hugger", [
                "Offer low ramps, steps to the sofa, shallow litter boxes and a lean, healthy weight. Extra pounds put pressure on the spine and joints, so measured meals and daily play matter more for a short-legged cat.",
            ]),
        ],
        "faqs": [
            ("Are rug hugger Munchkins healthy?", "Many live happy lives, but short-legged cats may face spinal or joint issues. We discuss this openly and provide a written health guarantee."),
            ("Can a rug hugger jump?", "Yes, though not as high as longer-legged cats. Provide ramps and low furniture."),
            ("Why do some registries not recognize the Munchkin?", "Concerns about the effects of the short-leg gene are the main reason. Read our breed guide for a balanced overview."),
        ],
        "related": ["munchkin-kittens-for-sale", "shorthair-munchkin-kittens", "longhair-munchkin-kittens"],
    },
}


def price_range_text(min_price, max_price):
    return f"${min_price:,} to ${max_price:,}"


def get_page(slug, min_price=800, max_price=1000):
    """Return a render-ready copy of a landing page with placeholders filled."""
    page = LANDING_PAGES.get(slug)
    if page is None:
        return None
    pr = price_range_text(min_price, max_price)

    def fill(text):
        return text.replace("{price_range}", pr)

    return {
        "slug": slug,
        "nav_label": page["nav_label"],
        "meta_title": fill(page["meta_title"]),
        "meta_description": fill(page["meta_description"]),
        "meta_keywords": page["meta_keywords"],
        "h1": page["h1"],
        "intro": fill(page["intro"]),
        "filters": page["filters"],
        "sections": [(h, [fill(p) for p in paras]) for h, paras in page["sections"]],
        "faqs": [(q, fill(a)) for q, a in page["faqs"]],
        "related": [
            {"slug": s, "label": LANDING_PAGES[s]["nav_label"]}
            for s in page["related"]
            if s in LANDING_PAGES
        ],
    }
