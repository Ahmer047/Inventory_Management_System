
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Sale, Products, Stock
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction


def create_sale(request):
    # Clear the cart when the page is loaded
    if 'cart_items' in request.session:
        del request.session['cart_items']
        request.session.modified = True

    products = Products.objects.all()
    stocks = Stock.objects.all()  # Fetch all stock items
    cart_items = request.session.get('cart_items', [])
    
    total_amount = sum(float(item['total']) for item in cart_items)
    
    context = {
        'products': products,
        'stocks': stocks,  # Add stocks to the context
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    return render(request, 'admin/pos.html', context)


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            
            # Changed from id to product_ID
            product = get_object_or_404(Products, product_ID=product_id)
            stock = Stock.objects.filter(product_ID=product).first()
            
            if not stock:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No stock found for this product'
                })
            
            # Check if enough stock is available
            if stock.available_stock < quantity:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Insufficient stock. Only {stock.available_stock} available.'
                })
            
            total = float(stock.current_sell_price) * quantity
            item = {
                'product_id': product_id,  # Keep this as product_id for consistency with frontend
                'product_name': stock.product_name,
                'quantity': quantity,
                'price': float(stock.current_sell_price),
                'total': total
            }
            
            cart_items = request.session.get('cart_items', [])
            cart_items.append(item)
            request.session['cart_items'] = cart_items
            
            return JsonResponse({
                'status': 'success',
                'item': item
            })
            
        except Products.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Product not found'
            })
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid quantity'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })



@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            index = int(data.get('index', -1))
            
            cart_items = request.session.get('cart_items', [])
            if 0 <= index < len(cart_items):
                removed_item = cart_items.pop(index)
                request.session['cart_items'] = cart_items
                request.session.modified = True
                return JsonResponse({
                    'status': 'success',
                    'removedItemTotal': removed_item['total']
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid cart item index'
                })
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid index value'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_method = data.get('payment_method', 'Cash')
        cart_items = request.session.get('cart_items', [])
        
        if not cart_items:
            return JsonResponse({
                'status': 'error',
                'message': 'Cart is empty'
            })
        
        try:
            with transaction.atomic():
                # Generate sale ID
                from datetime import datetime
                sale_id = datetime.now().strftime('%Y%m%d%H%M%S')
                
                for item in cart_items:
                    # Changed from id to product_ID
                    product = Products.objects.get(product_ID=item['product_id'])
                    
                    # Get and update stock
                    stock = Stock.objects.select_for_update().get(product_ID=product)
                    if stock.available_stock < item['quantity']:
                        raise ValueError(f'Insufficient stock for {product.product_name}')
                    
                    stock.available_stock -= item['quantity']
                    stock.save()
                    
                    # Create sale record
                    Sale.objects.create(
                        sale_id=sale_id,
                        product_ID=product,
                        quantity=item['quantity'],
                        payment_method=payment_method
                    )
                
                # Clear the cart
                request.session['cart_items'] = []
                request.session.modified = True
                
                return JsonResponse({
                    'status': 'success',
                    'sale_id': sale_id
                })
                
        except Products.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'One or more products not found'
            })
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error processing checkout: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })