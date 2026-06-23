from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=150, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    SKU = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_low_stock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_title = models.CharField(max_length=150, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['SKU']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.is_low_stock = self.stock <= 5
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def has_discount(self):
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def discount_percentage(self):
        if self.has_discount:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=150, blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=50)  # e.g., 'Color', 'Size'
    value = models.CharField(max_length=50) # e.g., 'Red', 'XL'
    price_override = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'name', 'value')

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
