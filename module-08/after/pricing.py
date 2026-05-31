"""Order pricing — deliberately messy. Refactor in Module 8.

Computes the final price of an order with discounts, taxes, and shipping.
"""

_TAX_RATES = {'US': 0.07, 'GB': 0.20, 'DE': 0.19, 'FR': 0.20}


def calc(items, country, customer):
    subtotal = 0
    for item in items:
        if item is None or len(item) != 3:
            continue
        _, qty, price = item
        if qty <= 0 or price <= 0:
            continue
        line = qty * price
        if customer is not None:
            if customer.get('vip') is True:
                line *= 0.9
            elif customer.get('coupon') == 'SAVE10':
                line *= 0.9
            elif customer.get('coupon') == 'SAVE20':
                line *= 0.8
        subtotal += line

    tax = subtotal * _TAX_RATES.get(country, 0.10)

    if subtotal < 50:
        ship = 9.99
    elif subtotal < 200:
        ship = 4.99
    else:
        ship = 0.0

    return round(subtotal + tax + ship, 2)
