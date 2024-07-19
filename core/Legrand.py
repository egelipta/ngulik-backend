
"""
@Created on : 2022/4/22 22:02
@Maintainer: dgos
@Des: Tool function
"""

import hashlib
import http
import json
import random
import time
from typing import List
import uuid
from models.device import Device
from models.person import Person
from datetime import timezone, tzinfo
import os
import hashlib
import http
import json
import math
import random
import time
import zoneinfo
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
import requests
from requests.auth import HTTPDigestAuth
from core.Response import fail, success
from models.device import Device
from models.email import Email
from models.logs import Logs
from models.passrecord import Passrecord
from models.attendance import Attendance
from models.person import Person

import urllib.parse
import http.client

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}


async def unlock_door_pj(device_ip: str):
    """
    Unlock Door
    :param post: Unlock Door
    :return:
    """

    device = await Device.get_or_none(ip_address=device_ip)
    if not device:
        return fail(msg=f"Failed to get device with IP {device_ip}!")

    # url = "192.168.99.153:8090/device/openDoorControl"
    url = f"http://{device.ip_address}:8090/device/openDoorControl?pass={device.password}"

    payload = json.dumps({
        "pass": f"{device.password}",
        "type": 1,
        "content": "1"
    })
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded'
    # }

    try:
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=payload,
            # auth=HTTPDigestAuthHandler(device.username, device.password),
            timeout=1
        )
        await Logs.create(operation="UNLOCK DOOR", device=f"{device.name}", data='', status="SUCCESS")
        return success(msg="Unlocking door success!", data=[])
    except Exception as e:
        await Logs.create(operation="UNLOCK DOOR", device=f"{device.name}", data='', status="FAILED")
        return fail(msg="Unlocking fail!")


