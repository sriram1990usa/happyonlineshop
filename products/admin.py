from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductVariant

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_featured', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_featured']
    search_fields = ['name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_featured']
    search_fields = ['name']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'SKU', 'price', 'discount_price', 'stock', 'is_active', 'is_low_stock']
    list_filter = ['is_active', 'is_low_stock', 'category', 'brand']
    search_fields = ['name', 'SKU', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
