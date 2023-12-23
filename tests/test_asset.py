import math

from unittest import TestCase

from er_calc.asset import Asset, ConstantGeomIncreaseAsset


class TestConstantGeomIncreaseAsset(TestCase):
    def test(self):
        provider = ConstantGeomIncreaseAsset(
            Asset.ETF_GLOBAL_STOCK,
            0.10
        )

        provider.update_value(2023, math.nan)
        self.assertAlmostEqual(100.0, provider.value())

        provider.update_value(2024, 1.0)
        self.assertAlmostEqual(110.0, provider.value())

        provider.update_value(2024.5, 0.5)
        self.assertAlmostEqual(115.36897329871668, provider.value())
