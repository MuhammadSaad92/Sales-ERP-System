from django.urls import path
from . import views

urlpatterns = [
    path('closing-report/', views.closing_report, name='closing_report'),
    path('sales-report-product-wise/', views.sales_report_product_wise, name='sales_report_product_wise'),
    path('purchase-report-product-wise/', views.purchase_report_product_wise, name='purchase_report_product_wise'),
    path('profit-report/', views.profit_report, name='profit_report'),
    path('vat-tax-report/', views.vat_tax_report, name='vat_tax_report'),
    path('shipping-cost-report/', views.shipping_cost_report, name='shipping_cost_report'),
    path('return-sale-report/', views.return_sale_report, name='return_sale_report'),
    path('return-purchase-report/', views.return_purchase_report, name='return_purchase_report'),
]