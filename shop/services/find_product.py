import requests
from shop.services.get_valid_token import get_valid_token

BILLZ_URL = "https://api-admin.billz.ai/v2/product-search-with-filters"

SHOP_MAIN = "6f09911e-e338-451a-82b9-d4d058ea4a8f"
SHOP_SECOND = "4c1bc0eb-3111-4592-92a2-0fbf7a469c36"

ALL_SHOPS = [SHOP_MAIN, SHOP_SECOND]


def find_product_from_billz(sku: str, billz_position: str):

    if not sku:
        return None

    token = get_valid_token()

    
    from_supplier, pos_str = billz_position.split("_")
    position = int(pos_str) - 1  # 1 → index 0, 2 → index 1

    
    if from_supplier == "main":
        shop_ids = [SHOP_MAIN]
    elif from_supplier == "sec":
        shop_ids = [SHOP_SECOND]
    else:  # "both"
        shop_ids = ALL_SHOPS

    
    def search(shops):
        payload = {
            "shop_ids": shops,
            "skus": [sku],
            "status": "all",
            "limit": 50,
            "page": 1
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        r = requests.post(BILLZ_URL, json=payload, headers=headers)
        return r.json()

    
    data = search(shop_ids)

    products = data.get("products") or []
    if not products:
        return None

    if position >= len(products):
        position = len(products) - 1

    product = products[position]

   
    stock_list = product.get("product_supplier_stock") or []

    qty_main = 0
    qty_second = 0
    wholesale_price = None

    for s in stock_list:
        shop_id = s.get("shop_id")

        if shop_id == SHOP_MAIN:
            qty_main = s.get("measurement_value") or 0
            wholesale_price = s.get("wholesale_price")

        elif shop_id == SHOP_SECOND:
            qty_second = s.get("measurement_value") or 0

    total_qty = qty_main + qty_second

    if total_qty == 0:
        return None

  
    return {
        "qty": total_qty,
        "wholesale": wholesale_price,
    }
