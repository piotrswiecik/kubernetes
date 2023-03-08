import pytest

from service_acc.cluster import (check_service_account, ServiceAccountException, apiserver_endpoint, KubernetesException)


def test_check_service_account_ok(monkeypatch):
    """positive scenario - expected serviceaccount == actual pod serviceaccount"""
    monkeypatch.setenv(name="EXPECTED_SERVICE_ACCOUNT_NAME", value="default")
    monkeypatch.setenv(name="ACTUAL_SERVICE_ACCOUNT_NAME", value="default")

    assert check_service_account() == "default"


def test_check_service_account_mismatch(monkeypatch):
    """negative scenario - expected != wanted"""
    monkeypatch.setenv(name="EXPECTED_SERVICE_ACCOUNT_NAME", value="a")
    monkeypatch.setenv(name="ACTUAL_SERVICE_ACCOUNT_NAME", value="b")

    with pytest.raises(ServiceAccountException):
        check_service_account()


def test_check_apiserver_endpoint_ok(monkeypatch):
    """apiserver url is a proper ip:port combo"""
    monkeypatch.setenv(name="APISERVER_IP", value="10.0.0.10")
    monkeypatch.setenv(name="APISERVER_PORT", value="8443")

    assert apiserver_endpoint() == "10.0.0.10:8443"


def test_check_apiserver_endpoint_noip(monkeypatch):
    """missing apiserver ip"""
    monkeypatch.setenv(name="APISERVER_PORT", value="8443")

    with pytest.raises(KubernetesException):
        apiserver_endpoint()


def test_check_apiserver_endpoint_noport(monkeypatch):
    """missing apiserver port"""
    monkeypatch.setenv(name="APISERVER_IP", value="10.0.0.10")

    with pytest.raises(KubernetesException):
        apiserver_endpoint()


def test_check_apiserver_endpoint_badid(monkeypatch):
    """malformed apiserver ip"""
    monkeypatch.setenv(name="APISERVER_IP", value="what_is_this")
    monkeypatch.setenv(name="APISERVER_PORT", value="8443")

    with pytest.raises(KubernetesException):
        apiserver_endpoint()


def test_check_apiserver_endpoint_badport(monkeypatch):
    """malformed apiserver port"""
    monkeypatch.setenv(name="APISERVER_IP", value="10.0.0.10")
    monkeypatch.setenv(name="APISERVER_PORT", value="xyz")

    with pytest.raises(KubernetesException):
        apiserver_endpoint()