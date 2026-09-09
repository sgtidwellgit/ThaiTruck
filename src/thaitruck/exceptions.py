"""exceptions — package-specific exception types for cleaner downstream handling."""


class ThaiTruckError(Exception):
    """Base class for all ThaiTruck exceptions."""


class DateColumnNotFound(ThaiTruckError, ValueError):
    """Raised when fried_rice cannot detect or validate a date column."""


class InvalidHeatLevel(ThaiTruckError, ValueError):
    """Raised when a heat parameter is outside its valid range."""


class SkewTypeError(ThaiTruckError, TypeError):
    """Raised when satay receives an unrecognised skewer type."""
