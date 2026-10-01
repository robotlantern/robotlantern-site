# Sales tax

Worked out 2026-10-01 for RJ, who files his own taxes. Not legal or tax advice; it's the plain
reading of the rules for a West Virginia seller at small volume. Recheck the thresholds once a
year, or when Stripe Tax says one is close.

## What applies

- **West Virginia: collect on every order shipped to a West Virginia address.** RJ is here, so
  the state taxes his sales there from the first one. The rate is 6% plus any city sales tax
  (0 to 1%), set by where the order is delivered.
- **Every other state: nothing yet.** A seller outside a state only has to collect its tax after
  passing that state's threshold: about $100,000 a year in sales into it in most states (some
  also count 200 orders, and a few are higher). Robot Lantern is far below all of them.
- **Abroad:** not shipping there (RJ, 2026-10-01: US only).

## How the shop collects it

**Stripe Tax** (decided 2026-10-01). Payment Links can't take a hand-set tax rate, only Stripe
Tax, and West Virginia's rate changes from city to city, which Stripe Tax handles from the
address.

- **Cost:** 0.5% of each sale **into a state where Robot Lantern is registered**, which means
  only West Virginia orders. Other orders cost nothing extra and carry no tax.
- **Setup** (an agent does this in the shop build): the head office address, prices that
  exclude tax, a tax code per product, `automatic_tax` on every Payment Link, and a West
  Virginia registration in Stripe Tax.
- **Thresholds:** Stripe Tax watches sales into each state and warns before one gets close.

## Before the first sale

1. **A West Virginia Business Registration Certificate**, which is what makes Robot Lantern
   registered to collect West Virginia sales tax. RJ checks whether the LLC already has one (in
   MyTaxes, `mytaxes.wvtax.gov`, or with the LLC's papers). If it doesn't, apply in MyTaxes.
   The application likely asks for the LLC's EIN, so the EIN comes first.
2. **The EIN.** The IRS's online application only works during its hours on weekdays. Form
   SS-4 by fax or mail is the fallback when the website won't cooperate.
3. **Stripe's business details.** The account is a sole proprietorship for now (no EIN yet).
   Once the EIN arrives, update it to Robot Lantern LLC, so the seller on the receipts, the tax
   registration and the site all match.
4. **Turn on West Virginia in Stripe Tax** with the registration's start date. Until then,
   Stripe Tax calculates but collects nothing.

## After it's running

- **Filing:** West Virginia sales tax returns go through MyTaxes, on the schedule the state
  assigns at registration (based on expected volume). Stripe Tax's reports give the totals per
  period and per city.
- **Gelato:** Gelato adds sales tax to its own charges unless it has a resale certificate. Once
  registered, give Gelato one (West Virginia is a Streamlined Sales Tax member, so its
  multistate certificate covers the Gelato orders shipped to most states).

## Sources (checked 2026-10-01)

- [Stripe Tax pricing](https://support.stripe.com/questions/understanding-stripe-tax-pricing)
- [West Virginia sales tax guide (Avalara)](https://www.avalara.com/us/en/taxrates/state-rates/west-virginia/west-virginia-sales-tax-guide.html)
- [Economic nexus by state (Sales Tax Institute)](https://www.salestaxinstitute.com/resources/economic-nexus-state-guide)
