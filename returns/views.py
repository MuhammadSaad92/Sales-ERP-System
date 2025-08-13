from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Return, ReturnItem
from customer.models import Customer
from supplier.models import Supplier
from sale.models import Sale, SaleItem
from purchase.models import Purchase, PurchaseItem
from product.models import Product
from django.utils import timezone
from django.http import JsonResponse

def customer_return_list(request):
    returns = Return.objects.filter(return_type='customer').select_related('customer', 'sale')
    context = {
        'returns': returns,
        'title': 'Customer Returns List'
    }
    return render(request, 'customer_return_list.html', context)

def supplier_return_list(request):
    returns = Return.objects.filter(return_type='supplier').select_related('supplier', 'purchase')
    context = {
        'returns': returns,
        'title': 'Supplier Returns List'
    }
    return render(request, 'supplier_return_list.html', context)

def add_return(request):
    if request.method == 'POST':
        invoice_no = request.POST.get('invoice_no')
        return_type = request.POST.get('return_type')
        customer_id = request.POST.get('customer_id') if return_type == 'customer' else None
        supplier_id = request.POST.get('supplier_id') if return_type == 'supplier' else None
        sale_id = request.POST.get('sale_id') if return_type == 'customer' else None
        purchase_id = request.POST.get('purchase_id') if return_type == 'supplier' else None
        date = request.POST.get('date')
        total_amount = request.POST.get('total_amount')
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')

        # Validation
        if not all([invoice_no, return_type, date, total_amount]):
            messages.error(request, 'All required fields must be filled.')
            return redirect('returns:add_return')

        try:
            if return_type == 'customer' and sale_id:
                sale = Sale.objects.filter(id=sale_id).first()
                if not sale:
                    messages.error(request, 'Invalid sale selected.')
                    return redirect('returns:add_return')
                
                sale_items = SaleItem.objects.filter(sale_id=sale_id).values_list('product_id', 'quantity')
                sale_products = {item[0]: item[1] for item in sale_items}
                
            elif return_type == 'supplier' and purchase_id:
                purchase = Purchase.objects.filter(id=purchase_id).first()
                if not purchase:
                    messages.error(request, 'Invalid purchase selected.')
                    return redirect('returns:add_return')
                
                purchase_items = PurchaseItem.objects.filter(purchase_id=purchase_id).values_list('product_id', 'quantity')
                purchase_products = {item[0]: item[1] for item in purchase_items}
                
            else:
                messages.error(request, 'Sale or purchase selection required.')
                return redirect('returns:add_return')

            # Validate return items
            for prod_id, qty, price in zip(product_ids, quantities, unit_prices):
                if not (prod_id and qty and price):
                    messages.error(request, 'All item fields must be filled.')
                    return redirect('returns:add_return')
                
                qty = float(qty)
                if return_type == 'customer' and int(prod_id) not in sale_products:
                    messages.error(request, f'Product ID {prod_id} is not part of the selected sale.')
                    return redirect('returns:add_return')
                elif return_type == 'supplier' and int(prod_id) not in purchase_products:
                    messages.error(request, f'Product ID {prod_id} is not part of the selected purchase.')
                    return redirect('returns:add_return')

            # Create Return instance
            return_obj = Return.objects.create(
                invoice_no=invoice_no,
                return_type=return_type,
                customer_id=customer_id,
                supplier_id=supplier_id,
                sale_id=sale_id,
                purchase_id=purchase_id,
                date=date,
                total_amount=total_amount
            )

            # Create ReturnItem instances
            for prod_id, qty, price in zip(product_ids, quantities, unit_prices):
                ReturnItem.objects.create(
                    return_record=return_obj,
                    product_id=prod_id,
                    quantity=float(qty),
                    unit_price=float(price)
                )

            messages.success(request, 'Return added successfully!')
            return redirect('returns:customer_return_list' if return_type == 'customer' else 'returns:supplier_return_list')
            
        except Exception as e:
            messages.error(request, f'Error adding return: {str(e)}')
            return redirect('returns:add_return')

    # GET request - show form
    context = {
        'customers': Customer.objects.all(),
        'suppliers': Supplier.objects.all(),
        'sales': Sale.objects.select_related('customer').all(),
        'purchases': Purchase.objects.select_related('supplier').all(),
        'products': Product.objects.all(),
    }
    return render(request, 'add_return.html', context)

def return_details(request, invoice_no):
    return_obj = get_object_or_404(Return, invoice_no=invoice_no)
    items = return_obj.items.all().select_related('product')
    
    # Calculate totals for each item
    items_with_totals = []
    for item in items:
        item.total = float(item.quantity) * float(item.unit_price)
        items_with_totals.append(item)
    
    context = {
        'return': return_obj,
        'items': items_with_totals,
        'title': f'{return_obj.return_type.capitalize()} Return Details - {invoice_no}'
    }
    return render(request, 'return_details.html', context)

def get_sale_products(request, sale_id):
    sale_items = SaleItem.objects.filter(sale_id=sale_id).select_related('product')
    products = [{
        'id': item.product.id,
        'name': item.product.name,
        'sale_price': str(item.product.sale_price),
        'quantity': str(item.quantity)
    } for item in sale_items if item.product]
    return JsonResponse({'products': products})

def get_purchase_products(request, purchase_id):
    purchase_items = PurchaseItem.objects.filter(purchase_id=purchase_id).select_related('product')
    products = [{
        'id': item.product.id,
        'name': item.product.name,
        'sale_price': str(item.product.sale_price),
        'quantity': str(item.quantity)
    } for item in purchase_items if item.product]
    return JsonResponse({'products': products})