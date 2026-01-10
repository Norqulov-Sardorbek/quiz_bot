from shop.models import Category




def get_all_categories( gender="all",is_all="no"):
    categories=Category.objects.all()
    if gender != "all":
        if gender == "male":
            categories=categories.exclude(gender="female")
        elif gender == "female":
            categories=categories.exclude(gender="male")
    
    date_info=[]
    for category in categories:
        if  is_all != "yes" and category.product_count <= 0:
            continue
        category_data = {
            "id": category.id,
            "name": category.name ,
            "product_count": category.product_count,
            "image": category.make_https if category.image else None,
        }
        date_info.append(category_data)
    return date_info