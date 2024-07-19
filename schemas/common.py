# -*- coding:utf-8 -*-

# @Time : 2022/4/27 5:29 PM
# @Author: me
# @Des: person Schema

from datetime import datetime
from pydantic import Field, BaseModel, validator
from typing import Optional, List
from schemas.base import BaseResp, ResAntTable


class AuthorizePerson(BaseModel):
    person_id: int
    device_ids: List[int]


class DeauthorizePerson(BaseModel):
    person_id: int
    device_ids: List[int]


class UnlockDoor(BaseModel):
    device_id: int


class Dashboard(BaseModel):
    totalPerson: int
    totalPersonToday: int
    totalEmployee: int
    # totalEmployeeMale:int
    # totalEmployeeFemale:int
    totalVisitor: int
    # totalVisitorMale:int
    # totalVisitorFemale:int
    totalDevice: int
    totalDeviceDc: int
    totalDevicePengelola: int
    totalHik: int
    totalLegrand: int
    totalDeviceLantai1Dc: int
    totalDeviceLantai2Dc: int
    totalDeviceLantai3Dc: int
    totalDeviceLantai4Dc: int
    totalDeviceLantai5Dc: int
    totalDeviceLantai6Dc: int
    totalDeviceLantai1Pengelola: int
    totalDeviceLantai2Pengelola: int
    totalDeviceLantai3Pengelola: int
    totalDeviceLantai4Pengelola: int
    totalDeviceLantai5Pengelola: int
    totalDeviceLantai6Pengelola: int


class LogDevice(BaseModel):
    device_ids: List[int]


class LogAttendance(BaseModel):
    device_ids: List[int]
