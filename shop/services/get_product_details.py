from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from shop.models import Products
from shop.services.find_product import find_product_from_billz




def get_product_details(product_id):
    product = Products.objects.prefetch_related("images").select_related("category").filter(id=product_id).first()
    if not product:
        raise CustomApiException(ErrorCodes.NOT_FOUND, "Product not found")
    product.views += 1
    product.save()
    
    quantity = find_product_from_billz(product.sku, product.billz_position)
    if quantity is not  None and product.quantity != quantity.get("qty", 0):
        product.quantity = quantity.get("qty", product.quantity)
        
        product.save()
    
    return {
            "id": product.id,
            "name": product.name,
            "category": product.category.name if product.category else None,
            "price": product.price,
            "quantity": product.quantity,
            "discount": product.discount,
            "video_url": product.video_url,
            "discounted_price": product.discounted_price,
            "average_rating": product.average_rating,
            "description": product.description,
            "images": [img.make_https for img in product.images.all()],
            "sold_count": product.sold      
            }
    