# -*- coding:utf-8 -*-
"""
@Time : 2022/4/27 5:24 PM
@Maintainer: dgos
@Des: User Management
"""
import os
import time

# from core.Utils import crop_face, remove_dots_except_last, compress_image
from api.endpoints.common import write_access_log
from api.endpoints.websocket import check_token
from core.Response import success, fail, res_antd
from models.base import User, Role, Access, AccessLog
from schemas import user
from core.Utils import en_password, check_password, random_str
from core.Auth import create_access_token, check_permissions
from fastapi import Request, Query, APIRouter, Security, File, UploadFile
from config import settings
from typing import List
from tortoise.queryset import F
from PIL import Image
from io import BytesIO
import requests
from requests.auth import HTTPDigestAuth

from schemas.user import UpdateUserInfo, ModifyMobile

router = APIRouter(prefix='/user')


@router.post("", summary="User add", dependencies=[Security(check_permissions, scopes=["user_add"])])
async def user_add(post: user.CreateUser):
    """
    Create users
    :param post: CreateUser
    :return:
    """
    # Filter user
    get_user = await User.get_or_none(username=post.username)
    if get_user:
        return fail(msg=f"username {post.username} already exists!")
    post.password = en_password(post.password)

    # Create users
    create_user = await User.create(**post.dict())
    # print(**post.dict())
    if not create_user:
        return fail(msg=f"user{post.username}Failed to create!")
    if post.roles:
        # Assigning role
        roles = await Role.filter(id__in=post.roles, role_status=True)
        await create_user.role.add(*roles)
    return success(msg=f"user{create_user.username}Successful creation")


@router.delete("", summary="User delete", dependencies=[Security(check_permissions, scopes=["user_delete"])])
async def user_del(req: Request, user_id: int):
    """
    delete users
    :param req:
    :param user_id: int
    :return:
    """
    if req.state.user_id == user_id:
        return fail(msg="You can't kick yourself out, right??")
    delete_action = await User.filter(pk=user_id).delete()
    if not delete_action:
        return fail(msg=f"user {user_id} failed to delete!")
    return success(msg="successfully deleted")


@router.put("", summary="User modification", dependencies=[Security(check_permissions, scopes=["user_update"])])
async def user_update(post: user.UpdateUser):
    """
    Update user information
    :param post:
    :return:
    """
    user_check = await User.get_or_none(pk=post.id)
    # Super administrator or no user
    if not user_check or user_check.pk == 1:
        return fail(msg="User does not exist")
    if user_check.username != post.username:
        check_username = await User.get_or_none(username=post.username)
        if check_username:
            return fail(msg=f"username {check_username.username} existed")

    # new password
    if post.password:
        post.password = en_password(post.password)

    data = post.dict()
    if not post.password:
        data.pop("password")
    data.pop("id")
    await User.filter(pk=post.id).update(**data)
    return success(msg="update completed!")


@router.put("/set/role", summary="Role Assignments", dependencies=[Security(check_permissions, scopes=["user_role"])])
async def set_role(post: user.SetRole):
    """
    Role Assignments
    :param post:
    :return:
    """
    user_obj = await User.get_or_none(pk=post.user_id)
    if not user_obj:
        return fail(msg="User does not exist!")
    # Empty character
    await user_obj.role.clear()
    # edit permission
    if post.roles:
        roles = await Role.filter(role_status=True, id__in=post.roles).all()
        # Assigning Roles
        await user_obj.role.add(*roles)

    return success(msg="Successful character distribution!")


@router.get("",
            summary="user list",
            response_model=user.UserListData,
            dependencies=[Security(check_permissions, scopes=["user_query"])]
            )
