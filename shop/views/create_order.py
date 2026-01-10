from rest_framework import  status,serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.views import APIView
from shop.services.create_order import create_order
from users.models import CustomUser
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
# Create your views here.


class OrderCreateSerializer(serializers.Serializer):
    class OrderItemsSerializer(serializers.Serializer):
        product_id = serializers.IntegerField()
        quantity = serializers.IntegerField(default=1)
    payment_method = serializers.ChoiceField(choices=['naxt', 'karta'], default='naxt')
    product_items = OrderItemsSerializer(many=True)

class OrderCreateResponseSerializer(serializers.Serializer):
    payment_link = serializers.CharField(max_length=500)

class OrderCreateAPIView(APIView):
    @swagger_auto_schema(operation_description="Create a new order",
                         operation_summary="Create Order",
                            request_body=OrderCreateSerializer,
                            responses={
                                status.HTTP_201_CREATED: OrderCreateResponseSerializer,
                                status.HTTP_200_OK: openapi.Response(description="Order created successfully")
                            }   
                         )

    def post(self, request):
        user_id= request.user.id
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            raise CustomApiException(ErrorCodes.UNAUTHORIZED,message="User not found.")
        data = request.data
        payment_link = create_order(data,user_id)
        if payment_link:
            return Response({"payment_link": payment_link}, status=status.HTTP_201_CREATED)
        return Response({"success": "Order created successfully"}, status=status.HTTP_200_OK)