from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_yasg.utils import swagger_auto_schema
from shop.services.update_cart_product import update_cart

class UpdateCartSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    
class UpdateCartProductView(APIView):
    @swagger_auto_schema(
        operation_description="Update the quantity of a product in the cart.",
        request_body=UpdateCartSerializer,
    )    
    def put(self,request):
        user_id = request.user.id
        serializer = UpdateCartSerializer(data=request.data)
        if serializer.is_valid():
            update_cart(user_id,serializer.validated_data)
            return Response({"detail": "Cart product updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)