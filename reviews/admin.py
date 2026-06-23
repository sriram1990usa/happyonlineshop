from django.contrib import admin
from .models import ProductReview, ReviewImage, DeliveryReview, ReviewVote, ReviewReport, AdminReply

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1

class AdminReplyInline(admin.StackedInline):
    model = AdminReply
    fk_name = 'product_review'
    extra = 0
    max_num = 1

class DeliveryAdminReplyInline(admin.StackedInline):
    model = AdminReply
    fk_name = 'delivery_review'
    extra = 0
    max_num = 1

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_verified_purchase', 'status', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'status', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'body']
    inlines = [ReviewImageInline, AdminReplyInline]
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(status='APPROVED')
        for review in queryset:
            review.update_product_rating_cache()
    approve_reviews.short_description = "Approve selected product reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(status='REJECTED')
        for review in queryset:
            review.update_product_rating_cache()
    reject_reviews.short_description = "Reject selected product reviews"


@admin.register(DeliveryReview)
class DeliveryReviewAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'rating', 'status', 'created_at']
    list_filter = ['rating', 'status', 'created_at']
    search_fields = ['order__order_number', 'user__email', 'body']
    inlines = [DeliveryAdminReplyInline]
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(status='APPROVED')
    approve_reviews.short_description = "Approve selected delivery reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_reviews.short_description = "Reject selected delivery reviews"


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_review', 'delivery_review', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_review', 'delivery_review', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reason', 'user__email']
    actions = ['dismiss_reports', 'action_reports']

    def dismiss_reports(self, request, queryset):
        queryset.update(status='DISMISSED')
    dismiss_reports.short_description = "Dismiss selected reports"

    def action_reports(self, request, queryset):
        queryset.update(status='ACTIONED')
        for report in queryset:
            if report.product_review:
                report.product_review.status = 'REJECTED'
                report.product_review.save()
            if report.delivery_review:
                report.delivery_review.status = 'REJECTED'
                report.delivery_review.save()
    action_reports.short_description = "Action selected reports (rejects reviews)"


@admin.register(AdminReply)
class AdminReplyAdmin(admin.ModelAdmin):
    list_display = ['admin', 'product_review', 'delivery_review', 'created_at']
    search_fields = ['body', 'admin__email']
