# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Maintainer: dgos
@Des: Tool function
"""
import os
import asyncio
import subprocess
import time

delay_in_second = 3
host_ip = os.getenv('PJVMS_HOST_IP', '192.168.99.99')
host_port = os.getenv('PJVMS_HOST_PORT', '80')

from datetime import timezone, tzinfo, datetime, timedelta
import hashlib
import http
import json
import math
import random
import time
import zoneinfo
import urllib.parse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
import pytz
import requests
from requests.auth import HTTPDigestAuth
from core.Response import fail, success
from models.device import Device
from models.email import Email
from models.elevator import Elevator
from models.logs import Logs
from models.passrecord import Passrecord
from models.stranger import Stranger
from models.buku_tamu import Buku_tamu
from models.attendance import Attendance
from models.person import Person
from fastapi import Request, Query, APIRouter, Security, File, UploadFile
from config import settings
# from core.Utils import crop_face, remove_dots_except_last, compress_image
# from endpoints.user import download_image
from PIL import Image
from io import BytesIO
import requests
from requests.auth import HTTPDigestAuth
import uuid
import threading




# proxy_ip = socket.gethostbyname("proxy-container-name")

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'ACCEPT': '*/*',
    'ACCEPT-ENCODING': 'gzip, deflate',
    'ACCEPT-LANGUAGE': 'en-US,en;q=0.9',
    # 'REFERER': 'https://dgos.id/',
    'Connection': 'Keep-Alive',
    'Keep-Alive': 'timeout=5, max=1000',
    'X-Requested-With': 'XMLHttpRequest'
}


async def authorize_person_hik(person_id: int, device_ids: list()):
    """
    Authorize Person to device
    :param post: Authorize Person
    :return:
    """

    print("INFO:     Authorizing person")

    # headers untuk request
    gedung_dc = []
    # gedung_pengelola = []

    person = await Person.get_or_none(id=person_id)
    if not person:
        print("person not found with id", person_id)
        return fail(msg=f"Could not find person with ID {person_id}")

    for device_id in device_ids:
        device = await Device.get_or_none(id=device_id)
        person_exist_on_device = True
        if not device:
            print("ERROR:     Could not find device with ID: ", device_id)
        else:
            url = f"http://{device.ip_address}:80/ISAPI/AccessControl/UserInfo/Search?format=json"
            payload = json.dumps({
                "UserInfoSearchCond": {
                    "searchID": "146",
                    "searchResultPosition": 0,
                    "maxResults": 10,
                    "EmployeeNoList": [{
                        "employeeNo": str(person_id)
                    }]
                }
            })
            try:
                response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                    device.username, device.password), timeout=5)
            except:
                print(
                    f"ERROR:     Checking person_id: {person_id} from device FAILED!")
            finally:
                if (response.status_code == 200):
                    print(
                        f"INFO:     Checking {person.id} from {device.ip_address} SUCCESS!")
                    if (response.json()['UserInfoSearch']['numOfMatches'] > 0):
                        person_exist_on_device = True
                    else:
                        person_exist_on_device = False
                else:
                    print(
                        f"INFO:     Checking {person.id} from {device.ip_address} FAILED!")

            # updating person because exist
            if person_exist_on_device:
                url = f"http://{device.ip_address}:80/ISAPI/AccessControl/UserInfo/Modify?format=json"
                payload = json.dumps({
                    "UserInfo": {
                        "employeeNo": str(person_id),
                        "name": person.name,
                        "userType": "normal",
                        "Valid": {
                            "enable": True,
                            "beginTime": person.starting_time.replace(microsecond=0, tzinfo=None).isoformat(),
                            "endTime": person.expire_time.replace(microsecond=0, tzinfo=None).isoformat(),
                            "timeType": "local"
                        }
                        # "doorRight": "1",
                        # "RightPlan": [
                        #     {
                        #         "doorNo": 1,
                        #         "planTemplateNo": "1"
                        #     }
                        # ],
                        # "password": "9999",
                        # "userVerifyMode": "cardOrFaceOrFp"
                    }
                })

                start = time.time()
                try:
                    response = requests.request("PUT", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                        device.username, device.password), timeout=5)
                except:
                    print("ERROR:     Update existing person FAILED!")
                finally:
                    end = time.time()
                    elapsed = (end-start)
                    elapsed = str("%.2f" % elapsed)

                    if (response.status_code == 200):
                        print(
                            f"INFO:     Update {person.name} to {device.ip_address} SUCCESS!")
                        await Logs.create(operation="UPDATE PERSON", device=f"{device.name}", data=person.name, status="SUCCESS", operation_time=elapsed)
                    else:
                        print(
                            f"INFO:     Update {person.name} to {device.ip_address} FAILED!")
                        await Logs.create(operation="UPDATE PERSON", device=f"{device.name}", data=person.name, status="FAILED", operation_time=elapsed)

            # add new person because not exist
            else:
                # building = device.building
                if device.building == 2:
                    # print("BUILDING  :", device)
                    # if not building:
                    url = f"http://{device.ip_address}:80/ISAPI/AccessControl/UserInfo/Record?format=json"
                    payload = json.dumps({
                        "UserInfo": {
                            "employeeNo": str(person_id),
                            "name": person.name,
                            "userType": "normal",
                            "Valid": {
                                "enable": True,
                                "beginTime": person.starting_time.replace(microsecond=0, tzinfo=None).isoformat(),
                                "endTime": person.expire_time.replace(microsecond=0, tzinfo=None).isoformat(),
                                "timeType": "local"
                            },
                            "doorRight": "1",
                            "RightPlan": [
                                {
                                    "doorNo": 1,
                                    "planTemplateNo": "1"
                                }
                            ],
                            "password": "9999",
                            "userVerifyMode": "cardOrFaceOrFp"
                        }
                    })
                    start = time.time()
                    try:
                        response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                            device.username, device.password), timeout=5)
                    except:
                        print("ERROR:     Register person exception happened")
                    finally:
                        end = time.time()
                        elapsed = (end-start)
                        elapsed = str("%.2f" % elapsed)

                        if (response.status_code == 200):
                            print(
                                f"INFO:     Register {person.name} to {device.ip_address} SUCCESS!")
                            await Logs.create(operation="ADD PERSON", device=f"{device.name}", data=person.name, status="SUCCESS", operation_time=elapsed)
                        else:
                            print("register person failed")
                            await Logs.create(operation="ADD PERSON", device=f"{device.name}", data=person.name, status="FAILED", operation_time=elapsed)

                if device.building == 1:
                    url = f"http://{device.ip_address}:80/ISAPI/AccessControl/UserInfo/Record?format=json"
                    payload = json.dumps({
                        "UserInfo": {
                            "employeeNo": str(person_id),
                            "name": person.name,
                            "userType": "normal",
                            "Valid": {
                                "enable": True,
                                "beginTime": person.starting_time.replace(microsecond=0, tzinfo=None).isoformat(),
                                "endTime": person.expire_time.replace(microsecond=0, tzinfo=None).isoformat(),
                                "timeType": "local"
                            },
                            "doorRight": "1",
                            "RightPlan": [
                                {
                                    "doorNo": 1,
                                    "planTemplateNo": "1"
                                }
                            ],
                            "password": "9999",
                            "userVerifyMode": "faceAndCard"
                        }
                    })

                    start = time.time()
                    try:
                        response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                            device.username, device.password), timeout=5)
                    except:
                        print("ERROR:     Register person exception happened")
                    finally:
                        end = time.time()
                        elapsed = (end-start)
                        elapsed = str("%.2f" % elapsed)

                        if (response.status_code == 200):
                            print(
                                f"INFO:     Register {person.name} to {device.ip_address} SUCCESS!")
                            await Logs.create(operation="ADD PERSON", device=f"{device.name}", data=person.name, status="SUCCESS", operation_time=elapsed)
                        else:
                            print("register person failed")
                            await Logs.create(operation="ADD PERSON", device=f"{device.name}", data=person.name, status="FAILED", operation_time=elapsed)

            if ((person.finger_hik != "") or (len(person.finger_hik) > 0)):
                print(f"INFO:     Updating {person.name} fingerprint...")
                url = f"http://{device.ip_address}:80/ISAPI/AccessControl/FingerPrint/SetUp?format=json"
                payload = json.dumps({
                    "FingerPrintCfg": {
                        "employeeNo": str(person_id),
                        "enableCardReader": [
                            1
                        ],
                        "fingerPrintID": 1,
                        "fingerType": "normalFP",
                        "fingerData": person.finger_hik
                    }
                })
                start = time.time()
                try:
                    response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                        device.username, device.password), timeout=5)
                except:
                    print(
                        f"INFO:     Updating {person.name} fingerprint FAILED!")
                finally:
                    end = time.time()
                    elapsed = (end-start)
                    elapsed = str("%.2f" % elapsed)
                    response.close()
                    if (response.status_code == 200):
                        print(
                            f"INFO:     Updating {person.name} fingerprint SUCCESS!")
                        await Logs.create(operation="UPDATE FINGERPRINT", device=f"{device.name}", data=person.name, status="SUCCESS")
                    else:
                        print("updating person fingerprint failed")
                        await Logs.create(operation="UPDATE FINGERPRINT", device=f"{device.name}", data=person.name, status="FAILED")

            if ((person.id_card != "") or (len(person.id_card) > 0)):
                print(f"INFO:     Updating {person.name} card...")
                url = f"http://{device.ip_address}:80/ISAPI/AccessControl/CardInfo/Record?format=json"
                payload = json.dumps({
                    "CardInfo": {
                        "employeeNo": str(person_id),
                        "cardNo": person.id_card,
                        "cardType": "normalCard"
                    }
                })
                start = time.time()
                try:
                    time.sleep(.4)
                    response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                        device.username, device.password), timeout=15)
                except:
                    print(f"ERROR:     Updating {person.name} id_card FAILED!")
                finally:
                    end = time.time()
                    elapsed = (end-start)
                    elapsed = str("%.2f" % elapsed)
                    response.close()
                    # if (response.status_code == 200):
                    #     print(
                    #         f"INFO:     Updating {person.name} id_card SUCCESS!")
                    #     await Logs.create(operation="UPDATE ID_CARD", device=f"{device.name}", data=person.id_card, status="SUCCESS")
                    # else:
                    #     print(
                    #         f"ERROR:     Updating {person.name} id_card FAILED!")
                    #     # print("payload card:", payload)
                    #     # print("response card:", response)
                    #     await Logs.create(operation="UPDATE ID_CARD", device=f"{device.name}", data=person.id_card, status="FAILED")

            if ((person.photo != "") or (len(person.photo) > 0)):
                print(f"INFO:     Updating {person.name} photo...")

                # eksekusi pengiriman foto ke user

                # memformat mesin agar ready menerima foto
                # print("updating person photo")
                # url = f"http://{device.ip_address}:80/ISAPI/Intelligent/FDLib?format=json"
                # payload = json.dumps({
                #   "faceLibType": "blackFD",
                #   "name": "local"
                # })
                # try:
                #   response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(device.username, device.password), timeout=5)
                # except:
                #   print("format person photo exception happened")

                # response.close()

                # if (response.status_code == 200):
                #   print("format person photo success")
                # else:
                #   print("format person photo failed")

                # mengirim foto ke mesin
                url = f"http://{device.ip_address}:80/ISAPI/Intelligent/FDLib/FaceDataRecord?format=json"
                # TODO:  ip address untuk ambil gambar jangan hardcode
                payload = json.dumps({
                    "faceLibType": "blackFD",
                    "FDID": "1",
                    "FPID": str(person.id),
                    "name": str(person.name),
                    "faceURL": f"http://{host_ip}:8000{person.photo}"
                })
                start = time.time()
                try:
                    # import docker
                    # client = docker.DockerClient()
                    # container = client.containers.get("frontend")
                    # ip_add = container.attrs['NetworkSettings']['IPAddress']
                    # print("INFO:    alamat IP container: ",ip_add)
                    # timeout=60
                    response = requests.post(
                        # "POST",
                        url,
                        headers=headers,
                        data=payload,
                        auth=HTTPDigestAuth(device.username,
                                            device.password),
                        timeout=120
                    )
                    print("response auth    :", response.auth)
                except Exception as e:
                    print("DEBUG:     PAYLOAD: ", payload)
                    print("ERROR:     ", e)
                finally:
                    end = time.time()
                    elapsed = (end-start)
                    elapsed = str("%.2f" % elapsed)
                    if (response.status_code == 200):
                        await Logs.create(operation="UPDATE PHOTO", device=f"{device.name}", data=person.name, status="SUCCESS", operation_time=elapsed)
                    else:
                        print("payload photo:", payload)
                        print("response photo:", response.json())
                        await Logs.create(operation="UPDATE PHOTO", device=f"{device.name}", data=person.name, status="FAILED", operation_time=elapsed)


async def deauthorize_person_hik(person_id: int, device_ids: list()):
    """
    Authorize Person to device
    :param post: Authorize Person
    :return:
    """

    print("INFO:     Deauthorizing person")
    person = await Person.get_or_none(id=person_id)
    if not person:
        print(f"ERROR:     Could not find person with ID: {person_id}")
        return fail(msg=f"Could not find person with ID {person_id}")
    for device_id in device_ids:
        device = await Device.get_or_none(id=device_id)
        if not device:
            print(f"ERROR:     Could not find device with ID: {device_id}")
        else:
            url = f"http://{device.ip_address}:80/ISAPI/AccessControl/UserInfoDetail/Delete?format=json"
            payload = json.dumps({
                "UserInfoDetail": {
                    "mode": "byEmployeeNo",
                    "EmployeeNoList": [
                        {
                            "employeeNo": str(person.id)
                        }
                    ]
                }
            })
            start = time.time()
            try:
                response = requests.request("PUT", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                    device.username, device.password), timeout=5)
            except:
                print("deauthorize person exception happened")
            finally:
                response.close()
                end = time.time()
                elapsed = (end-start)
                elapsed = str("%.2f" % elapsed)
                if (response.status_code == 200):
                    print(f"INFO:     Deauthorize {person.name} SUCCESS!")
                    await Logs.create(
                        operation="DEAUTHORIZE PERSON",
                        device=f"{device.name}",
                        data=person.name,
                        status="SUCCESS",
                        operation_time=elapsed
                    )
                else:
                    print(f"INFO:     Deauthorize {person.name} FAILED!")
                    await Logs.create(
                        operation="DEAUTHORIZE PERSON",
                        device=f"{device.name}",
                        data=person.name,
                        status="FAILED",
                        operation_time=elapsed
                    )



async def get_registered_person(device: Device):
    """
    Log from devices
    :param post: Log Device
    :return:
    """

    registered_person_ids = []

    # print("log_device terpanggil")

    # headers untuk request
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'ACCEPT': '*/*',
        'ACCEPT-ENCODING': 'gzip, deflate',
        'ACCEPT-LANGUAGE': 'en-US,en;q=0.9',
        'REFERER': 'https://dgos.id/',
        'Connection': 'close',
        'X-Requested-With': 'XMLHttpRequest'
    }

    url = f"http://192.168.101.170:80/ISAPI/AccessControl/UserInfo/Search?format=json"

    import datetime

    
    payload = json.dumps({
    "UserInfoSearchCond": {
        "searchID": "146",
        "searchResultPosition": 0,
        "maxResults": 30,
        "EmployeeNoList": []
    }
    })
    start = time.time()
    try:
        # print("trying to get first data...")
        response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
            "admin", "rahasia123"), timeout=5)
    except Exception as e:
        print("get registered person exception happened :", e)
    else:
        if (response.status_code == 200):
            # print(response.json()['AcsEvent']['InfoList'])
            totalMatches = response.json()['UserInfoSearch']['totalMatches']
            
            total_tarikan = math.ceil(totalMatches / 30)
            # print(
            #     f"Total data ada {totalMatches}, akan ditarik sebanyak {total_tarikan}")

            for lupingan in range(1, total_tarikan+1):
                if lupingan == 1:
                    searchResultPos = 0
                else:
                    searchResultPos = (lupingan * 30) - 31
                payload = json.dumps({
                    "UserInfoSearchCond": {
                        "searchID": "146",
                        "searchResultPosition": int(searchResultPos),
                        "maxResults": 30,
                        "EmployeeNoList": []
                    }}
                )
                try:
                    # print(f"INFO: melakukan tarikan data person ke-{lupingan}")
                    # print(f"Payload: {payload}")
                    # print("response lupingan", response.json())
                    response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                        "admin", "rahasia123"), timeout=5)
                except:
                    print("get log devices exception happened")
                finally:
                    response.close()
                    if (response.status_code == 200) and response.json()['UserInfoSearch']['totalMatches'] > 0:
                        # proses data person di sini
                        userInfos = response.json()['UserInfoSearch']['UserInfo']
                        for u in userInfos:
                            # print(u['employeeNo'])
                            registered_person_ids.append(u['employeeNo'])

    end = time.time()
    elapsed = (end-start)
    elapsed = str("%.2f" % elapsed)
    print("time spent:", elapsed)
    print(len(registered_person_ids))

async def set_http_listening():
    """
    Set HTTP Listening to all devices
    :param post: Log Device
    :return:
    """

    print("set_http_listening terpanggil")

    # headers untuk request
    header = {
        'Content-Type': 'application/xml',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'ACCEPT': '*/*',
        'ACCEPT-ENCODING': 'gzip, deflate',
        'ACCEPT-LANGUAGE': 'en-US,en;q=0.9',
        'REFERER': 'https://dgos.id/',
        'Connection': 'close',
        'X-Requested-With': 'XMLHttpRequest'
    }

    semua_device_hik = await Device.filter(family=1)
    # print("HIKVISION    :", semua_device_hik)
    
    for device in semua_device_hik:
        # print(device.id, device.ip_address)
        if not device:
            print("Could not find device with ID:", device.id)
        else:
            url = f"http://{device.ip_address}:80/ISAPI/Event/notification/httpHosts"
            # print("INFO:    ",device.ip_address)
            payload = f"""
            <HttpHostNotificationList version=\"2.0\" xmlns=\"http://www.isapi.org/ver20/XMLSchema\">
                <HttpHostNotification>
                    <id>2</id>
                    <url>/laporanpintu</url>
                    <protocolType>HTTP</protocolType>
                    <parameterFormatType>XML</parameterFormatType>
                    <addressingFormatType>ipaddress</addressingFormatType>
                    <ipAddress>{host_ip}</ipAddress>
                    <portNo>{host_port}</portNo>
                    <userName></userName>
                    <httpAuthenticationMethod>none</httpAuthenticationMethod>
                </HttpHostNotification>
            </HttpHostNotificationList>
            """
            # print(payload)
            try:
                response = requests.request("PUT", url, headers=header, data=payload, auth=HTTPDigestAuth(
                    device.username, device.password), timeout=5)
                # print(response)
                # print("Device Username:", device.username)
                # print("Device Password:", device.password)
            except Exception as e:
                print("set_http_listening exception happened:", e)
            else:
                response.close()

                if (response.status_code == 200):
                    # print(response.json()['AcsEvent']['InfoList'])
                    print(device.ip_address, " succeeded")
    

async def log_device():
    """
    Log from devices
    :param post: Log Device
    :return:
    """

    print("log_device terpanggil")

    # headers untuk request
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'ACCEPT': '*/*',
        'ACCEPT-ENCODING': 'gzip, deflate',
        'ACCEPT-LANGUAGE': 'en-US,en;q=0.9',
        'REFERER': 'https://dgos.id/',
        'Connection': 'close',
        'X-Requested-With': 'XMLHttpRequest'
    }

    semua_device_hik = await Device.filter(family=1)
    print("HIKVISION    :", semua_device_hik)
    semua_device_pj = await Device.filter(family=2)
    print("PJ08 :", semua_device_pj)

    for device in semua_device_hik:
        if not device:
            print("Could not find device with ID:", device.id)
        else:
            url = f"http://{device.ip_address}:80/ISAPI/AccessControl/AcsEvent?format=json"

            import datetime

            tod = datetime.datetime.now()
            d = datetime.timedelta(days=2)
            kemarin = tod - d
            kemarin = kemarin.replace(
                microsecond=0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Jakarta')).isoformat()
            sekarang = tod.replace(microsecond=0, tzinfo=zoneinfo.ZoneInfo(
                key='Asia/Jakarta')).isoformat()
            # print("kemarin: ", kemarin)
            # print("sekarang: ", sekarang)

            payload = json.dumps({
                "AcsEventCond": {
                    "searchID": "pjvms",
                    "searchResultPosition": 0,
                    "maxResults": 99999,
                    "major": 0,
                    "minor": 0,
                    "picEnable": True,
                    "startTime": str(kemarin),
                    "endTime": str(sekarang)
                }
            })
            # print("payload", payload)
            try:
                response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                    device.username, device.password), timeout=5)
            except Exception as e:
                print("get log devices exception happened :", e)
            else:
                response.close()

                if (response.status_code == 200):
                    # print(response.json()['AcsEvent']['InfoList'])
                    InfoLists = response.json()['AcsEvent']['InfoList']
                    # print("Info List:", InfoLists)
                    # print("length:", len(InfoLists))
                    total_data_log = response.json(
                    )['AcsEvent']['totalMatches']

                    total_tarikan = math.ceil(total_data_log / 30)
                    print(
                        f"Total data ada {total_data_log}, akan ditarik sebanyak {total_tarikan}")

                    for lupingan in range(1, total_tarikan+1):
                        if lupingan == 1:
                            searchResultPos = 0
                        else:
                            searchResultPos = (lupingan * 30) - 31
                        payload = json.dumps({
                            "AcsEventCond": {
                                "searchID": "pjvms",
                                "searchResultPosition": int(searchResultPos),
                                "maxResults": 99999,
                                "major": 0,
                                "minor": 0,
                                "picEnable": True,
                                "startTime": str(kemarin),
                                "endTime": str(sekarang)
                            }
                        })
                        try:
                            print(f"INFO: melakukan tarikan log ke-{lupingan}")
                            # print(f"Payload: {payload}")
                            # print("response lupingan", response.json())
                            response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                                device.username, device.password), timeout=5)
                        except:
                            print("get log devices exception happened")
                        finally:
                            response.close()
                            if (response.status_code == 200) and response.json()['AcsEvent']['numOfMatches'] > 0:
                                InfoLists = response.json(
                                )['AcsEvent']['InfoList']
                                for InfoList in InfoLists:
                                    # if (InfoList['major'] == ""):
                                    if InfoList['minor'] == 1 or InfoList['minor'] == 38 or InfoList['minor'] == 75:
                                        # print(InfoList)
                                        if 'pictureURL' in InfoList:
                                            if InfoList['pictureURL'] != '':
                                                photo = InfoList['pictureURL']
                                        else:
                                            photo = ''

                                        if 'cardNo' in InfoList:
                                            if InfoList['cardNo'] != '':
                                                card = InfoList["cardNo"]
                                        else:
                                            card = ''

                                        if InfoList['minor'] == 75:
                                            passrecord_type = 'Face'
                                        elif InfoList['minor'] == 1:
                                            passrecord_type = 'Card'
                                        elif InfoList['minor'] == 38:
                                            passrecord_type = 'Fingerprint'

                                        try:
                                            await Passrecord.create(
                                                name=InfoList["name"],
                                                device_name=device.name,
                                                photo=photo,
                                                card_number=card,
                                                passrecord_type=passrecord_type,
                                                pass_time=InfoList['time']
                                            )
                                            print(
                                                "Non duplicate entry logged...")
                                        except:
                                            print(
                                                "Duplicate entry for log skipped")
                                    # if InfoList['minor'].
    for device in semua_device_pj:
        headerss = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        if not device:
            print("Could not find device with ID:", device.id)
        else:
            url = f"http://{device.ip_address}:8090/newFindRecords"

            import datetime

            # tod = datetime.datetime.now()
            # print("TODAY    :", tod)
            tod = datetime.datetime.fromtimestamp(
                time.time(), tz=pytz.timezone('Asia/Jakarta'))
            d = datetime.timedelta(days=2)
            kemarin = tod - d
            kemarin = kemarin.replace(
                microsecond=0)
            print("KEMARIN     :", kemarin)
            sekarang = tod.replace(microsecond=0)
            # sekarang = tod.replace(microsecond=0, tzinfo=zoneinfo.ZoneInfo(
            #     key='Asia/Jakarta'))
            # print("kemarin: ", kemarin)
            print("sekarang: ", sekarang)
            startTime = str(kemarin)
            endTime = str(sekarang)
            startTime = urllib.parse.quote(startTime)
            endTime = urllib.parse.quote(endTime)
            lengthNum = 99999999
            indexNum = 0
            modelNum = -1
            orderNum = 0
            payload = f'pass={device.password}&personId=-1&length={lengthNum}&index={indexNum}&startTime={startTime}&endTime={endTime}&model={modelNum}&order={orderNum}'
            print("PAYLOAD  :", payload)
            response = ""
            try:
                response = requests.request(
                    "POST", url, headers=headerss, data=payload)
            except Exception as e:
                print("get log devices exception pj happened :", e)
            finally:
                if response != "":
                    response.close()

                    if (response.status_code == 200):
                        # print(response.json()['AcsEvent']['InfoList'])
                        records = response.json()['data']['records']
                        print("RECORD   :", records)
                        # print("Info List:", InfoLists)
                        # print("length:", len(InfoLists))
                        # total_data_log = response.json(
                        # )['data']['total']

                        # total_tarikan = math.ceil(total_data_log / 30)
                        # print(
                        #     f"Total data ada {total_data_log}, akan ditarik sebanyak {total_tarikan}")

                        # for lupingan in range(1, total_tarikan+1):
                        #     if lupingan == 1:
                        #         searchResultPos = 0
                        #     else:
                        #         searchResultPos = (lupingan * 30) - 31
                        #         payload = f'pass={device.password}&personId=-1&length=-1&index=0&startTime=' + \
                        #             startTime+'&endTime='+endTime+'&model=-1&order=1'
                        #         response = ""
                        #     try:
                        #         print(f"INFO: melakukan tarikan log ke-{lupingan}")
                        #         # print(f"Payload: {payload}")
                        #         # print("response lupingan", response.json())
                        #         response = requests.request(
                        #         "POST", url, headers=headerss, data=payload)
                        #     except:
                        #         print("get log devices exception happened")
                        #     finally:
                        # if response !="":
                        #     response.close()
                        # if (response.status_code == 200) and response.json()['data'] > 0:
                        # records = response.json(
                        # )['data']

                        for record in records:
                            # if (InfoList['major'] == ""):
                            if record in records:
                                # print(InfoList)
                                if 'personId' in record:
                                    if record['personId'] != 0:
                                        personId = record['personId']
                                        person = await Person.filter(id=personId)
                                        if person:
                                            person = person[0]
                                else:
                                    personId = ''
                                # print("PERSON ID    :", personId)
                                print("PERSON     :", person)

                                if 'idcard' in record:
                                    if record['idcard'] != '':
                                        card = record["idcard"]
                                else:
                                    card = ''

                                if 'time' in record:
                                    if record['time'] != '':
                                        epoch = record['time']
                                        waktu = datetime.datetime.fromtimestamp(
                                            int(epoch/1000)).strftime('%Y-%m-%d %H:%M:%S')
                                else:
                                    waktu = ''
                                # print('EPOCH   :', epoch)
                                # print("TIME    :", time)

                                if record['type'] == "face_0":
                                    passrecord_type = 'Face'
                                elif record['type'] == "card_0":
                                    passrecord_type = 'Card'
                                elif record['type'] == "finger_0":
                                    passrecord_type = 'Fingerprint'

                                try:
                                    await Passrecord.create(
                                        name=person.name,
                                        device_name=device.name,
                                        photo=person.photo,
                                        card_number=card,
                                        passrecord_type=passrecord_type,
                                        pass_time=waktu
                                    )
                                    print(
                                        "Non duplicate entry logged...")
                                except:
                                    print(
                                        "Duplicate entry for log skipped")
                        print("get log devices success")


async def log_attendance():
    """
    Log Attendance
    :param post: Log Attendance
    :return:
    """

    print("log_attendance terpanggil")
    devices = await Device.filter(name__contains="absensi").all()
    for device in devices:
        print(device.name)
        if not devices:
            print("Could not find device with name absensi")
        else:
            url = f"http://{device.ip_address}:80/ISAPI/AccessControl/AcsEvent?format=json"

            import datetime

            tod = datetime.datetime.now()
            d = datetime.timedelta(days=4)
            kemarin = tod - d
            kemarin = kemarin.replace(
                microsecond=0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Jakarta'))
            sekarang = tod.replace(microsecond=0, tzinfo=zoneinfo.ZoneInfo(
                key='Asia/Jakarta'))
            print("kemarin: ", kemarin)
            print("sekarang: ", sekarang)

            payload = json.dumps({
                "AcsEventCond": {
                    "searchID": "pjvms",
                    "searchResultPosition": 0,
                    "maxResults": 99999,
                    "major": 0,
                    "minor": 0,
                    "picEnable": True,
                    "startTime": str(kemarin),
                    "endTime": str(sekarang)
                }
            })
            print("payload", payload)
            try:
                response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                    device.username, device.password), timeout=5)
            except:
                print("get attendance exception happened")
            finally:
                response.close()

            print("response", response)

            if (response.status_code == 200):
                # print(response.json()['AcsEvent']['InfoList'])
                InfoLists = response.json()['AcsEvent']['InfoList']
                print("Info List:", InfoLists)
                print("length:", len(InfoLists))
                total_data_log = response.json()['AcsEvent']['totalMatches']

                total_tarikan = math.ceil(total_data_log / 30)
                print(
                    f"Total data ada {total_data_log}, akan ditarik sebanyak {total_tarikan}")

                for lupingan in range(1, total_tarikan+1):
                    if lupingan == 1:
                        searchResultPos = 0
                    else:
                        searchResultPos = (lupingan * 30) - 31
                    payload = json.dumps({
                        "AcsEventCond": {
                            "searchID": "pjvms",
                            "searchResultPosition": int(searchResultPos),
                            "maxResults": 99999,
                            "major": 0,
                            "minor": 0,
                            "picEnable": True,
                            "startTime": str(kemarin),
                            "endTime": str(sekarang)
                        }
                    })
                    try:
                        print(
                            f"INFO: melakukan tarikan attendance ke-{lupingan}")
                        print(f"Payload: {payload}")
                        response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                            device.username, device.password), timeout=5)

                    except:
                        print("get attndance exception happened")
                    finally:
                        response.close()
                        if (response.status_code == 200) and response.json()['AcsEvent']['numOfMatches'] > 0:
                            InfoLists = response.json()['AcsEvent']['InfoList']
                            for InfoList in InfoLists:
                                # if (InfoList['major'] == ""):
                                if InfoList['minor'] == 1 or InfoList['minor'] == 38 or InfoList['minor'] == 75:
                                    # print(InfoList)
                                    if 'pictureURL' in InfoList:
                                        if InfoList['pictureURL'] != '':
                                            photo = InfoList['pictureURL']
                                    else:
                                        photo = ''

                                    if 'cardNo' in InfoList:
                                        if InfoList['cardNo'] != '':
                                            card = InfoList["cardNo"]
                                    else:
                                        card = ''

                                    if InfoList['minor'] == 75:
                                        passrecord_type = 'Face'
                                    elif InfoList['minor'] == 1:
                                        passrecord_type = 'Card'
                                    elif InfoList['minor'] == 38:
                                        passrecord_type = 'Fingerprint'

                                    try:
                                        await Attendance.create(
                                            name=InfoList["name"],
                                            device_name=device.name,
                                            photo=photo,
                                            card_number=card,
                                            passrecord_type=passrecord_type,
                                            pass_time=InfoList['time']
                                        )
                                        print("Non duplicate entry logged...")
                                    except:
                                        print("Duplicate entry for log skipped")
                                # if InfoList['minor'].

                            print("get log devices success")


async def fungsi_test_email():
    """
    Test Email
    :param post: Test Email
    :return:
    """

    print("Fungsi Test email terpanggil")

    # headers untuk request

    email_setting = await Email.all()
    print("email :", email_setting)

    for emails in email_setting:
        if not emails:
            print("Could not find :", emails.email)
        else:
            conf = ConnectionConfig(
                MAIL_USERNAME=emails.username_email,
                MAIL_PASSWORD=emails.password_email,
                MAIL_PORT=emails.port,
                MAIL_SERVER=emails.host,
                MAIL_FROM=emails.email,
                MAIL_TLS=True,
                MAIL_SSL=False
            )
            template = """
                    
            
                    Halo !!!
                    Ini adalah email uji coba yang dikirim dari PJVMS, nantinya email ini akan berisi notifikasi atau rekap laporan
            
            
                    """

            message = MessageSchema(
                subject="PJVMS Test Email",
                # List of recipients, as many as you can pass
                recipients={emails.email, },
                body=template,
                subtype="plain"
            )

            fm = FastMail(conf)
            await fm.send_message(message)
            print(message)


async def unlock_door_hik(device_ip: str):
    """
    Unlock Door
    :param post: Unlock Door
    :return:
    """

    device = await Device.get_or_none(ip_address=device_ip)
    if not device:
        return fail(msg=f"Failed to get device with IP {device_ip}!")

    url = f"http://{device.ip_address}:80/ISAPI/AccessControl/RemoteControl/door/1"

    payload = "<RemoteControlDoor version=\"2.0\" xmlns=\"http://www.isapi.org/ver20/XMLSchema\">\r\n    <cmd>open</cmd>\r\n</RemoteControlDoor>"
    headers = {
        'Content-Type': 'application/xml'
    }

    try:
        response = requests.request(
            "PUT",
            url,
            headers=headers,
            data=payload,
            auth=HTTPDigestAuth('admin', 'rahasia123'),
            timeout=1
        )
        await Logs.create(operation="UNLOCK DOOR", device=f"{device.name}", data='', status="SUCCESS")
        return success(msg="Unlocking door success!", data=[])
    except Exception as e:
        await Logs.create(operation="UNLOCK DOOR", device=f"{device.name}", data='', status="FAILED")
        return fail(msg="Unlocking fail!")


# async def daftarRuangan():
#     """
#     daftarRuangan
#     :param post: daftarRuangan
#     :return:
#     """

