from enum import Enum, auto
from collections import defaultdict

from er_calc.asset import Asset, AssetProviderType


class Expense(Enum):
    RENT = auto()
    LIVING = auto()


class Income(Enum):
    UK_SALARY = auto()
    UK_RENTAL = auto()
    UK_TRADING = auto()


class Portfolio:
    providers: dict[Asset, AssetProviderType]

    # Maps assets to number of units held
    asset_holdings: dict[Asset, float]
    expenses: dict[Expense, float]
    income: dict[Income, float]

    def __init__(self, providers: dict[Asset, AssetProviderType]):
        self.providers = providers
        self.asset_holdings = {}
        for asset in providers:
            self.asset_holdings[asset] = 0.0
        self.expenses = defaultdict(lambda: 0.0)
        self.income = defaultdict(lambda: 0.0)

    def add(
        self,
        asset: Asset,
        /,
        cash: float | None = None,
        units: float | None = None,
    ):
        if cash is None and units is None:
            raise ValueError("Didn't specify anything to add")

        if units is not None:
            self.asset_holdings[asset] += units

        if cash is not None:
            asset_provider = self.providers[asset]
            cash_units = cash / asset_provider.value()
            self.asset_holdings[asset] += cash_units

    def current_value(self):
        return sum(
            self.providers[asset].value() * units
            for asset, units in self.asset_holdings.items()
        )

    def asset_value_per_unit(self, asset: Asset):
        return self.providers[asset].value()

    def units_of_asset_held(self, asset: Asset):
        return self.asset_holdings[asset]

    def cash_of_asset_held(self, asset: Asset):
        return self.units_of_asset_held(asset) * self.asset_value_per_unit(asset)

    def total_income(self):
        return sum(self.income.values())

    def total_expenses(self):
        return sum(self.expenses.values())
