from shop.models import Cart
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes


def update_cart(user_id,data):
    cart_id = data.get('cart_id')
    quantity = data.get('quantity')
    cart = Cart.objects.filter(user_id=user_id,id=cart_id).first()
    if not cart:
        raise CustomApiException(ErrorCodes.NOT_FOUND, message="The specified cart product does not exist.")
    if quantity is None:
        raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Quantity is required.")
    
    cart.quantity = quantity
    cart.save()
    return True
    