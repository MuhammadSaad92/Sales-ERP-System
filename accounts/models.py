from django.db import models

class OpeningBalance(models.Model):
    sl_no = models.AutoField(primary_key=True)
    financial_year = models.PositiveIntegerField()
    date = models.DateField()
    account_name = models.CharField(max_length=100)
    sub_type = models.CharField(max_length=50)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    action = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.account_name} - {self.financial_year}"

    class Meta:
        verbose_name = "Opening Balance"
        verbose_name_plural = "Opening Balances"