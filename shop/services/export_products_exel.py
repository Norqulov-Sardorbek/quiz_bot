import pandas as pd
from io import BytesIO
from shop.models import Products


def export_products_to_excel():
    """
    Products jadvalidan barcha ma'lumotlarni olib,
    Excel fayl shaklida BytesIO obyektini qaytaradi.
    """
    # 1️⃣ Barcha mahsulotlarni olish
    products = Products.objects.all().values(
        'id',
        'category__name',
        'name',
        'price',
        'quantity',
        'discount',
        'description',
        'sku',
        'video_url',
        'created_datetime',
        'modified_datetime',
    )

    if not products.exists():
        df = pd.DataFrame(columns=[
            'ID', 'Kategoriya', "O'yinchoq nomi", "Narxi (so'mda)", "Miqdori", "Chegirma (%)",
            "Tavsif",  "Karobka kodi",
            "YouTube video havolasi", "Yaratilgan sana", "Yangilangan sana"
        ])
    else:
        
        df = pd.DataFrame(products)
        for col in ['created_datetime', 'modified_datetime']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.tz_localize(None)

        df.rename(columns={
            'id': 'ID',
            'category__name': 'Kategoriya',
            'name': "O'yinchoq nomi",
            'price': "Narxi (so'mda)",
            "quantity": "Miqdori",
            'discount': "Chegirma (%)",
            'description': "Tavsif",
            'sku': "Karobka kodi",
            'video_url': "YouTube video havolasi",
            'created_datetime': "Yaratilgan sana",
            'modified_datetime': "Yangilangan sana",
        }, inplace=True)

    # 2️⃣ Excel faylni xotirada yaratish
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mahsulotlar')

    buffer.seek(0)
    return buffer
