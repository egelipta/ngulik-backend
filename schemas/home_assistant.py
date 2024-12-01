# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: HomeAssistant Schema
"""
from datetime import datetime
from pydantic import Field, BaseModel, validator
from typing import Optional, List, Dict
from schemas.base import BaseResp, ResAntTable


class CreateHomeAssistant(BaseModel):
    datachart: Dict = Field(default_factory=dict)
    
class UpdateHomeAssistant(CreateHomeAssistant):
    id: int

class HomeAssistantItem(UpdateHomeAssistant):
    key: int
    id: int
    create_time: datetime
    update_time: datetime

class HomeAssistantDelete(BaseModel):
    id: int

class HomeAssistantListData(ResAntTable):
    data: List[HomeAssistantItem]
