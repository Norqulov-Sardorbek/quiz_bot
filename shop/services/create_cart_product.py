from shop.models import Cart, Products
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes


def create_cart_product(user_id, data):
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id:
        raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Product ID is required.")
    if quantity is None:
        raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Quantity is required.")

    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        raise CustomApiException(ErrorCodes.NOT_FOUND, message="The specified product does not exist.")

    cart_product, created = Cart.objects.get_or_create(
        user_id=user_id,
        product_id=product.id,
        price=product.discounted_price,
        defaults={'quantity': max(quantity, 0)}  
    )

    if not created:
        new_quantity = cart_product.quantity + quantity

        if new_quantity <= 0:
            cart_product.delete()
            return True

        cart_product.quantity = new_quantity
        cart_product.save()

    return True