#     print("Daftar Ruangan terpanggil")

#     # headers untuk request

#     ruangan = await Device.filter(fanily=1).all()
#     print("ruangan :", ruangan)

#     for ruangans in ruangan:
#         if not ruangans:
#             print("Could not find :", ruangans.ruangan)
#         else:
#             ruangan = ''


# async def daftarPengunjung():
#     """
#     daftarPengunjung
#     :param post: daftarPengunjung
#     :return:
#     """

#     print("Daftar Pengunjung terpanggil")

#     # headers untuk request

#     pengunjung = await Person.filter(type=2).all()
#     print("pengunjung :", pengunjung)

#     for pengunjungs in pengunjung:
#         if not pengunjungs:
#             print("Could not find :", pengunjungs.pengunjung)
#         else:
#             pengunjung = ''

async def code_by_yo(ip_a:str, sekarang_ya:str):
    """
    Log from devices
    :param post: Log Device
    :return:
    """

    print("log_device terpanggil")

    # headers untuk request
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'ACCEPT': '*/*',
        'ACCEPT-ENCODING': 'gzip, deflate',
        'ACCEPT-LANGUAGE': 'en-US,en;q=0.9',
        'REFERER': 'https://dgos.id/',
        'Connection': 'close',
        'X-Requested-With': 'XMLHttpRequest'
    }

    semua_device_hik = await Device.filter(family=1, ip_address=ip_a)
    print("HIKVISION    :", semua_device_hik)
   

    for device in semua_device_hik:
        if not device:
            print("Could not find device with ID:", device.id)
        else:
            url = f"http://{device.ip_address}:80/ISAPI/AccessControl/AcsEvent?format=json"

            import datetime

            
            
            kemarin = sekarang_ya
            sekarang = sekarang_ya
            # print("kemarin: ", kemarin)
            # print("sekarang: ", sekarang)

            payload = json.dumps({
                "AcsEventCond": {
                    "searchID": "pjvms",
                    "searchResultPosition": 0,
                    "maxResults": 99999,
                    "major": 0,
                    "minor": 0,
                    "picEnable": True,
                    "startTime": (kemarin),
                    "endTime": (sekarang)
                }
            })
            # print("payload", payload)
            try:
                response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                    device.username, device.password), timeout=5)
            except Exception as e:
                print("get log devices exception happened :", e)
            else:
                response.close()

                if (response.status_code == 200):
                    # print(response.json()['AcsEvent']['InfoList'])
                    InfoLists = response.json()['AcsEvent']['InfoList']
                    # print("Info List:", InfoLists)
                    # print("length:", len(InfoLists))
                    total_data_log = response.json(
                    )['AcsEvent']['totalMatches']

                    total_tarikan = math.ceil(total_data_log / 30)
                    print(
                        f"Total data ada {total_data_log}, akan ditarik sebanyak {total_tarikan}")

                    for lupingan in range(1, total_tarikan+1):
                        if lupingan == 1:
                            searchResultPos = 0
                        else:
                            searchResultPos = (lupingan * 30) - 31
                        payload = json.dumps({
                            "AcsEventCond": {
                                "searchID": "pjvms",
                                "searchResultPosition": int(searchResultPos),
                                "maxResults": 99999,
                                "major": 0,
                                "minor": 0,
                                "picEnable": True,
                                "startTime": (kemarin),
                                "endTime": (sekarang)
                            }
                        })
                        try:
                            print(f"INFO: melakukan tarikan log ke-{lupingan}")
                            # print(f"Payload: {payload}")
                            # print("response lupingan", response.json())
                            response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                                device.username, device.password), timeout=5)
                        except:
                            print("get log devices exception happened")
                        finally:
                            response.close()
                            # print(response.json())
                            if (response.status_code == 200) and response.json()['AcsEvent']['numOfMatches'] > 0:
                                InfoLists = response.json(
                                )['AcsEvent']['InfoList']
                                for InfoList in InfoLists:
                                    # if (InfoList['major'] == ""):
                                    if InfoList['minor'] == 1 or InfoList['minor'] == 38 or InfoList['minor'] == 75 or InfoList['minor'] == 76:
                                        # print(InfoList)
                                        nama_foto = str(uuid.uuid4())
                                        if 'pictureURL' in InfoList:
                                            if InfoList['pictureURL'] != '':
                                                photo = InfoList['pictureURL']
                                                # print(photo)
                                                response = requests.get(str(photo))
                                                
                                                save_path = "static/upload/photo/"+nama_foto+".jpeg"
                                                save_path_small= "static/upload/photo/"+nama_foto+"_small.jpeg"

                                                username ="admin"
                                                password = "rahasia123"
                                                
                                                with requests.Session() as session:
                                                    session.auth = HTTPDigestAuth(username, password)

                                                    # Send a GET request to the URL
                                                    response = session.get(photo)

                                                    # Check if the request was successful (status code 200)
                                                    if response.status_code == 200:
                                                        # Open the image using Pillow
                                                        image = Image.open(BytesIO(response.content))
                                                        
                                                        # Save the image to the specified path
                                                        
                                                        image.save(save_path)
                                                        crop_face(save_path,save_path_small,0)
                                                        print(f"Image downloaded and saved to {save_path}")
                                                    else:
                                                        print(f"Failed to download image. Status code: {response.status_code}")
                                        else:
                                            photo = ''

                                        if 'cardNo' in InfoList:
                                            if InfoList['cardNo'] != '':
                                                card = InfoList["cardNo"]
                                        else:
                                            card = ''

                                        if InfoList['minor'] == 75:
                                            passrecord_type = 'Face'
                                        elif InfoList['minor'] == 1:
                                            passrecord_type = 'Card'
                                        elif InfoList['minor'] == 76:
                                            passrecord_type = 'Asing'
                                        elif InfoList['minor'] == 38:
                                            passrecord_type = 'Fingerprint'

                                        try:
                                            if InfoList['minor'] == 75:
                                                await Buku_tamu.create(
                                                    name=InfoList["name"],
                                                    device_name=device.name,
                                                    photo="/upload/photo/"+nama_foto+".jpeg",
                                                    pass_time=InfoList['time'])

                                            elif InfoList['minor'] == 76:
                                                await Stranger.create(
                                                    device_name=device.name,
                                                    photo="/upload/photo/"+nama_foto+".jpeg",
                                                    pass_time=InfoList['time'])
                                            
                                            print(
                                                "Non duplicate entry logged...")
                                        except:
                                            print(
                                                "Duplicate entry for log skipped")
                                    # if InfoList['minor'].
    
                        print("get log devices success")


