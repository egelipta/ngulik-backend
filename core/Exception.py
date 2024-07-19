# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Maintainer: dgos
@Des: Abnormal treatment
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Union
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from tortoise.exceptions import OperationalError, DoesNotExist, IntegrityError, ValidationError as MysqlValidationError


async def mysql_validation_error(_: Request, exc: MysqlValidationError):
    """
    Database field verification error
    :param _:
    :param exc:
    :return:
    """
    print("ValidationError", exc)
    return JSONResponse({
        "code": -1,
        "message": exc.__str__(),
        "data": []
    }, status_code=422)


async def mysql_integrity_error(_: Request, exc: IntegrityError):
    """
    Integrity error
    :param _:
    :param exc:
    :return:
    """
    print("IntegrityError", exc)
    return JSONResponse({
        "code": -1,
        "message": exc.__str__(),
        "data": []
    }, status_code=422)


async def mysql_does_not_exist(_: Request, exc: DoesNotExist):
    """
    mysql There is no abnormal treatment in the query object
    :param _:
    :param exc:
    :return:
    """
    print("DoesNotExist", exc)
    return JSONResponse({
        "code": -1,
        "message": "The requests are targeted at non -existent records, and the server does not operate.",
        "data": []
    }, status_code=404)


async def mysql_operational_error(_: Request, exc: OperationalError):
    """
    mysql Database abnormal error treatment
    :param _:
    :param exc:
    :return:
    """
    print("OperationalError", exc)
    return JSONResponse({
        "code": -1,
        "message": "Data operation failure",
        "data": []
    }, status_code=500)


async def http_error_handler(_: Request, exc: HTTPException):
    """
    http exception processing
    :param _:
    :param exc:
    :return:
    """
    if exc.status_code == 401:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    return JSONResponse({
        "code": exc.status_code,
        "message": exc.detail,
        "data": exc.detail
    }, status_code=exc.status_code, headers=exc.headers)


class UnicornException(Exception):

    def __init__(self, code, errmsg, data=None):
        """
        Failure return format
        :param code:
        :param errmsg:
        """
        if data is None:
            data = {}
        self.code = code
        self.errmsg = errmsg
        self.data = data


async def unicorn_exception_handler(_: Request, exc: UnicornException):
    """
    unicorn Abnormal treatment
    :param _:
    :param exc:
    :return:
    """
    return JSONResponse({
        "code": exc.code,
        "message": exc.errmsg,
        "data": exc.data,
    })


async def http422_error_handler(_: Request, exc: Union[RequestValidationError, ValidationError],) -> JSONResponse:
    """
    Parameter check error treatment
    :param _:
    :param exc:
    :return:
    """
    print("[422]", exc.errors())
    return JSONResponse(
        {
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": f"Data verification error {exc.errors()}",
            "data": exc.errors(),
        },
        status_code=422,
    )
