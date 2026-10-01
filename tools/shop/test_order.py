"""Buy a product in Stripe's sandbox without a browser, to test the order Worker (docs/SHOP.md).

    python3 tools/shop/test_order.py tools/shop/fixtures/test-mug/shop.json

It makes a Checkout Session like the product's Payment Link, ships it to the West Virginia
State Capitol (so sales tax shows), and pays with Stripe's test card token. Stripe then calls
the Worker as it would for a real order. Sandbox only: it refuses a live key. Printed products
leave a Gelato draft, which costs nothing; delete it afterwards (docs/SHOP.md).

This uses the endpoints the Stripe CLI's `stripe trigger` uses to complete a session. They're
not in Stripe's public reference, so if they change, test through the Payment Link instead.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sync  # noqa: E402

ADDRESS = {'line1': '1900 Kanawha Blvd E', 'city': 'Charleston', 'state': 'WV',
           'postal_code': '25305', 'country': 'US'}


def main():
    path = Path(sys.argv[1])
    p = json.loads(path.read_text())
    ids = p['stripe']['test']
    if 'options' in p:
        # The confirm endpoint below won't take a custom field's value; test a product with a
        # size choice through its Payment Link.
        raise SystemExit('products with options are tested through their Payment Link')
    key = sync.secret('STRIPE_SECRET_KEY_TEST')
    if not key.startswith('sk_test_'):
        raise SystemExit('not a test key')
    stripe = sync.Stripe(key)

    session = {
        'mode': 'payment', 'success_url': 'https://example.com/',
        'line_items': [{'price': ids['price'], 'quantity': 1}],
        'shipping_address_collection': {'allowed_countries': ['US']},
        'shipping_options': [{'shipping_rate': ids['shippingRate']}],
        'automatic_tax': {'enabled': True},
        'customer_email': 'test@example.com',
    }
    cs = stripe('POST', 'checkout/sessions', session)

    page = stripe('POST', f'payment_pages/{cs["id"]}', {'tax_region': ADDRESS})
    card = stripe('POST', 'payment_methods', {
        'type': 'card', 'card': {'token': 'tok_visa'},
        'billing_details': {'name': 'Test Buyer', 'email': 'test@example.com'}})
    done = stripe('POST', f'payment_pages/{cs["id"]}/confirm', {
        'payment_method': card['id'], 'expected_amount': page['total_summary']['due'],
        'shipping': {'name': 'Test Buyer', 'address': ADDRESS}})
    paid = stripe('GET', f'checkout/sessions/{cs["id"]}')
    print(f'{cs["id"]}: {done.get("payment_status")}, ${paid["amount_total"] / 100:.2f} '
          f'(tax ${paid["total_details"]["amount_tax"] / 100:.2f})')


if __name__ == '__main__':
    main()
