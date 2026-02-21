from django.contrib import admin
from .models import Product, Cart, Order
admin.site.site_header = "Store Management "
admin.site.site_title = "Store Admin"
admin.site.index_title = "Admin Dashboard"

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)