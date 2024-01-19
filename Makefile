PROTOC_OUTDIR := nlm_utils

compile:
	@python -m grpc_tools.protoc \
			-I $(PROTOC_OUTDIR)/protos \
			--python_out=./$(PROTOC_OUTDIR)/grpc_pb2 \
			--grpc_python_out=./$(PROTOC_OUTDIR)/grpc_pb2 \
			./$(PROTOC_OUTDIR)/protos/*.proto
	#sed -i -E 's/^import.*_pb2/from . \0/' $(PROTOC_OUTDIR)/grpc_pb2/*_pb2_grpc.py
