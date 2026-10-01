// The shop's order Worker (docs/SHOP.md).
//
// POST /stripe: Stripe's webhook for completed Checkout Sessions. After checking Stripe's
// signature, it reads the session's line items. Printed items (fulfillment "gelato") become one
// Gelato order with the Checkout Session ID as its orderReferenceId; it searches for that ID
// first, so Stripe's retries never place an order twice. Self-shipped items need nothing here:
// Stripe's payment email tells RJ.
//
// Gelato orders are always created as drafts. RJ confirms each one in the Gelato dashboard, which
// is when Gelato charges. Turning that off is a code change, on RJ's say-so (docs/CHARGES.md).

const ORDER_TYPE = 'draft';
const STRIPE_VERSION = '2026-08-26.dahlia';
const TOLERANCE_SECONDS = 300;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== '/stripe' || request.method !== 'POST') {
      return new Response('Not found', { status: 404 });
    }
    const body = await request.text();
    const secrets = [env.STRIPE_WEBHOOK_SECRET_TEST, env.STRIPE_WEBHOOK_SECRET_LIVE].filter(Boolean);
    if (!(await verified(body, request.headers.get('stripe-signature'), secrets))) {
      return new Response('Bad signature', { status: 400 });
    }
    const event = JSON.parse(body);
    const session = event.data.object;
    const done = (note) => {
      console.log(JSON.stringify({ event: event.id, session: session.id, livemode: event.livemode, note }));
      return new Response(note);
    };
    if (!['checkout.session.completed', 'checkout.session.async_payment_succeeded'].includes(event.type)) {
      return done(`ignored ${event.type}`);
    }
    if (session.payment_status !== 'paid') return done('not paid yet');

    try {
      return done(await fulfil(session, event.livemode, env));
    } catch (err) {
      // A 500 makes Stripe retry, for up to three days, and shows the failure in its dashboard.
      console.error(JSON.stringify({ event: event.id, session: session.id, error: String(err.message || err) }));
      return new Response('Order failed; Stripe will retry', { status: 500 });
    }
  },
};

async function fulfil(session, livemode, env) {
  const stripeKey = livemode ? env.STRIPE_SECRET_KEY_LIVE : env.STRIPE_SECRET_KEY_TEST;
  const gelatoKey = livemode ? env.GELATO_API_KEY_LIVE : env.GELATO_API_KEY_TEST;
  if (!stripeKey || !gelatoKey) throw new Error(`no keys for ${livemode ? 'live' : 'test'} mode`);

  const lines = await stripe(stripeKey,
    `checkout/sessions/${session.id}/line_items?limit=100&expand[]=data.price.product`);
  const choices = Object.fromEntries((session.custom_fields || [])
    .map((f) => [f.key, f.dropdown?.value]));

  const items = [];
  for (const line of lines.data) {
    const md = line.price.product.metadata || {};
    if (md.fulfillment !== 'gelato') continue;
    const productUid = md.option ? md[`uid_${choices[md.option]}`] : md.uid;
    if (!productUid) throw new Error(`no Gelato product for ${md.slug} (${md.option}: ${choices[md.option]})`);
    const files = Object.entries(md)
      .filter(([k]) => k.startsWith('file_'))
      .map(([k, url]) => ({ type: k.slice(5), url }));
    items.push({ itemReferenceId: line.id, productUid, files, quantity: line.quantity });
  }
  if (!items.length) return 'nothing for Gelato';

  const found = await gelato(gelatoKey, 'orders:search', { orderReferenceId: session.id, limit: 1 });
  if (found.orders?.length) return `Gelato order exists: ${found.orders[0].id}`;

  const ship = session.collected_information?.shipping_details || session.shipping_details;
  if (!ship?.address) throw new Error('no shipping address on the session');
  const name = ship.name.trim();
  const cut = name.lastIndexOf(' ');
  const a = ship.address;
  const order = await gelato(gelatoKey, 'orders', {
    orderType: ORDER_TYPE,
    orderReferenceId: session.id,
    customerReferenceId: session.customer || session.customer_details.email,
    currency: 'USD',
    items,
    shippingAddress: {
      firstName: (cut > 0 ? name.slice(0, cut) : name).slice(0, 25),
      lastName: (cut > 0 ? name.slice(cut + 1) : '-').slice(0, 25),
      addressLine1: a.line1,
      addressLine2: a.line2 || undefined,
      city: a.city,
      postCode: a.postal_code,
      state: a.state,
      country: a.country,
      email: session.customer_details.email,
      phone: session.customer_details.phone || undefined,
    },
    metadata: [{ key: 'stripeMode', value: livemode ? 'live' : 'test' }],
  });
  return `Gelato ${ORDER_TYPE} ${order.id}`;
}

async function stripe(key, path) {
  const res = await fetch(`https://api.stripe.com/v1/${path}`, {
    headers: { Authorization: `Bearer ${key}`, 'Stripe-Version': STRIPE_VERSION },
  });
  const json = await res.json();
  if (!res.ok) throw new Error(`Stripe ${res.status}: ${json.error?.message}`);
  return json;
}

async function gelato(key, path, body) {
  const res = await fetch(`https://order.gelatoapis.com/v4/${path}`, {
    method: 'POST',
    headers: { 'X-API-KEY': key, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`Gelato ${path} ${res.status}: ${text.slice(0, 500)}`);
  return JSON.parse(text);
}

// Stripe-Signature: t=<unix time>,v1=<hex HMAC-SHA256 of "<t>.<body>">[,v1=...]
async function verified(body, header, secrets) {
  if (!header) return false;
  const parts = header.split(',').map((p) => p.split('='));
  const t = parts.find(([k]) => k === 't')?.[1];
  const sigs = parts.filter(([k]) => k === 'v1').map(([, v]) => v);
  if (!t || !sigs.length || Math.abs(Date.now() / 1000 - Number(t)) > TOLERANCE_SECONDS) return false;
  const enc = new TextEncoder();
  for (const secret of secrets) {
    const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const mac = new Uint8Array(await crypto.subtle.sign('HMAC', key, enc.encode(`${t}.${body}`)));
    const hex = [...mac].map((b) => b.toString(16).padStart(2, '0')).join('');
    if (sigs.some((s) => s.length === hex.length && crypto.subtle.timingSafeEqual(enc.encode(s), enc.encode(hex)))) {
      return true;
    }
  }
  return false;
}
