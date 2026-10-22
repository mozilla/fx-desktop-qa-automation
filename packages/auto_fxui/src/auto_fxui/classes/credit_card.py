from dataclasses import dataclass


@dataclass
class CreditCardBase:
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    card_number: str | None = None
    expiration_month: str | None = None
    expiration_year: str | None = None
    expiration_date: str | None = None
    telephone: str | None = None
    cvv: str | None = None
    """
    This class instantiates a CreditCardBase object that can be extended in future autofill related objects.

    Attributes
    ----------
    name : str | None
        The name of the cardholder.
    given_name : str | None
        First Name of the individual or entity at the address
    family_name : str | None
        Last Name of the individual or entity at the address
    card_number : str | None
        The credit card number.
    expiration_month : str | None
        The month when the credit card expires.
    expiration_year : str | None
        The year when the credit card expires.
    expiration_date : str | None
        The year and month when the credit card expires.
    telephone : str | None
        The telephone number associated with the credit card owner.
    cvv : str | None
        The Card Verification Value (CVV) associated with the credit card.
    """
