import pandas as pd
import pytest
from thaitruck import (
    fried_rice,
    orange_chicken,
    larb,
    satay,
    ThaiTruckError,
    DateColumnNotFound,
    InvalidHeatLevel,
    SkewTypeError,
)


class TestHierarchy:
    def test_date_column_not_found_is_thaitruck_error(self):
        assert issubclass(DateColumnNotFound, ThaiTruckError)

    def test_invalid_heat_level_is_thaitruck_error(self):
        assert issubclass(InvalidHeatLevel, ThaiTruckError)

    def test_skew_type_error_is_thaitruck_error(self):
        assert issubclass(SkewTypeError, ThaiTruckError)

    def test_date_column_not_found_is_value_error(self):
        assert issubclass(DateColumnNotFound, ValueError)

    def test_invalid_heat_level_is_value_error(self):
        assert issubclass(InvalidHeatLevel, ValueError)

    def test_skew_type_error_is_type_error(self):
        assert issubclass(SkewTypeError, TypeError)


class TestRaisedByFunctions:
    def test_fried_rice_raises_date_column_not_found(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with pytest.raises(DateColumnNotFound):
            fried_rice(df)

    def test_orange_chicken_raises_invalid_heat_level(self):
        with pytest.raises(InvalidHeatLevel):
            orange_chicken(pd.DataFrame({"a": [1]}), heat=9)

    def test_larb_raises_invalid_heat_level(self):
        with pytest.raises(InvalidHeatLevel):
            larb(pd.DataFrame({"a": [1]}), heat=9)

    def test_satay_raises_skew_type_error(self):
        with pytest.raises(SkewTypeError):
            satay(pd.DataFrame({"a": [1]}), 42)

    def test_still_catchable_as_thaitruck_error(self):
        with pytest.raises(ThaiTruckError):
            orange_chicken(pd.DataFrame({"a": [1]}), heat=9)
