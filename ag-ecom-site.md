# PremiumShop AI - Project Summary & Reference Guide

PremiumShop AI is a production-grade, highly scalable multi-category ecommerce platform built with Django. It features a responsive modern UI (inspired by Amazon, Myntra, and Apple Store) and incorporates modular Django apps with decoupled signals and mock integrations.

---

## 1. Project Directory Structure

The application is structured into modular, decoupled Django apps:

- **`core/`**: Shared settings, template tags, global context, and layouts (e.g. `base.html`).
- **`accounts/`**: Customer user profiles, addresses, authentication, and registration.
- **`products/`**: Catalog pages, hierarchical categories, brand filters, and size variants.
- **`cart/`**: Shopping cart, item quantities, and discount coupon calculations.
- **`orders/`**: Address steps, payment selections, order placement, and order state history.
- **`payments/`**: Stripe and Razorpay payment controller logic with webhook processing.
- **`reviews/`**: Rating stars, verified purchase badges, review titles, and descriptions.
- **`wishlist/`**: Adding/removing items and quick cart movements.
- **`notifications/`**: In-app notifications, mock SMS logging, and console email dispatches.
- **`dashboard/`**: Admin/staff panel for catalog, inventory updates, and sales statistics.

---

## 2. Test Credentials

You can use these seeded credentials for testing features on the local development server:

- **Admin Account**:
  - **Email**: `admin@premiumshop.ai`
  - **Password**: `AdminPass123!`
- **Customer Account**:
  - **Email**: `customer@premiumshop.ai`
  - **Password**: `CustomerPass123!`
- **Reviewer Account**:
  - **Email**: `reviewer@premiumshop.ai`
  - **Password**: `ReviewPass123!`

---

## 3. Command Checklist

Run these commands inside your activated Python virtual environment:

### Database Seeding
To reset the SQLite database tables and seed fresh test data:
```bash
python seed_data.py
```

### Running the Server
To start the local development server:
```bash
python manage.py runserver
```

### Running Unit Tests
To run all 18 automated unit and integration tests covering auth, catalog, cart, checkouts, and reviews:
```bash
python manage.py test
```

---

## 4. Key Refactorings & Implementations

### A. Reviews Model Realignment
To address the Django loader startup `FieldError: Unknown field(s) (body, title) specified for Review`, we refactored:
1. `reviews/models.py`: Added `title = models.CharField(max_length=255, blank=True)` and renamed the `comment` field to `body = models.TextField()` to align with `reviews/forms.py` and `templates/products/detail.html`.
2. Created and applied migration files (`0002_rename_comment_review_body_review_title.py`) to align the SQLite database.

### B. Template Filters Optimization
1. Django templates do not support direct multiplication (e.g. `forloop.counter | mul:20`). We added a custom `mul` multiplication filter inside `core/templatetags/currency_filters.py`.
2. This resolved compile-time template errors in `templates/products/list.html`.

### C. Event-Driven Notifications
1. We created `orders/signals.py` to listen for post-save operations on the `Order` model.
2. Placing an order or updating its delivery status automatically dispatches a detailed notification to the customer.
3. `notifications/services.py` implements an extensible log dispatcher that logs transaction SMS simulations to the console and emails using the console email backend.

### D. Mock Webhook Endpoints
1. `payments/views.py` contains CSRF-exempt views for Stripe (`/payments/webhook/stripe/`) and Razorpay (`/payments/webhook/razorpay/`).
2. They parse mock webhook JSON payloads, retrieve the associated `Order`, set `payment_status` to `PAID`, update transaction statuses, and log entries to the `Transaction` table.
