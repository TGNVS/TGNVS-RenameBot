from aiohttp import web
from flask import Flask
from time import sleep, time
from psutil import boot_time, disk_usage, net_io_counters
from subprocess import check_output
from os import path as ospath

botStartTime = time()


routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("PyʀᴏBᴏᴛᴢ")

@routes.get("/status/{code}")
async def status_route_handler(request):
    bot_uptime = time() - botStartTime
    uptime = time() - boot_time()
    sent = net_io_counters().bytes_sent
    recv = net_io_counters().bytes_recv
    return web.Response('uptime': uptime,'on_time': bot_uptime,'free_disk': disk_usage('.').free,'total_disk': : disk_usage('.').total,'network':{'sent': sent,'recv': recv,})


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app
