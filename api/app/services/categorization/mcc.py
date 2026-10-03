"""Merchant category codes (ISO 18245 MCC) mapped to CREAM's system category keys.

Grouping follows Plaid's personal finance taxonomy as a guide, adapted to Monarch's categories.
Codes that don't say enough about the purchase (e.g. 5511 car dealers, 6051 quasi-cash,
4829 money transfers) are left out on purpose: those transactions stay in Uncategorized.
Pure module: no database, no network.
"""

from collections.abc import Mapping

# Category key -> the MCCs (single codes, or ranges with an exclusive end) that map to it
_CODES_BY_CATEGORY: Mapping[str, tuple[int | range, ...]] = {
    # Food & Dining
    "food_and_dining.groceries": (5411, 5422, 5441, 5451, 5462, 5499),
    "food_and_dining.restaurants_and_bars": (5811, 5812, 5813, 5814),
    # Auto & Transport
    "auto_and_transport.public_transit": (4111, 4112, 4131, 4789),
    "auto_and_transport.taxi_and_ride_shares": (4121,),
    "auto_and_transport.gas": (5172, 5541, 5542, 5552),
    "auto_and_transport.parking_and_tolls": (4784, 7523),
    "auto_and_transport.auto_maintenance": (5531, 5532, 5533, 7531, 7534, 7535, 7538, 7542, 7549),
    # Travel & Lifestyle
    "travel_and_lifestyle.travel_and_vacation": (
        range(3000, 3300),  # airlines
        range(3351, 3442),  # car rental agencies
        range(3501, 4000),  # hotels and resorts
        4411, 4468, 4511, 4582, 4722, 7011, 7012, 7032, 7033, 7512, 7513,
    ),
    "travel_and_lifestyle.entertainment_and_recreation": (
        5735, 5815, 5816, 5818, 7829, 7832, 7841, 7911, 7922, 7929, 7932, 7933, 7941,
        7991, 7992, 7993, 7994, 7995, 7996, 7998, 7999,
    ),
    "travel_and_lifestyle.personal": (5977, 7210, 7211, 7216, 7230, 7251, 7297, 7298),
    "travel_and_lifestyle.pets": (742, 5995),
    # Shopping
    "shopping.shopping": (
        5262, 5300, 5310, 5311, 5331, 5399, 5733, 5931, 5932, 5933, 5937, 5940, 5941, 5942, 5943,
        5944, 5945, 5948, 5949, 5950, 5970, 5971, 5972, 5973, 5993, 5999,
        range(5961, 5970),  # direct marketing and catalog merchants (5960 is insurance)
    ),
    "shopping.clothing": (
        5137, 5139, 5611, 5621, 5631, 5641, 5651, 5655, 5661, 5681, 5691, 5697, 5698, 5699,
    ),
    "shopping.furniture_and_housewares": (5712, 5713, 5714, 5718, 5719, 5722, 7641),
    "shopping.electronics": (5045, 5732, 5734, 5817, 5946, 7622),
    # Housing
    "housing.home_improvement": (
        1520, 1711, 1731, 1740, 1750, 1761, 1771, 1799, 5200, 5211, 5231, 5251, 5261,
    ),
    # Bills & Utilities
    "bills_and_utilities.gas_and_electric": (4900, 5983),
    "bills_and_utilities.internet_and_cable": (4816, 4899),
    "bills_and_utilities.phone": (4812, 4814, 4821),
    # Health & Wellness
    "health_and_wellness.medical": (
        5047, 5122, 5912, 5975, 5976, 8011, 8031, 8041, 8042, 8043, 8049, 8050, 8062, 8071, 8099,
    ),
    "health_and_wellness.dentist": (8021,),
    "health_and_wellness.fitness": (7997,),
    # Children and Education
    "children.child_care": (8351,),
    "education.education": (8211, 8220, 8241, 8244, 8249, 8299),
    # Gifts & Donations
    "gifts_and_donations.gifts": (5947, 5992),
    "gifts_and_donations.charity": (8398, 8661),
    # Financial
    "financial.cash_and_atm": (6010, 6011),
    "financial.insurance": (5960, 6300, 6381, 6399),
    "financial.taxes": (9311,),
    "financial.financial_and_legal_services": (8111, 8931, 9211),
    # Business
    "business.advertising_and_promotion": (7311,),
    "business.office_supplies_and_expenses": (5044, 5111, 7338),
    "business.postage_and_shipping": (4214, 4215, 9402),
}


def _build_lookup() -> dict[int, str]:
    lookup: dict[int, str] = {}
    for category_key, entries in _CODES_BY_CATEGORY.items():
        for entry in entries:
            for code in entry if isinstance(entry, range) else (entry,):
                if code in lookup:
                    raise ValueError(f"MCC {code} is mapped twice ({lookup[code]}, {category_key})")
                lookup[code] = category_key
    return lookup


_CATEGORY_BY_CODE = _build_lookup()

# Every category key the mapping can produce
MCC_CATEGORY_KEYS: frozenset[str] = frozenset(_CODES_BY_CATEGORY)


def category_key_for_mcc(mcc: str | None) -> str | None:
    """The system category key for a 4-digit MCC, or None when the code isn't mapped."""
    if not mcc or not mcc.isdigit():
        return None
    return _CATEGORY_BY_CODE.get(int(mcc))
