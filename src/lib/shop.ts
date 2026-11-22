// Which Stripe mode the shop page links to. 'test' until launch (NOW.md), when it becomes 'live'
// and every listed product needs a live Payment Link (python3 tools/shop/sync.py --live).
export const SHOP_MODE: 'test' | 'live' = 'live';
