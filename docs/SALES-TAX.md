# Sales tax

Worked out 2026-10-01 for RJ, who files his own taxes. Not legal or tax advice; it's the plain
reading of the rules for a West Virginia seller at small volume. Recheck the thresholds once a
year, or when Stripe Tax says one is close. "Before the first sale" was rechecked 2026-11-12
against the IRS, Stripe and the state's own pages.

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

Rechecked 2026-11-12 against the IRS, Stripe and West Virginia's own pages and papers. RJ's copies of the
state letters, the Business4WV registration summary and receipt, and the MyTaxes filing receipts are in his
tax folder outside the repo (they carry his SSN and account numbers: never copy them in here).

1. **West Virginia registration: done.** The LLC was formed and registered with the Tax Department in one
   Business4WV filing on 2025-12-11 ($100 Articles + $30 Business Registration Fee). It used the owner's
   SSN, because there was no EIN: the state's own booklet says an LLC gives an FEIN, but the portal took the
   SSN. The certificate was issued 2025-12-16, with a monthly Combined Sales and Use Tax account. The filing
   lists "Service" and computer systems design as the primary activity, with electronic shopping as the
   secondary; the sales tax account exists either way.
2. **Monthly returns: caught up (submitted by 2026-11-12).** The state mails a blank return for every month from Dec 2025 on, and
   each is due by the 20th of the next month even with no sales. None were filed. On 2026-11-12 RJ phoned the
   Tax Department, which said there is no charge for unfiled returns reporting $0. The MyTaxes login was
   made by entering the owner's SSN with the ID type set to **FEIN** (the portal's "WV Tax ID Number" and
   other options did not work). RJ submitted Dec 2025 through Oct 2026 in MyTaxes and kept the
   confirmations (the December 2025 receipt is still to check). After that: one $0 return a month until the first sale, then real ones. Still to ask:
   whether quarterly or annual filing is allowed while sales are zero.
3. **The EIN: no longer a blocker.** Not needed for the state registration, Stripe or launch. It is still
   wanted for a business bank account and any hiring. Facts found:
   - **Online** at irs.gov/EIN: Mon–Fri 6 a.m.–1 a.m. ET, Sat 6 a.m.–9 p.m., Sun 6 p.m.–midnight; 15
     minutes idle restarts it; one EIN per responsible party per day.
   - **2026-11-12: the online tool stopped at Review & Submit with reference number 101.** Third-party
     guides say 101 means the IRS has an entity with the same or a very similar name, which may be an
     unrelated "Robot Lantern" somewhere. The registration shows no EIN was issued at formation. The screen
     tells you to phone 800-829-4933 (weekdays 7 a.m.–7 p.m. local); RJ's calls end after about 90 seconds
     with a "high call volume" message. The IRS no longer issues EINs by phone to US applicants except
     through that line's agents.
   - **Fax** Form SS-4 to 855-641-6935 with a return fax number that can receive faxes (not Google Voice):
     the EIN comes back in about 4 business days. Line 9a for a single-member LLC is "Other" and
     "disregarded entity". Mail takes about 4 weeks. A filled draft and a cover note for the 101 are in
     `.private/tax/`. 855-215-1627, which some guides list, is the territory and international number.
   - **Other routes:** the Taxpayer Advocate Service (877-777-4778) when the IRS process keeps failing.
4. **Stripe's business details.** The account is a sole proprietorship on RJ's SSN, activated for live
   payments 2026-10-01, and it doesn't need the EIN to take them: Stripe's help says a single-member LLC uses
   its owner's name and SSN, and 1099s go out under the owner's personal tax details. Switching to
   Company / Robot Lantern LLC with an EIN is optional. Stripe wants the name exactly as the IRS has it and
   may ask for new documents. The Stripe pages found are for Connect accounts, so look at what Settings →
   Business → Business details offers before relying on it.
5. **Turn on West Virginia in Stripe Tax.** Dashboard → Tax → Locations → Add registration → West Virginia
   → "I've already registered" → enter the sales tax account number (the Combined Sales and Use line on the
   certificate letter, not the Business Registration Tax line above it) → "Start collecting immediately"
   (the registration has been active since 2025-12-16 and there are no earlier sales) → confirm the rates.
   Needs the head office address and the preset product tax code set (the sandbox has both). Until then,
   Stripe Tax calculates but collects nothing. Do this once the catch-up returns are in. Stripe Tax collects;
   it does not file. RJ files the monthly return in MyTaxes, using Stripe's reports for the totals and the
   city (Schedule M) breakdown.

## After it's running

- **Filing:** West Virginia sales tax returns go through MyTaxes, on the schedule the state
  assigns at registration (based on expected volume). Stripe Tax's reports give the totals per
  period and per city.
- **Gelato:** Gelato adds sales tax to its own charges unless it has a resale certificate. Once
  registered, give Gelato one (West Virginia is a Streamlined Sales Tax member, so its
  multistate certificate covers the Gelato orders shipped to most states).

## Sources (checked 2026-10-01)

- [IRS: apply for an EIN online](https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online) and [Form SS-4 instructions](https://www.irs.gov/instructions/iss4) (2026-11-12)
- [West Virginia business registration instructions](https://tax.wv.gov/Documents/Business/BusinessRegistrationInformationAndInstructions.pdf) and [Business Registration FAQ](https://tax.wv.gov/Business/BusinessRegistration/Pages/BusinessRegistrationQuestionsAndAnswers.aspx) (2026-11-12)
- [Stripe on EIN reference number 101](https://stripe.com/resources/more/irs-ein-reference-number-101) and [Taxpayer Advocate Service: getting an EIN](https://www.taxpayeradvocate.irs.gov/get-help/general/getting-an-ein/) (third-party and IRS pages, 2026-11-12)
- [Stripe: tax ID guidelines by business type](https://support.stripe.com/embedded-connect/questions/tax-id-verification-guidelines-by-business-type-in-the-us), [sole proprietor without an EIN](https://support.stripe.com/questions/signing-up-for-stripe-as-a-sole-proprietor-without-employer-id-number) and [update your sole proprietor data](https://support.stripe.com/questions/update-your-sole-proprietor-business-data) (2026-11-12)
- [Stripe Tax pricing](https://support.stripe.com/questions/understanding-stripe-tax-pricing)
- [West Virginia sales tax guide (Avalara)](https://www.avalara.com/us/en/taxrates/state-rates/west-virginia/west-virginia-sales-tax-guide.html)
- [Economic nexus by state (Sales Tax Institute)](https://www.salestaxinstitute.com/resources/economic-nexus-state-guide)
