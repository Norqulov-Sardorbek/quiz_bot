from shop.models import Cart


def delete_grouped_cart_products(user_id, datas):
    for item in datas:
        product_id = item.get("product_id")
        if not product_id :
            continue

        Cart.objects.filter(
            user_id=user_id,
            product_id=product_id,
        ).delete()

        
    return True
