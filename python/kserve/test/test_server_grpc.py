import unittest
import pytest
import kserve
from libraries.get_tls_certs import get_secret_data


# Import Kserve
from typing import Dict, Union
from kserve import Model, ModelServer, model_server, InferRequest, InferOutput, InferResponse
from kserve.utils.utils import generate_uuid


#from ..kserve import InferRequest, InferResponse
#from ..kserve.model_server import Model, ModelServer
#from ..kserve.protocol.grpc.grpc_predict_v2_pb2 import ModelInferRequest


@pytest.fixture(scope="class")
def run_model(self, secure_grpc_server, server_key, server_cert, ca_cert, models):
    return ModelServer(
        secure_grpc_server=secure_grpc_server,
        server_key=server_key,
        server_cert=server_cert,
        ca_cert=ca_cert
    ).start([models])


#Minimal Kserve Model solely to return data to verify secure grpc, data irrelevant
class TestModel(kserve.Model): #Test model
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        self.ready = True
        pass

    #Returns a number + 1
    def predict(self, payload: InferRequest, headers: Dict[str, str] = None) -> InferResponse:
        req = payload.inputs[0]
        print(req)
        input_number = req.data[0] #Input should be a single number
        assert isinstance(input_number, (int, float)), "Data is not a number or float"
        result = [float(input_number + 1)]
        
        response_id = generate_uuid()
        infer_output = InferOutput(name="output-0", shape=[1], datatype="FP32", data=result)
        infer_response = InferResponse(model_name=self.name, infer_outputs=[infer_output], response_id=response_id)
        return infer_response

  
@pytest.mark.asyncio
class TestGrpcSecureServer:

    @pytest.mark.usefixtures("run_model")
    def test_secure_server_returns(self):
        # TODO: create certs
        server_key = "test"
        server_cert = "test"
        ca_cert = "test"
        models = [TestModel("test-model")]
        run_model(True, server_key, server_cert, ca_cert, models)

