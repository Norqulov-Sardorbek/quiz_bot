from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status,serializers
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from shop.services.delete_cart_products import delete_grouped_cart_products
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from users.models import CustomUser



class DeleteCartProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    
    


class DeleteCartProductsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Add a product to the user's cart",
        operation_summary="Create Cart Product",
        request_body=DeleteCartProductSerializer(many=True),
        responses={
            status.HTTP_200_OK: openapi.Response("Product added to cart successfully."),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Invalid input."),
            status.HTTP_404_NOT_FOUND: openapi.Response("Product not found.")
        }
    )
    def post(self,request):
        user_id= request.user.id
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            raise CustomApiException(ErrorCodes.UNAUTHORIZED,message="User not found.")
        serializer = DeleteCartProductSerializer(data=request.data, many=True)
        if serializer.is_valid():
            delete_grouped_cart_products(user_id=user_id,datas=serializer.validated_data)
            return Response({"message": "Product deleted from cart successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            