from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from redis_config_server import config_server, ConfigGroup, REDIS_URL, REDIS_PORT, REDIS_DB
import os
from pydantic import ValidationError


app = FastAPI()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# 获取环境信息
REDIS_CONFIG_CENTER_TYPE = os.getenv("REDIS_CONFIG_CENTER_TYPE", "PRODUCTION")

def get_redis_info():
    return {
            "host": REDIS_URL,
            "port": REDIS_PORT,
            "db": REDIS_DB,
            "config_server_name": config_server.config_server_name,
            "environment": REDIS_CONFIG_CENTER_TYPE
        }

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, search: str = ""):
    if search:
        config_groups = [g for g in await config_server.get_all_config_groups() if search.lower() in g.group_name.lower()]
    else:
        config_groups = await config_server.get_all_config_groups()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "config_groups": config_groups,
        "redis_info": get_redis_info()
    })

@app.get("/config-groups", response_class=JSONResponse)
async def get_config_groups_api(search: Optional[str] = None):
    if search:
        config_groups = [g.model_dump() for g in await config_server.get_all_config_groups() if search.lower() in g.group_name.lower()]
    else:
        config_groups = [g.model_dump() for g in await config_server.get_all_config_groups()]
    return {
        "config_groups": config_groups,
        "redis_info": get_redis_info()
    }

@app.get("/view-config-group/{group_name}", response_class=HTMLResponse)
async def view_config_group(request: Request, group_name: str):
    config_group = await config_server.get_config_group(group_name)
    if not config_group:
        raise HTTPException(status_code=404, detail="配置组未找到")
    return templates.TemplateResponse("view_config_group.html", {
        "request": request,
        "config_group": config_group,
        "redis_info": get_redis_info()
    })

@app.post("/delete-config-group/{group_name}", response_class=JSONResponse)
async def delete_config_group(group_name: str):
    try:
        await config_server.delete_config_group(group_name)
        return JSONResponse(content={"success": True, "message": "配置组已删除"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/add-config-group", response_class=HTMLResponse)
async def add_config_group_page(request: Request):
    return templates.TemplateResponse("add_config_group.html", {"request": request, "redis_info": get_redis_info()})

@app.post("/add-config-group", response_class=JSONResponse)
async def add_config_group(
    group_name: str = Form(...),
    group_version: str = Form(...),
    config_dict_json: str = Form(...)
):
    try:
        if await config_server.get_config_group(group_name):
            return JSONResponse(content={"success": False, "message": "无效的配置，该配置组已存在"}, status_code=status.HTTP_200_OK)

        config_dict = json.loads(config_dict_json)
        config_group = ConfigGroup(group_name=group_name, group_version=group_version, config_dict=config_dict)
        await config_server.insert_config_group(config_group)
        return JSONResponse(content={"success": True, "message": "配置组已添加"}, status_code=status.HTTP_200_OK)
    except json.JSONDecodeError as e:
        return JSONResponse(content={"success": False, "message": "无效的 JSON 格式"}, status_code=status.HTTP_200_OK)
    except ValidationError as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=status.HTTP_200_OK)

@app.get("/edit-config-group/{group_name}", response_class=HTMLResponse)
async def edit_config_group_page(request: Request, group_name: str):
    config_group = await config_server.get_config_group(group_name)
    if not config_group:
        raise HTTPException(status_code=404, detail="配置组未找到")
    return templates.TemplateResponse("edit_config_group.html", {
        "request": request,
        "config_group": config_group,
        "redis_info": get_redis_info()
    })

@app.post("/edit-config-group/{group_name}", response_class=JSONResponse)
async def edit_config_group(
    group_name: str,
    group_version: str = Form(...),
    config_dict_json: str = Form(...)
):
    try:
        config_dict = json.loads(config_dict_json)
        config_group = ConfigGroup(group_name=group_name, group_version=group_version, config_dict=config_dict)
        await config_server.insert_config_group(config_group)
        return JSONResponse(content={"success": True, "message": "配置组已更新"}, status_code=status.HTTP_200_OK)
    except json.JSONDecodeError as e:
        return JSONResponse(content={"success": False, "message": "无效的 JSON 格式"}, status_code=status.HTTP_200_OK)
    except ValidationError as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=status.HTTP_200_OK)

@app.get("/import-config-group", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("import_config_group.html", {
        "request": request,
        "redis_info": get_redis_info()
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8079)

