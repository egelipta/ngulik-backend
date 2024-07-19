# -*- coding:utf-8 -*-
"""
@Time : 2022/4/27 5:29 PM
@Maintainer: dgos
@Des: schemas模型
"""
from datetime import datetime
from pydantic import Field, BaseModel, validator
from typing import Optional, List
from schemas.base import BaseResp, ResAntTable


class CreateUser(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6, max_length=255)
    user_phone: Optional[str] = Field()
    user_status: Optional[bool]
    remarks: Optional[str]
    roles: Optional[List[int]]
    nickname: str = Field(min_length=3, max_length=25)
    user_type: Optional[bool]


class UpdateUser(BaseModel):
    id: int
    username: Optional[str] = Field(min_length=3, max_length=25)
    password: Optional[str] = Field(min_length=6, max_length=255)
    user_phone: Optional[str] = Field()
    user_status: Optional[bool]
    remarks: Optional[str]


class SetRole(BaseModel):
    user_id: int
    roles: Optional[List[int]] = Field(default=[], description="Role")


class AccountLogin(BaseModel):
    username: Optional[str] = Field(min_length=3, max_length=255, description="username")
    password: Optional[str] = Field(min_length=6, max_length=255, description="password")
    mobile: Optional[str] = Field(description="phone number")
    captcha: Optional[str] = Field(min_length=6, max_length=6, description="6-digit verification code")


class ModifyMobile(BaseModel):
    mobile: str = Field(description="phone number")
    captcha: str = Field(min_length=6, max_length=6, description="6-digit verification code")


class UserInfo(BaseModel):
    username: str
    age: Optional[int]
    user_type: bool
    nickname: Optional[str]
    user_phone: Optional[str]
    user_email: Optional[str]
    full_name: Optional[str]
    scopes: Optional[List[str]]
    user_status: bool
    header_img: Optional[str]
    sex: int


class UserListItem(BaseModel):
    key: int
    id: int
    username: str
    age: Optional[int]
    user_type: bool
    nickname: Optional[str]
    user_phone: Optional[str]
    user_email: Optional[str]
    full_name: Optional[str]
    user_status: bool
    header_img: Optional[str]
    sex: int
    remarks: Optional[str]
    create_time: datetime
    update_time: datetime


class CurrentUser(BaseResp):
    data: UserInfo


class AccessToken(BaseModel):
    token: Optional[str]
    expires_in: Optional[int]


class UserLogin(BaseResp):
    data: AccessToken


class UserListData(ResAntTable):
    data: List[UserListItem]


class UpdateUserInfo(BaseModel):
    nickname: Optional[str]
    user_email: Optional[str]
    header_img: Optional[str]
    user_phone: Optional[str] = Field(description="phone number")
    password: Optional[str] = Field(min_length=6, max_length=255, description="password")

    @validator('*')
    def blank_strings(cls, v):
        if v == "":
            return None
        return v
