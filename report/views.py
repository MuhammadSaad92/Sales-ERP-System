from django.shortcuts import render
from django.utils import timezone
from sale.models import Sale, SaleItem
from product.models import Product
from customer.models import Customer
from supplier.models import Supplier
from purchase.models import Purchase, PurchaseItem 
import datetime
from django.db.models import Sum

def closing_report(request):
    # Fetch sales and aggregate by date for Cash In
    sales = Sale.objects.values('date', 'paid_amount')
    sales_by_date = {}
    for sale in sales:
        if sale['date']:
            sale_date = sale['date'].date() if hasattr(sale['date'], 'date') else sale['date']
            sales_by_date[sale_date] = sales_by_date.get(sale_date, 0) + (sale['paid_amount'] or 0)

    # Fetch purchases and aggregate by date for Cash Out
    purchases = Purchase.objects.values('purchase_date', 'grand_total')
    purchases_by_date = {}
    for purchase in purchases:
        if purchase['purchase_date']:
            purchase_date = purchase['purchase_date'].date() if hasattr(purchase['purchase_date'], 'date') else purchase['purchase_date']
            purchases_by_date[purchase_date] = purchases_by_date.get(purchase_date, 0) + (purchase['grand_total'] or 0)

    # Combine and process data
    report_data = []
    cumulative_balance = 0
    sum_of_balances = 0
    
    # Get and sort unique dates
    dates = set(sales_by_date.keys()) | set(purchases_by_date.keys())
    sorted_dates = sorted([
        date if isinstance(date, datetime.date) else date.date() 
        for date in dates 
        if date is not None
    ])

    # Prepare report data
    for idx, date_item in enumerate(sorted_dates, start=1):
        cash_in = sales_by_date.get(date_item, 0)
        cash_out = purchases_by_date.get(date_item, 0)
        daily_balance = cash_in - cash_out
        cumulative_balance += daily_balance
        sum_of_balances += daily_balance
        
        report_data.append({
            'sl': idx,
            'date': date_item,
            'cash_in': cash_in,
            'cash_out': cash_out,
            'balance': cumulative_balance,
            'daily_balance': daily_balance
        })

    context = {
        'report_title': 'Closing Report',
        'report_data': report_data,
        'report_date': timezone.now().date(),
        'total_balance': sum_of_balances,
        'cumulative_balance': cumulative_balance
    }
    return render(request, 'closing_report.html', context)

def sales_report_product_wise(request):
    from_date_str = request.GET.get('fromDate')
    to_date_str = request.GET.get('toDate')
    
    today = timezone.now().date()
    try:
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    except (ValueError, TypeError):
        from_date = None
    try:
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except (ValueError, TypeError):
        to_date = None

    if from_date and to_date and from_date > to_date:
        from_date, to_date = to_date, from_date

    if from_date and to_date:
        sale_items = SaleItem.objects.filter(
            sale__date__date__range=[from_date, to_date]
        ).select_related('sale__customer', 'product')
        report_title = f"Sales Report ({from_date} to {to_date})"
    else:
        sale_items = SaleItem.objects.all().select_related('sale__customer', 'product')
        report_title = "All Sales"

    total_sales = sum(item.total or 0 for item in sale_items)

    context = {
        'report_title': report_title,
        'sales': [
            {
                'sales_date': item.sale.date,
                'product_name': item.product.name,
                'product_model': item.product.model,
                'invoice_no': item.sale.id,
                'customer_name': item.sale.customer.customer_name,
                'rate': item.rate,
                'quantity': item.quantity,
                'total_amount': item.total,
            } for item in sale_items
        ],
        'report_date': timezone.now().date(),
        'total_sales': total_sales,
        'from_date_str': from_date_str,
        'to_date_str': to_date_str,
    }
    return render(request, 'sales_report_product_wise.html', context)

def purchase_report_product_wise(request):
    from_date_str = request.GET.get('fromDate')
    to_date_str = request.GET.get('toDate')
    
    today = timezone.now().date()
    try:
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    except (ValueError, TypeError):
        from_date = None
    try:
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except (ValueError, TypeError):
        to_date = None

    if from_date and to_date and from_date > to_date:
        from_date, to_date = to_date, from_date

    if from_date and to_date:
        purchase_items = PurchaseItem.objects.filter(
            purchase__purchase_date__range=[from_date, to_date]
        ).select_related('purchase__supplier', 'product')
        report_title = f"Purchase Report ({from_date} to {to_date})"
    else:
        purchase_items = PurchaseItem.objects.all().select_related('purchase__supplier', 'product')
        report_title = "All Purchases"

    total_purchases = sum(item.total or 0 for item in purchase_items)

    context = {
        'report_title': report_title,
        'purchases': [
            {
                'purchase_date': item.purchase.purchase_date,
                'product_name': item.product.name if item.product else item.item_name,
                'product_model': item.product.model if item.product else '-',
                'invoice_no': item.purchase.challan_no,
                'supplier_name': item.purchase.supplier.supplier_name,
                'rate': item.rate,
                'quantity': item.quantity,
                'total_amount': item.total,
            } for item in purchase_items
        ],
        'report_date': timezone.now().date(),
        'total_purchases': total_purchases,
        'from_date_str': from_date_str,
        'to_date_str': to_date_str,
    }
    return render(request, 'purchase_report_product_wise.html', context)

