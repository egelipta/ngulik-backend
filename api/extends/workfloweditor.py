# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: WorkflowEditor Extends
"""

import datetime
from typing import Any, Dict, List, Optional
from core.Response import success, fail, res_antd
from models.workfloweditor import WorkflowEditor
from schemas import workfloweditor
from fastapi import HTTPException, Request, Query, APIRouter
from tortoise.queryset import F

router = APIRouter(prefix='/workfloweditor')
@router.get("/get-data", summary="Get Data")
async def workfloweditor():
    data = await WorkflowEditor.all()
    return data
