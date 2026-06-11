import time
from pathlib import Path
from unittest.mock import patch

import pytest
from thaitruck import sticky_rice


@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path / "cache"


class TestBasicCaching:
    def test_returns_correct_result(self, cache_dir):
        @sticky_rice(cache_dir=cache_dir)
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_caches_to_disk(self, cache_dir):
        @sticky_rice(cache_dir=cache_dir)
        def compute(x):
            return x * 10

        compute(7)
        assert any(cache_dir.glob("*.pkl"))

    def test_second_call_uses_cache(self, cache_dir):
        call_count = 0

        @sticky_rice(cache_dir=cache_dir)
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        expensive(5)
        expensive(5)
        assert call_count == 1

    def test_different_args_computed_separately(self, cache_dir):
        call_count = 0

        @sticky_rice(cache_dir=cache_dir)
        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        fn(1)
        fn(2)
        assert call_count == 2


class TestTTL:
    def test_expired_cache_recomputes(self, cache_dir):
        call_count = 0

        @sticky_rice(ttl=60, cache_dir=cache_dir)
        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        with patch("thaitruck.sticky_rice.time") as mock_time:
            mock_time.time.return_value = 1000.0
            fn(1)
            assert call_count == 1

            mock_time.time.return_value = 1000.0 + 61
            fn(1)
            assert call_count == 2

    def test_ttl_zero_never_expires(self, cache_dir):
        call_count = 0

        @sticky_rice(ttl=0, cache_dir=cache_dir)
        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        with patch("thaitruck.sticky_rice.time") as mock_time:
            mock_time.time.return_value = 1000.0
            fn(1)
            mock_time.time.return_value = 9999999.0
            fn(1)
        assert call_count == 1


class TestBareDecorator:
    def test_bare_decorator_works(self, cache_dir):
        # @sticky_rice without parentheses — can't inject cache_dir this way,
        # so just verify the decorated function still returns the right value
        @sticky_rice
        def greet(name):
            return f"hello {name}"

        assert greet("world") == "hello world"


class TestFixedKey:
    def test_fixed_key_shares_cache_across_calls(self, cache_dir):
        call_count = 0

        @sticky_rice(key="shared", cache_dir=cache_dir)
        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        fn(1)
        fn(99)  # different args, same key
        assert call_count == 1

    def test_clear_removes_fixed_key_file(self, cache_dir):
        @sticky_rice(key="mykey", cache_dir=cache_dir)
        def fn(x):
            return x

        fn(1)
        assert (cache_dir / "mykey.pkl").exists()
        fn.clear()
        assert not (cache_dir / "mykey.pkl").exists()


class TestClear:
    def test_clear_forces_recompute(self, cache_dir):
        call_count = 0

        @sticky_rice(key="ck", cache_dir=cache_dir)
        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        fn(1)
        fn.clear()
        fn(1)
        assert call_count == 2
