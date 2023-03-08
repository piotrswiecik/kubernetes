import os, sys
import requests
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError, IPvAnyAddress
from pydantic.tools import parse_obj_as


DEFAULT_SA_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"

app = FastAPI()


class ServiceAccountException(Exception):
    pass


class KubernetesException(Exception):
    pass


def check_service_account() -> str:
    """check if expected service account is loaded by kubernetes"""
    expected_sa = os.getenv("EXPECTED_SERVICE_ACCOUNT_NAME", "default")
    active_sa = os.getenv("ACTUAL_SERVICE_ACCOUNT_NAME", None)

    if not active_sa:
        raise ServiceAccountException("service account not set in pod")

    if expected_sa != active_sa:
        raise ServiceAccountException(f"sa mismatch: expected {expected_sa}, got {active_sa}")

    return active_sa


def service_account_token(path: str = DEFAULT_SA_PATH) -> str:
    """extract service account token from file"""
    check_service_account()  # potentially raises ServiceAccountException

    try:
        with open(path, "r") as token_file:
            token = token_file.read()
    except OSError as e:
        raise ServiceAccountException from e

    return token


def apiserver_endpoint() -> str:
    """validate kube-apiserver endpoint & return as str"""
    ip = os.environ.get("APISERVER_IP")
    port = os.environ.get("APISERVER_PORT")

    if not ip or not port:
        raise KubernetesException("apiserver endpoint not configured")

    try:
        parse_obj_as(IPvAnyAddress, ip)
        int(port)
    except (ValidationError, ValueError):
        raise KubernetesException("apiserver endpoint format invalid")

    return f"{ip}:{port}"


@app.exception_handler(ServiceAccountException)
def handle_service_account_exception(request: Request, exc: ServiceAccountException):
    """overrides custom exception handling to intercept missing sa token"""
    return JSONResponse(status_code=401, content={"error": "unauthorized"})


@app.exception_handler(KubernetesException)
def handle_kubernetes_apiserver_exception(request: Request, exc: KubernetesException):
    """overrides custom exception handling for kube api related error"""
    return JSONResponse(status_code=500, content={
        "error": exc,
        "message": "kube-apiserver error"
    })


@app.get("/nodes")
async def get_nodes(
        token: bytes = Depends(service_account_token),
        endpoint: str = Depends(apiserver_endpoint)
):
    """list all kubernetes nodes"""
    response = requests.get(
        url=f"https://{endpoint}/api/v1/namespaces/default/pods",
        headers={
            "Authorization": f"Bearer {token}"
        },
        verify=False
    )
    return {
        "response_code": response.status_code,
        "response_body": response.content
    }
