Please generate a production-grade Django ecommerce application rather than a simple demo with the following requirements:

ROLE:

You are a world-class Senior Software Architect, Principal Django Engineer,
Senior UI/UX Designer, Product Manager, Database Architect, Security Engineer,
DevOps Engineer, QA Engineer, and Ecommerce Platform Expert.

Your task is to design and generate a complete premium Ecommerce Web Application
using Django (Python), HTML5, CSS3, JavaScript, Bootstrap/Tailwind,
PostgreSQL, Redis, Celery, Django REST Framework, and modern frontend techniques.

The final product must feel comparable to Amazon, Flipkart, Myntra,
Nike Store, Apple Store, and premium modern ecommerce websites.

Build the application as if it will be used by thousands of customers.

======================================================================
PROJECT NAME
======================================================================

PremiumShop AI

A complete multi-category ecommerce platform with modern UI/UX,
advanced shopping experience, responsive design,
high performance, scalability, and enterprise-grade architecture.

======================================================================
PRIMARY OBJECTIVES
======================================================================

1. Create a premium ecommerce shopping experience.
2. Mobile-first responsive design.
3. Modern clean UI.
4. Fast page loading.
5. Smooth animations.
6. Professional product browsing.
7. Secure authentication.
8. Full cart and checkout flow.
9. Admin management panel.
10. Real-world ecommerce functionality.

======================================================================
TECHNOLOGY STACK
======================================================================

Backend:
- Python
- Django
- Django REST Framework

Database:
- PostgreSQL

Caching:
- Redis

Background Tasks:
- Celery

Authentication:
- Django Authentication
- JWT Authentication

Frontend:
- HTML5
- CSS3
- Tailwind CSS
- Bootstrap 5
- JavaScript ES6+
- AJAX
- HTMX (optional)

Icons:
- Font Awesome
- Hero Icons

Charts:
- Chart.js

Image Handling:
- Pillow

Payments:
- Razorpay Integration
- Stripe Integration
- Cash On Delivery

Deployment Ready:
- Docker
- Nginx
- Gunicorn

======================================================================
DEVELOPMENT ENVIRONMENT
======================================================================

The entire project must be developed inside a Python virtual environment.

Requirements:

- Create and activate a dedicated Python venv.
- Never install dependencies globally.
- Isolate all project dependencies.
- Generate requirements.txt automatically.
- Ensure reproducible environments.

Commands:

python -m venv venv

Windows:

venv\Scripts\activate

Linux/macOS:

source venv/bin/activate

Install all dependencies inside the virtual environment.

Generate:

pip freeze > requirements.txt

Project structure should include:

project_root/
│
├── venv/
├── requirements.txt
├── manage.py
├── .env
├── .gitignore

Add .gitignore rules:

venv/
__pycache__/
*.pyc
.env
media/
staticfiles/

The generated setup instructions must always assume usage of virtual environment.

======================================================================
UI/UX REQUIREMENTS
======================================================================

Design must be premium.

Look and feel inspired by:

- Amazon
- Flipkart
- Myntra
- Apple
- Nike
- Adidas

Requirements:

- Elegant typography
- Large hero banners
- Gradient accents
- Card-based layout
- Smooth hover effects
- Skeleton loaders
- Micro animations
- Modern shadows
- Glassmorphism sections
- Responsive navigation
- Sticky header
- Sticky cart button
- Mobile bottom navigation

Use:

- Rounded corners
- Premium spacing
- Consistent color palette
- Dark mode support
- Light mode support

======================================================================
RESPONSIVE DESIGN
======================================================================

Fully responsive for:

- Mobile
- Tablet
- Laptop
- Desktop
- Large screens

Breakpoints:

- 320px
- 480px
- 768px
- 1024px
- 1440px
- 1920px

======================================================================
HOME PAGE
======================================================================

Create a premium homepage containing:

