from rest_framework import  status,serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from shop.services.get_cart_product import get_cart_product
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from users.models import CustomUser


class CartProductsSerializer(serializers.Serializer):
    id= serializers.IntegerField()
    product_id= serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity= serializers.IntegerField()
    sklad_quantity = serializers.IntegerField()
    discount = serializers.IntegerField()
    video_url = serializers.URLField(required=False, allow_blank=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1)
    description = serializers.CharField()
    images = serializers.ListField(child=serializers.URLField(), allow_null=True)
    sold_count = serializers.IntegerField()

class GetCartProductAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve all products in the authenticated user's cart",
        operation_summary="Get Cart Products",
        responses={
            status.HTTP_200_OK: CartProductsSerializer(many=True),
            status.HTTP_404_NOT_FOUND: openapi.Response("The cart is empty.")
        }
    )
    def get(self, request):
        user_id = request.user.id
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            raise CustomApiException(ErrorCodes.UNAUTHORIZED,message="User not found.")
        cart_products = get_cart_product(user_id)
        serializer = CartProductsSerializer(cart_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
