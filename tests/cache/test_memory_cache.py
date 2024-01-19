from nlm_utils.cache import Cache


class TestCache:
    def test_cache(self):

        cache = Cache("MemoryAgent")
        assert cache.connected

        @cache
        def function1(a):
            return a

        @cache
        def function2(a):
            return a

        cache.reset()

        assert function1(1) == 1
        assert function1(1, overwrite=False) == 1
        assert function1(1, overwrite=True) == 1
        assert function1(1) == 1

        assert function1(2) == 2
        assert function1(2, overwrite=False) == 2
        assert function1(2, overwrite=True) == 2
        assert function1(2) == 2

    def test_cache_with_prefix(self):

        cache = Cache("MemoryAgent", prefix="prefix")
        assert cache.connected

        @cache
        def function1(a):
            return a

        @cache
        def function2(a):
            return a

        cache.reset()

        assert function1(1) == 1
        assert function1(1, overwrite=False) == 1
        assert function1(1, overwrite=True) == 1
        assert function1(1) == 1

        assert function1(2) == 2
        assert function1(2, overwrite=False) == 2
        assert function1(2, overwrite=True) == 2
        assert function1(2) == 2
