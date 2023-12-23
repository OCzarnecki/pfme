from er_calc.asset import Asset, AssetProviderType


class Portfolio:
    # Maps assets to number of units held
    providers: dict[Asset, AssetProviderType]
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
