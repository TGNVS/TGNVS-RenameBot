import math, time
import requests
import pytz
import re, os, time
import asyncio
import logging
import aiohttp
from base64 import standard_b64encode, standard_b64decode
from datetime import datetime
from datetime import datetime
from pytz import timezone
from config import Config, Txt 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

URL_SHORTENR_WEBSITE = os.environ.get('URL_SHORTENR_WEBSITE', '')
URL_SHORTNER_WEBSITE_API = os.environ.get('URL_SHORTNER_WEBSITE_API', '')
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "120"))
TIME_GAP = int(os.environ.get("TIME_GAP", 30))
GAP = {}

logger = logging.getLogger("keep_alive")

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:        
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["▣" for i in range(math.floor(percentage / 5))]),
            ''.join(["▢" for i in range(20 - math.floor(percentage / 5))])
        )            
        tmp = progress + Txt.PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),            
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",               
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close")]])                                               
            )
        except:
            pass

def humanbytes(size):    
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ, ") if seconds else "") + \
        ((str(milliseconds) + "ᴍꜱ, ") if milliseconds else "")
    return tmp[:-2] 

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def str_to_b64(__str: str) -> str:
    str_bytes = __str.encode('ascii')
    bytes_b64 = standard_b64encode(str_bytes)
    b64 = bytes_b64.decode('ascii')
    return b64

def b64_to_str(b64: str) -> str:
    bytes_b64 = b64.encode('ascii')
    bytes_str = standard_b64decode(bytes_b64)
    __str = bytes_str.decode('ascii')
    return __str

def get_current_time():
    tz = pytz.timezone('Asia/Kolkata')
    return int(datetime.now(tz).timestamp())

def get_readable_time(seconds):
    dt = datetime.fromtimestamp(int(seconds))
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def shorten_url(url):
    site_url = f"https://{URL_SHORTENR_WEBSITE}/api?api={URL_SHORTNER_WEBSITE_API}&url={url}&format=text"
    #site_url = f"{url}"
    return str(requests.get(site_url).text)
    #return site_url

async def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

async def send_log(b, u):
    if Config.LOG_CHANNEL is not None:
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        await b.send_message(
            Config.LOG_CHANNEL,
            f"**--#New User--**\nUser: {u.mention}\nId: `{u.id}`\nUsername: @{u.username}\nDᴀᴛᴇ: {date}\nTɪᴍᴇ: {time}\nBot Name: {b.mention}"
        )

async def ping_server():
    sleep_time = PING_INTERVAL
    logger.info("Started with {}s interval between pings".format(sleep_time))
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(f"http://0.0.0.0:8080") as resp:
                    logging.info(f"Pinged server with response: {resp.status}")
        except TimeoutError:
            logging.warning("Couldn't connect to the site URL..!")
        except Exception:
            traceback.print_exc()
        
async def CheckTimeGap(user_id: int):
    """A Function for checking user time gap!
    :parameter user_id Telegram User ID"""

    if str(user_id) in GAP:
        current_time = time.time()
        previous_time = GAP[str(user_id)]
        if round(current_time - previous_time) < TIME_GAP:
            return True, round(previous_time - current_time + TIME_GAP)
        elif round(current_time - previous_time) >= TIME_GAP:
            del GAP[str(user_id)]
            return False, None
    elif str(user_id) not in GAP:
        GAP[str(user_id)] = time.time()
        return False, None


