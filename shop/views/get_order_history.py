from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,serializers
from shop.services.get_order_history import get_order_history
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from users.models import CustomUser

class OrderHistorySerializer(serializers.Serializer):
    class OrderItemSerializer(serializers.Serializer):
        item_id = serializers.IntegerField()
        product_id = serializers.IntegerField()
        product_name = serializers.CharField()
        price = serializers.FloatField()
        quantity = serializers.IntegerField()
        total_price = serializers.FloatField()
        images = serializers.ListField(child=serializers.URLField())
    order_id = serializers.IntegerField()
    status = serializers.CharField()
    payment_method = serializers.CharField()
    payment_link = serializers.CharField(allow_null=True, required=False)
    is_paid = serializers.BooleanField()
    items = OrderItemSerializer(many=True)
    total_price = serializers.FloatField()





class GetOrderHistoryAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve the order history for the authenticated user",
        operation_summary="Get Order History",
        responses={
            status.HTTP_200_OK: OrderHistorySerializer(many=True),
            status.HTTP_404_NOT_FOUND: openapi.Response("No orders found for the user.")
        })
   

    def get(self, request):
        user_id = request.user.id
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            raise CustomApiException(ErrorCodes.UNAUTHORIZED,message="User not found.")

        response = get_order_history(user_id)
        if response:
            serializer = OrderHistorySerializer(data=response, many=True)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "No orders found."}, status=status.HTTP_404_NOT_FOUND)
       