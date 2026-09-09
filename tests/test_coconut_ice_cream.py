import importlib

import pytest
from thaitruck import coconut_ice_cream

coconut_ice_cream_module = importlib.import_module("thaitruck.coconut_ice_cream")


class TestClearCache:
    def test_removes_cache_dir_contents(self, tmp_path):
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "entry.pkl").write_bytes(b"data")

        coconut_ice_cream(clear_cache=True, cache_dir=cache_dir)
        assert not cache_dir.exists()

    def test_missing_cache_dir_is_a_noop(self, tmp_path):
        cache_dir = tmp_path / "does_not_exist"
        coconut_ice_cream(clear_cache=True, cache_dir=cache_dir)  # should not raise

    def test_clear_cache_false_leaves_dir_untouched(self, tmp_path):
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "entry.pkl").write_bytes(b"data")

        coconut_ice_cream(clear_cache=False, cache_dir=cache_dir)
        assert (cache_dir / "entry.pkl").exists()


class TestFlushTemp:
    def test_flush_temp_calls_gc_collect(self, monkeypatch):
        called = []
        monkeypatch.setattr(coconut_ice_cream_module.gc, "collect", lambda: called.append(True))
        coconut_ice_cream(flush_temp=True)
        assert called == [True]

    def test_flush_temp_false_does_not_call_gc(self, monkeypatch):
        called = []
        monkeypatch.setattr(coconut_ice_cream_module.gc, "collect", lambda: called.append(True))
        coconut_ice_cream(flush_temp=False)
        assert called == []


class TestNoArgs:
    def test_no_args_is_a_noop(self):
        coconut_ice_cream()  # should not raise
