import pandas as pd
import pytest
from thaitruck import TruckPipeline


class TestChaining:
    def test_orange_chicken_then_result(self):
        raw = pd.DataFrame({"Price": ["1.5", "2.0"]})
        result = TruckPipeline(raw).orange_chicken(heat=3).result()
        assert "price" in result.columns
        assert pd.api.types.is_numeric_dtype(result["price"])

    def test_orange_chicken_then_satay(self):
        raw = pd.DataFrame({"Sector": ["Tech", "Energy"], "Price": [10.0, 20.0]})
        result = (
            TruckPipeline(raw)
            .orange_chicken(heat=3)
            .satay({"sector": "Tech"})
            .result()
        )
        assert len(result) == 1
        assert result.iloc[0]["price"] == 10.0

    def test_full_chain_with_fried_rice(self):
        idx = pd.date_range("2024-01-01", periods=3, freq="D")
        raw = pd.DataFrame({"Price": [1.0, 2.0, 3.0]}, index=idx)
        other = pd.DataFrame({"volume": [10, 20, 30]}, index=idx)
        result = (
            TruckPipeline(raw)
            .orange_chicken(heat=3)
            .fried_rice(other, freq="D")
            .result()
        )
        assert "price" in result.columns
        assert "volume" in result.columns

    def test_orange_chicken_rename_dtypes_in_chain(self):
        raw = pd.DataFrame({"Open Price": ["1.5", "2.5"]})
        result = (
            TruckPipeline(raw)
            .orange_chicken(heat=1, rename={"open_price": "price"}, dtypes={"price": "float64"})
            .result()
        )
        assert result["price"].dtype == "float64"

    def test_fried_rice_join_in_chain(self):
        idx_a = pd.date_range("2024-01-01", periods=3, freq="D")
        idx_b = pd.date_range("2024-01-02", periods=3, freq="D")
        a = pd.DataFrame({"price": [1.0, 2.0, 3.0]}, index=idx_a)
        b = pd.DataFrame({"volume": [10, 20, 30]}, index=idx_b)
        result = TruckPipeline(a).fried_rice(b, join="inner").result()
        assert len(result) == 2

    def test_massaman_in_chain(self):
        df = pd.DataFrame({"price": [float(i) for i in range(1, 11)]})
        result = TruckPipeline(df).massaman("price", window=3, ops=["mean"]).result()
        assert "price_roll_mean_3" in result.columns

    def test_returns_dataframe(self):
        df = pd.DataFrame({"a": [1]})
        result = TruckPipeline(df).result()
        assert isinstance(result, pd.DataFrame)

    def test_intermediate_steps_return_pipeline(self):
        df = pd.DataFrame({"a": [1]})
        step = TruckPipeline(df).satay("a")
        assert isinstance(step, TruckPipeline)
