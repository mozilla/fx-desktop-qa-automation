from dataclasses import dataclass


@dataclass
class AutofillAddressBase:
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    organization: str | None = None
    street_address: str | None = None
    address_level_2: str | None = None
    address_level_1: str | None = None
    postal_code: str | None = None
    country: str | None = None
    country_code: str | None = None
    email: str | None = None
    telephone: str | None = None
    """
    This class instantiates an AutofillAddress object that can be extended in future autofill related objects.

    Attributes
    ----------
    name : str | None
        The name of the individual or entity at the address.
    given_name : str | None
        First Name of the individual or entity at the address
    family_name : str | None
        Last Name of the individual or entity at the address
    organization : str | None
        The name of the organization or company at the address.
    street_address : str | None
        The primary street address.
    address_level_2 : str | None
        Additional address detail, such as suite or apartment number.
    address_level_1 : str | None
        A higher level of address detail, typically state, region, or province.
    postal_code : str | None
        The postal code for the address.
    country : str | None
        The country of the address.
    country_code: str | None
        The code of the country.
    email : str | None
        The email address associated with the address.
    telephone : str | None
        The telephone number associated with the address.
        """
