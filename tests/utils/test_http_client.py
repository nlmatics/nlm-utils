from nlm_utils.utils import AsyncHttpClient


def test_async_http_client():
    client = AsyncHttpClient(out_protocal="text", in_protocal="text")

    client.get("https://www.google.com")
    raw_outputs = client.run()

    assert len(raw_outputs) == 1
