from django.contrib import admin
from .models import Product, Cart, Order

class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("name", "description")
    list_filter = ("created_at",)
    fieldsets = (
        (None, {
            "fields": ("name", "description", "price", "stock", "image")
        }),
        ("Advanced options", {
            "classes": ("collapse",),
            "fields": ("created_at",),
        }),
    )

class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "added_at")
    readonly_fields = ("added_at",)
    search_fields = ("user__username", "product__name")

class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "status", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("user__username",)
    list_filter = ("status", "created_at")

admin.site.site_header = "Store Management"
admin.site.site_title = "Store Admin"
admin.site.index_title = "Admin Dashboard"

admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)

