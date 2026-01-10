from drf_yasg import openapi
from users.models import CustomUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_yasg.utils import swagger_auto_schema
from shop.services.cancel_order import cancel_order
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException




class CancelOrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    
    
class CancelOrderView(APIView):
    @swagger_auto_schema(
        operation_description="Cancel a pending order",
        operation_summary="Cancel Order",
        request_body=CancelOrderSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response("Order canceled successfully."),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Invalid input."),
            status.HTTP_404_NOT_FOUND: openapi.Response("Order not found or cannot be canceled.")
        }
    )
    def post(self, request):
        user_id = request.user.id
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            raise CustomApiException(ErrorCodes.UNAUTHORIZED, message="User not found.")
        serializer = CancelOrderSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            if cancel_order(user_id, order_id):
                return Response({"message": "Order canceled successfully."}, status=status.HTTP_200_OK)
            else:
                raise CustomApiException(ErrorCodes.NOT_FOUND, message="Order not found or cannot be canceled.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)