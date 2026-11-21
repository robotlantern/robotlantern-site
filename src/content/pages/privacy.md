---
title: Privacy
description: What robotlantern.com collects (next to nothing), exactly what happens to a photo you order an ornament with and when it's deleted, and the privacy policy for the Robot Lantern Uploader.
updated: 2026-11-20
---

Robot Lantern LLC, a West Virginia company, runs robotlantern.com. This page says what happens to information about you when you use the site, email
us or order something. If anything here is unclear, write to
[admin@robotlantern.com](mailto:admin@robotlantern.com).

## The short version

The site doesn't track you. It has no accounts, comments, analytics, ads, cookies or third-party
scripts. If you order an ornament from a photo, the photo goes to OpenAI, which makes the drawing,
and to our order service, which keeps it until 60 days after your order ships. Slant 3D, which
prints and ships the ornament, never gets the photo. Stripe takes your payment. We don't sell
personal information, and we don't share it for advertising.

## Reading the site

The pages load their text, images, fonts and scripts only from robotlantern.com and make no
requests to other sites. The interactive pages under Builds, including "The Sky, Unprojected",
work the same way, and so does the ornament's page: it talks only to our own order service, and
paying is the one step that takes you to another site, Stripe's. Nothing is saved in your browser.

## Ordering an ornament from a photo

**In your browser.** When you add a photo, your browser turns it the right way up and you crop it
to a square. Your browser then makes a fresh copy of the square, 1024 pixels across, without the
hidden details cameras add, such as where the photo was taken. Nothing has left your phone or
computer yet.

