# American Munchkin House

A production-ready Django 5.2 website for selling Munchkin kittens ($800 to $1,000), built on the same architecture and configuration as the findapomsky project: `config/` + `core`, `kittens` (was `puppies`), `reservations`, `reviews`, `dashboard`, `accounts`; python-decouple env config, WhiteNoise static files, optional AWS S3 media, SQLite by default (Postgres via `DB_*`), DRF API with throttling, SMTP notifications, and Render/Docker/Procfile deployment.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # local: DJANGO_DEBUG=False, SERVE_LOCAL_MEDIA=True, USE_S3=False, SECURE_SSL_REDIRECT=False
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_data     # 8 placeholder kittens with generated art (dev/design review only)
python manage.py seed_journal       # 7 starter care articles (safe for production, edit to taste)
python manage.py runserver
```

Tests: `python manage.py test`.
Administrator dashboard: `/dashboard/` (active Django superuser accounts only). Create the administrator account with `python manage.py createsuperuser`; regular users and staff accounts cannot sign in to or use the dashboard or Django admin. Django admin: `/admin/`.

## Before you launch (please read)

1. **Replace placeholder kittens.** `seed_demo_data` creates illustrated stand-ins. Run `python manage.py seed_demo_data --clear`, then add real kittens and photos in the dashboard.
2. **Set your real business details** in Django admin > Site Settings (city/state, phone, WhatsApp, email, social links, announcement banner). City/state default to a placeholder; clear the city field to hide the address from schema markup.
3. **Connect your domain.** Add `americanmunchkinhouse.com` and `www.americanmunchkinhouse.com` to the Render service and configure the DNS records shown by Render at your domain registrar. `render.yaml` and the default `SITE_DOMAIN` are set for `americanmunchkinhouse.com`; update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` if you use another domain.
4. **Review all policy copy** (health-guarantee length, deposit handling, delivery options, "starter kit", vaccination claims) in `core/content.py`, `core/landing_pages.py`, the templates, and the Privacy/Terms pages. They are sensible starting points, not legal advice. Have the contract, privacy policy and terms reviewed by a professional.
5. **No fake reviews.** Customers submit their own reviews and confirm they reflect a real experience. Nothing appears publicly until a staff member with the `reviews.change_testimonial` permission (or a superuser) approves it; staff without that permission cannot moderate. Review text is read-only to moderators, and star-rating markup appears only when approved reviews exist. Fabricated reviews violate Google's guidelines and consumer-protection law.
6. Optional SEO env vars: `GA_MEASUREMENT_ID`, `GOOGLE_SITE_VERIFICATION`, `BING_SITE_VERIFICATION`. Submit `https://<domain>/sitemap.xml` in Google Search Console and Bing Webmaster Tools.

## What's new compared with findapomsky

**Features**
- Kitten Match quiz (`/kitten-match/`): transparent weighted scoring, shareable result URLs, works without JS.
- Favorites (`/favorites/`): heart any kitten; stored on the device only.
- Instant filters with price slider capped to $800 to $1,000, sorting, pagination; the same view serves the page and the AJAX partial (one template, no duplicated markup).
- Litters and "Meet the parents", full photo gallery with lightbox (keyboard + swipe), sticky mobile reserve bar, share button.
- Three-step reservation form with delivery method and honeypot spam trap.
- Real contact form and waitlist (with preferences), both saved to the database before any email is sent.
- Care journal (`/journal/`) with Article schema, and a long-form breed guide.
- Administrator dashboard: responsive overview, reservation pipeline with status changes, CSV export (formula-injection safe), inbox for contact messages and waitlist, full kitten CRUD with photo galleries, journal post create/edit/publish/delete, review moderation, and first-party analytics charts. All dashboard routes require an active superuser.

**Price rule ($800 to $1,000)** is enforced in three places: model validators, a database `CHECK` constraint, and the filter UI/API.

**Animation and design** (all disabled under `prefers-reduced-motion`): animated SVG hero kitten whose eyes follow the cursor, crown drop, tail swish, blinking; heart burst; 3D card tilt with glare; arched photo frames; scroll progress bar; circular-reveal mobile menu; scroll-drawn timeline; animated accordions; step transitions; CSS view transitions between pages.

**SEO**
- Unique title, description and canonical on every page; faceted filter URLs are `noindex` and canonicalised to `/kittens/`.
- JSON-LD: Organization, WebSite + SearchAction, PetStore, BreadcrumbList, Product + Offer (+ AggregateRating only with real reviews), FAQPage (generated from the same data as the visible FAQ), CollectionPage/ItemList/AggregateOffer, BlogPosting, Article.
- 11 keyword landing pages, each with unique copy and its own FAQ (the original reused identical text), plus breed guide and journal for topical authority.
- Image sitemap, robots.txt, web manifest, Open Graph/Twitter cards (generated 1200x630 share image), semantic headings, breadcrumbs, lazy images with dimensions, no render-blocking JS framework (Bootstrap was dropped; first-party CSS/JS only), gzip + hashed static assets.

## Fixes to issues found in the original project
- `reservations/admin.py` used `HttpResponseRedirect` without importing it, and injected a `mailto:` URL into inline JavaScript unescaped. Replaced with escaped output.
- Email failures after saving a reservation returned a 500; sending is now wrapped and logged, and the lead is always kept.
- `SECURE_SSL_REDIRECT` without `SECURE_PROXY_SSL_HEADER` loops forever behind Render's proxy. Added.
- Rate limiter trusted the left-most `X-Forwarded-For` value (spoofable). It now counts from the right using `TRUSTED_PROXY_COUNT`.
- Approve/reject review actions changed state on GET links (CSRF-able). They are POST-only now; logout is POST (required by Django 5).
- `hreflang` tags claimed en-us/en-gb/nl on one URL, and `aggregateRating` was emitted with zero reviews. Both removed.
- `DeleteView.delete()` overrides no longer run in Django 4+, so success messages never showed. Now uses `form_valid`.
- The public API listed adopted animals. It now excludes them.
- The unused `Post` model had no URLs or templates. It now powers the journal.

## Deployment
Same as before: Render (`render.yaml`, `Procfile`), or Docker. Production env example is in `.env.example`. Remember: with `USE_S3=True` fill in the AWS variables, and run on Postgres if you expect more than light traffic. The default in-memory cache is per-process; use Redis if you add workers and want shared rate limits.

## Project layout
```
config/        settings, urls, wsgi/asgi
core/          site settings, journal, waitlist, contact, landing pages, sitemaps, middleware, SEO helpers
kittens/       Kitten, Litter, KittenImage, filters, quiz, favorites, API, placeholder art
reservations/  Reservation model, form, emails, API
reviews/       Testimonial moderation, form, API
dashboard/     superuser-only admin dashboard + first-party analytics
accounts/      login/logout
templates/ static/
```
