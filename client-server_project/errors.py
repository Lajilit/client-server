class RequiredFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}'


class ServerError(Exception):
    def __init__(self, error_text):
        self.error_text = error_text

    def __str__(self):
        return self.error_text