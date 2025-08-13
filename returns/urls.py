from django.urls import path
from . import views

app_name = 'returns'

urlpatterns = [
    path('returns/customer/list/', views.customer_return_list, name='customer_return_list'),
    path('returns/supplier/list/', views.supplier_return_list, name='supplier_return_list'),
    path('returns/add/', views.add_return, name='add_return'),
    path('returns/<str:invoice_no>/details/', views.return_details, name='return_details'),
    path('returns/get_sale_products/<int:sale_id>/', views.get_sale_products, name='get_sale_products'),
    path('returns/get_purchase_products/<int:purchase_id>/', views.get_purchase_products, name='get_purchase_products'),
]