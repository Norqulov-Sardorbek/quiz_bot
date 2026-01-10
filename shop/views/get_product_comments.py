from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,serializers
from shop.services.get_product_comments import get_product_comments
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class GetProductCommentsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    text = serializers.CharField()
    rating = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    
    
    
class ProductComments(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve comments for a specific product",
        operation_summary="Get Product Comments",
        responses={status.HTTP_200_OK: GetProductCommentsSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "product_id",
                openapi.IN_PATH,
                description="ID of the product",
                type=openapi.TYPE_INTEGER
            )
        ]
    )

    def get(self, request, product_id):

        comments = get_product_comments(product_id)
        serializer = GetProductCommentsSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)