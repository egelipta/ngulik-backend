# -*- coding:utf-8 -*-
"""
@Time : 2022/5/18 1:03 AM
@Maintainer: dgos
@Des: 权限管理
"""
from fastapi import APIRouter, Security
from tortoise.queryset import F
from core.Auth import check_permissions
from core.Response import fail, success
from schemas import role, base
from models.base import Role, Access

router = APIRouter(prefix='/access')


@router.post('', summary="权限创建", response_model=base.BaseResp)
async def create_access(post: role.CreateAccess):
    """
    创建权限
    :param post: CreateAccess
    :return:
    """
    # 超级管理员可以创建权限
    # if req.state.user_id is not 1 and req.state.user_type is not False:
    #     return fail(msg="无法建权限!")

    check = await Access.get_or_none(scopes=post.scopes)
    if check:
        return fail(msg=f"scopes:{post.scopes} already exists!")
    result = await Access.create(**post.dict())
    if not result:
        return fail(msg="Successfully created!")
    return success(msg=f"permissions {result.pk} Created successfully!")


@router.get('', summary="Permission query", dependencies=[Security(check_permissions, scopes=["role_access"])])
async def get_all_access(role_id: int):
    """
    Get all permissions
    :return:
    """
    result = await Access.annotate(key=F('id'), title=F('access_name')).all() \
        .values("key", "title", "parent_id")
    # 当前角色权限
    role_access = await Access.filter(role__id=role_id).values_list('id')

    # 系统权限
    tree_data = access_tree(result, 0)
    # 角色权限
    role_access = [i[0] for i in role_access]
    data = {
        "all_access": tree_data,
        "role_access": role_access
    }
    return success(msg="The permissions that the current user can post", data=data)


@router.put('', summary="Permission settings",
            dependencies=[Security(check_permissions, scopes=["role_access"])], response_model=base.BaseResp)
async def set_role_access(post: role.SetAccess):
    """
    Set role permission
    :param post:
    :return:
    """
    # Get the current role
    role_data = await Role.get_or_none(id=post.role_id)
    # Clearance
    await role_data.access.clear()
    # No settings permissions
    if not post.access:
        return success(msg="Has cleared the current role ownership!")
    # Obtaining allocation permissions collection
    access = await Access.filter(id__in=post.access, is_check=True).all()
    # Additional permissions
    await role_data.access.add(*access)
    return success(msg="Saved successfully!")


def access_tree(data, pid):
    """
    Traversing permissions trees
    :param data: rule[]
    :param pid: ParentID
    :return: list
    """
    result = []
    for item in data:
        if pid == item["parent_id"]:
            temp = access_tree(data, item["key"])
            if len(temp) > 0:
                # item["key"] = str(item["key"])
                item["children"] = temp
            result.append(item)
    return result
