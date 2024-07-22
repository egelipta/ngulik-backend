# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: Gedung Schema
"""
from datetime import datetime
from pydantic import Field, BaseModel, validator
from typing import Optional, List
from schemas.base import BaseResp, ResAntTable


class CreateGedung(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    width: int
    height: int
    depth: int
    x: int
    y: int
    z: int
    
class UpdateGedung(CreateGedung):
    id: int

class GedungItem(UpdateGedung):
    key: int
    id: int
    create_time: datetime
    update_time: datetime

class GedungDelete(BaseModel):
    id: int

class GedungListData(ResAntTable):
    data: List[GedungItem]