# async def photo_upload(file: UploadFile = File(...)):
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

def download_image(url ):
    response = requests.get(url)
    save_path = "static/upload/photo/"+str(uuid.uuid4())+".jpeg"
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


async def code_by_yos(ip_a:str, sekarang_ya:str):
    """
    Log from devices
    :param post: Log Device
    :return:
    """

    print("log_device terpanggil")

    # headers untuk request
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'ACCEPT': '*/*',
        'ACCEPT-ENCODING': 'gzip, deflate',
        'ACCEPT-LANGUAGE': 'en-US,en;q=0.9',
        'REFERER': 'https://dgos.id/',
        'Connection': 'close',
        'X-Requested-With': 'XMLHttpRequest'
    }

    semua_device_hik = await Device.filter(family=1, ip_address=ip_a)
    print("HIKVISION    :", semua_device_hik)
   

    for device in semua_device_hik:
        if not device:
            print("Could not find device with ID:", device.id)
        else:
            url = f"http://{device.ip_address}:80/ISAPI/AccessControl/AcsEvent?format=json"

            import datetime

            
            
            kemarin = sekarang_ya
            sekarang = sekarang_ya
            # print("kemarin: ", kemarin)
            # print("sekarang: ", sekarang)

            payload = json.dumps({
                "AcsEventCond": {
                    "searchID": "pjvms",
                    "searchResultPosition": 0,
                    "maxResults": 99999,
                    "major": 0,
                    "minor": 0,
                    "picEnable": True,
                    "startTime": (kemarin),
                    "endTime": (sekarang)
                }
            })
            # print("payload", payload)
            try:
                response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                    device.username, device.password), timeout=5)
            except Exception as e:
                print("get log devices exception happened :", e)
            else:
                response.close()

                if (response.status_code == 200):
                    # print(response.json())
                    data_id =response.json()['AcsEvent']['InfoList']
                    # print(data_id[0]['employeeNoString'])

                    if data_id and data_id[0] :
                        if 'employeeNoString' in data_id[0]:
                            print("triggerring buka_laintai")
                            await buka_lantai(data_id[0]['employeeNoString'])


