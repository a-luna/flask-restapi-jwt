"""Reports the results of an operation."""

class Result():

    def __init__(self, success, value=None, error=None):
        self.success = success
        self.error = error
        self.value = value

    @property
    def failure(self):
        return not self.success

    @failure.setter
    def failure(self, failure):
        raise AttributeError('failure: read-only field')

    def __str__(self):
        if self.success:
            return f'[Success]'
        else:
            return f'[Failure] {self.error}'

    def __repr__(self):
        return f'Result(success={self.success}, message="{self.error}")'

    @staticmethod
    def Fail(message):
        return Result(False, error=message)

    @staticmethod
    def Ok(value=None):
        return Result(True, value=value)