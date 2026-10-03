"""Account types and their subtypes, as in Monarch (Plaid's taxonomy). Pure module: no database, no network.

The one catalog of what an account can be: validation, the API's catalog endpoint and the web all read it.
Each type's subtypes are in Monarch's order; the first is the one a new account starts with.
"""

from dataclasses import dataclass

from app.models.wallet import AccountClass, WalletType


@dataclass(frozen=True)
class Subtype:
    key: str
    label: str


@dataclass(frozen=True)
class TypeInfo:
    label: str
    account_class: AccountClass
    subtypes: tuple[Subtype, ...]

    @property
    def default_subtype(self) -> str:
        return self.subtypes[0].key


def _subtypes(*pairs: tuple[str, str]) -> tuple[Subtype, ...]:
    return tuple(Subtype(key, label) for key, label in pairs)


OTHER = ("other", "Other")

# In the order Monarch lists them: assets, then liabilities
ACCOUNT_TYPES: dict[WalletType, TypeInfo] = {
    WalletType.CASH: TypeInfo("Cash", AccountClass.ASSET, _subtypes(
        ("cd", "CD"),
        ("cash_management", "Cash Management"),
        ("checking", "Checking"),
        ("ebt", "EBT"),
        ("hsa", "HSA"),
        ("limited_purpose_checking", "Limited Purpose Checking"),
        ("money_market", "Money Market"),
        ("paypal", "PayPal"),
        ("prepaid", "Prepaid"),
        ("savings", "Savings"),
    )),
    WalletType.INVESTMENT: TypeInfo("Investments", AccountClass.ASSET, _subtypes(
        ("401a", "401a"), ("401k", "401k"), ("403b", "403b"), ("457b", "457b"), ("529", "529"),
        ("brokerage", "Brokerage"),
        ("cash_isa", "Cash ISA"),
        ("crypto_exchange", "Crypto Exchange"),
        ("education_savings_account", "Education Savings Account"),
        ("fhsa", "FHSA"),
        ("fixed_annuity", "Fixed Annuity"),
        ("gic", "GIC"),
        ("health_reimbursement_arrangement", "Health Reimbursement Arrangement"),
        ("hsa", "HSA"),
        ("ira", "IRA"),
        ("isa", "ISA"),
        ("keogh", "Keogh"),
        ("lif", "LIF"),
        ("life_insurance", "Life Insurance"),
        ("line_of_credit", "Line of Credit"),
        ("lira", "LIRA"),
        ("lrif", "LRIF"),
        ("lrsp", "LRSP"),
        ("mutual_fund", "Mutual Fund"),
        ("non_custodial_wallet", "Non-custodial Wallet"),
        ("non_taxable_brokerage_account", "Non-taxable Brokerage Account"),
        ("other_annuity", "Other Annuity"),
        ("other_insurance", "Other Insurance"),
        ("pension", "Pension"),
        ("prediction_market", "Prediction Market"),
        ("prif", "PRIF"),
        ("profit_sharing_plan", "Profit Sharing Plan"),
        ("qshr", "QSHR"),
        ("rdsp", "RDSP"),
        ("resp", "RESP"),
        ("retirement", "Retirement"),
        ("rlif", "RLIF"),
        ("roth", "Roth"),
        ("roth_401k", "Roth 401k"),
        ("roth_403b", "Roth 403b"),
        ("roth_457b", "Roth 457b"),
        ("roth_pension", "Roth Pension"),
        ("roth_profit_sharing_plan", "Roth Profit Sharing Plan"),
        ("roth_thrift_savings_plan", "Roth Thrift Savings Plan"),
        ("rrif", "RRIF"),
        ("rrsp", "RRSP"),
        ("sarsep", "SARSEP"),
        ("sep_ira", "SEP IRA"),
        ("simple_ira", "SIMPLE IRA"),
        ("sipp", "SIPP"),
        ("stock_plan", "Stock Plan"),
        ("tfsa", "TFSA"),
        ("thrift_savings_plan", "Thrift Savings Plan"),
        ("trust", "Trust"),
        ("ugma", "UGMA"),
        ("utma", "UTMA"),
        ("variable_annuity", "Variable Annuity"),
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
