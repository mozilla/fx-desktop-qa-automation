from dataclasses import dataclass


@dataclass
class AutofillAddressBase:
    name: str = ""
    organization: str = ""
    street_address: str = ""
    address_level_2: str = ""
    address_level_1: str = ""
    postal_code: str = ""
    country: str = ""
    email: str = ""
    telephone: str = ""
    """
    This class instantiates an AutofillAddress object that can be extended in future autofill related objects.

    Attributes
    ----------
    name : str
        The name of the individual or entity at the address.
    organization : str
        The name of the organization or company at the address.
    street_address : str
        The primary street address.
    address_level_2 : str
        Additional address detail, such as suite or apartment number.
    address_level_1 : str
        A higher level of address detail, typically state, region, or province.
    postal_code : str
        The postal code for the address.
    country : str
        The country of the address.
    email : str
        The email address associated with the address.
    telephone : str
        The telephone number associated with the address.
    """
