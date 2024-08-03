import math

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

from ipython_utils.finance import uk_net_income

from er_calc.asset import Asset
from er_calc.portfolio import Portfolio


@dataclass
class Strategy(ABC):
    @abstractmethod
    def requested_assets(self) -> list[Asset]:
        ...

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        ...


StrategyType = TypeVar('StrategyType', bound=Strategy)


@dataclass
class CombinedStrategy(Strategy):
    children: list[StrategyType]

    def requested_assets(self) -> list[Asset]:
        return [
            asset
            for strategy in self.children
            for asset in strategy.requested_assets()
        ]

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        for child in self.children:
            child.execute(portfolio, year, increment)


@dataclass
class LimitedDurationStrategy(Strategy):
    """Only execute the child strategy for times in the interval
    [start, end] (inclusive).
    """
    child: StrategyType
    start: float = -math.inf
    end: float = math.inf
    relative: bool = True

    elapsed: float = field(default=0.0, init=False)

    def requested_assets(self) -> set[Asset]:
        return self.child.requested_assets()

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        if self.relative:
            if not math.isnan(increment):
                self.elapsed += increment
            if self.start <= self.elapsed <= self.end:
                self.child.execute(portfolio, year, increment)
        else:
            if self.start <= year <= self.end:
                self.child.execute(portfolio, year, increment)


@dataclass
class FixedYearlyInvestmentStrategy(Strategy):
    asset: Asset
    amount: float

    def requested_assets(self) -> set[Asset]:
        return {self.asset}

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        portfolio.add(asset=self.asset, cash=self.amount * increment)


@dataclass
class SaveEarningsMinusExpenses(Strategy):
    def requested_assets(self) -> set[Asset]:
        return {Asset.SALARY, Asset.EXPENSES, Asset.CASH}

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        net_income = uk_net_income(portfolio.providers[Asset.SALARY].value())
        savings = net_income - portfolio.providers[Asset.EXPENSES].value()

        portfolio.add(asset=Asset.CASH, cash=savings * increment)


@dataclass
class InvestFractionOfCashAfterBuffer(Strategy):
    buffer_per_yearly_expenses: float
    allocation: dict[Asset, float]

    def __post_init__(self):
        if abs(sum(self.allocation.values()) - 1.0) > 1e-12:
            raise ValueError("Allocation ratios must add up to one")
        if any([ratio < 0.0 for ratio in self.allocation.values()]):
            raise ValueError("Allocation ratios cannot be negative")

    def requested_assets(self) -> set[Asset]:
        return {Asset.CASH} | set(self.allocation.keys())

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        yearly_buffer = self.buffer_per_yearly_expenses * portfolio.asset_value_per_unit(Asset.EXPENSES)
        investable = (portfolio.cash_of_asset_held(Asset.CASH) - yearly_buffer) * increment
        if investable < 0:
            return

        for asset, ratio in self.allocation.items():
            portfolio.add(asset, cash=investable * ratio)

        portfolio.add(Asset.CASH, cash=-investable)
