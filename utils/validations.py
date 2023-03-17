import re
from django.core.exceptions import ValidationError


def phone_number_validation(number):
    x = re.findall("^9|^4|^5", number)

    if x and x[0] == "9" and len(number) != 10:
        raise ValidationError("Number must be of length 10")
    elif x and (x[0] == "4" or x[0] == "5") and len(number) != 7:
        raise ValidationError("Number must be of length 7")
    elif not x:
        raise ValidationError("Number must start with either 9 or 4 or 5")


def mobile_number_validation(number):
    x = re.findall("^9", number)

    if x and x[0] == "9" and len(number) != 10:
        raise ValidationError("Number must be of length 10")
    elif x and (x[0] == "4" or x[0] == "5") and len(number) != 7:
        raise ValidationError("Number must be of length 7")
    elif not x:
        raise ValidationError("Number must start with either 9 or 4 or 5")