**When you press "Make my drawing".** The cropped square goes to our order service, which runs on
Cloudflare. It sends the photo to **OpenAI**, whose image model redraws it as a two-colour stencil,
and keeps the photo and the drawing. "Try again" sends the same photo to OpenAI for another
drawing, up to three in all. OpenAI handles the photo under its
[API data policy](https://developers.openai.com/api/docs/guides/your-data): it doesn't train its models
on it, and it keeps it, and the drawing, for up to 30 days to watch for abuse, or longer if the law
requires. If its safety checks flag an image, it may keep that image for review.

**When you order.** The page sends us your choices (colours, the name tag's text and font, how
many) and the preview you saw. Stripe takes the payment and the shipping address. Then:

- An AI agent (Claude, made by Anthropic) builds the two print files from your drawing and checks
  them against your preview. Anthropic processes what the agent works on, under its own terms.
- The print files go to **Slant 3D**, which prints the ornament and ships it to you. Slant gets
  the print files, your name and your shipping address, but not your photo or your email address.
  It handles them under its own privacy policy.
- RJ approves each order before it's printed, and he or an agent looks at your photo only if
  something needs checking.

We never post your photo, or use it to advertise anything, without your written OK.

**How long we keep it.**

- **If you don't order,** your photo and its drawings delete themselves after two days.
- **Your photo, its drawings and the print files** are deleted 60 days after your order ships, or
  after it's cancelled.
- **Your preview and the build report** (a short record of how the print files were made and
  checked) are kept 180 days after your order ships, then deleted. They show what you approved,
  in case a payment is disputed: a card dispute can come up to about four months after delivery.
- **A record of the order**, with no photos or drawings, is kept for seven years, for tax: what
  you bought, your choices (including the tag's text), what you paid and the dates.
- If RJ runs an order by hand on his own computer, the copy there is deleted on the same
  schedule.

**If you or your AI assistant make the drawing.** If you upload your own drawing ("I have my own
drawing"), we receive only the drawing, never your photo, and nothing goes to OpenAI. Your
assistant's provider handles the photo under its own terms. We keep the drawing like any other:
two days if you don't order, and 60 days after your order ships if you do.

**Ready-made designs** need no photo at all.

**Limits on drawings.** To stop anyone running up our drawing bill, the order service counts how
many drawings each visitor makes in a day. It counts them under a scrambled code made from your IP
address with a key that changes every day, keeps the count for one day, and never writes it to a
log. OpenAI gets the same day's code with each drawing, to help it spot abuse, but not your IP
address.

**Photos of people and children.** Only send a photo of someone if they've said yes, and for a
child, if you're their parent or guardian or have one's OK. Photos of people are handled like every
other photo, under the rules above.

## Paying with Stripe

When you check out, you leave robotlantern.com for a page run by Stripe.

- **Stripe** collects what it needs to take your payment: your name, email, shipping address and
  card details. Your card details go straight to Stripe, which meets the card industry's security
  standard (PCI DSS). They never reach our site, and we never see your card number. Stripe handles
  all this under its [privacy policy](https://stripe.com/privacy), and it also uses some of it for
  its own purposes, such as preventing fraud. It uses your email to send your receipt.
- **We** see the order in Stripe: your name, email, shipping address, what you bought and what you
  paid, with the card's brand and last four digits. We use it to make and ship your order, answer
  questions about it, handle refunds and keep the records the law requires. Our order service
  doesn't copy your name, email or address into its own records. It passes your name and address
  from Stripe to Slant for shipping.

## Shipping

Slant 3D ships your order with a carrier, which gets your name and address and handles them under
its own privacy policy. When your order ships, an agent reads your name and email from Stripe and
drafts an email to you with the tracking link, in our mailbox. RJ sends it.

## The web host

The site is hosted by Cloudflare. Like any web host, it records technical details of each visit, such as your IP
address, your browser and device type, the page you asked for and when. It uses these records
to deliver the site and keep it secure, and it keeps them as its own privacy statement
describes. We don't receive those records for the pages you read. At most, the host shows us
totals, such as how many requests a page got.

Our order service runs on Cloudflare too. Its logs hold order numbers, never what's in an order,
and Cloudflare shows them to us for three days, so we can find and fix problems.

See the [Cloudflare Privacy Policy](https://www.cloudflare.com/privacypolicy/).

## Email

If you email [help@robotlantern.com](mailto:help@robotlantern.com) or
[admin@robotlantern.com](mailto:admin@robotlantern.com), we get your address and whatever you
write. We use it to reply, and we don't add you to any list. If you write to
[signup@robotlantern.com](mailto:signup@robotlantern.com) to hear when a product is ready, we use
your address only to tell you. We don't send newsletters or other marketing email. Messages stay in
the mailbox, which is hosted by Google Workspace, until we delete them or you ask us to. If you
email us a photo for an order, we delete it from the mailbox on the same schedule as the order's
other photos.

## Links to other sites

Essays and chats link to other sites, such as Wikipedia, Reddit and NASA. Once you follow a
link, that site's own privacy policy applies.

## Children

This site isn't aimed at children, and we don't knowingly collect information from anyone under
13. If you think a child has sent us personal information, tell us and we'll delete it. Photos of
children that grown-ups order with are covered under "Ordering an ornament from a photo", above.

## Your choices and rights

You can ask us what we hold about you, ask for a copy, and ask us to correct or delete it.
Email [admin@robotlantern.com](mailto:admin@robotlantern.com), or
[help@robotlantern.com](mailto:help@robotlantern.com) about an order, and we'll answer within 30
days. You can ask us to delete your photo before the 60 days are up. If your order hasn't gone to
print yet, that cancels it, with a full refund. We may need to keep some order records for tax and
accounting, and we'll tell you if so. We can't delete what OpenAI keeps for its 30 days. For data
Stripe holds for its own purposes, use
[Stripe's privacy center](https://stripe.com/legal/privacy-center).

If you're in the EU or UK: we use order details to carry out your purchase and to meet legal
record-keeping duties, and we use emails to reply to you. We and our providers process data in
the United States and other countries. You can also complain to your local data protection
authority.

## Changes

If this policy changes, the date at the top changes with it.

## Robot Lantern Uploader

Robot Lantern Uploader (the "App") is a private tool that Robot Lantern LLC uses to upload videos
to its own YouTube channels. It isn't offered to anyone else. **The App uses YouTube API
Services**, so using it means agreeing to the [YouTube Terms of Service](https://www.youtube.com/t/terms),
and Google's handling of data is covered by the
[Google Privacy Policy](http://www.google.com/policies/privacy).

The App asks Google for one permission, uploading videos
(`https://www.googleapis.com/auth/youtube.upload`), and keeps the sign-in token on its operator's
own computers. It doesn't sell or share Google user data, or use it for advertising. Access can be
revoked at any time in [Google's security settings](https://security.google.com/settings/security/permissions).
Questions: [admin@robotlantern.com](mailto:admin@robotlantern.com).
