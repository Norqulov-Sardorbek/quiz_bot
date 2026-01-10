from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shop.models import Order



class PermissionToCommentAPIView(APIView):

    def get(self, request):
        product_id = request.query_params.get('product_id')

        user_id = request.user.id
        exists = Order.objects.filter(
            ordered_by_id=user_id,
            status="delivered",
            items__product_id=product_id
        ).exists()

        if exists:
            return Response({"message": True}, status=status.HTTP_200_OK)

        return Response({"message": False}, status=status.HTTP_403_FORBIDDEN)
