import pandas as pd
import pytest
import thaitruck  # noqa: F401  registers the `.truck` accessor


class TestAccessorRegistration:
    def test_truck_accessor_available_on_any_dataframe(self):
        df = pd.DataFrame({"a": [1]})
        assert hasattr(df, "truck")


class TestAccessorMethods:
    def test_orange_chicken(self):
        df = pd.DataFrame({"Price": ["1.5", "2.0"]})
        result = df.truck.orange_chicken(heat=3)
        assert "price" in result.columns

    def test_larb(self):
        df = pd.DataFrame({"price": [1.0, 2.0, 3.0]})
        result = df.truck.larb()
        assert "price" in result.index

    def test_satay(self):
        df = pd.DataFrame({"sector": ["Tech", "Energy"], "price": [10.0, 20.0]})
        result = df.truck.satay({"sector": "Tech"})
        assert len(result) == 1

    def test_fried_rice(self):
        idx = pd.date_range("2024-01-01", periods=3, freq="D")
        a = pd.DataFrame({"price": [1.0, 2.0, 3.0]}, index=idx)
        b = pd.DataFrame({"volume": [10, 20, 30]}, index=idx)
        result = a.truck.fried_rice(b, freq="D")
        assert "volume" in result.columns

    def test_massaman(self):
        df = pd.DataFrame({"price": [float(i) for i in range(1, 11)]})
        result = df.truck.massaman("price", window=3, ops=["mean"])
        assert "price_roll_mean_3" in result.columns

    def test_orange_chicken_rename_dtypes(self):
        df = pd.DataFrame({"Price": ["1.5"]})
        result = df.truck.orange_chicken(heat=1, rename={"price": "p"}, dtypes={"p": "float64"})
        assert result["p"].dtype == "float64"

    def test_larb_include_exclude(self):
        df = pd.DataFrame({"price": [1.0], "id": [1]})
        result = df.truck.larb(exclude=["id"])
        assert set(result.index) == {"price"}

    def test_fried_rice_join(self):
        idx_a = pd.date_range("2024-01-01", periods=3, freq="D")
        idx_b = pd.date_range("2024-01-02", periods=3, freq="D")
        a = pd.DataFrame({"price": [1.0, 2.0, 3.0]}, index=idx_a)
        b = pd.DataFrame({"volume": [10, 20, 30]}, index=idx_b)
        result = a.truck.fried_rice(b, join="left")
        assert len(result) == 3

    def test_nam_pla(self):
        df = pd.DataFrame({"price": [-5.0, 10.0]})
        result = df.truck.nam_pla({"price": {"min": 0}})
        assert (result["check"] == "min").any()

    def test_does_not_mutate_original(self):
        df = pd.DataFrame({"Price": ["1.5"]})
        original_cols = list(df.columns)
        df.truck.orange_chicken()
        assert list(df.columns) == original_cols