async def user_list(
        pageSize: int = 10,
        current: int = 1,
        username: str = Query(None),
        user_phone: str = Query(None),
        user_status: bool = Query(None),
        create_time: List[str] = Query(None)

):
    """
    Get all administrators
    :return:
    """
    # Query conditions
    query = {}
    if username:
        query.setdefault('username', username)
    if user_phone:
        query.setdefault('user_phone', user_phone)
    if user_status is not None:
        query.setdefault('user_status', user_status)
    if create_time:
        query.setdefault('create_time__range', create_time)

    user_data = User.annotate(key=F("id")).filter(
        **query).filter(id__not=1).all()
    # total
    total = await user_data.count()
    # Inquire
    data = await user_data.limit(pageSize).offset(pageSize * (current - 1)).order_by("-create_time") \
        .values(
        "key", "id", "username", "user_type", "user_phone", "user_email",
        "user_status", "header_img", "sex", "remarks", "create_time", "update_time")

    return res_antd(code=True, data=data, total=total)


@router.get("/info",
            summary="Get the current user information",
            response_model=user.CurrentUser,
            dependencies=[Security(check_permissions)]
            )
async def user_info(req: Request):
    """
    Get the current login user information
    :return:
    """
    user_data = await User.get_or_none(pk=req.state.user_id)
    if not user_data:
        return fail(msg=f"User ID {req.state.user_id} does not exist!")
    # Non -super administrator
    access = []
    if not req.state.user_type:
        # Two level access
        two_level_access = await Access.filter(role__user__id=req.state.user_id, is_check=True).values_list("parent_id")
        two_level_access = [i[0] for i in two_level_access]
        # One level access
        one_level_access = await Access.filter(id__in=list(set(two_level_access))).values_list("parent_id")
        one_level_access = [i[0] for i in one_level_access]

        query_access = await Access.filter(id__in=list(set(one_level_access + two_level_access))).values_list("scopes")
        access = [i[0] for i in query_access]
    # Processing mobile phone number ****
    if user_data.user_phone:
        user_data.user_phone = user_data.user_phone.replace(
            user_data.user_phone[3:7], "****")
    # Add the scope to the user information
    user_data.__setattr__("scopes", access)

    return success(msg="User Info", data=user_data.__dict__)


@router.post("/account/login", response_model=user.UserLogin, summary="user login")
async def account_login(req: Request, post: user.AccountLogin):
    """
    user login
    :param req:
    :param post:
    :return: jwt token
    """
    if post.mobile and post.captcha:
        # Mobile phone number login
        is_check = await check_token(req, post.captcha, post.mobile)
        if not is_check:
            return fail(msg="The verification code is invalid, the login fails, please log in again!")
        mobile_user = await User.get_or_none(user_phone=post.mobile)
        jwt_data = {
            "user_id": mobile_user.pk,
            "user_type": mobile_user.user_type
        }
        jwt_token = create_access_token(data=jwt_data)
        data = {"token": jwt_token,
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60}
        await write_access_log(req, mobile_user.pk, "Login the system through the mobile phone number!")
        return success(msg="Login successfully 😄", data=data)

    if post.username and post.password:
        # Account password login
        get_user = await User.get_or_none(username=post.username)
        if not get_user:
            return fail(msg=f"User {post.username} Password verification failure!")
        if not get_user.password:
            return fail(msg=f"User {post.username} Password verification failure!")
        if not check_password(post.password, get_user.password):
            return fail(msg=f"User {post.username} Password verification failure!")
        if not get_user.user_status:
            return fail(msg=f"User {post.username} Have been banned by administrators!")
        jwt_data = {
            "user_id": get_user.pk,
            "user_type": get_user.user_type
        }
        jwt_token = create_access_token(data=jwt_data)
        data = {"token": jwt_token,
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60}
        await write_access_log(req, get_user.pk, "Login the system through the username!")
        return success(msg="Login successfully 😄", data=data)

    return fail(msg="Choose at least one login method!")


@router.get("/access/log", dependencies=[Security(check_permissions)], summary="User access record")
async def get_access_log(req: Request):
    """
    Query current user access record
    :param req:
    :return:
    """
    log = await AccessLog().filter(user_id=req.state.user_id).limit(10).order_by("-create_time") \
        .values("create_time", "ip", "note", "id")

    return success(msg="access log", data=log)


