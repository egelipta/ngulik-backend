# -*- coding:utf-8 -*-
"""
@Time : 2022/6/16 6:17 PM
@Maintainer: dgos
@Des: public
"""
from fastapi import Request
from models.base import AccessLog


async def write_access_log(req: Request, user_id: int,  note: str = None):
    """
    Write access log
    :param user_id: User ID
    :param req: Request
    :param note: Remark
    :return:
    """
    data = {
        "user_id": user_id,
        "target_url": req.get("path"),
        "user_agent": req.headers.get('user-agent'),
        "request_params": {
            "method": req.method,
            "params": dict(req.query_params),
            "body": bytes(await req.body()).decode()
        },
        "ip": req.headers.get('x-forwarded-for'),
        "note": note
    }
    await AccessLog.create(**data)
