from rest_framework import status,serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from shop.services.create_products import create_products
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CreateProductsSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    product_name = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    discount = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=0)
    quantity = serializers.IntegerField(required=False, default=0)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    sku = serializers.CharField(required=False, allow_blank=True, default="")
    billz_position = serializers.CharField(required=False, allow_blank=True, default="")
    video_url = serializers.URLField(required=False, allow_blank=True, default="")

    images = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )
    
    
    
class CreateProductView(APIView):
    @swagger_auto_schema(
        request_body=CreateProductsSerializer,
        responses={201: openapi.Response('Product created successfully')}
    )
    def post(self, request):
        serializer = CreateProductsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        images = request.FILES.getlist("images")  
        create_products(data=data, images=images)

        return Response({"message": "Product created successfully"}, status=status.HTTP_201_CREATED)