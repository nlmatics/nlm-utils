from nlm_utils.cache import Cache


class DummyObject:
    uid = 12345


class TestCache:
    def test_cache(self):

        cache = Cache("FileAgent", path=".cache")
        assert cache.connected is True

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

    def test_cache_with_path(self):
        cache = Cache("FileAgent", path=".cache")
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

    def test_cache_with_path_collection(self):
        cache = Cache("FileAgent", path=".cache", collection="collection")
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

    def test_cache_with_cache_key(self):

        cache = Cache("FileAgent", path=".cache")
        assert cache.connected is True

        @cache
        def function1(a):
            return a

        @cache
        def function2(a):
            return a

        cache.reset()

        assert function1(1, cache_key="cache_key") == 1
        assert function1(1, cache_key="cache_key", overwrite=False) == 1
        assert function1(1, cache_key="cache_key", overwrite=True) == 1
        assert function1(1, cache_key="cache_key") == 1

        cache.reset()

    def test_cache_with_uid(self):

        cache = Cache("FileAgent", path=".cache")
        assert cache.connected is True

        @cache
        def function1(a):
            return a

        @cache
        def function2(a):
            return a

        obj = DummyObject()

        cache.reset()

        assert function1(obj, cache_key="cache_key").uid == obj.uid
        assert function1(obj, cache_key="cache_key", overwrite=False).uid == obj.uid
        assert function1(obj, cache_key="cache_key", overwrite=True).uid == obj.uid
        assert function1(obj, cache_key="cache_key").uid == obj.uid

        # cache.reset()
