# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 8:33 PM
@Maintainer: dgos
@Des: views home
"""
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", tags=["Home"], response_class=HTMLResponse)
async def home(request: Request):
    """
    Home
    :param request:
    :return:
    """
    return request.app.state.views.TemplateResponse("index.html", {"request": request})
