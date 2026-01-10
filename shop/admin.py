from django.db import models
from django.urls import path
from django.contrib import admin
from django.utils.html import format_html
from django.template.response import TemplateResponse
from shop.services.get_valid_token import get_valid_token

from .models import (
    Category,
    Products,
    ImageProducts,
    Cart,
    Order,
    OrderItem,
    BillzToken,
)


class ImageProductsInline(admin.TabularInline):
    model = ImageProducts
    extra = 1
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:8px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Rasm oldindan ko'rish"



class ProductsAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sku", "colored_price","quantity", "views", "product_image", )
    list_filter = ("category",)
    search_fields = ("name","sku",)
    inlines = [ImageProductsInline]
    readonly_fields = ("product_image",)

    def colored_price(self, obj):
        return format_html(
            '<span style="color:{};">{} so’m</span>',
            "green" if obj.discount > 0 else "black",
            obj.discounted_price
        )
    colored_price.short_description = "Chegirmali narx"

    def product_image(self, obj):
        """Mahsulotga tegishli birinchi rasmni chiqarish"""
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:8px;" />',
                    first_image.image.url
                )
        return "—"
    product_image.short_description = "Asosiy rasm"



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    exclude = ("price",)
    readonly_fields = ("product", "sku", "quantity", "calculated_total_price", "product_image")

    def calculated_total_price(self, obj):
        return f"{obj.quantity * (obj.price or 0):,.0f} so’m"
    calculated_total_price.short_description = "Jami narx"

    def sku(self, obj):
        return obj.product.sku if obj.product else "—"
    sku.short_description = "Ishlab chiqaruvchi kodi"

    def product_image(self, obj):
        image = obj.product.images.first()
        if image and image.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:8px;" />', image.image.url)
        return "—"
    product_image.short_description = "Rasm"


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "ordered_by_name",
        "colored_payment_method",
        "colored_is_paid",
        "colored_status",
        "order_map_link", 
        "created_datetime",
    )
    list_filter = ("status", "is_paid", "payment_method")
    search_fields = ("ordered_by__first_name", "order_number")
    readonly_fields = (
        "ordered_by",
        "payment_method",
        "payment_link",
        "order_number",
        "created_datetime",
        "modified_datetime",
    )
    inlines = [OrderItemInline]
    def order_map_link(self, obj):
        user = obj.ordered_by

        if not user:
            return "❌ Mavjud emas"

        if getattr(user, "lat", None) and getattr(user, "lang", None):
            lat = user.lat
            lon = user.lang
            url = f"https://www.google.com/maps?q={lat},{lon}"

            return format_html(
                '<a href="{}" target="_blank" style="font-weight:600;">📍 Xaritada (GPS)</a>',
                url
            )

        # 2️⃣ Agar koordinata bo‘lmasa — address matni bo‘yicha ochiladi
        if user.address:
            address = user.address.replace(" ", "+")
            url = f"https://www.google.com/maps?q={address}"

            return format_html(
                '<a href="{}" target="_blank" style="font-weight:600;">📍 Xaritada (Manzil)</a>',
                url
            )

    # 3️⃣ Umuman maʼlumot bo‘lmasa
        return "❌ Maʼlumot yo‘q"

    order_map_link.short_description = "Manzil (Google Maps)"


    order_map_link.short_description = "Manzil"
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if not obj or obj.payment_method != "naxt":
            readonly.append("is_paid")
        return readonly
    def ordered_by_name(self, obj):
        return obj.ordered_by.first_name if obj.ordered_by else "No User"
    ordered_by_name.short_description = "Buyurtmachi"

    def colored_payment_method(self, obj):
        color = {
            "naxt": "green",
            "karta": "#4dabf7"
        }.get(obj.payment_method.lower(), "#888")

        return format_html(
            '<span style="color: white; background-color: {}; padding: 4px 10px; border-radius: 6px; font-weight: 600;">{}</span>',
            color,
            obj.payment_method.capitalize()
        )
    colored_payment_method.short_description = "To‘lov turi"

    def colored_is_paid(self, obj):
        if obj.is_paid:
            return format_html('<span style="background-color:#2ecc71; color:white; padding:3px 8px; border-radius:6px;">✅ To‘landi</span>')
        return format_html('<span style="background-color:#e74c3c; color:white; padding:3px 8px; border-radius:6px;">❌ To‘lanmagan</span>')
    colored_is_paid.short_description = "To‘lov holati"

    def colored_status(self, obj):
        colors = {
            "pending": "#f1c40f",
            "delivering": "#3498db",
            "delivered": "#2ecc71",
            "cancelled": "#e74c3c",
        }
        labels = {
            "pending": "⏳ Kutilmoqda",
            "delivering": "🚚 Yetkazilmoqda",
            "delivered": "✅ Yetkazib berildi",
            "cancelled": "❌ Bekor qilindi",
        }
        status = obj.status.lower() if obj.status else ""
        color = colors.get(status, "#7f8c8d")
        label = labels.get(status, status.capitalize())

        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 10px; border-radius:6px; font-weight:600;">{}</span>',
            color,
            label,
        )
    colored_status.short_description = "Buyurtma holati"


class CustomHTMLAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.custom_view), name='admin-custom-html'),
        ]
        return custom_urls + urls

    def custom_view(self, request):
        token = get_valid_token()
        context = dict(
            self.admin_site.each_context(request),
            title="📄 Excel eksport sahifasi",
            token = token,
        )
        return TemplateResponse(request, "shop/index.html", context)


class DummyModel(models.Model):
    class Meta:
        verbose_name_plural = "📄 O‘yinchoqlarni Excel orqali yuklash"
        managed = False



admin.site.register(Cart)
admin.site.register(Category)
admin.site.register(BillzToken)
admin.site.register(ImageProducts)
admin.site.register(Order, OrderAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(DummyModel, CustomHTMLAdmin)
