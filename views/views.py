# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 11:46 AM
@Maintainer: dgos
@Des: 视图路由
"""
from fastapi import APIRouter
from views.viewpoints import home

views_router = APIRouter()

views_router.include_router(home.router)

