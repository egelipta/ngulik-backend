# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Maintainer: dgos
@Des: 工具函数
"""

import subprocess
from PIL import Image
import os
import hashlib
import random
import uuid
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from datetime import datetime

async def rand_angka():
    return random.randint(1, 2147483648)

def init_folder():
    sekarang = datetime.now()
    command= list(range(24))
    command[0] = "mkdir /tmp/elevator/lantai -p"
    command[1] = "mkdir /tmp/elevator/timer -p"
    command[2] = "touch /tmp/elevator/timer/ {1,2,3,4,5,6,7,8,all}"
    command[3] = "touch /tmp/elevator/lantai/ {1,2,3,4,5,6,7,8,all}"

    command[4] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/1"
    command[5] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/2"
    command[6] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/3"
    command[7] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/4"
    command[8] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/5"
    command[9] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/6"
    command[10] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/7"
    command[11] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/8"
    command[12] = "echo \""+str(sekarang)+"\" > /tmp/elevator/timer/all"

    command[13] = "echo \"99\" > /tmp/elevator/lantai/1"
    command[14] = "echo \"99\" > /tmp/elevator/lantai/2"
    command[15] = "echo \"99\" > /tmp/elevator/lantai/3"
    command[16] = "echo \"99\" > /tmp/elevator/lantai/4"
    command[17] = "echo \"99\" > /tmp/elevator/lantai/5"
    command[18] = "echo \"99\" > /tmp/elevator/lantai/6"
    command[19] = "echo \"99\" > /tmp/elevator/lantai/7"
    command[20] = "echo \"99\" > /tmp/elevator/lantai/8"
    command[21] = "echo \"99\" > /tmp/elevator/lantai/all"
    command[22] = "touch /tmp/elevator/lantai/ awal"
    command[23] = "echo 1 > /tmp/elevator/lantai/awal"


    command2=f"modpoll -m rtu -a 1 -r 1 -c 8 -t0 -b 9600 -p none /dev/ttyUSB0 0 0 0 0 0 0 0 0"
    subprocess.run(command2, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for i in range(24):
        print("ini loop i ke ",i)
        subprocess.run(command[i], shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


async def count_items_in_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return
    
    # Get a list of all items in the folder
    items = os.listdir(folder_path)
    
    # Count the number of items
    num_items = len(items)
    
    # Print the result
    return num_items

async def baca():
    jumlah_baterai = await count_items_in_folder('/var/run/dgos/')

    for i in range(jumlah_baterai):
        for x in range(53):
            file_path = f"/var/run/dgos/{i+1}/{x+1}"
            try:
                with open(file_path, 'r') as file:
                    isi = file.read().strip()  # Use strip() to remove leading/trailing whitespace

                # berisi = await Nilai.get_or_none(letak=file_path)
              
                # if not berisi:
                #     await Nilai.create(letak=file_path,isi=isi)
                # elif berisi.isi != isi:
                #     await Nilai.filter(letak=file_path).update(isi=isi)
                
                # print(f"{file_path} = {isi}")
            except FileNotFoundError:
                print(f"File {file_path} not found.")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

    


def random_str():
    """
    唯一随机字符串
    :return: str
    """
    only = hashlib.md5(str(uuid.uuid1()).encode(encoding='UTF-8')).hexdigest()
    return str(only)


def en_password(psw: str):
    """
    密码加密
    :param psw: 需要加密的密码
    :return: 加密后的密码
    """
    password = pbkdf2_sha256.hash(psw)
    return password


def check_password(password: str, old: str):
    """
    密码校验
    :param password: 用户输入的密码
    :param old: 数据库密码
    :return: Boolean
    """
    check = pbkdf2_sha256.verify(password, old)
    if check:
        return True
    else:
        return False


def code_number(ln: int):
    """
    随机数字
    :param ln: 长度
    :return: str
    """
    code = ""
    for i in range(ln):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        code += ch

    return code


def cleanse_filename_for_url(filename):
    # Remove any characters that are not URL-friendly
    url_friendly_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.'
    filename = ''.join(c for c in filename if c in url_friendly_chars)

    # Replace any remaining spaces with hyphens or underscores
    filename = filename.replace(' ', '-')

    # Convert the filename to lowercase
    filename = filename.lower()

    # Return the cleansed filename
    return filename


def remove_dots_except_last(filename, replacement_char=''):
    # Split the filename into base name and extension
    base_name, ext = os.path.splitext(filename)

    # Replace all dots in the base name with the replacement character
    base_name = base_name.replace('.', replacement_char)

    # Return the new filename
    return base_name + ext


