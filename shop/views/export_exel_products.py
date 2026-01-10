from rest_framework.views import APIView
from django.http import HttpResponse
from shop.services.export_products_exel import export_products_to_excel


class ExportExcelProductsView(APIView):
    """
    GET -> Excel faylni yuklab olish.
    """
    def get(self, request):
        excel_buffer = export_products_to_excel()

        response = HttpResponse(
            excel_buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

        return response
