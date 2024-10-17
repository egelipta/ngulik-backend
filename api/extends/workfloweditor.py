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
from schemas.workfloweditor import CreateWorkflowEditor  # Sesuaikan path ini dengan struktur proyek Anda
from fastapi import HTTPException, Request, Query, APIRouter
from tortoise.queryset import F
import json

router = APIRouter(prefix='/workfloweditor')

@router.get(
    "",
    summary="Table Data",
    response_model=workfloweditor.WorkflowEditorListData,
    # dependencies=[Security(check_permissions, scopes=["workfloweditor_query"])]
)
async def workfloweditor_list(
        pageSize: int = 10,
        current: int = 1,
        name: str = Query(None),
        create_time: str = Query(None),
        update_time: str = Query(None),
):
    """
    Get All WorkflowEditors
    :return:
    """
    query = {}
    if name:
        query.setdefault('name__icontains', name)
    if create_time:
        query.setdefault('create_time__range', create_time)
    if update_time:
        query.setdefault('update_time__range', update_time)

    workfloweditor_data = WorkflowEditor.annotate(key=F("id")).filter(**query).all()
    total = await workfloweditor_data.count()

    data = await workfloweditor_data.limit(pageSize).offset(pageSize * (current - 1)).order_by("-create_time").values(
        "key", "id", "name", "nodesjson", "edgesjson", "create_time", "update_time"
    )

    # Pastikan nodesjson dan edgesjson berupa list of strings
    formatted_data = [
        {
            **item,
            "nodesjson": [json.loads(node) if isinstance(node, str) else node for node in item["nodesjson"]] if isinstance(item["nodesjson"], list) else [],
            "edgesjson": [json.loads(edge) if isinstance(edge, str) else edge for edge in item["edgesjson"]] if isinstance(item["edgesjson"], list) else [],
        }
        for item in data
    ]
    return res_antd(code=True, data=formatted_data, total=total)
    

@router.get("/get-data", summary="Get Data")
async def workfloweditor(id):
    data = await WorkflowEditor.filter(id=id)
    return data


@router.post("/add-data", summary="Add Data")
async def workfloweditor_add(post: CreateWorkflowEditor):
    """
    Tugas Add
    :param post: Create Workflow Editor
    :return:
    """
    create_workfloweditor = await WorkflowEditor.create(**post.dict())
    
    if not create_workfloweditor:
        return fail(msg=f"Failed {post.name}!")
    
    return success(msg=f"{create_workfloweditor.name} Success")
