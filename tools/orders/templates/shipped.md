<!--
The shipping email, drafted by rl-daily for each newly shipped order (docs/PRODUCTION.md, "The daily run").
It's a Gmail draft to the customer that RJ sends himself. Fill the {braces} and send nothing.

- {first_name}: the first word of the name from /api/orders/<id>/contact. If it's empty or looks like a
  business, use "Hello," alone.
- {order_id}, {tracking_url}: from the order record.
- The code paragraph: copy shop.json's "promotion" (code, off, until). Leave the paragraph out after its
  "until" date, or if shop.json has no promotion.
- Nothing else from the order (no photo, drawing, tag text, address) goes in the email.
-->
Subject: Your Robot Lantern order is on its way

Hello {first_name},

Good news: your order {order_id} has shipped from Slant 3D. You can follow the package here:

{tracking_url}

If anything arrives broken, or doesn't match the preview you approved, write to
help@robotlantern.com with a photo, and we'll make it again for free or refund you, whichever you'd
rather.

Ordering another? Use the code AGAIN on the checkout page for $3 off a second order, until December
10. Share it with anyone you like.

Thank you for ordering,
RJ
Robot Lantern
https://robotlantern.com
