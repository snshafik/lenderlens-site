from __future__ import annotations

from dataclasses import dataclass, asdict
from math import log1p, sqrt
from random import Random
from typing import Iterable


@dataclass(frozen=True)
class Channel:
    name: str
    baseline_spend: float
    cost_per_lead: float
    application_rate: float
    funded_rate: float
    contribution_per_funded_loan: float
    saturation: float = 2.0
    rate_strength: float = 250.0
    cpl_volatility: float = 0.12

    def validate(self) -> None:
        if self.baseline_spend <= 0 or self.cost_per_lead <= 0:
            raise ValueError("baseline_spend and cost_per_lead must be positive")
        if not 0 < self.application_rate < 1 or not 0 < self.funded_rate < 1:
            raise ValueError("rates must be between 0 and 1")
        if self.contribution_per_funded_loan <= 0 or self.saturation <= 0:
            raise ValueError("contribution and saturation must be positive")


@dataclass(frozen=True)
class Outcome:
    channel: str
    spend: float
    leads: float
    applications: float
    funded_loans: float
    contribution: float
    profit: float
    roi: float


@dataclass(frozen=True)
class Recommendation:
    channel: str
    current_spend: float
    recommended_spend: float
    delta: float
    marginal_profit_per_dollar: float
    reason: str


def _effective_leads(channel: Channel, spend: float, cpl: float | None = None) -> float:
    """Saturating response curve calibrated to equal baseline leads at baseline spend."""
    channel.validate()
    if spend < 0:
        raise ValueError("spend cannot be negative")
    cpl = cpl or channel.cost_per_lead
    if spend == 0:
        return 0.0
    ratio = spend / channel.baseline_spend
    response = log1p(channel.saturation * ratio) / log1p(channel.saturation)
    return (channel.baseline_spend / cpl) * response


def expected_outcome(channel: Channel, spend: float) -> Outcome:
    leads = _effective_leads(channel, spend)
    applications = leads * channel.application_rate
    funded = applications * channel.funded_rate
    contribution = funded * channel.contribution_per_funded_loan
    profit = contribution - spend
    roi = (profit / spend) if spend else 0.0
    return Outcome(channel.name, spend, leads, applications, funded, contribution, profit, roi)


def portfolio_outcome(channels: Iterable[Channel], allocation: dict[str, float]) -> dict:
    outcomes = [expected_outcome(c, allocation.get(c.name, 0.0)) for c in channels]
    total_spend = sum(o.spend for o in outcomes)
    total_profit = sum(o.profit for o in outcomes)
    total_funded = sum(o.funded_loans for o in outcomes)
    return {
        "total_spend": total_spend,
        "total_profit": total_profit,
        "portfolio_roi": total_profit / total_spend if total_spend else 0.0,
        "funded_loans": total_funded,
        "channels": [asdict(o) for o in outcomes],
    }


def _marginal_profit(channel: Channel, spend: float, step: float) -> float:
    before = expected_outcome(channel, spend).profit
    after = expected_outcome(channel, spend + step).profit
    return (after - before) / step


def optimize_budget(
    channels: Iterable[Channel],
    total_budget: float,
    step: float = 1000.0,
    max_channel_multiplier: float = 2.25,
) -> dict[str, float]:
    """Greedy discrete optimizer on marginal profit with per-channel saturation guardrails."""
    channels = list(channels)
    if total_budget < 0 or step <= 0:
        raise ValueError("total_budget must be non-negative and step must be positive")
    if not channels:
        return {}

    allocation = {c.name: 0.0 for c in channels}
    remaining = total_budget

    while remaining >= min(step, total_budget) and remaining > 1e-9:
        chunk = min(step, remaining)
        candidates: list[tuple[float, Channel]] = []
        for c in channels:
            cap = c.baseline_spend * max_channel_multiplier
            if allocation[c.name] + chunk <= cap + 1e-9:
                candidates.append((_marginal_profit(c, allocation[c.name], chunk), c))

        if not candidates:
            break
        _, best = max(candidates, key=lambda item: item[0])
        allocation[best.name] += chunk
        remaining -= chunk

    return allocation


