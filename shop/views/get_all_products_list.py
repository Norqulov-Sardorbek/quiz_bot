from rest_framework.views import APIView
from shop.services.get_all_products_list import get_all_products_list
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes
from rest_framework import serializers ,status
from core.constants import CustomPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProductsSerializer(serializers.Serializer):
    
    id= serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity= serializers.IntegerField()
    discount = serializers.IntegerField()
    video_url = serializers.URLField(required=False, allow_blank=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1)
    description = serializers.CharField()
    images = serializers.ListField(child=serializers.URLField())
    sold_count = serializers.IntegerField()




class ProductListAPIView(APIView):
    pagination_class = CustomPagination
    @swagger_auto_schema(
        operation_description="Retrieve all products with optional filters",
        operation_summary="Get All Products",
        manual_parameters=[
            openapi.Parameter(
                "category_id",
                openapi.IN_QUERY,
                description="Filter by category",
                type=openapi.TYPE_STRING
            ),
          
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search term for product name or description",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "min_price",
                openapi.IN_QUERY,
                description="Minimum price filter",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                "max_price",
                openapi.IN_QUERY,
                description="Maximum price filter",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                "min_rating",
                openapi.IN_QUERY,
                description="Minimum average rating filter",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                "max_rating",
                openapi.IN_QUERY,
                description="Maximum average rating filter",
                type=openapi.TYPE_NUMBER
            ),
            
        ],
        responses={status.HTTP_200_OK: ProductsSerializer(many=True)}
    )
    
    def get(self, request):
        data = request.query_params

        products = get_all_products_list(data)
        if not products:
            raise CustomApiException(ErrorCodes.NOT_FOUND, message="No products found.")

        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request, view=self)
        
        serializer = ProductsSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)
