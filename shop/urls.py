from django.urls import path
from shop.views.get_all_products_list import ProductListAPIView
from shop.views.get_all_categories import CategoryListAPIView
from shop.views.get_product_comments import ProductComments
from shop.views.get_product_details import ProductDetailsAPIView
from shop.views.create_product_comments import CreateCommentProductAPIView
from shop.views.create_order import OrderCreateAPIView
from shop.views.get_permission_to_comment import PermissionToCommentAPIView
from shop.views.get_order_history import GetOrderHistoryAPIView
from shop.views.get_popular_products import PopularProducts
from shop.views.export_exel_products import ExportExcelProductsView
from shop.views.get_cart_product import GetCartProductAPIView
from shop.views.create_cart_product import CreateCartProductView
from shop.views.delete_cart_products import DeleteCartProductsAPIView
from shop.views.cancel_order import CancelOrderView
from shop.views.create_products import CreateProductView
from shop.views.update_cart_product import UpdateCartProductView

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('products/', ProductListAPIView.as_view(), name='products'),
    path('create-product/', CreateProductView.as_view(), name='create-product'),
    path('new-products/', PopularProducts.as_view(), name='popular-products'),
    path('product-details/', ProductDetailsAPIView.as_view(), name='product-details'),
    path('comment-create/', CreateCommentProductAPIView.as_view(), name='comment-create'),
    path('comment-permission/', PermissionToCommentAPIView.as_view(), name='comment-premission'),
    path('order-product/', OrderCreateAPIView.as_view(), name='order-product'),
    path('order-history/',GetOrderHistoryAPIView.as_view(), name='order-history'),
    path('cancel-order/', CancelOrderView.as_view(), name='cancel-order'),
    path('product-comments/<int:product_id>/', ProductComments.as_view(), name='product-comments'),
    path('export-products/', ExportExcelProductsView.as_view(), name='export-products'),
    path('get-cart-products/', GetCartProductAPIView.as_view(), name='cart-products'),
    path('create-cart-product/', CreateCartProductView.as_view(), name='create-cart-product'),
    path('update-cart-product/', UpdateCartProductView.as_view(), name='update-cart-product'),
    path("delete-cart-products/",DeleteCartProductsAPIView.as_view(),name='delete-cart-products')
]