def recommendations(channels: Iterable[Channel], current: dict[str, float], recommended: dict[str, float]) -> list[Recommendation]:
    rows: list[Recommendation] = []
    for c in channels:
        cur = current.get(c.name, 0.0)
        rec = recommended.get(c.name, 0.0)
        marginal = _marginal_profit(c, cur, max(250.0, c.baseline_spend * 0.02))
        delta = rec - cur
        if delta > 1e-9:
            reason = "Scale: the next dollar has stronger expected downstream contribution."
        elif delta < -1e-9:
            reason = "Reduce: diminishing returns make incremental spend less efficient."
        else:
            reason = "Hold: current allocation is near the model's local efficiency frontier."
        rows.append(Recommendation(c.name, cur, rec, delta, marginal, reason))
    return sorted(rows, key=lambda r: r.delta, reverse=True)


def simulate_portfolio(
    channels: Iterable[Channel],
    allocation: dict[str, float],
    iterations: int = 2000,
    seed: int = 42,
) -> dict:
    """Monte Carlo uncertainty layer using beta funnel rates and stochastic CPL shocks."""
    channels = list(channels)
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    rng = Random(seed)
    profits: list[float] = []
    funded_counts: list[float] = []

    for _ in range(iterations):
        total_profit = 0.0
        total_funded = 0.0
        for c in channels:
            spend = allocation.get(c.name, 0.0)
            a1 = c.application_rate * c.rate_strength
            b1 = (1 - c.application_rate) * c.rate_strength
            a2 = c.funded_rate * c.rate_strength
            b2 = (1 - c.funded_rate) * c.rate_strength
            app_rate = rng.betavariate(a1, b1)
            funded_rate = rng.betavariate(a2, b2)
            shock = max(0.55, 1.0 + rng.gauss(0, c.cpl_volatility))
            leads = _effective_leads(c, spend, c.cost_per_lead * shock)
            funded = leads * app_rate * funded_rate
            profit = funded * c.contribution_per_funded_loan - spend
            total_profit += profit
            total_funded += funded
        profits.append(total_profit)
        funded_counts.append(total_funded)

    profits.sort()
    funded_counts.sort()
    mean_profit = sum(profits) / iterations
    variance = sum((p - mean_profit) ** 2 for p in profits) / max(1, iterations - 1)

    def q(values: list[float], pct: float) -> float:
        idx = int((len(values) - 1) * pct)
        return values[idx]

    return {
        "mean_profit": mean_profit,
        "profit_stddev": sqrt(variance),
        "profit_p05": q(profits, 0.05),
        "profit_p50": q(profits, 0.50),
        "profit_p95": q(profits, 0.95),
        "funded_p50": q(funded_counts, 0.50),
        "probability_of_loss": sum(1 for p in profits if p < 0) / iterations,
    }


DEMO_CHANNELS = [
    Channel("Paid Search", 120_000, 82, 0.205, 0.278, 4_900, saturation=2.2),
    Channel("Social", 90_000, 61, 0.142, 0.216, 4_300, saturation=2.8),
    Channel("Affiliates", 75_000, 108, 0.251, 0.318, 5_400, saturation=1.8),
    Channel("Organic/Content", 35_000, 39, 0.198, 0.295, 4_700, saturation=3.5),
]


if __name__ == "__main__":
    current = {c.name: c.baseline_spend for c in DEMO_CHANNELS}
    optimized = optimize_budget(DEMO_CHANNELS, sum(current.values()), step=5_000)
    print("CURRENT", portfolio_outcome(DEMO_CHANNELS, current))
    print("OPTIMIZED", portfolio_outcome(DEMO_CHANNELS, optimized))
    print("RISK", simulate_portfolio(DEMO_CHANNELS, optimized, iterations=1000))
    for row in recommendations(DEMO_CHANNELS, current, optimized):
        print(row)