def profit_report(request):
    from_date_str = request.GET.get('fromDate')
    to_date_str = request.GET.get('toDate')
    
    try:
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    except (ValueError, TypeError):
        from_date = None
    try:
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except (ValueError, TypeError):
        to_date = None

    if from_date and to_date and from_date > to_date:
        from_date, to_date = to_date, from_date

    if from_date and to_date:
        sale_items = SaleItem.objects.filter(
            sale__date__date__range=[from_date, to_date]
        ).select_related('sale__customer', 'product')
        report_title = f"Profit Report ({from_date} to {to_date})"
    else:
        sale_items = SaleItem.objects.all().select_related('sale__customer', 'product')
        report_title = "All Profits"

    profit_data = []
    total_sale = 0
    total_cost = 0
    total_profit = 0

    for item in sale_items:
        cost_rate = item.product.cost_price or 0
        cost_total = cost_rate * item.quantity
        profit = item.total - cost_total

        profit_data.append({
            'sales_date': item.sale.date,
            'product_name': item.product.name,
            'product_model': item.product.model,
            'invoice_no': item.sale.id,
            'sale_rate': item.rate,
            'sale_quantity': item.quantity,
            'sale_total': item.total,
            'cost_rate': cost_rate,
            'cost_total': cost_total,
            'profit': profit,
        })

        total_sale += item.total or 0
        total_cost += cost_total
        total_profit += profit

    context = {
        'report_title': report_title,
        'profits': profit_data,
        'report_date': timezone.now().date(),
        'total_sale': total_sale,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'from_date_str': from_date_str,
        'to_date_str': to_date_str,
    }
    return render(request, 'profit_report.html', context)

def vat_tax_report(request):
    from_date_str = request.GET.get('fromDate')
    to_date_str = request.GET.get('toDate')
    
    try:
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    except (ValueError, TypeError):
        from_date = None
    try:
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except (ValueError, TypeError):
        to_date = None

    if from_date and to_date and from_date > to_date:
        from_date, to_date = to_date, from_date

    if from_date and to_date:
        sale_items = SaleItem.objects.filter(
            sale__date__date__range=[from_date, to_date]
        ).select_related('sale__customer')
        purchase_items = PurchaseItem.objects.filter(
            purchase__purchase_date__range=[from_date, to_date]
        ).select_related('purchase__supplier')
        report_title = f"VAT & Tax Report ({from_date} to {to_date})"
    else:
        sale_items = SaleItem.objects.all().select_related('sale__customer')
        purchase_items = PurchaseItem.objects.all().select_related('purchase__supplier')
        report_title = "All VAT & Taxes"

    vat_tax_data = []
    total_vat = 0
    total_tax = 0
    total_vat_tax = 0

    for item in sale_items:
        vat_value = item.vat_value or 0
        tax_value = item.discount_value or 0
        vat_tax_total = vat_value + tax_value
        vat_tax_data.append({
            'transaction_type': 'Sale',
            'date': item.sale.date,
            'invoice_no': item.sale.id,
            'party_name': item.sale.customer.customer_name,
            'vat_amount': vat_value,
            'tax_amount': tax_value,
            'vat_tax_total': vat_tax_total,
        })
        total_vat += vat_value
        total_tax += tax_value
        total_vat_tax += vat_tax_total

    for item in purchase_items:
        vat_value = item.vat_value or 0
        tax_value = item.discount_value or 0
        vat_tax_total = vat_value + tax_value
        vat_tax_data.append({
            'transaction_type': 'Purchase',
            'date': item.purchase.purchase_date,
            'invoice_no': item.purchase.challan_no,
            'party_name': item.purchase.supplier.supplier_name,
            'vat_amount': vat_value,
            'tax_amount': tax_value,
            'vat_tax_total': vat_tax_total,
        })
        total_vat += vat_value
        total_tax += tax_value
        total_vat_tax += vat_tax_total

    context = {
        'report_title': report_title,
        'vat_taxes': vat_tax_data,
        'report_date': timezone.now().date(),
        'total_vat': total_vat,
        'total_tax': total_tax,
        'total_vat_tax': total_vat_tax,
        'from_date_str': from_date_str,
        'to_date_str': to_date_str,
    }
    return render(request, 'vat_tax_report.html', context)

