# LenderLens Analytics

**Decision intelligence for the full mortgage funnel — from marketing spend to funded-loan economics.**

[![Analytics Engine CI](https://github.com/snshafik/lenderlens-site/actions/workflows/ci.yml/badge.svg)](https://github.com/snshafik/lenderlens-site/actions/workflows/ci.yml)

**Live site:** https://lenderlens.net  
**Interactive Decision Lab:** https://lenderlens.net/decision-lab.html

## Why this repo exists

Most marketing dashboards answer **what happened**. This project is designed to answer a harder question:

> **Given a fixed budget, where should the next dollar go — and why?**

The repo combines an interactive browser demo, a dependency-light Python decision engine, and a warehouse SQL model to demonstrate the path from raw acquisition data to an explainable recommendation.

## What makes the Decision Lab different

- **Downstream optimization:** evaluates spend against applications and funded-loan contribution, not just clicks or leads.
- **Diminishing-return response curves:** prevents the unrealistic assumption that every additional dollar scales linearly.
- **Explainable recommendations:** shows the marginal expected profit of the next dollar for each channel.
- **Fixed-budget optimizer:** reallocates the same portfolio budget instead of simply recommending “spend more.”
- **Uncertainty modeling:** the Python engine includes Monte Carlo simulation across funnel rates and CPL volatility.
- **Warehouse-ready thinking:** the SQL reference mart joins spend, lead, application, and funded-loan outcomes and emits anomaly/decision flags.
- **Reproducibility:** deterministic simulation seeds and automated tests run in GitHub Actions.

## Architecture

```text
Marketing spend ─┐
Lead events ─────┼──> Funnel intelligence SQL ──> channel-day decision mart
Applications ────┤                                  │
Funded loans ────┘                                  ▼
                                              Python decision engine
                                      expected value + saturation + risk
                                                      │
                                                      ▼
                                         Explainable budget frontier
                                                      │
                              ┌───────────────────────┴───────────────────────┐
                              ▼                                               ▼
                      Interactive web lab                              Decision flags
```

## Repository map

| Path | Purpose |
|---|---|
| `decision-lab.html` | Interactive, zero-dependency portfolio optimizer |
| `analytics_engine.py` | Reusable expected-value, optimization, recommendation, and Monte Carlo logic |
| `sql/funnel_intelligence.sql` | Snowflake-oriented spend-to-funded-loan analytical mart |
| `tests/test_analytics_engine.py` | Behavioral tests for saturation, optimization, coverage, and deterministic simulation |
| `.github/workflows/ci.yml` | Automated Python test workflow |
| `index.html` | LenderLens product/portfolio landing page |

## Core model

For each channel, expected funded loans are modeled as:

```text
Spend
  -> saturating response curve
  -> effective leads
  -> applications
  -> funded loans
  -> contribution
  -> profit = contribution - spend
```

The optimizer evaluates the **marginal profit of the next budget increment** and allocates the portfolio budget to the best available channel while respecting channel-level saturation guardrails.

This is intentionally a decision model, not a claim that historical attribution alone proves causality. In a production environment I would pair this layer with incrementality experiments, causal holdouts, or geo-based lift designs where feasible.

## Run the analytics engine

```bash
python analytics_engine.py
```

Run tests:

```bash
python -m pip install pytest
pytest -q
```

No runtime third-party Python packages are required by the engine itself.

## Example questions this architecture can answer

1. Which channel has the strongest downstream economics after lead quality is considered?
2. Where is spend beyond the efficient part of the response curve?
3. If the total budget cannot increase, how should it be reallocated?
4. How sensitive is the recommendation to funnel-rate and CPL uncertainty?
5. Which campaigns are degrading relative to their own recent efficiency baseline?
6. Where should an analyst investigate before a budget decision is operationalized?

## Design principles

**Decision > dashboard.** A chart is useful; a recommended action with traceable assumptions is more useful.  
**Revenue truth > vanity metrics.** Cheap leads are not cheap if they fail downstream.  
**Explainability > black box.** Stakeholders should be able to understand why a recommendation moved.  
**Guardrails > unconstrained optimization.** Mathematical optima still need operational and market constraints.  
**Synthetic examples > leaked business data.** This public repository intentionally contains no employer or client data.

## Next production extensions

- dbt model + schema tests and freshness checks
- Snowflake/Databricks feature tables
- Bayesian hierarchical response curves by channel and geography
- causal incrementality calibration from experiments
- MLflow model registry / experiment tracking
- scenario API with FastAPI
- Power BI or Looker semantic layer on top of the decision mart
- drift monitoring for CPL and funnel-rate assumptions

---

Built as a public analytics-engineering portfolio project. All data and example economics are synthetic and illustrative.
