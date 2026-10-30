# LenderLens Stripe implementation plan
_Updated October 29, 2026. Dedicated LenderLens live checkout now verified; no customer payments found as of the latest account-wide check._

## Accounts and payment isolation
- LenderLens **live**: `acct_1UW7EWDE8Z6DKZCU`.
- LenderLens **sandbox**: `acct_1UW7EdDcY3FKg0lw`.
- CaptureKite **live**: `acct_1UDzTDDp32e4frG4`. This is a different business account.
- Use the LenderLens live merchant for all new LenderLens billing and client records. Do not create new LenderLens subscriptions or invoices in CaptureKite.
- The public one-time $495 audit checkout now uses **LenderLens live** Payment Link `plink_1UW7SoDE8Z6DKZCUPOyuK2ol` at `https://buy.stripe.com/14A4gz2etaPOgijapGeUU00`. The former CaptureKite link was removed from both audit-page CTA locations; do not repurpose the old link or alter CaptureKite orders.

## Current live Stripe objects

| Product | Product ID | Price ID | Amount | Status |
| --- | --- | --- | --- | --- |
| Starter Analytics | `prod_VXBlB39WAMfNXX` | — | $1,250/mo planned | Product exists; API price creation blocked by safety checks |
| Growth Analytics | `prod_VXBlv0Ja9eZLYm` | `price_1UW7O1DE8Z6DKZCUcQjGLv0b` | $2,500/mo | Recurring monthly price verified |
| Executive Analytics | `prod_VXBlw8xqf0en2A` | `price_1UW7O3DE8Z6DKZCU9imLFJn0` | $5,000/mo | Recurring monthly price verified |
| Mortgage Funnel Leak Audit | `prod_VXBqkAWiIgE7pP` | `price_1UW7SoDE8Z6DKZCUssrjCz2R` | $495 once | Product and price verified from the live Payment Link line item; active |

Sandbox Starter, Growth and Executive products and monthly prices were also created. A sandbox audit Payment Link was successfully created after setting `managed_payments[enabled]=false` for the link; no production sandbox payment is a sale.

## Customer billing portal — ACTIVE, LenderLens live account
- Portal configuration: `bpc_1UW7OgDE8Z6DKZCUIlcxJu7f`
- Login URL: https://billing.stripe.com/p/login/14A4gz2etaPOgijapGeUU00
- Features: invoice history; update payment method, email and address; cancellation at end of the paid billing period, with cancellation reasons.
- Plan upgrades and downgrades intentionally disabled. This is a sales-led scoped consulting business, not automatic commodity SaaS.
- Public site homepage and pilot page footer link to the LenderLens Customer Billing Portal.
- No customers, paid invoices or recurring subscriptions were found in the new account on first check.

## Commercial offer and fulfillment rules
- **Audit:** Fixed-scope $495 one-time consulting project, up to 90 days of aggregate data, three channels and one business unit; findings PDF and 30-minute review. Confirm project fit, client permission and data availability. No borrower PII.
- **Monthly service:** Starter $1,250, Growth $2,500, Executive $5,000 monthly. Scope, delivery SLAs, term, and cancellation policy must be agreed in writing. Product and price creation does not start a subscription or charge a customer.
- **Custom invoice:** Use Stripe Invoicing with a Hosted Invoice Page after client agreement. Card and bank methods depend on the merchant's settings. Draft/sent invoices are not paid revenue.

## Next steps (do not falsely mark done)
1. Verify LenderLens merchant KYC, payment acceptance, payouts, statement descriptor, branding/support details, tax obligations and invoice legal footer directly in Stripe Dashboard.
2. **DONE:** Created dedicated LenderLens $495 one-time audit Payment Link via `PostPaymentLinks` with inline `price_data` and `managed_payments[enabled]=false`. Link `plink_1UW7SoDE8Z6DKZCUPOyuK2ol`; price `price_1UW7SoDE8Z6DKZCUssrjCz2R`. No account-wide Managed Payments settings were changed.
3. Create the Starter $1,250/mo recurring price in the LenderLens live account; API operation was blocked. Avoid duplicating Growth/Executive prices.
4. **DONE (API configuration):** Verified active live link, one $495 USD non-recurring line item, required business website custom field, business/name collection, and hosted post-checkout onboarding confirmation. **OPEN:** Independently inspect buyer-visible checkout merchant identity and complete a non-payment browser walkthrough; do not create a fake paid order.
5. **DONE:** Replaced both CaptureKite checkout references in `/funnel-audit.html`, corrected merchant disclosure, and updated the GitHub Actions sales-site smoke test. Pages deployment and checkout CTA smoke test both succeeded at commit `981dcb90`.
6. Configure Stripe invoicing defaults and payment terms after account holder confirms legal/operating details; don't send invoices without genuine customer and accepted proposal.
7. Implement signed, idempotent server-side webhooks before automated fulfillment, subscriptions, and asynchronous payment handling. GitHub Pages is static; no secret-bearing backend or webhook handler can run there. Relevant events include checkout completions/success/failure; `customer.subscription.*`, `invoice.paid`, `invoice.payment_failed`, disputes, refunds and early fraud warnings.
8. Confirm any applicable Stripe Tax registrations before enabling `automatic_tax`. No auto tax was enabled.
9. **NOT YET:** Latest LenderLens live account-wide reads returned 0 Checkout Sessions, 0 PaymentIntents, 0 invoices and 0 charges. Verify first sale only from an authentic succeeded externally paid LenderLens checkout or paid invoice, excluding all tests, spam, refunds and other merchants.

## Security
Never paste or commit Stripe secret keys or webhook signing secrets. The publishable `pk_test_` key shown in chat is not a secret and is not needed for hosted Payment Links. If a future backend is needed, use a restricted key in a secrets manager, never GitHub Pages or plain frontend JavaScript. Use dynamic payment methods; avoid specifying payment_method_types unless Terminal.

## Stripe references
- https://docs.stripe.com/payment-links
- https://docs.stripe.com/billing/subscriptions/design-an-integration
- https://docs.stripe.com/invoicing/dashboard
- https://docs.stripe.com/customer-management/activate-no-code-customer-portal
- https://docs.stripe.com/billing/subscriptions/webhooks
- https://docs.stripe.com/keys-best-practices
- https://docs.stripe.com/billing/taxes/collect-taxes


## Sales acquisition status — October 29, 2026
- The LenderLens sales sheet now contains eight researched mortgage-industry organizations (five existing, three newly added). Three existing partner/agency recipients were re-verified against official contact pages; three new agencies have official-site-published contacts and personalized **unsent** copy in the `Outreach Drafts` tab.
- Do not confuse drafts with sent emails, replies, qualified leads, or customers. The connected Gmail mailboxes are personal, not the authorized `insights@lenderlens.net` Google Workspace account. No outreach was sent.
- The site intake form has a client-side honeypot, a time threshold and a spam-text filter, but suspicious form submissions have still reached notification mail. Because direct HTTP POSTs can bypass browser JavaScript, implement validation, deduplication and rate limits **in the Apps Script handler**; no backend changes have been made in this run. Do not count those messages as leads.
- Before commercial outreach, use an authorized LenderLens sender, verify the valid business postal address, clear any employer-conflict concerns, identify the message as a solicitation, provide a working opt-out and maintain suppression. Follow applicable law, including CAN-SPAM.
- Do not send borrower PII or employer-confidential information; request only aggregate/de-identified data through a secure agreed transfer process.
