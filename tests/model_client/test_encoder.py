import os

from nlm_utils.model_client import EncoderClient


URL = os.getenv("MODEL_SERVER_URL")


class TestEncoder:
    def test_encoder_client_sif(self):
        encoder = "sif"
        client = EncoderClient(encoder, URL)
        embs = client(["test"])["embeddings"]
        assert isinstance(embs, list)

    def test_encoder_client_sif_empty_input(self):
        encoder = "sif"
        client = EncoderClient(encoder, URL)
        embs = client([])["embeddings"]
        assert embs == []
