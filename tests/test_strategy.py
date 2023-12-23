from unittest import TestCase

from er_calc.asset import Asset, ConstantGeomIncreaseAsset
from er_calc.portfolio import Portfolio
from er_calc.strategy import (
    CombinedStrategy,
    LimitedDurationStrategy,
    FixedYearlyInvestmentStrategy,
)


class TestFixedYearlyInvestmentStrategy(TestCase):
    def test(self):
        asset = Asset.ETF_GLOBAL_STOCK
        p = Portfolio(
            providers={
                asset: ConstantGeomIncreaseAsset(asset, 1.0),
            }
        )

        strategy = FixedYearlyInvestmentStrategy(asset, 50.0)

        self.assertAlmostEqual(0.0, p.asset_holdings[asset])

        strategy.execute(p, 2024.0, 1.0)
        self.assertAlmostEqual(0.5, p.asset_holdings[asset])

        strategy.execute(p, 2025.0, 0.5)
        self.assertAlmostEqual(0.75, p.asset_holdings[asset])


class TestCombinedStrategy(TestCase):
    def test(self):
        asset_1 = Asset.ETF_GLOBAL_STOCK
        asset_2 = Asset.SAVINGS_ACCOUNT_VARIABLE_RATE
        p = Portfolio(
            providers={
                asset_1: ConstantGeomIncreaseAsset(asset_1, 1.0),
                asset_2: ConstantGeomIncreaseAsset(asset_2, 1.0),
            }
        )

        combined_strategy = CombinedStrategy([
            FixedYearlyInvestmentStrategy(asset_1, 50.0),
            FixedYearlyInvestmentStrategy(asset_2, 100.0),
        ])

        self.assertAlmostEqual(0.0, p.asset_holdings[asset_1])
        self.assertAlmostEqual(0.0, p.asset_holdings[asset_2])

        combined_strategy.execute(p, 2024.0, 1.0)
        self.assertAlmostEqual(0.5, p.asset_holdings[asset_1])
        self.assertAlmostEqual(1.0, p.asset_holdings[asset_2])

        combined_strategy.execute(p, 2025.0, 0.5)
        self.assertAlmostEqual(0.75, p.asset_holdings[asset_1])
        self.assertAlmostEqual(1.5, p.asset_holdings[asset_2])


class TestLimitedDurationStrategy(TestCase):
    def setUp(self):
        self.asset = Asset.ETF_GLOBAL_STOCK
        self.p = Portfolio(
            providers={
                self.asset: ConstantGeomIncreaseAsset(self.asset, 1.0),
            }
        )

        self.child = FixedYearlyInvestmentStrategy(self.asset, 100.0)

    def test_absolute_start_end(self):
        strategy = LimitedDurationStrategy(
            self.child,
            start=2024.0,
            end=2025.0,
            relative=False
        )

        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2023.0, 1.0)
        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.0, 1.0)
        self.assertAlmostEqual(1.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.5, 0.5)
        self.assertAlmostEqual(1.5, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.0, 0.5)
        self.assertAlmostEqual(2.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2026.0, 1.0)
        self.assertAlmostEqual(2.0, self.p.asset_holdings[self.asset])

    def test_absolute_start_only(self):
        strategy = LimitedDurationStrategy(
            self.child,
            start=2024.0,
            relative=False
        )

        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2023.0, 1.0)
        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.0, 1.0)
        self.assertAlmostEqual(1.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.5, 0.5)
        self.assertAlmostEqual(1.5, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.0, 0.5)
        self.assertAlmostEqual(2.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2026.0, 1.0)
        self.assertAlmostEqual(3.0, self.p.asset_holdings[self.asset])

    def test_absolute_end_only(self):
        strategy = LimitedDurationStrategy(
            self.child,
            end=2025.0,
            relative=False
        )

        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2023.0, 1.0)
        self.assertAlmostEqual(1.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.0, 1.0)
        self.assertAlmostEqual(2.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.5, 0.5)
        self.assertAlmostEqual(2.5, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.0, 0.5)
        self.assertAlmostEqual(3.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2026.0, 1.0)
        self.assertAlmostEqual(3.0, self.p.asset_holdings[self.asset])

    def test_relative_start_end(self):
        strategy = LimitedDurationStrategy(
            self.child,
            start=2.0,
            end=3.0,
            relative=True
        )

        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.0, 1.0)
        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.0, 1.0)
        self.assertAlmostEqual(1.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.5, 0.5)
        self.assertAlmostEqual(1.5, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2026.0, 0.5)
        self.assertAlmostEqual(2.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2027.0, 1.0)
        self.assertAlmostEqual(2.0, self.p.asset_holdings[self.asset])

    def test_relative_start_only(self):
        strategy = LimitedDurationStrategy(
            self.child,
            start=2.0,
            relative=True
        )

        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.0, 1.0)
        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.0, 1.0)
        self.assertAlmostEqual(1.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.5, 0.5)
        self.assertAlmostEqual(1.5, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2026.0, 0.5)
        self.assertAlmostEqual(2.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2027.0, 1.0)
        self.assertAlmostEqual(3.0, self.p.asset_holdings[self.asset])

    def test_relative_end_only(self):
        strategy = LimitedDurationStrategy(
            self.child,
            end=3.0,
            relative=True
        )

        self.assertAlmostEqual(0.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2024.0, 1.0)
        self.assertAlmostEqual(1.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.0, 1.0)
        self.assertAlmostEqual(2.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2025.5, 0.5)
        self.assertAlmostEqual(2.5, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2026.0, 0.5)
        self.assertAlmostEqual(3.0, self.p.asset_holdings[self.asset])

        strategy.execute(self.p, 2027.0, 1.0)
        self.assertAlmostEqual(3.0, self.p.asset_holdings[self.asset])
