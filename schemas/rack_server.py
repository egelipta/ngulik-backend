# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: RackServer Schema
"""
from datetime import datetime
from pydantic import Field, BaseModel, validator
from typing import Optional, List
from schemas.base import BaseResp, ResAntTable


class CreateRackServer(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    width: int
    height: int
    depth: int
    x: int
    y: int
    z: int
    
class UpdateRackServer(CreateRackServer):
    id: int

class RackServerItem(UpdateRackServer):
    key: int
    id: int
    create_time: datetime
    update_time: datetime

class RackServerDelete(BaseModel):
    id: int

class RackServerListData(ResAntTable):
    data: List[RackServerItem]
