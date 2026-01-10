from shop.models import Cart,Products
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes






def get_cart_product(user_id):
    cart_products=Cart.objects.filter(user_id=user_id).select_related("product__category").prefetch_related("product__images")
    if not cart_products.exists():
        return []
    data=[]
    for item in cart_products:
        product = Products.objects.filter(id=item.product.id).first()
        data.append({
            "id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "category": item.product.category.name if item.product.category else None,
            "price": item.price,
            "quantity": item.quantity,
            "sklad_quantity": product.quantity if product else 0,
            "discount": item.product.discount,
            "video_url": item.product.video_url,
            "discounted_price": item.product.discounted_price,
            "average_rating": item.product.average_rating,
            "description": item.product.description,
            "sold_count": item.product.sold,
            "images": [img.make_https for img in product.images.all()] if product else [],
            
        })
    return data