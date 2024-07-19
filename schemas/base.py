# -*- coding:utf-8 -*-
"""
@Time : 2022/5/4 10:54 PM
@Maintainer: dgos
@Des: 基础schemas
"""
from pydantic import BaseModel, Field
from typing import List, Any, Optional


class BaseResp(BaseModel):
    code: int = Field(description="status code")
    message: str = Field(description="message")
    data: List = Field(description="data")


class ResAntTable(BaseModel):
    success: bool = Field(description="status code")
    data: List = Field(description="data")
    total: int = Field(description="total")


class WebsocketMessage(BaseModel):
    action: Optional[str]
    user: Optional[int]
    data: Optional[Any]


class WechatOAuthData(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    unionid: Optional[str]
    scope: str
    openid: str


class WechatUserInfo(BaseModel):
    openid: str
    nickname: str
    sex: int
    city: str
    province: str
    country: str
    headimgurl: str
    unionid: Optional[str]
