from shop.models import Products
from django.db.models import Q,Avg,Value
from django.db.models.functions import Coalesce


def get_all_products_list(data):
    """
    Fetches all products, optionally filtered by category.
    """
    category_id = data.get("category_id")
    search = data.get("search")
    min_price = data.get("min_price")
    max_price = data.get("max_price")
    min_rating = data.get("min_rating")
    max_rating = data.get("max_rating")
    queryset = Products.objects.prefetch_related('images').select_related("category").filter(quantity__gt=0)
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    if min_rating or max_rating:
        queryset = queryset.annotate(
        avg_rating=Coalesce(Avg('comments__rating'), Value(5.0))
    )
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=min_rating)
        if max_rating:
            queryset = queryset.filter(avg_rating__lte=max_rating)

    products_data = []
    queryset = queryset.order_by('-created_datetime')
    for product in queryset:
        
        product_data = {
            "id": product.id,
            "name": product.name ,
            "category": product.category.name if product.category else None,
            "price": product.price,
            "quantity": product.quantity,
            "discount": product.discount,
            "video_url": product.video_url,
            "discounted_price": product.discounted_price,
            "average_rating": product.average_rating,
            "description": product.description ,
            "sold_count": product.sold,
            "images": [img.make_https for img in product.images.all()],
        }        
        products_data.append(product_data)

    return products_data
