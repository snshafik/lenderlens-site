# LenderLens Stripe implementation plan
_Last reviewed October 29, 2026. Status: planning completed; dedicated LenderLens Stripe account connection and product provisioning pending._

## Merchant account isolation
Use the dedicated Stripe merchant named **lenderlens** shown in the owner's Dashboard. Do not provision new LenderLens services into CaptureKite, Atlas.ai, or Data Desk AI accounts. The LenderLens account must be explicitly authorized in the ChatGPT Stripe connection before Stripe API changes. Verify legal business details, support email, merchant statement descriptor, payout bank setup, and payment acceptance eligibility in Stripe Dashboard. No API secrets belong in GitHub or frontend code.

**Existing checkout:** The one-time $495 pilot currently links to a live **CaptureKite** Stripe Payment Link. Maintain honest on-site processor disclosure until a new LenderLens payment link has been created, verified and deployed; then change both CTAs, disclose the new payment merchant, and retire the old CaptureKite link only after verifying no unfulfilled orders depend on it. Do not switch blindly.

## Service catalog
Separate Stripe Products for each customer-facing service; Prices are independent objects. Amounts are in USD.

| Product | Price model | Amount | Sales policy |
| --- | --- | ---: | --- |
| LenderLens Mortgage Funnel Leak Audit | One-time | $495 | Payment Link; up to 90 days aggregate data, 3 channels, one business unit; written scope & data-readiness confirmation |
| LenderLens Starter | Monthly flat-rate | $1,250 per month | Scope and service agreement accepted before first charge |
| LenderLens Growth | Monthly flat-rate | $2,500 per month | Scope and service agreement accepted before first charge |
| LenderLens Executive | Monthly flat-rate | $5,000 per month | Scope and service agreement accepted before first charge |

Do not treat these prices as tax-inclusive promises; tax obligations and registrations must be reviewed first. Scope changes, onboarding fees, and annual pricing require explicit agreement; avoid silently adding recurring items.

## Checkout and invoicing choices
- **Pilot:** Stripe-hosted Payment Link on the dedicated LenderLens account. Require customer/business name, email, and billing details. Link from `/funnel-audit.html` and avoid collecting borrower data or card numbers on lenderlens.net.
- **Signed monthly services:** Stripe Billing flat-fee Products and recurring Prices; for sales-led deals, prefer a quote/approved scope and an invoice or customer-approved subscription. Avoid unqualified self-serve recurring purchases until onboarding scope is documented.
- **Custom work:** Stripe Invoicing with Hosted Invoice Page, due date and payment terms per accepted proposal; support card and eligible bank transfer/ACH methods available to the merchant. A final invoice is never proof of payment.
- **Customer Portal:** Stripe-hosted subscription management for permitted payment method updates, cancellation, and receipt retrieval, with policies consistent with contract terms.
- **Payment recovery:** enable Stripe Smart Retries and customer notifications for failed recurring payments.

## Operational safeguards
1. Use Stripe's connected app tools, not a personal secret key shared in a chat. For any future server integration, prefer restricted API keys in a server-side secrets vault.
2. No raw `sk_live_`, `sk_test_`, `rk_live_`, or webhook signing secrets in GitHub, static Pages, HTML, JavaScript, or screenshots.
3. Keep dynamic payment methods enabled by omitting explicit `payment_method_types`.
4. For **automated onboarding, fulfillment or recurring billing integration**, implement a server-side webhook endpoint with signature validation. At minimum process `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`, `charge.refunded`, `charge.dispute.created`, and `radar.early_fraud_warning.created` as applicable. All processing must be idempotent. GitHub Pages cannot host a secret-bearing webhook endpoint. Stripe-hosted invoicing and Dashboard monitoring can be used for human-operated fulfillment before any automatic systems exist.
5. Separate confirmed LenderLens paid orders from test mode, CaptureKite orders, unpaid invoices, spam leads and refunds. Confirm payment success in Stripe before treating a purchase as revenue or starting client access.
6. Do not enable `automatic_tax` until tax nexus, product treatment, and Stripe Tax registrations are confirmed. Review US state sales/use taxes for professional analytics services and subscription invoicing.
7. Use Dashboard for branding, statement descriptor, customer support, refund policy, tax/legal address and payout onboarding. Do not expose sensitive onboarding details to the website.
8. Perform a test-mode checkout in the new LenderLens account, verify names/amounts/confirmation, then enable its corresponding live prices and links.

## Deployment checklist
- [x] GitHub Pages site and custom domain HTTPS established
- [x] Scoped $495 audit page and illustrative sample published
- [x] Stripe-hosted $495 Payment Link available **via CaptureKite** (temporary)
- [x] New LenderLens Stripe architecture documented
- [ ] Authorize **lenderlens** Stripe merchant in ChatGPT Stripe connection
- [ ] Verify merchant business readiness and branding in Dashboard
- [ ] Create new LenderLens-branded $495 audit Product / one-time Price / Payment Link
- [ ] Create 3 separate monthly flat-fee Products and Prices in dedicated account
- [ ] Configure hosted invoicing templates, payment terms, dunning and portal
- [ ] Verify dedicated checkout non-charging in test mode and live product/link configuration
- [ ] Update public website to point to dedicated LenderLens Stripe checkout and verify website smoke test
- [ ] Implement signed webhooks before claiming fully automated lifecycle fulfillment
- [ ] Start sales outreach only with authorized business mailbox and compliant contact practices

## References
- https://docs.stripe.com/payment-links
- https://docs.stripe.com/billing/subscriptions/design-an-integration
- https://docs.stripe.com/invoicing/dashboard
- https://docs.stripe.com/customer-management/activate-no-code-customer-portal
- https://docs.stripe.com/billing/subscriptions/webhooks
- https://docs.stripe.com/keys-best-practices
- https://docs.stripe.com/billing/taxes/collect-taxes