sementara = 00000000
# lantai1,lantai2,lantai3,lantai4,lantai5,lantai6,lantai7,lantai8 = 0
lantai = [0,0,0,0,0,0,0,0]
# timer1,timer2,timer3,timer4,timer5,timer6,timer7,timer8 = 0
timer = [datetime.now() for x in range(8)]



async def buka_lantai(id_person:str):
    # print("ini id nya si  kawan ========> "+ id_person)
    # start = datetime.now()
    # start_plus_5s = start+timedelta(seconds=1)
    # if start_plus_5s > datetime.now():
    #     print("start:", start)
    #     print("start_plus_5s", start_plus_5s)
    #     print("masih belum 5 detik")
        # await asyncio.sleep(1)
    # while
    
    data_lantai = await Elevator.get_or_none(id_person=id_person)
    if data_lantai :
        izin_lantai = list(data_lantai.lantai)
        index = 0
        for izin in izin_lantai:
            # print("index:", index)
            if izin == "1":
                print(f"Lantai {index+1} bernilai 1")
                lantai[index] = 1
                command="sed -i 's/.*/1/g' /tmp/elevator/lantai/" + str(index+1)
                subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                timer[index] = datetime.now()
                command="sed -i 's/.*/" + str(timer[index]) + "/g' /tmp/elevator/timer/" + str(index+1)
                subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                

            elif izin == "0":
                if timer[index]+timedelta(seconds=delay_in_second) > datetime.now():
                    print(f"Lantai {index+1} bernilai 1")
                else:
                    lantai[index] = 0
                    command="sed -i 's/.*/0/g' /tmp/elevator/lantai/" + str(index+1)
                    subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(f"---------------------------------Lantai {index+1} bernilai 0")
            index+=1

    tutup_lantai()
                # print("Mereset men")
    # command = "sed -i 's/.*/"+str(data_lantai.lantai)+"/g' /tmp/elevator/lantai"
    # print(command)
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # x=0
    # list_sementara = list(sementara)

    # for i in izin_lantai :
    #     status = "CLOSE"
        
    #     if i == "1":
    #         status = "OPEN"
    #         print("Lantai "+ str(x+1) + " " + status)
    #         lantai[x] = 1
    #         timer[x] = time.time()
    #     else :
    #         status = "CLOSE"
    #         elapsed = time.time() - timer[x]
    #         print(elapsed)
    #         if int(elapsed)  > 3:
    #             print("expired")
    #     x=x+1

            
    # await tutup()
    
