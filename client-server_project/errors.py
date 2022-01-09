class RequiredFieldMissedError(Exception):
    def __init__(self, missed_field):
        self.missed_field = missed_field

    def __str__(self):
        return f'Missed field {self.missed_field}'


class ServerError(Exception):
    def __init__(self, error_text):
        self.error_text = error_text

    def __str__(self):
        return self.error_text


class IncorrectDataReceivedError(Exception):
    def __str__(self):
        return 'Reseived message is incorrect'


class NonDictDataError(Exception):
    def __str__(self):
        return 'Data to send should be a dictionary'