from shop.models import Order,OrderItem, Products
from orders_bot.signals import send_order_cancellation_message



def cancel_order(user_id, order_id):
    try:
        order = Order.objects.get(id=order_id, ordered_by=user_id,status="pending",is_paid=False)
        order.status = "cancelled"
        order.save()
        order_items = OrderItem.objects.filter(order_id=order.id)
        for item in order_items:
            product = Products.objects.filter(id=item.product.id).first()
            product.quantity += item.quantity
            product.save()
        data={
            "order_number": order.order_number,
            "first_name": order.ordered_by.full_name,
            "phone_number": order.ordered_by.phone_number,
            "address": order.ordered_by.address,
            "payment_method": order.payment_method,
            "created_datetime": order.created_datetime,
            "items": []
        }
        for item in order_items:
            data["items"].append({
                "product_name": item.product.name,
                "quantity": item.quantity,
                "calculated_total_price": item.quantity * item.product.discounted_price,
                "sku": item.product.sku,
            })
        send_order_cancellation_message(data)
        
        return True
    except Order.DoesNotExist:
        return False