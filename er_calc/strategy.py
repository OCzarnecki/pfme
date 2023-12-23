import math

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

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

    def requested_assets(self) -> list[Asset]:
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

    def requested_assets(self) -> list[Asset]:
        return [self.asset]

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        portfolio.add(asset=self.asset, cash=self.amount * increment)
