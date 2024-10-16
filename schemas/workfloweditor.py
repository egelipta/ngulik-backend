# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: WorkflowEditor Schema
"""
from datetime import datetime
from pydantic import Field, BaseModel, validator
from typing import Optional, List
from schemas.base import BaseResp, ResAntTable


class CreateWorkflowEditor(BaseModel):
    name: str = Field(max_length=255)
    nodesjson: List[str] = Field(max_length=5000)
    edgesjson: List[str] = Field(max_length=5000)
    
class UpdateWorkflowEditor(CreateWorkflowEditor):
    id: int

class WorkflowEditorItem(UpdateWorkflowEditor):
    key: int
    id: int
    create_time: datetime
    update_time: datetime

class WorkflowEditorDelete(BaseModel):
    id: int

class WorkflowEditorListData(ResAntTable):
    data: List[WorkflowEditorItem]
