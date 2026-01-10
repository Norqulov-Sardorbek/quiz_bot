from shop.models import Products, CommentProducts





def get_product_comments(product_id):
    try:
        product = Products.objects.get(id=product_id)
        comments = CommentProducts.objects.filter(product=product).select_related('commented_by').order_by('-created_datetime')
        comment_list = []
        for comment in comments:
            comment_list.append({
                "id": comment.id,
                "first_name": comment.commented_by.first_name if comment.commented_by else "Anonymous",
                "text": comment.comment,
                "rating": comment.rating,
                "created_at": comment.created_datetime,
            })
        return comment_list
    except Products.DoesNotExist:
        return []