1. Top announcement bar
2. Navigation bar
3. Search bar
4. Hero carousel
5. Featured categories
6. Trending products
7. Best sellers
8. Flash sale section
9. New arrivals
10. Popular brands
11. Recommended products
12. Customer testimonials
13. Newsletter signup
14. Blog previews
15. Footer

======================================================================
HEADER FEATURES
======================================================================

Header must include:

- Logo
- Search
- Categories dropdown
- Wishlist icon
- Cart icon
- Notification icon
- User profile
- Login
- Register
- Orders
- Language switcher

Sticky while scrolling.

======================================================================
PRODUCT CATALOG
======================================================================

Build advanced product catalog.

Features:

- Product grid
- Product list view
- Pagination
- Infinite scroll
- Product filtering
- Sorting
- Search suggestions
- Dynamic filters

Filter by:

- Category
- Brand
- Price
- Rating
- Color
- Size
- Availability

Sort by:

- Popularity
- Newest
- Price Low to High
- Price High to Low
- Rating

======================================================================
PRODUCT DETAIL PAGE
======================================================================

Must include:

- Product gallery
- Zoom image
- Multiple images
- Video support
- Product variants
- Color selection
- Size selection
- Stock status
- Price
- Discount
- Ratings
- Reviews

Buttons:

- Add to Cart
- Buy Now
- Wishlist

Additional Sections:

- Product description
- Specifications
- Reviews
- Questions & Answers
- Related products
- Similar products

======================================================================
SHOPPING CART
======================================================================

Features:

- Add item
- Remove item
- Update quantity
- Save for later
- Coupon code
- Gift wrapping
- Shipping estimation
- Cart summary

Real-time calculations.

======================================================================
CHECKOUT SYSTEM
======================================================================

Multi-step checkout.

Steps:

1. Address
2. Shipping
3. Payment
4. Review
5. Confirmation

Support:

- COD
- Razorpay
- Stripe

Order summary visible throughout.

======================================================================
LOCALIZATION & CURRENCY SETTINGS
======================================================================

Primary Currency:

- Indian Rupee (INR)

Currency Display Rules:

- Always display currency using ₹ symbol.
- Fallback support for ₨ where applicable.
- Currency symbol must appear before all monetary values.

Examples:

- ₹499
- ₹1,299
- ₹24,999

Apply currency formatting consistently across:

- Product listing page
- Product detail page
- Cart page
- Checkout page
- Order summary
- Invoice
- User dashboard
- Admin dashboard
- Revenue reports
- Discounts
- Coupons
- Shipping charges
- Refunds

Implement reusable currency formatter utility.

Support future multi-currency expansion.

======================================================================
USER AUTHENTICATION
======================================================================

Features:

- Register
- Login
- Logout
- Email verification
- Forgot password
- Reset password
- Social login

Social Login:

- Google
- Facebook
- GitHub

Security:

- CSRF protection
- XSS protection
- Rate limiting

======================================================================
USER DASHBOARD
======================================================================

Dashboard must include:

- Profile
- Orders
- Wishlist
- Addresses
- Notifications
- Returns
- Wallet
- Coupons

Order tracking timeline.

======================================================================
WISHLIST SYSTEM
======================================================================

Features:

- Add wishlist
- Remove wishlist
- Move to cart
- Share wishlist

======================================================================
REVIEWS AND RATINGS
======================================================================

Features:

- Star rating
- Verified purchase badge
- Images in reviews
- Helpful votes
- Review moderation

======================================================================
ORDER MANAGEMENT
======================================================================

Order states:

- Pending
- Confirmed
- Packed
- Shipped
- Out for Delivery
- Delivered
- Cancelled
- Returned
- Refunded

Timeline visualization required.

======================================================================
ADMIN PANEL
======================================================================

Create advanced admin dashboard.

Admin Features:

- Dashboard analytics
- Revenue tracking
- Product management
- Category management
- Brand management
- Inventory management
- Coupon management
- Customer management
- Vendor management
- Order management
- Review moderation

Charts:

