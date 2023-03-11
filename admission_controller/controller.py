import logging
import sys

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import Optional, Any, Union


def logger(name: str = __name__) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler(sys.stdout))
    return log


app = FastAPI()


class KubernetesAdmissionRequestNestedContent(BaseModel):
    uid: str
    kind: dict
    resource: dict
    request_kind: dict = Field(alias="requestKind")
    request_resource: dict = Field(alias="requestResource")
    name: str
    namespace: str
    operation: str
    user_info: dict = Field(alias="userInfo")
    object: dict
    old_object: Optional[dict] = Field(alias="oldObject")
    dry_run: Union[str, bool] = Field(alias="dryRun")
    options: Optional[dict]


class KubernetesAdmissionRequest(BaseModel):
    kind: Any
    request: KubernetesAdmissionRequestNestedContent
    resource: Any
    request_kind: Optional[dict] = Field(alias="requestKind")
    request_resource: Optional[dict] = Field(alias="requestResource")
    name: Optional[str]
    namespace: Optional[str]
    operation: Optional[str]
    user_info: Optional[dict] = Field(alias="userInfo")
    object: Optional[dict]
    old_object: Optional[dict] = Field(alias="oldObject")
    dry_run: Optional[str] = Field(alias="dryRun")
    options: Optional[dict]


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc),
            "message": "incorrect admission request content"
        }
    )


@app.post("/")
async def admission_controller(
        request: KubernetesAdmissionRequest,
        log: logging.Logger = Depends(logger)
):
    log.debug("admission controller received request")
    log.debug(f"request uid: {request.request.uid}")
    log.debug(f"request details: kind={request.request.kind.get('kind')},"
              f" operation={request.request.operation},"
              f" namespace={request.request.namespace}")
    log.debug(f"requested by: {request.request.user_info}")

    # after validation steps:
    return {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": request.request.uid,
            "allowed": True
        }
    }
