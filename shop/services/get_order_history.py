from shop.models import  OrderItem,Order








def get_order_history(user_id):
    """
    Fetches the order history for a given user.
    :param user_id: ID of the user whose order history is to be fetched.
    :return: A list of dictionaries containing order details.
    """
    orders = (
            Order.objects
            .filter(ordered_by=user_id)
            .order_by('-id')
        )
    if not orders.exists():
        return []

    result = []
    for order in orders:
        order_dict = {
            "order_id": order.id,
            "status": order.status,
            "payment_method": order.payment_method,
            "is_paid": order.is_paid,
            "payment_link": order.payment_link if not order.is_paid and order.payment_method.lower() == "karta" else None,
            "items": [],
            "total_price":0
        }
        order_items=OrderItem.objects.filter(order_id=order.id).prefetch_related("product__images").select_related("product")
        total_price = 0
        for item in order_items:
            total_price += item.price * item.quantity
            
            order_dict["items"].append({
                "item_id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name if item.product else None,
                "price": float(item.price) ,
                "quantity": item.quantity,
                "images": [img.make_https for img in item.product.images.all()] if item.product else [],
                "total_price": float(item.price * item.quantity)
            })
        order_dict["total_price"] = total_price
        result.append(order_dict)

    return result