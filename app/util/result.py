class Result():
    """Represents the outcome of an operation.

    Attributes
    ----------
    success : bool
        A flag that is set to True if the operation was successful, False if
        the operation failed.
    value :
        The result of the operation if successful, value is None if operation
        failed or if the operation has no return value.
    error : str
        Error message detailing why the operation failed, value is None if
        operation was successful.

    Methods
    -------
    Fail(message)
        Class method which creates a Result object for a failed operation,
        must provide an error message which details why the operation failed.
    Ok(value=None)
        Class method which creates a Result object for a successful operation,
        if the operation produces a result it is provided in the 'value'
        parameter.

    Raises
    ------
    AttributeError
        If value for 'failure' is changed, since this field is read-only.
    """

    def __init__(self, success, value, error):
        """Represents the outcome of an operation.

        Parameters
        ----------
        success : bool
            A flag that is set to True if the operation was successful, False if
            the operation failed.
        value :
            The result of the operation if successful, value is None if operation
            failed or if the operation has no return value.
        error : str
            Error message detailing why the operation failed, value is None if
            operation was successful.
        """
        self.success = success
        self.error = error
        self.value = value

    @property
    def failure(self):
        """True if operation failed, False if successful (read-only)."""
        return not self.success

    def __str__(self):
        if self.success:
            return f'[Success]'
        else:
            return f'[Failure] {self.error}'

    def __repr__(self):
        if self.success:
            return f'Result<(success={self.success}>'
        else:
            return f'Result<(success={self.success}, message="{self.error}")>'

    @classmethod
    def Fail(cls, error_message):
        """Create a Result object for a failed operation.

        Parameters
        ----------
        error_message : str
            Error message detailing why the operation failed.

        Returns
        -------
        Result
            A Result with error message detailing reason for failure.
        """
        return cls(False, value=None, error=error_message)

    @classmethod
    def Ok(cls, value=None):
        """Create a Result object for a successful operation.

        Parameters
        ----------
        value : object, optional
            The return value of the successful operation (default is None).

        Returns
        -------
        Result
            A Result with the return value of the successful operation, if any.
        """
        return cls(True, value=value, error=None)