def shipping_cost_report(request):
    from_date_str = request.GET.get('fromDate')
    to_date_str = request.GET.get('toDate')
    
    try:
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    except (ValueError, TypeError):
        from_date = None
    try:
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except (ValueError, TypeError):
        to_date = None

    if from_date and to_date and from_date > to_date:
        from_date, to_date = to_date, from_date

    if from_date and to_date:
        sales = Sale.objects.filter(
            date__date__range=[from_date, to_date]
        ).select_related('customer')
        report_title = f"Shipping Cost Report ({from_date} to {to_date})"
    else:
        sales = Sale.objects.all().select_related('customer')
        report_title = "All Shipping Costs"

    total_shipping_cost = sum(sale.shipping_cost or 0 for sale in sales)

    context = {
        'report_title': report_title,
        'sales': [
            {
                'sale_date': sale.date,
                'invoice_no': sale.id,
                'customer_name': sale.customer.customer_name,
                'shipping_cost': sale.shipping_cost,
            } for sale in sales
        ],
        'report_date': timezone.now().date(),
        'total_shipping_cost': total_shipping_cost,
        'from_date_str': from_date_str,
        'to_date_str': to_date_str,
    }
    return render(request, 'shipping_cost_report.html', context)

def return_sale_report(request):
    from_date_str = request.GET.get('fromDate')
    to_date_str = request.GET.get('toDate')
    
    try:
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    except (ValueError, TypeError):
        from_date = None
    try:
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except (ValueError, TypeError):
        to_date = None

    if from_date and to_date and from_date > to_date:
        from_date, to_date = to_date, from_date

    if from_date and to_date:
        sale_items = SaleItem.objects.filter(
            sale__date__date__range=[from_date, to_date],
            total__lt=0
        ).select_related('sale__customer', 'product')
        report_title = f"Return Sale Report ({from_date} to {to_date})"
    else:
        sale_items = SaleItem.objects.filter(total__lt=0).select_related('sale__customer', 'product')
        report_title = "All Return Sales"

    total_returns = sum(item.total or 0 for item in sale_items)

    context = {
        'report_title': report_title,
        'returns': [
            {
                'return_date': item.sale.date,
                'product_name': item.product.name,
                'product_model': item.product.model,
                'invoice_no': item.sale.id,
                'customer_name': item.sale.customer.customer_name,
                'rate': item.rate,
                'quantity': item.quantity,
                'total_amount': item.total,
            } for item in sale_items
        ],
        'report_date': timezone.now().date(),
        'total_returns': total_returns,
        'from_date_str': from_date_str,
        'to_date_str': to_date_str,
    }
    return render(request, 'return_sale_report.html', context)

def return_purchase_report(request):
    from_date_str = request.GET.get('fromDate')
    to_date_str = request.GET.get('toDate')
    
    try:
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    except (ValueError, TypeError):
        from_date = None
    try:
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except (ValueError, TypeError):
        to_date = None

    if from_date and to_date and from_date > to_date:
        from_date, to_date = to_date, from_date

    if from_date and to_date:
        purchase_items = PurchaseItem.objects.filter(
            purchase__purchase_date__range=[from_date, to_date],
            total__lt=0
        ).select_related('purchase__supplier', 'product')
        report_title = f"Return Purchase Report ({from_date} to {to_date})"
    else:
        purchase_items = PurchaseItem.objects.filter(total__lt=0).select_related('purchase__supplier', 'product')
        report_title = "All Return Purchases"

    total_returns = sum(item.total or 0 for item in purchase_items)

    context = {
        'report_title': report_title,
        'returns': [
            {
                'return_date': item.purchase.purchase_date,
                'product_name': item.product.name if item.product else item.item_name,
                'product_model': item.product.model if item.product else '-',
                'invoice_no': item.purchase.challan_no,
                'supplier_name': item.purchase.supplier.supplier_name,
                'rate': item.rate,
                'quantity': item.quantity,
                'total_amount': item.total,
            } for item in purchase_items
        ],
        'report_date': timezone.now().date(),
        'total_returns': total_returns,
        'from_date_str': from_date_str,
        'to_date_str': to_date_str,
    }
    return render(request, 'return_purchase_report.html', context)