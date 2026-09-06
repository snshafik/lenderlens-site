import math

from analytics_engine import (
    DEMO_CHANNELS,
    expected_outcome,
    optimize_budget,
    portfolio_outcome,
    recommendations,
    simulate_portfolio,
)


def test_baseline_has_positive_funnel_volume():
    outcome = expected_outcome(DEMO_CHANNELS[0], DEMO_CHANNELS[0].baseline_spend)
    assert outcome.leads > 0
    assert outcome.applications > 0
    assert outcome.funded_loans > 0


def test_diminishing_returns_are_present():
    channel = DEMO_CHANNELS[0]
    low = expected_outcome(channel, channel.baseline_spend).leads / channel.baseline_spend
    high = expected_outcome(channel, channel.baseline_spend * 2).leads / (channel.baseline_spend * 2)
    assert high < low


def test_optimizer_preserves_budget_when_capacity_allows():
    budget = 200_000
    allocation = optimize_budget(DEMO_CHANNELS, budget, step=5_000)
    assert math.isclose(sum(allocation.values()), budget, rel_tol=0, abs_tol=1e-9)


def test_optimizer_does_not_make_expected_profit_worse_than_equal_split():
    budget = 240_000
    equal = {c.name: budget / len(DEMO_CHANNELS) for c in DEMO_CHANNELS}
    optimized = optimize_budget(DEMO_CHANNELS, budget, step=5_000)
    equal_profit = portfolio_outcome(DEMO_CHANNELS, equal)["total_profit"]
    optimized_profit = portfolio_outcome(DEMO_CHANNELS, optimized)["total_profit"]
    assert optimized_profit >= equal_profit


def test_recommendations_cover_every_channel():
    current = {c.name: c.baseline_spend for c in DEMO_CHANNELS}
    optimized = optimize_budget(DEMO_CHANNELS, sum(current.values()), step=5_000)
    rows = recommendations(DEMO_CHANNELS, current, optimized)
    assert {r.channel for r in rows} == {c.name for c in DEMO_CHANNELS}


def test_monte_carlo_is_reproducible_with_seed():
    allocation = {c.name: c.baseline_spend for c in DEMO_CHANNELS}
    a = simulate_portfolio(DEMO_CHANNELS, allocation, iterations=250, seed=7)
    b = simulate_portfolio(DEMO_CHANNELS, allocation, iterations=250, seed=7)
    assert a == b
    assert 0 <= a["probability_of_loss"] <= 1
