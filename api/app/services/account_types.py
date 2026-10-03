"""Account types and their subtypes, as in Monarch (Plaid's taxonomy). Pure module: no database, no network.

The one catalog of what an account can be: validation, the API's catalog endpoint and the web all read it.
Each type's subtypes are in Monarch's order; the first is the one a new account starts with.
Some subtypes only come from banks: Monarch's "Add Manual Account" doesn't offer them (`manual=False`).
"""

from dataclasses import dataclass

from app.models.wallet import AccountClass, WalletType


@dataclass(frozen=True)
class Subtype:
    key: str
    label: str
    # Offered when adding an account by hand; the rest only arrive from a bank
    manual: bool = True


@dataclass(frozen=True)
class TypeInfo:
    label: str
    account_class: AccountClass
    subtypes: tuple[Subtype, ...]

    @property
    def default_subtype(self) -> str:
        # The first one "Add Manual Account" offers, as Monarch preselects it
        return next(subtype.key for subtype in self.subtypes if subtype.manual)


def _subtypes(*pairs: tuple[str, str]) -> tuple[Subtype, ...]:
    return tuple(Subtype(key, label) for key, label in pairs)


def _bank_only(*pairs: tuple[str, str]) -> tuple[Subtype, ...]:
    return tuple(Subtype(key, label, manual=False) for key, label in pairs)


OTHER = ("other", "Other")

# In the order Monarch lists them: assets, then liabilities
ACCOUNT_TYPES: dict[WalletType, TypeInfo] = {
    # Monarch's "Add Manual Account" list first, in its order; then Plaid's bank-only ones
    WalletType.CASH: TypeInfo("Cash", AccountClass.ASSET, _subtypes(
        ("cd", "CD"),
        ("checking", "Checking"),
        ("savings", "Savings"),
        ("money_market", "Money Market"),
        ("mobile_payment_system", "Mobile Payment System"),
        ("prepaid", "Prepaid"),
        ("cash_management", "Cash Management"),
    ) + _bank_only(
        ("ebt", "EBT"),
        ("hsa", "HSA"),
        ("limited_purpose_checking", "Limited Purpose Checking"),
        ("paypal", "PayPal"),
    )),
    # Only what people in Greece hold, all tracked by hand: PSD2 (Enable Banking) reaches payment accounts,
    # not securities, so no investment account can be linked. Labels as in Monarch's list.
    WalletType.INVESTMENT: TypeInfo("Investments", AccountClass.ASSET, _subtypes(
        ("brokerage", "Brokerage"),
        ("crypto_exchange", "Cryptocurrency"),
        ("mutual_fund", "Mutual Fund"),
        ("pension", "Pension"),
        ("stock_plan", "Stock Plan"),
        OTHER,
    )),
    WalletType.REAL_ESTATE: TypeInfo("Real Estate", AccountClass.ASSET, _subtypes(
        ("primary_home", "Primary Home"),
        ("secondary_home", "Secondary Home"),
        ("rental_property", "Rental Property"),
    )),
    WalletType.VEHICLE: TypeInfo("Vehicles", AccountClass.ASSET, _subtypes(
        ("car", "Car"),
        ("boat", "Boat"),
        ("motorcycle", "Motorcycle"),
        ("snowmobile", "Snowmobile"),
        ("bicycle", "Bicycle"),
        OTHER,
    )),
    WalletType.VALUABLES: TypeInfo("Valuables", AccountClass.ASSET, _subtypes(
        ("art", "Art"),
        ("jewelry", "Jewelry"),
        ("collectibles", "Collectibles"),
        ("furniture", "Furniture"),
        OTHER,
    )),
    WalletType.OTHER_ASSET: TypeInfo("Other Assets", AccountClass.ASSET, _subtypes(OTHER)),
    WalletType.CREDIT_CARD: TypeInfo("Credit Card", AccountClass.LIABILITY, _subtypes(
        ("credit_card", "Credit Card"),
        ("paypal", "PayPal"),
    )),
    WalletType.MORTGAGE: TypeInfo("Mortgage", AccountClass.LIABILITY, _subtypes(("mortgage", "Mortgage"))),
    WalletType.LOAN: TypeInfo("Loans", AccountClass.LIABILITY, _subtypes(
        ("auto", "Auto"),
        ("business", "Business"),
        ("commercial", "Commercial"),
        ("construction", "Construction"),
        ("consumer", "Consumer"),
        ("home", "Home"),
        ("home_equity", "Home Equity"),
        ("loan", "Loan"),
        ("mortgage", "Mortgage"),
        ("overdraft", "Overdraft"),
        ("line_of_credit", "Line of Credit"),
        ("student", "Student"),
    )),
    WalletType.OTHER_LIABILITY: TypeInfo("Other Liabilities", AccountClass.LIABILITY, _subtypes(OTHER)),
}

class InvalidSubtypeError(ValueError):
    def __init__(self, wallet_type: WalletType, subtype: str):
        super().__init__(f"'{subtype}' isn't a kind of {ACCOUNT_TYPES[wallet_type].label} account")


def resolve_subtype(wallet_type: WalletType, subtype: str | None) -> str:
    """The subtype to store: the one given if the type has it, else the type's default when none is given."""
    info = ACCOUNT_TYPES[wallet_type]
    if subtype is None:
        return info.default_subtype
    if subtype not in {known.key for known in info.subtypes}:
        raise InvalidSubtypeError(wallet_type, subtype)
    return subtype
