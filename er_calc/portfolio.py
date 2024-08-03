from er_calc.asset import Asset, AssetProviderType


class Portfolio:
    providers: dict[Asset, AssetProviderType]

    # Maps assets to number of units held
    asset_holdings: dict[Asset, float]

    def __init__(self, providers: dict[Asset, AssetProviderType]):
        self.providers = providers
        self.asset_holdings = {}
        for asset in providers:
            self.asset_holdings[asset] = 0.0

    def add(
        self,
        asset: Asset,
        *_ignore,
        cash: float | None = None,
        units: float | None = None,
    ):
        if _ignore != ():
            raise ValueError(f"Received unexpected positional arguments: {_ignore}. Amount of assets to add must be specified via keyword args.")
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
