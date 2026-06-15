# PremiumShop AI — Premium Django Ecommerce Platform

PremiumShop AI is an enterprise-grade, multi-category ecommerce web application built using **Django**, **Bootstrap/Tailwind CSS**, and **JavaScript (ES6+)**. The platform delivers a premium, responsive shopping experience comparable to Amazon, Flipkart, and Myntra, featuring dark mode layouts, dynamic sorting, interactive cart sidebars, coupons, review moderation, and database-backed transactional events.

---

## Features

- 📱 **Mobile-First Responsive Design**: Optimized layouts supporting breakpoints down to 320px.
- 🛍️ **Advanced Product Catalog**: Multi-attribute filtering (category, brand, price range), sorting (newest, price, rating), and search.
- 🛒 **Dynamic Shopping Cart**: Instant item additions, variant selections (sizes/colors), quantity updates, and automatic price recalculations.
- 🎟️ **Promo & Coupon System**: Supports percentage discounts, flat cash off, and free shipping checks.
- 💳 **Mock Webhook Integrations**: Full transactional handlers for Stripe and Razorpay checkout loops.
- 🔔 **Event-Driven Notifications**: Automatically dispatches in-app, console-email, and logged-SMS notifications when order statuses change.
- 📊 **Staff Dashboard Panel**: Interactive Chart.js graphs displaying revenue summaries, stock levels, and customer signups.
- 🌟 **Verified Customer Reviews**: Star ratings, summary titles, and descriptive reviews per product.

---

## Tech Stack

- **Backend**: Python 3.12, Django 6.0, Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Local Fallback)
- **Frontend**: HTML5, Tailwind CSS, JavaScript (ES6+), FontAwesome
- **Caching & Tasks**: Redis & Celery (Configured, falling back to local memory caches for development)
- **Static Assets Serving**: WhiteNoise

---

## Quick Setup (Local Development)

### 1. Set Up Virtual Environment
Initialize and activate a local Python virtual environment:
```powershell
python -m venv venv

# Windows Activation:
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Generate Database and Seed Mock Data
Apply migrations and run the custom seeding script to populate users, addresses, categories, products, coupons, and reviews:
```powershell
python manage.py migrate
python seed_data.py
```

### 4. Run Server
Start the Django local development server:
```powershell
python manage.py runserver
```
Visit the application in your browser at `http://127.0.0.1:8000/`.

---

## Automated Testing
Run the automated test suite containing 18 unit and integration tests:
```powershell
python manage.py test
```

---

## Seeded Test Accounts

Use these credentials to test customer and admin roles:

| Account Type | Email | Password |
| :--- | :--- | :--- |
| **Superuser / Admin** | `admin@premiumshop.ai` | `AdminPass123!` |
| **Customer** | `customer@premiumshop.ai` | `CustomerPass123!` |
| **Reviewer** | `reviewer@premiumshop.ai` | `ReviewPass123!` |

---

## Deployment to Vercel
See the instructions in the `vercel-deploy-steps` file at the root of the project to initialize git, collect static assets, add environment variables, and push the build to Vercel.
