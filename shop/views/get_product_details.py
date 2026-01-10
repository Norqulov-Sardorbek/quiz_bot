from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shop.services.get_product_details import get_product_details
from shop.views.get_all_products_list import ProductsSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class ProductDetailsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve detailed information about a specific product",
        operation_summary="Get Product Details",
        manual_parameters=[
            openapi.Parameter(
                "product_id",
                openapi.IN_QUERY,
                description="ID of the product to retrieve details for",
                type=openapi.TYPE_INTEGER
            )
        ]
    )

    def get(self, request):
        product_id = request.query_params.get("product_id")
        product = get_product_details(product_id)
        serializer = ProductsSerializer(product)
        return Response(serializer.data,status=status.HTTP_200_OK)



