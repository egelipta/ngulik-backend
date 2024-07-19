# -*- coding:utf-8 -*-
"""
@Time : 2022/5/15 11:51 PM
@Maintainer: dgos
@Des: 角色管理
"""
from typing import List
from fastapi import Query, APIRouter, Security
from core.Auth import check_permissions
from core.Response import res_antd, success, fail
from schemas.role import CreateRole, UpdateRole, RoleList
from models.base import Role
from tortoise.queryset import F
router = APIRouter(prefix='/role')


@router.get("/all", summary="All characters are dedicated to pull off options", dependencies=[Security(check_permissions, scopes=["user_role"])])
async def all_roles_options(user_id: int = Query(None)):
    # Query the role of enabled
    roles = await Role.annotate(label=F("role_name"), value=F('id')).filter(role_status=True).values('label', "value")
    user_roles = []
    if user_id:
        # Current user role
        user_role = await Role.filter(user__id=user_id, role_status=True).values_list('id')
        user_roles = [i[0] for i in user_role]
    data = {
        "all_role": roles,
        "user_roles": user_roles
    }
    return success(msg="All characters are dedicated to pull off options", data=data)


@router.post("", summary="Character add", dependencies=[Security(check_permissions, scopes=["role_add"])])
async def create_role(post: CreateRole):
    """
    Creating a Role
    :param post: CreateRole
    :return:
    """
    result = await Role.create(**post.dict())
    if not result:
        return fail(msg="Failed to create!")
    return success(msg="Successful creation!")


@router.delete("", summary="Character delete", dependencies=[Security(check_permissions, scopes=["role_delete"])])
async def delete_role(role_id: int):
    """
    Delete the role
    :param role_id:
    :return:
    """
    role = await Role.get_or_none(pk=role_id)
    if not role:
        return fail(msg="The character does not exist!")
    result = await Role.filter(pk=role_id).delete()
    if not result:
        return fail(msg="failed to delete!")
    return success(msg="successfully deleted!")


@router.put("", summary="Role modification", dependencies=[Security(check_permissions, scopes=["role_update"])])
async def update_role(post: UpdateRole):
    """
    Update role
    :param post:
    :return:
    """
    data = post.dict()
    data.pop("id")
    result = await Role.filter(pk=post.id).update(**data)
    if not result:
        return fail(msg="Update failure!")
    return success(msg="update completed!")


@router.get('', summary="Corner list", response_model=RoleList,
            dependencies=[Security(check_permissions, scopes=["role_query"])])
async def get_all_role(
        pageSize: int = 10,
        current: int = 1,
        role_name: str = Query(None),
        role_status: bool = Query(None),
        create_time: List[str] = Query(None)

) -> RoleList:
    """
    Corner list
    :param role_status:
    :param pageSize:
    :param current:
    :param role_name:
    :param create_time:
    :return:
    """
    query = {}
    if role_name:
        query.setdefault('role_name', role_name)
    if role_status is not None:
        query.setdefault('role_status', role_status)
    if create_time:
        query.setdefault('create_time__range', create_time)

    role = Role.annotate(key=F("id")).filter(**query).all()
    # total
    total = await role.count()
    # Inquire
    data = await role.limit(pageSize).offset(pageSize * (current - 1)).order_by("-create_time") \
        .values(
        "key", "id", "role_name", "role_status", "role_desc", "create_time", "update_time")
    return res_antd(code=True, data=data, total=total)
