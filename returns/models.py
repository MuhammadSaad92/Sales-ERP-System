from django.db import models
from customer.models import Customer
from supplier.models import Supplier
from sale.models import Sale
from purchase.models import Purchase
from product.models import Product

# Create your models here.

class Return(models.Model):
    RETURN_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
    ]
    invoice_no = models.CharField(max_length=50, unique=True)
    return_type = models.CharField(max_length=20, choices=RETURN_TYPE_CHOICES)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.return_type.capitalize()} Return {self.invoice_no}"

    def save(self, *args, **kwargs):
        # Ensure only one of customer or supplier is set based on return_type
        if self.return_type == 'customer':
            self.supplier = None
            self.purchase = None
        elif self.return_type == 'supplier':
            self.customer = None
            self.sale = None
        super().save(*args, **kwargs)

class ReturnItem(models.Model):
    return_record = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='return_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name if self.product else 'N/A'} ({self.quantity}) in Return {self.return_record.invoice_no}"