- Sales chart
- Revenue chart
- User growth chart

======================================================================
PRODUCT MANAGEMENT
======================================================================

Fields:

- Name
- SKU
- Slug
- Description
- Category
- Brand
- Price
- Discount
- Images
- Stock
- Variants
- SEO fields

Support:

- Bulk upload
- CSV import/export

======================================================================
INVENTORY SYSTEM
======================================================================

Features:

- Stock tracking
- Low stock alerts
- Inventory history
- Warehouse support

======================================================================
SEARCH SYSTEM
======================================================================

Advanced search.

Features:

- Autocomplete
- Suggestions
- Typo tolerance
- Recent searches
- Popular searches

======================================================================
COUPON SYSTEM
======================================================================

Support:

- Percentage discount
- Fixed discount
- Free shipping
- Referral coupon

======================================================================
NOTIFICATION SYSTEM
======================================================================

Notifications:

- Order updates
- Shipping updates
- Promotions
- Offers

Channels:

- Email
- SMS
- In-app

======================================================================
SEO OPTIMIZATION
======================================================================

Implement:

- Meta tags
- Open Graph
- Structured Data
- Sitemap
- Robots.txt
- Canonical URLs

======================================================================
PERFORMANCE OPTIMIZATION
======================================================================

Requirements:

- Lazy loading
- Caching
- Image optimization
- Query optimization
- CDN readiness

Target:

- Lighthouse score > 90

======================================================================
ACCESSIBILITY
======================================================================

Follow WCAG standards.

Requirements:

- Keyboard navigation
- ARIA labels
- Screen reader support

======================================================================
SECURITY
======================================================================

Implement:

- CSRF protection
- XSS prevention
- SQL injection prevention
- Secure cookies
- JWT security
- Password hashing
- Rate limiting
- Audit logs

======================================================================
DATABASE DESIGN
======================================================================

Generate complete models for:

- User
- Profile
- Category
- Brand
- Product
- ProductImage
- ProductVariant
- Wishlist
- Cart
- CartItem
- Address
- Order
- OrderItem
- Coupon
- Review
- Notification

Include:

- Relationships
- Indexes
- Constraints

======================================================================
API DESIGN
======================================================================

Generate REST APIs for:

- Authentication
- Products
- Categories
- Cart
- Orders
- Payments
- Reviews
- Wishlist

Provide:

- Request examples
- Response examples

======================================================================
PROJECT STRUCTURE
======================================================================

Generate complete scalable folder structure.

Use modular apps:

accounts/
products/
cart/
orders/
payments/
reviews/
wishlist/
notifications/
dashboard/
core/

======================================================================
CODE QUALITY
======================================================================

Use:

- Class-based views
- Service layer
- Repository pattern
- Signals
- Mixins
- Custom managers

Follow:

- PEP8
- SOLID principles
- Clean Architecture

Currency Handling:

- Create custom Django template filters for INR formatting.
- Create reusable currency utility functions.
- Store monetary values using DecimalField.
- Avoid float values for prices.
- Ensure all templates automatically render ₹ before amounts.

Example:
Python
price = models.DecimalField(max_digits=12, decimal_places=2)

HTML: 
₹{{ product.price }}
OR
{{ product.price|inr }}
======================================================================
DELIVERABLES
======================================================================
Generate complete setup instructions for:

- Local Development
- Virtual Environment Setup
- PostgreSQL Setup
- Redis Setup
- Docker Setup
- Production Deployment

All local development commands must assume execution from an activated Python virtual environment.

Generate:

1. Complete architecture
2. Database schema
3. Django models
4. URL routes
5. Views
6. Serializers
7. Templates
8. Tailwind UI design
9. REST APIs
10. Authentication flow
11. Payment flow
12. Admin dashboard
13. Docker configuration
14. Deployment guide
15. Testing strategy

The generated solution must be production-ready,
enterprise-grade,
highly scalable,
cleanly organized,
and visually comparable to leading ecommerce platforms.