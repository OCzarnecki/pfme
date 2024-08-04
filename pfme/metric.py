from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar

from pfme.asset import Asset
from pfme.portfolio import Portfolio


class RunMetric(ABC):
    def __init__(self):
        self.values = []

    def name(self):
        return type(self).__name__

    def requested_assets(self) -> set[Asset]:
        return set()

    @abstractmethod
    def calculate(self, portfolio: Portfolio):
        ...

    def record(self, portfolio: Portfolio, year: float):
        value = self.calculate(portfolio)
        self.values.append(
            {
                "year": year,
                "value": value,
            }
        )


RunMetricType = TypeVar('MetricType', bound=RunMetric)


class TotalAssets(RunMetric):
    def calculate(self, portfolio: Portfolio):
        return portfolio.current_value()


class HoldingsByAsset(RunMetric):
    def calculate(self, portfolio: Portfolio):
        return [
            {
                "asset": asset.name,
                "units": units,
                "unit_value": portfolio.asset_value_per_unit(asset),
            }
            for asset, units in portfolio.asset_holdings.items()
        ]


class FIReached(RunMetric):
    withdrawal_rate: float

    def __init__(self, withdrawal_rate: float):
        self.withdrawal_rate = withdrawal_rate
        super().__init__()

    def calculate(self, portfolio: Portfolio):
        return (
            portfolio.current_value() * self.withdrawal_rate
            >= sum(portfolio.expenses.values())
        )


class CashflowStatement(RunMetric):
    def calculate(self, portfolio: Portfolio):
        return {
            "income": [
                {
                    "name": key.name,
                    "value": value,
                }
                for key, value in portfolio.income.items()
            ],
            "expenses": [
                {
                    "name": key.name,
                    "value": value,
                }
                for key, value in portfolio.expenses.items()
            ]
        }
