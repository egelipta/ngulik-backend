# -*- coding:utf-8 -*-
"""
@Time : 2022/4/27 5:29 PM
@Author: me
@Des: heat_map Schema
"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from schemas.base import ResAntTable


class CreateHeatmap(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    d: str = Field(min_length=1, max_length=500)
    floor: str = Field(min_length=1, max_length=255)


class UpdateHeatmap(CreateHeatmap):
    id: int


class HeatmapItem(UpdateHeatmap):
    key: int
    id: int
    # create_time: datetime
    # update_time: datetime


class HeatmapDelete(BaseModel):
    id: int


class HeatmapListData(ResAntTable):
    data: List[HeatmapItem]