@router.put("/info", dependencies=[Security(check_permissions)], summary="Basic user information modification")
async def update_user_info(req: Request, post: UpdateUserInfo):
    """
    edit personal information
    :param req:
    :param post:
    :return:
    """
    await User.filter(id=req.state.user_id).update(**post.dict(exclude_none=True))
    return success(msg="update completed!")


@router.put("/modify/mobile", dependencies=[Security(check_permissions)], summary="User mobile phone number modification")
async def update_user_info(req: Request, post: ModifyMobile):
    """
    Modify the binding mobile phone number
    :param req:
    :param post:
    :return:
    """
    is_check = await check_token(req, post.captcha, post.mobile)
    if not is_check:
        return fail(msg="Effective verification code or verification has expired!")
    await User.filter(id=req.state.user_id).update(user_phone=post.mobile)
    return success(msg="Modification of mobile phone numbers success, Please log using newly added mobile phone number!")


@router.put("/avatar/upload", dependencies=[Security(check_permissions)], summary="Avatar modification")
async def avatar_upload(req: Request, avatar: UploadFile = File(...)):
    """
    Avatar upload
    :param req:
    :param avatar:
    :return:
    """
    # File storage path
    path = f"{settings.STATIC_DIR}/upload/avatar"
    start = time.time()
    filename = random_str() + '.' + avatar.filename.split(".")[1]
    try:
        if not os.path.isdir(path):
            os.makedirs(path, 0o777)
        res = await avatar.read()
        with open(f"{path}/{filename}", "wb") as f:
            f.write(res)
        await User.filter(id=req.state.user_id).update(header_img=f"/upload/avatar/{filename}")
        data = {
            'time': time.time() - start,
            'url': f"/upload/avatar/{filename}"}
        return success(msg="Update avatar success", data=data)
    except Exception as e:
        print("The avatar upload failed:", e)
        return fail(msg=f"{avatar.filename} upload failed!")


# @router.post("/photo/upload", dependencies=[Security(check_permissions)], summary="Photo upload")
# async def photo_upload(req: Request, file: UploadFile = File(...)):
#     """
#     Photo upload
#     :param req:
#     :param photo:
#     :return:
#     """
#     # File storage path
#     path = f"{settings.STATIC_DIR}/upload/photo"
#     start = time.time()
#     filename = remove_dots_except_last(file.filename)
#     filename = random_str() + '_' + filename
#     filename = filename.replace(" ", "")
#     try:
#         if not os.path.isdir(path):
#             os.makedirs(path, 777)
#         res = await file.read()
#         with open(f"{path}/{filename}", "wb") as f:
#             f.write(res)
#         namapenuh = f"{path}/{filename}"
#         print("Cropping", namapenuh)
#         crop_face(namapenuh, namapenuh, 0)
#         compress_image(namapenuh)
#         # await User.filter(id=req.state.user_id).update(header_img=f"/upload/photo/{filename}")
#         data = {
#             'time': time.time() - start,
#             'url': f"/upload/photo/{filename}"}
#         return success(msg="Update photo success", data=data)
#     except Exception as e:
#         print("The photo upload failed:", e)
#         return fail(msg=f"{file.filename} upload failed!")


@router.post("/photo/upload_tes", 
# dependencies=[Security(check_permissions)],
 summary="Photo real cuy")
def download_image(url ):
    response = requests.get(url)
    save_path = "static/upload/photo/dihwibu.jpeg"
    username ="admin"
    password = "rahasia123"
    
    with requests.Session() as session:
        session.auth = HTTPDigestAuth(username, password)

        # Send a GET request to the URL
        response = session.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open the image using Pillow
            image = Image.open(BytesIO(response.content))
            
            # Save the image to the specified path
            image.save(save_path)
            print(f"Image downloaded and saved to {save_path}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")

@router.get("/data-user", summary="Data User")
async def get_data_user():
    users = await User.all()
    data = []

    for u in users:

        data.append({
            "id": u.id,
            "username": u.username,
            "user_status": bool(u.user_status),
            "name": u.nickname,
        })
        
    return data