class AutofillAddressBase:
    def __init__(
        self,
        name: str | None,
        organization: str | None,
        street_address: str | None,
        address_level_2: str | None,
        address_level_1: str | None,
        postal_code: str | None,
        country: str | None,
        email: str | None,
        telephone: str | None,
    ):
        """
        This class instantiates an AutofillAddress object that can be extended in future autofill related objects.

        Attributes
        ----------
        name : str | None
            The name of the individual or entity at the address.
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
        email : str | None
            The email address associated with the address.
        telephone : str | None
            The telephone number associated with the address.
        """
        self.name = name
        self.organization = organization
        self.street_address = street_address
        self.address_level_2 = address_level_2
        self.address_level_1 = address_level_1
        self.postal_code = postal_code
        self.country = country
        self.email = email
        self.telephone = telephone
