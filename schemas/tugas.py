# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: Tugas Schema
"""
from datetime import datetime
from pydantic import Field, BaseModel, validator
from typing import Optional, List
from schemas.base import BaseResp, ResAntTable


class CreateTugas(BaseModel):
    name: str = Field(max_length=255)
    start: datetime
    end: datetime
    progress: int
    tipe: str = Field(max_length=255)
    project: Optional[str] = Field(max_length=255)
    dependencies: Optional[str] = Field(max_length=255)
    # hidechildren: bool
    
class UpdateTugas(CreateTugas):
    id: int

class TugasItem(UpdateTugas):
    key: int
    id: int
    create_time: datetime
    update_time: datetime

class TugasDelete(BaseModel):
    id: int

class TugasListData(ResAntTable):
    data: List[TugasItem]
