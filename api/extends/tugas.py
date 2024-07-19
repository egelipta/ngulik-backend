# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: Tugas Extends
"""

import datetime
from typing import Any, Dict, List, Optional
from core.Response import success, fail, res_antd
from models.tugas import Tugas
from schemas import tugas
from fastapi import HTTPException, Request, Query, APIRouter
from tortoise.queryset import F

router = APIRouter(prefix='/tugas')

@router.get("",
            summary="Tugas List",
            response_model=tugas.TugasListData,
            # dependencies=[Security(check_permissions, scopes=["tugas_query"])]
            )
async def tugas_list(
        pageSize: int = 10,
        current: int = 1,
        name: str = Query(None),
        start: str = Query(None),
        end: str = Query(None),
        progress: str = Query(None),
        tipe: str = Query(None),
        project: str = Query(None),
        dependencies: str = Query(None),
        create_time: str = Query(None),
        update_time: str = Query(None),

):
    """
    Get All Tugass
    :return:
    """
    query = {}
    if name:
        query.setdefault('name__icontains', name)
    if start:
        query.setdefault('start__icontains', start)
    if end:
        query.setdefault('end__icontains', end)
    if progress:
        query.setdefault('progress__icontains', progress)
    if tipe:
        query.setdefault('tipe__icontains', tipe)
    if project:
        query.setdefault('project__icontains', project)
    if dependencies:
        query.setdefault('dependencies__icontains', dependencies)
    if create_time:
        query.setdefault('create_time__range', create_time)
    if update_time:
        query.setdefault('update_time__range', update_time)

    tugas_data = Tugas.annotate(key=F("id")).filter(tipe="project", **query).all()
    total = await tugas_data.count()

    
    data = await tugas_data.limit(pageSize).offset(pageSize * (current - 1)).order_by("-create_time") \
        .values(
        "key", "id","name", "start", "end", "progress", "tipe", "project", "dependencies", "create_time", "update_time")

    return res_antd(code=True, data=data, total=total)


@router.post("", summary="Tugas Add",
# dependencies=[Security(check_permissions, scopes=["tugas_add"])]
)
async def tugas_add(post: tugas.CreateTugas):
    """
    Tugas Add
    :param post: CreateTugas
    :return:
    """
    # Filter Tugass
    # get_name_tugas = await Tugas.get_or_none(name_tugas=post.name_tugas)
    # if get_name_tugas:
    #     return fail(msg=f"Tugas {post.name_tugas} sudah ada!")

    create_tugas = await Tugas.create(**post.dict())
    if not create_tugas:
        return fail(msg=f"Failed to create Tugas {post.name}!")
    return success(msg=f"{create_tugas.name} berhasil disimpan")



# @router.get("/gantt-task", summary="Data Gantt Task")
# async def gantt_task():
#     data_tugas = await Tugas.all()

#     if data_tugas:
#         data = []
#         for tugas in data_tugas:
#             start_date = f"{tugas.start.year}, {tugas.start.month}, {tugas.start.day}"  # Adjust month to be zero-indexed
#             end_date = f"{tugas.end.year}, {tugas.end.month}, {tugas.end.day}"  # Adjust month to be zero-indexed
            
#             task_data = {
#                 "start": start_date,
#                 "end": end_date,
#                 "name": tugas.name,
#                 "id": str(tugas.id),
#                 "progress": tugas.progress,
#                 "type": tugas.tipe,
#             }
#             if tugas.tipe != "project":
#                 task_data["dependencies"] = tugas.dependencies,
#                 task_data["project"] = tugas.project
#             else:
#                 task_data["hideChildren"] = False
#             data.append(task_data)
#     else:
#         data = {"message": "Tidak ada data"}

#     return data


@router.get("/gantt-task", summary="Data Gantt Task")
async def gantt_task():
    data_tugas = await Tugas.all()
    
    # Group tasks by project
    projects: Dict[int, Dict[str, Any]] = {}  # Use int as the type for project IDs
    for task in data_tugas:
        if task.tipe == "project":
            projects[int(task.id)] = {  # Convert project ID to int
                "project": task,
                "tasks": []
            }
        elif task.tipe == "task":
            project_id = int(task.project)  # Convert project ID to int
            if project_id in projects:
                projects[project_id]["tasks"].append(task)
            else:
                projects[project_id] = {
                    "project": None,
                    "tasks": [task]
                }
    
    # Sort projects by ID
    sorted_projects = dict(sorted(projects.items()))
    
    # Format tasks within each project
    format_data = []
    for project_data in sorted_projects.values():
        proj = project_data["project"]

        if proj:
            format_data.append({
                "start": proj.start,
                "end": proj.end,
                "name": proj.name,
                "id": str(proj.id),
                "progress": proj.progress,
                "type": proj.tipe,
                "hideChildren": False
            })
            # Sort tasks by ID within the project
            sorted_tasks = sorted(project_data["tasks"], key=lambda x: x.id)
            for task in sorted_tasks:
                format_data.append({
                    "start": task.start,
                    "end": task.end,
                    "name": task.name,
                    "id": str(task.id),
                    "progress": task.progress,
                    "type": task.tipe,
                    "project": task.project,
                    "dependencies": task.dependencies,
                })
    return format_data


@router.get("/project", summary="Data Project")
async def project():
        
    data_project = await Tugas.filter(tipe="project").order_by("-create_time")
    # total = await Tugas.filter(tipe="project").count()
    datas = []
    if data_project:
        for dp in data_project:
            data_task = await Tugas.filter(project=dp.id)
            if data_task:
                total_progress = sum(data_task.progress for data_task in data_task)
                rata_progress = total_progress / len(data_task)
                rata_progress = round(rata_progress, 1)
            else:
                rata_progress = 0
            data_tampil = {
                "key": dp.id,
                "id": dp.id,
                "name": dp.name,
                "start": dp.start,
                "end": dp.end,
                "tipe": dp.tipe,
                "progress": rata_progress,
                "create_time": dp.create_time,
                "update_time": dp.update_time
            }
            datas.append(data_tampil)
    else:
        datas = []        
    return datas


@router.get("/data-subproject", summary="Data Sub Project")
async def data_subproject(id):
    data = await Tugas.filter(tipe="task", project=id).order_by("-id")
    return data


@router.delete("/hapus-data", summary="Hapus Data", 
# dependencies=[Security(check_permissions, scopes=["tugas_delete"])]
)
async def hapus_data(id: int):
    """
    Hapus Data
    :param req:
    :return:
    """
    datas = await Tugas.filter(id=id).all()
    for d in datas:
        names = d.name

    del_project = await Tugas.filter(id=id).delete()
    del_task = await Tugas.filter(project=id).delete()

    delete = del_project + del_task
    if not delete:
        return fail(msg=f"Gagal dihapus! {id}!")
    return success(msg=f"{names} Berhasil dihapus! ")


@router.put("/update", summary="Update Tugas",
# dependencies=[Security(check_permissions, scopes=["tugas_update"])]
)
async def tugas_update(post: tugas.UpdateTugas):
    """
    Update tugas information
    :param post:
    :return:
    """
    tugas_check = await Tugas.get_or_none(pk=post.id)
    if not tugas_check:
        return fail(msg="Tugas tidak ada")
    # if tugas_check.merek != post.merek:
    #     check = await Tugas.get_or_none(merek=post.merek)
    #     if check:
    #         return fail(msg=f"Tugas {check.merek} sudah ada!")

    data = post.dict()
    data.pop("id")
    await Tugas.filter(pk=post.id).update(**data)
    return success(msg=f"Berhasil diubah!")