#2024-01-17 13:12:41.456174
    
def tutup_lantai():
    timer = ""
    lantai = ""
    lantai_binary = ""
    print("\n")    
    for i in range(1,9):
        with open("/tmp/elevator/lantai/"+str(i), 'r') as file:
            lantai = file.read().replace('\n','')
        with open("/tmp/elevator/timer/"+str(i), 'r') as file:
            timer = file.read().replace('\n','')
        # timer = "2024-01-17 13:12:41.456174"
        print(f"Lantai-{str(i)} berstatus {lantai} sejak {timer}")

        time = datetime.strptime(timer, '%Y-%m-%d %H:%M:%S.%f')
        print("time", time)

        if datetime.now() > time+timedelta(seconds=delay_in_second):
            lantai_binary= lantai_binary +"0 "
            command="sed -i 's/.*/0/g' /tmp/elevator/lantai/" + str(i)
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
     

        else:
            lantai_binary= lantai_binary +"1 "
            command="sed -i 's/.*/1/g' /tmp/elevator/lantai/" + str(i)
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # print(f"Print lantai-{str(i)} expired")

    all_lantai = ""
    with open("/tmp/elevator/lantai/all", 'r') as file:
        all_lantai = file.read().replace('\n','')
    # command="sed -i 's/.*/0/g' /tmp/elevator/lantai/" + str(index+1)
    # subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("all_lantai:", all_lantai)


    lantai_binary = lantai_binary[:-1]
    
    if lantai_binary == all_lantai:
        print("State masih sama, tidak merubah apapun")
    else:

        awal=""
        with open("/tmp/elevator/lantai/awal", 'r') as file:
            awal = file.read().replace('\n','')
        print("awal: ", awal)
        if int(awal) == 1 : 
            command2=f"modpoll -m rtu -a 1 -r 1 -c 8 -t0 -b 9600 -p none /dev/ttyUSB0 0 0 0 0 0 0 0 0"
            command="sed -i 's/.*/"+ lantai_binary +"/g' /tmp/elevator/lantai/all"
            command3="sed -i 's/.*/0/g' /tmp/elevator/lantai/awal"
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(command2, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(command3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        else:
            # l_bin = ''.join(lantai_binary)
            command2=f"modpoll -m rtu -a 1 -r 1 -c 8 -t0 -b 9600 -p none /dev/ttyUSB0 {lantai_binary}"
            command="sed -i 's/.*/"+ lantai_binary +"/g' /tmp/elevator/lantai/all"
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(command2, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


async def tulis_log(ip_a:str, sekarang_ya:str):
    """
    Log from devices
    :param post: Log Device
    :return:
    """

    print("log_device terpanggil")

    # headers untuk request
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'ACCEPT': '*/*',
        'ACCEPT-ENCODING': 'gzip, deflate',
        'ACCEPT-LANGUAGE': 'en-US,en;q=0.9',
        'REFERER': 'https://dgos.id/',
        'Connection': 'close',
        'X-Requested-With': 'XMLHttpRequest'
    }

    semua_device_hik = await Device.filter(family=1, ip_address=ip_a)
    print("HIKVISION    :", semua_device_hik)
   

    for device in semua_device_hik:
        if not device:
            print("Could not find device with ID:", device.id)
        else:
            url = f"http://{device.ip_address}:80/ISAPI/AccessControl/AcsEvent?format=json"

            import datetime

            
            
            kemarin = sekarang_ya
            sekarang = sekarang_ya
            # print("kemarin: ", kemarin)
            # print("sekarang: ", sekarang)

            payload = json.dumps({
                "AcsEventCond": {
                    "searchID": "pjvms",
                    "searchResultPosition": 0,
                    "maxResults": 99999,
                    "major": 0,
                    "minor": 0,
                    "picEnable": True,
                    "startTime": (kemarin),
                    "endTime": (sekarang)
                }
            })
            # print("payload", payload)
            try:
                response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                    device.username, device.password), timeout=5)
            except Exception as e:
                print("get log devices exception happened :", e)
            else:
                response.close()

                if (response.status_code == 200):
                    # print(response.json()['AcsEvent']['InfoList'])
                    InfoLists = response.json()['AcsEvent']['InfoList']
                    # print("Info List:", InfoLists)
                    # print("length:", len(InfoLists))
                    total_data_log = response.json(
                    )['AcsEvent']['totalMatches']

                    total_tarikan = math.ceil(total_data_log / 30)
                    print(
                        f"Total data ada {total_data_log}, akan ditarik sebanyak {total_tarikan}")

                    for lupingan in range(1, total_tarikan+1):
                        if lupingan == 1:
                            searchResultPos = 0
                        else:
                            searchResultPos = (lupingan * 30) - 31
                        payload = json.dumps({
                            "AcsEventCond": {
                                "searchID": "pjvms",
                                "searchResultPosition": int(searchResultPos),
                                "maxResults": 99999,
                                "major": 0,
                                "minor": 0,
                                "picEnable": True,
                                "startTime": (kemarin),
                                "endTime": (sekarang)
                            }
                        })
                        try:
                            print(f"INFO: melakukan tarikan log ke-{lupingan}")
                            # print(f"Payload: {payload}")
                            # print("response lupingan", response.json())
                            response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(
                                device.username, device.password), timeout=5)
                        except:
                            print("get log devices exception happened")
                        finally:
                            response.close()
                            # print(response.json())
                            if (response.status_code == 200) and response.json()['AcsEvent']['numOfMatches'] > 0:
                                InfoLists = response.json(
                                )['AcsEvent']['InfoList']
                                for InfoList in InfoLists:
                                    # if (InfoList['major'] == ""):
                                    if InfoList['minor'] == 1 or InfoList['minor'] == 38 or InfoList['minor'] == 75 or InfoList['minor'] == 76:
                                        # print(InfoList)
                                        nama_foto = str(uuid.uuid4())
                                        if 'pictureURL' in InfoList:
                                            if InfoList['pictureURL'] != '':
                                                photo = InfoList['pictureURL']
                                                # print(photo)
                                                # response = requests.get(str(photo))
                                                
                                                # save_path = "static/upload/photo/"+nama_foto+".jpeg"
                                                # save_path_small= "static/upload/photo/"+nama_foto+"_small.jpeg"

                                                # username ="admin"
                                                # password = "rahasia123"
                                                
                                                # with requests.Session() as session:
                                                #     session.auth = HTTPDigestAuth(username, password)

                                                #     # Send a GET request to the URL
                                                #     response = session.get(photo)

                                                #     # Check if the request was successful (status code 200)
                                                #     if response.status_code == 200:
                                                #         # Open the image using Pillow
                                                #         image = Image.open(BytesIO(response.content))
                                                        
                                                #         # Save the image to the specified path
                                                        
                                                #         image.save(save_path)
                                                #         crop_face(save_path,save_path_small,0)
                                                #         print(f"Image downloaded and saved to {save_path}")
                                                #     else:
                                                #         print(f"Failed to download image. Status code: {response.status_code}")
                                        else:
                                            photo = ''

                                        if 'cardNo' in InfoList:
                                            if InfoList['cardNo'] != '':
                                                card = InfoList["cardNo"]
                                        else:
                                            card = ''

                                        if InfoList['minor'] == 75:
                                            passrecord_type = 'Face'
                                        elif InfoList['minor'] == 1:
                                            passrecord_type = 'Card'
                                        elif InfoList['minor'] == 76:
                                            passrecord_type = 'Asing'
                                        elif InfoList['minor'] == 38:
                                            passrecord_type = 'Fingerprint'

                                        try:
                                            await Passrecord.create(
                                            name=InfoList["name"],
                                            device_name=device.name,
                                            photo=photo,
                                            card_number=card,
                                            passrecord_type=passrecord_type,
                                            pass_time=InfoList['time']
                                            )
                                            
                                            print("Non duplicate entry logged...")
                                        except:
                                            print(
                                                "Duplicate entry for log skipped")
                                    # if InfoList['minor'].
    
                        print("get log devices success")


    # print("Timer Jalan")

    # # await asyncio.sleep(10)
    # # print ("Lantai ALL CLOSE")
    # print("Lantai ALL CLOSE")

    # return "jadi true"
    # Call the function after the delay
    # await my_function()