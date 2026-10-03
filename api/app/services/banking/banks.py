"""The banks a user can connect in a country: Enable Banking's list with what our catalog adds."""

from app.schemas.bank import AspspRead
from app.services.banking.client import BankClient
from app.services.banking.institutions import find_institution, popularity


def available_banks(country: str, client: BankClient) -> list[AspspRead]:
    """The country's banks, the most popular first in their order (Monarch's "Most popular"), then the rest."""
    banks = []
    for aspsp in client.list_aspsps(country):
        institution = find_institution(aspsp["name"])
        rank = popularity(country, aspsp["name"])
        banks.append((rank, AspspRead(
            name=aspsp["name"],
            country=aspsp["country"],
            logo=aspsp.get("logo"),
            website=institution.website if institution else None,
            popular=rank is not None,
        )))
    # Stable sort: popular by rank, the rest keep the provider's order
    banks.sort(key=lambda item: (item[0] is None, item[0] or 0))
    return [bank for _, bank in banks]
