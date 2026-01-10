from shop.models import CommentProducts,Products
from users.models import CustomUser as User
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException



def create_comment_product(data, user_id):
    product = Products.objects.get(id=data.get("product_id"))
    if not product:
        raise CustomApiException(ErrorCodes.NOT_FOUND, "Product not found")
    CommentProducts.objects.create(
        product_id=product.id,
        comment=data.get("comment"),
        rating=data.get("rating"),
        commented_by_id=user_id
    )
    return True