async def authorize_person_pj(person_id: int, device_ids: list()):
    print("AUTHORZIE PERSON PJ TRIGGERED!!!")
    persons = await Person.get_or_none(id=person_id)
    if not persons:
        print("person not found with id", person_id)
        return fail(msg=f"Could not find person with ID {person_id}")

    for device_id in device_ids:
        device = await Device.get_or_none(id=device_id)
        persons_exist_on_device = True
        if not device:
            print("ERROR:     Could not find device with ID: ", device_id)
        else:

            url = f"http://{device.ip_address}:8090/person/create"
            person = json.dumps({
                "id": f"{persons.id}",
                "name": f"{persons.name}",
                "idCardNum": f"{persons.id_card}"

            })
            person = urllib.parse.quote(person)

            payload = f'pass={device.password}&'+'person='+person

            print("Payload Encoded  :", payload)
            response = ""
            start = time.time()
            try:
                response = requests.request(
                    "POST", url, headers=headers, data=payload)
            except:
                print("Authorize exception happened!")
            finally:
                if response != "":
                    response.close()
                    print(response)
                    end = time.time()
                    elapsed = (end-start)
                    elapsed = str("%.2f" % elapsed)
                    if (response.status_code == 200):
                        print(
                            f"INFO:     Register {device.name} to {device.ip_address} SUCCESS!")
                        await Logs.create(operation="ADD PERSON", device=f"{device.name}", data=persons.name, status="SUCCESS", operation_time=elapsed)
                    else:
                        print("register person failed")
                        await Logs.create(operation="ADD PERSON", device=f"{device.name}", data=persons.name, status="FAILED", operation_time=elapsed)
                else:
                    print(response)

    if ((persons.finger_pj != "") or (len(persons.finger_pj) > 0)):
        print(f"INFO:     Updating {persons.name} fingerprint...")
        url = f"http://{device.ip_address}:8090/api/v2/finger/create"
        data = json.dumps({"fingerId": "",
                          "personId": f"{persons.id}",
                           "fingerNum": "",
                           "feature": f"{persons.finger_pj}"
                           })
        data = urllib.parse.quote(data)
        print("DATA    :", data)
        payload = f'pass={device.password}&'+'data='+'%5B'+data+'%5D'
        print("PAYLOAD  :", payload)
        start = time.time()
        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload)
        except:
            print(
                f"INFO:     Updating {persons.name} fingerprint FAILED!")
        finally:
            end = time.time()
            elapsed = (end-start)
            elapsed = str("%.2f" % elapsed)
            if response != "":
                response.close()
                if (response.status_code == 200):
                    print(
                        f"INFO:     Updating {persons.name} fingerprint SUCCESS!")
                    await Logs.create(operation="UPDATE FINGERPRINT", device=f"{device.name}", data=persons.name, status="SUCCESS")
                else:
                    print("updating person fingerprint failed")
                    await Logs.create(operation="UPDATE FINGERPRINT", device=f"{device.name}", data=persons.name, status="FAILED")

    if ((persons.photo != "") or (len(persons.photo) > 0)):
        print(f"INFO:     Updating {persons.name} photo...")
        url = f"http://{device.ip_address}:8090/face/createByUrl"
        # TODO:  ip address untuk ambil gambar jangan hardcode
        image = (f'http://192.168.99.103{persons.photo}')
        print("IMAGE       :", image)
        imageUrl = json.dumps(image)
        imgUrl = imageUrl.replace('"', '')
        print("IMGURL   :", imgUrl)
        imgUrl = urllib.parse.quote(imgUrl)
        payload = f'pass={device.password}&personId={persons.id}&faceId=&' + \
            'imgUrl='+imgUrl
        print("PAYLOAD  :", payload)
        response = ""
        start = time.time()
        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload)
        except Exception as e:
            print("DEBUG:     PAYLOAD: ", payload)
            print("ERROR:     ", e)
        finally:
            end = time.time()
            elapsed = (end-start)
            elapsed = str("%.2f" % elapsed)
            if response != "":
                response.close()
                if (response.status_code == 200):
                    await Logs.create(operation="UPDATE PHOTO", device=f"{device.name}", data=persons.name, status="SUCCESS", operation_time=elapsed)
                else:
                    print("payload photo:", payload)
                    print("response photo:", response)
                    await Logs.create(operation="UPDATE PHOTO", device=f"{device.name}", data=persons.name, status="FAILED", operation_time=elapsed)

    if ((persons.expire_time != "") or (len(persons.expire_time) > 0)):
        # print(f"INFO:     Updating {persons.name} fingerprint...")
        url = f"http://{device.ip_address}:8090/person/permissionsCreate"
        times = f"{persons.expire_time}"
        times = urllib.parse.quote(times)
        print("TIMES    :", times)
        payload = f'pass={device.password}&personId={persons.id}&time='+times
        print("PAYLOAD  :", payload)
        start = time.time()

        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload)
        except:
            print(
                f"INFO:     Updating {persons.name} fingerprint FAILED!")
        finally:
            end = time.time()
            elapsed = (end-start)
            elapsed = str("%.2f" % elapsed)
            if response != "":
                response.close()
                # if (response.status_code == 200):
                #     print(
                #         f"INFO:     Updating {persons.name} fingerprint SUCCESS!")
                #     await Logs.create(operation="UPDATE FINGERPRINT", device=f"{device.name}", data=persons.name, status="SUCCESS")
                # else:
                #     print("updating person fingerprint failed")
                #     await Logs.create(operation="UPDATE FINGERPRINT", device=f"{device.name}", data=persons.name, status="FAILED")


async def deauthorize_person_pj(person_id: int, device_ids: list()):
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
            url = f"http://{device.ip_address}:8090/person/delete"
            payload = f'pass={device.password}&id={person.id}'
            print("PAYLOAD :", payload)
            response = ""
            start = time.time()
            try:
                response = requests.request(
                    "POST", url, headers=headers, data=payload)
            except Exception as e:
                print("deauthorize person exception happened :", e)
            finally:
                if response != "":
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
