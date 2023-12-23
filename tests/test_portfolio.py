from unittest import TestCase

from er_calc.asset import Asset, ConstantGeomIncreaseAsset
from er_calc.portfolio import Portfolio


class TestPortfolio(TestCase):
    def test_add(self):
        asset = Asset.ETF_GLOBAL_STOCK
        p = Portfolio(
            providers={
                asset: ConstantGeomIncreaseAsset(asset, 1.0),
            }
        )

        self.assertEqual(0.0, p.asset_holdings[asset])

        p.add(asset, units=5.0)
        self.assertAlmostEqual(5.0, p.asset_holdings[asset])

        self.assertAlmostEqual(100.0, p.providers[asset].value())
        p.add(asset, cash=200.0)
        self.assertAlmostEqual(7.0, p.asset_holdings[asset])
