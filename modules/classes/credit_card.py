from dataclasses import dataclass


@dataclass
class CreditCardBase:
    name: str | None = None
    card_number: str | None = None
    expiration_month: str | None = None
    expiration_year: str | None = None
    cvv: str | None = None
    """
    This class instantiates a CreditCardBase object that can be extended in future autofill related objects.

    Attributes
    ----------
    name : str | None
        The name of the cardholder.
    card_number : str | None
        The credit card number.
    expiration_month : str | None
        The month when the credit card expires.
    expiration_year : str | None
        The year when the credit card expires.
    cvv : str | None
        The Card Verification Value (CVV) associated with the credit card.
    """
