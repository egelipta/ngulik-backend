# -*- coding:utf-8 -*-
"""
@Time : 2022/4/27 5:24 PM
@Author: me
@Des: Heatmap Management
"""
import random
from fastapi import APIRouter
from models.heat_map import Heatmap

router = APIRouter(prefix='/heat_map')

@router.get('/heat-map')
async def get_heatmap_list():
    try:
        heatmaps = await Heatmap.all()
        response_data = [
            { "id": str(heatmap.id), "nama": heatmap.nama, "nilai": '', "d": heatmap.d, "floor": heatmap.floor }
            for heatmap in heatmaps
        ]
        return response_data
    except Exception as e:
        return {"error": str(e)}
    
@router.get('/heat-map-lantai1')
async def get_heatmap_lantai1_list():
    try:
        heatmaps = await Heatmap.filter(floor="Lantai 1").all()
        response_data = [
            { 
                "id": str(heatmap.id), 
                "nama": heatmap.nama,
                "nilai": random.randint(0, 100), 
                "d": heatmap.d, 
                "floor": heatmap.floor 
                }
            for heatmap in heatmaps
        ]
        return response_data
    except Exception as e:
        return {"error": str(e)}
    
@router.get('/heat-map-lantai2')
async def get_heatmap_lantai2_list():
    try:
        heatmaps = await Heatmap.filter(floor="Lantai 2").all()
        response_data = [
            { 
                "id": str(heatmap.id), 
                "nama": heatmap.nama, 
                "nilai": random.randint(0, 100), 
                "d": heatmap.d, 
                "floor": heatmap.floor 
            }
            for heatmap in heatmaps
        ]
        return response_data
    except Exception as e:
        return {"error": str(e)}
    
@router.get('/heat-map-lantai3')
async def get_heatmap_lantai3_list():
    try:
        heatmaps = await Heatmap.filter(floor="Lantai 3").all()
        response_data = [
            { 
                "id": str(heatmap.id), 
                "nama": heatmap.nama, 
                "nilai": random.randint(0, 100), 
                "d": heatmap.d, 
                "floor": heatmap.floor 
                }
            for heatmap in heatmaps
        ]
        return response_data
    except Exception as e:
        return {"error": str(e)}

@router.get('/heat-map-datacenter')
async def get_heatmap_datacenter_list():
    try:
        heatmaps = await Heatmap.filter(floor="Data Center").all()
        response_data = [
            { 
                "id": str(heatmap.id), 
                "nama": heatmap.nama, 
                "nilai": random.randint(0, 100),
                "d": heatmap.d, 
                "floor": heatmap.floor 
            }
            for heatmap in heatmaps
        ]
        return response_data
    except Exception as e:
        return {"error": str(e)}
