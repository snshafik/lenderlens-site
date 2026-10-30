# LenderLens Stripe implementation plan
_Updated October 29, 2026. Dedicated LenderLens live and sandbox Stripe accounts now connected; partial live catalog provisioned._

## Accounts and payment isolation
- LenderLens **live**: `acct_1UW7EWDE8Z6DKZCU`.
- LenderLens **sandbox**: `acct_1UW7EdDcY3FKg0lw`.
- CaptureKite **live**: `acct_1UDzTDDp32e4frG4`. This is a different business account.
- Use the LenderLens live merchant for all new LenderLens billing and client records. Do not create new LenderLens subscriptions or invoices in CaptureKite.
- Existing one-time $495 checkout on site **still uses CaptureKite**: `https://buy.stripe.com/cNi7sL6rH57L21Je5OaVa04`. Maintain accurate merchant disclosure until a verified LenderLens replacement link exists.

## Current live Stripe objects

| Product | Product ID | Price ID | Amount | Status |
| --- | --- | --- | --- | --- |
| Starter Analytics | `prod_VXBlB39WAMfNXX` | — | $1,250/mo planned | Product exists; API price creation blocked by safety checks |
| Growth Analytics | `prod_VXBlv0Ja9eZLYm` | `price_1UW7O1DE8Z6DKZCUcQjGLv0b` | $2,500/mo | Recurring monthly price verified |
| Executive Analytics | `prod_VXBlw8xqf0en2A` | `price_1UW7O3DE8Z6DKZCU9imLFJn0` | $5,000/mo | Recurring monthly price verified |
| Mortgage Funnel Leak Audit | — | — | $495 once planned | API product creation blocked; existing CaptureKite link remains until replacement |

Sandbox Starter, Growth and Executive products and monthly prices were also created. The sandbox Mortgage Funnel Leak Audit product creation was blocked.

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
2. Through the merchant Dashboard or an approved API operation, create the $495 audit product, price and hosted Payment Link in the **LenderLens** account. API-based creation has been blocked by safety checks; do not reattempt blindly.
3. Create the Starter $1,250/mo recurring price in the LenderLens live account; API operation was blocked. Avoid duplicating Growth/Executive prices.
4. Verify the new LenderLens audit link is active, has a $495 one-time line item, carries merchant business name, collects business contact details and leads to a clear onboarding confirmation.
5. Replace **both existing CaptureKite link occurrences** on `/funnel-audit.html`, change merchant disclosure, confirm new public deployment and successful website smoke test. Preserve CaptureKite link until old orders are reviewed.
6. Configure Stripe invoicing defaults and payment terms after account holder confirms legal/operating details; don't send invoices without genuine customer and accepted proposal.
7. Implement signed, idempotent server-side webhooks before automated fulfillment, subscriptions, and asynchronous payment handling. GitHub Pages is static; no secret-bearing backend or webhook handler can run there. Relevant events include checkout completions/success/failure; `customer.subscription.*`, `invoice.paid`, `invoice.payment_failed`, disputes, refunds and early fraud warnings.
8. Confirm any applicable Stripe Tax registrations before enabling `automatic_tax`. No auto tax was enabled.
9. Verify first sale from an authentic succeeded externally paid LenderLens checkout or paid invoice, excluding all tests, spam, and non-LenderLens account transactions.

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
