from django.core.exceptions import ValidationError


def check_bank_account(value):
    for i in value[0:2]:
        if not i.isalpha():
            raise ValidationError("Невалидна банкова сметка")
    for i in value[2:4]:
        if not i.isdigit():
            raise ValidationError("Невалидна банкова сметка")
    for i in value[4:8]:
        if not i.isalpha():
            raise ValidationError("Невалидна банкова сметка")
    for i in value[8:]:
        if not i.isdigit():
            raise ValidationError("Невалидна банкова сметка")
    if len(value) > 22:
        raise ValidationError("Невалидна банкова сметка")