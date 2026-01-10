from core.constants import click_up
from decimal import Decimal
from shop.models import Order, OrderItem, Products,Cart
from users.models import CustomUser as User
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from orders_bot.signals import send_order_message


def create_order(data, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise CustomApiException(ErrorCodes.NOT_FOUND, "User not found")

    product_items = data.get('product_items')
    payment_method = data.get('payment_method', 'naxt')

    if not product_items :
        raise CustomApiException(ErrorCodes.INVALID_INPUT, "Product items are required and must be a list.")

    order = Order.objects.create(
        ordered_by=user,
        payment_method=payment_method,
    )

    total_price = Decimal("0")
    data_to_send = {
        "order_number": order.order_number,
        "first_name": user.first_name,
        "phone_number": user.phone_number,
        "address": user.address,
        "payment_method": order.payment_method,
        "is_paid": order.is_paid,
        "created_datetime": order.created_datetime,
        "items": []
    }

    for item in product_items:
        product_id = item.get('product_id')
        quantity = item.get('quantity')

        if not product_id:
            raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Product ID is required.")
           
        product = Products.objects.filter(id=product_id).first()
        if not product:
            raise CustomApiException(ErrorCodes.NOT_FOUND, f"Product with id {product_id} not found")

        OrderItem.objects.create(
            order=order,
            product_id=product.id,
            quantity=quantity,
            price=product.discounted_price,
        )
        cart_item = Cart.objects.filter(product_id=product.id, user_id=user.id).first()
        if cart_item:
            cart_item.delete()
        product = Products.objects.filter(id=product.id).first()
        if product and product.quantity >= quantity:
            product.quantity -= quantity
            product.save()
        else:
            raise CustomApiException(ErrorCodes.INVALID_INPUT, f"Insufficient stock for product {product.name}")
    
        total_price += product.discounted_price * Decimal(str(quantity))
        data_to_send["items"].append({
            "product_name": product.name,
            "quantity": quantity,
            "sku": product.sku,
            "calculated_total_price": product.discounted_price * Decimal(str(quantity))
        })

    # 4️⃣ Telegram signaliga ma’lumot jo‘natamiz
    send_order_message(data_to_send)

    if payment_method == "karta":
        payment_link = click_up.initializer.generate_pay_link(
            id=order.uuid,
            amount=total_price,
            return_url="https://toysmars.uz"
        )
        order.payment_link = payment_link
        order.save()
        return payment_link

    return None
