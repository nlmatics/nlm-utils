import logging
from timeit import default_timer

import grpc

from nlm_utils.grpc_pb2.search_engine_pb2 import AddToIndexRequest
from nlm_utils.grpc_pb2.search_engine_pb2 import CreateIndexRequest
from nlm_utils.grpc_pb2.search_engine_pb2 import GetCandidatesRequest
from nlm_utils.grpc_pb2.search_engine_pb2_grpc import SearchEngineStub


class SearchEngineClient:
    def __init__(self, host="localhost", port="50051"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = SearchEngineStub(self.channel)

    def get_candidates(
        self,
        templates,
        questions,
        headers,
        workspace_idx,
        file_idx,
        matches_per_doc,
    ):
        request = GetCandidatesRequest(
            templates=templates,
            questions=questions,
            headers=headers,
            workspace_idx=workspace_idx,
            file_idx=file_idx or "",
            matches_per_doc=matches_per_doc,
        )
        wall_time = default_timer()
        yield from self.stub.get_candidates(request)

        wall_time = (default_timer() - wall_time) * 1000

        self.logger.info(
            f"{self.__class__.__name__} Finished. Wall time: {wall_time:.2f}ms",
        )

    async def async_get_candidates(
        self,
        templates,
        questions,
        headers,
        workspace_idx,
        file_idx,
        matches_per_doc,
    ):
        request = GetCandidatesRequest(
            templates=templates,
            questions=questions,
            headers=headers,
            workspace_idx=workspace_idx,
            file_idx=file_idx or "",
            matches_per_doc=matches_per_doc,
        )
        wall_time = default_timer()
        candidates = self.stub.async_get_candidates(request).candidates

        wall_time = (default_timer() - wall_time) * 1000

        self.logger.info(
            f"{self.__class__.__name__} Finished. Wall time: {wall_time:.2f}ms",
        )
        return candidates

    def create_index(self, workspace_idx):

        request = CreateIndexRequest(workspace_idx=workspace_idx)
        wall_time = default_timer()
        yield from self.stub.create_index(request)

        wall_time = (default_timer() - wall_time) * 1000

        self.logger.info(
            f"{self.__class__.__name__} Finished. Wall time: {wall_time:.2f}ms",
        )

    def add_to_index(self, workspace_idx, file_idx=None):

        request = AddToIndexRequest(workspace_idx=workspace_idx, file_idx=file_idx)
        wall_time = default_timer()
        yield from self.stub.add_to_index(request)

        wall_time = (default_timer() - wall_time) * 1000

        self.logger.info(
            f"{self.__class__.__name__} Finished. Wall time: {wall_time:.2f}ms",
        )
