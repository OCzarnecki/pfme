import math

import numpy as np
from tqdm.auto import tqdm

from pfme.asset import Asset, AssetProviderType
from pfme.config import SimulationConfig
from pfme.metric import RunMetricType
from pfme.portfolio import Portfolio
from pfme.strategy import StrategyType


class Simulation:
    metrics: list[RunMetricType]
    asset_providers: dict[Asset, AssetProviderType]
    strategies: list[StrategyType]

    def __init__(
        self,
        config: SimulationConfig
    ):
        self.metrics = config.metrics
        self.strategies = config.strategies
        self.config = config

        collected_assets = set()
        for strategy in self.strategies:
            collected_assets |= strategy.requested_assets()
        for metric in self.metrics:
            collected_assets |= metric.requested_assets()

        self.asset_providers = {
            asset: self.config.asset_provider_mapping[asset]
            for asset in collected_assets
        }

    def run(self) -> None:
        c = self.config
        portfolio = Portfolio(self.asset_providers)

        for asset_provider in self.asset_providers.values():
            asset_provider.update_value(c.start_year, math.nan)
        for year in tqdm(np.arange(c.start_year, c.end_year, c.increment)):
            year = float(year)
            for strategy in self.strategies:
                strategy.update_income(portfolio.income, year, c.increment)
            for strategy in self.strategies:
                strategy.update_expenses(portfolio.expenses, year, c.increment)
            for strategy in self.strategies:
                strategy.execute(portfolio, year, c.increment)

            for metric in self.metrics:
                metric.record(portfolio, year)
            for asset_provider in self.asset_providers.values():
                asset_provider.update_value(year, c.increment)
