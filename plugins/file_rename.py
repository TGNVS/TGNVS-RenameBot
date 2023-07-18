from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
import requests
from pymongo import MongoClient
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import b64_to_str, get_current_time, shorten_url, str_to_b64, CheckTimeGap
from helper.utils import progress_for_pyrogram, convert, humanbytes
from helper.database import db
from config import Config
import re, os, time
from asyncio import sleep
from PIL import Image
import os, time

id_pattern = re.compile(r'^.\d+$')
ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5490240193').split()]
BIN_CHANNEL = int(os.environ.get("BIN_CHANNEL", ""))

@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    bin_msg = await message.forward(chat_id=BIN_CHANNEL)
    isInGap, sleepTime = await CheckTimeGap(message.from_user.id)
    if isInGap is True:
        await message.reply_text(f"Sorry Sir,\nNo Flooding Allowed!\nSend Video After `{str(sleepTime)}s` !!", quote=True)
        return
    await db.add_user(client, message)
    uid = message.from_user.id
    result = await db.get_user(message.from_user.id)
    time_left = await db.get_time(message.from_user.id)
    if uid not in ADMIN:
            if result is None:
                ad_code = str_to_b64(f"{uid}:{str(get_current_time() + 3600)}")
                ad_url = shorten_url(f"https://telegram.me/{client.username}?start={ad_code}")
                await message.reply_text(f"Hey **{message.from_user.mention}** \n\nYour token is expired, refresh your token. \n\n**Token Timeout:** `1 Hour` \n\n**What is token?** \nThis is an ads token. If you pass 1 ad, you can use the bot for 30 minute after passing the ad.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Click Here To Refresh Token",url=ad_url)]]
                ),disable_web_page_preview = True)
                return
            elif int(time_left) < get_current_time():
                ad_code = str_to_b64(f"{uid}:{str(get_current_time() + 3600)}")
                ad_url = shorten_url(f"https://telegram.me/{client.username}?start={ad_code}")
                await db.new_token(message.from_user.id, token=ad_code)
                await message.reply_text(f"Hey **{message.from_user.mention}** \n\nYour token is expired, refresh your token. \n\n**Token Timeout:** `1 Hour` \n\n**What is token?** \nThis is an ads token. If you pass 1 ad, you can use the bot for 30 minute after passing the ad.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Click Here To Refresh Token",url=ad_url)]]
                ),disable_web_page_preview = True)
                return
    file = getattr(message, message.media.value)
    filename = file.file_name
    userdc = message.from_user.dc_id
    print(filename)
    if file.file_size > 2000 * 1024 * 1024:
         return await message.reply_text("Sᴏʀʀy Bʀᴏ Tʜɪꜱ Bᴏᴛ Iꜱ Dᴏᴇꜱɴ'ᴛ Sᴜᴩᴩᴏʀᴛ Uᴩʟᴏᴀᴅɪɴɢ Fɪʟᴇꜱ Bɪɢɢᴇʀ Tʜᴀɴ 2Gʙ")

    try:
        await message.reply_text(
            text=f"𝙁𝙞𝙡𝙚 𝘿𝘾:-`{userdc}\n**__Pʟᴇᴀꜱᴇ Eɴᴛᴇʀ Nᴇᴡ Fɪʟᴇɴᴀᴍᴇ...__**\n\n**Oʟᴅ Fɪʟᴇ Nᴀᴍᴇ** :- `{filename}`",
	    reply_to_message_id=message.id,  
	    reply_markup=ForceReply(True)
        )       
        await sleep(8)
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"𝙁𝙞𝙡𝙚 𝘿𝘾:-`{userdc}\n**__Pʟᴇᴀꜱᴇ Eɴᴛᴇʀ Nᴇᴡ Fɪʟᴇɴᴀᴍᴇ...__**\n\n**Oʟᴅ Fɪʟᴇ Nᴀᴍᴇ** :- `{filename}`",
	    reply_to_message_id=message.id,  
	    reply_markup=ForceReply(True)
        )
    except:
        pass
    



@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message
    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text
        userdc = message.from_user.dc_id
        await message.delete() 
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
        if not "." in new_name:
            if "." in media.file_name:
                extn = media.file_name.rsplit('.', 1)[-1]
            else:
                extn = "mkv"
            new_name = new_name + "." + extn
        await reply_message.delete()

        button = [[InlineKeyboardButton("📁 Dᴏᴄᴜᴍᴇɴᴛ",callback_data = "upload_document")]]
        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton("🎥 Vɪᴅᴇᴏ", callback_data = "upload_video")])
        elif file.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton("🎵 Aᴜᴅɪᴏ", callback_data = "upload_audio")])
        await message.reply(
            text=f"𝙁𝙞𝙡𝙚 𝘿𝘾:-`{userdc}\n**Sᴇʟᴇᴄᴛ Tʜᴇ Oᴜᴛᴩᴜᴛ Fɪʟᴇ Tyᴩᴇ**\n**• Fɪʟᴇ Nᴀᴍᴇ :-**```{new_name}```",
            reply_to_message_id=file.id,
            reply_markup=InlineKeyboardMarkup(button)
        )



@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):    
    new_name = update.message.text
    new_filename = new_name.split(":-")[2]
    file_path = f"downloads/{new_filename}"
    file = update.message.reply_to_message

    ms = await update.message.edit("Tʀyɪɴɢ Tᴏ Dᴏᴡɴʟᴏᴀᴅɪɴɢ....")    
    try:
     	path = await bot.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram,progress_args=("Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ....", ms, time.time()))                    
    except Exception as e:
     	return await ms.edit(e)
     	     
    duration = 0
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata.has("duration"):
           duration = metadata.get('duration').seconds
    except:
        pass
    ph_path = None
    user_id = int(update.message.chat.id) 
    media = getattr(file, file.media.value)
    c_caption = await db.get_caption(update.message.chat.id)
    c_thumb = await db.get_thumbnail(update.message.chat.id)

    if c_caption:
         try:
             caption = c_caption.format(filename=new_filename, filesize=humanbytes(media.file_size), duration=convert(duration))
         except Exception as e:
             return await ms.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ Exᴄᴇᴩᴛ Kᴇyᴡᴏʀᴅ Aʀɢᴜᴍᴇɴᴛ ●> ({e})")             
    else:
         caption = f"**{new_filename}**"
 
    if (media.thumbs or c_thumb):
         if c_thumb:
             ph_path = await bot.download_media(c_thumb) 
         else:
             ph_path = await bot.download_media(media.thumbs[0].file_id)
         Image.open(ph_path).convert("RGB").save(ph_path)
         img = Image.open(ph_path)
         img.resize((320, 320))
         img.save(ph_path, "JPEG")

    await ms.edit("Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....")
    type = update.data.split("_")[1]
    try:
        if type == "document":
            await bot.send_document(
                update.message.chat.id,
                document=file_path,
                thumb=ph_path, 
                caption=caption, 
                progress=progress_for_pyrogram,
                progress_args=("Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....", ms, time.time()))
        elif type == "video": 
            await bot.send_video(
		update.message.chat.id,
	        video=file_path,
	        caption=caption,
		thumb=ph_path,
		duration=duration,
	        progress=progress_for_pyrogram,
		progress_args=("Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....", ms, time.time()))
        elif type == "audio": 
            await bot.send_audio(
		update.message.chat.id,
		audio=file_path,
		caption=caption,
		thumb=ph_path,
		duration=duration,
	        progress=progress_for_pyrogram,
	        progress_args=("Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....", ms, time.time()))
    except Exception as e:          
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)
        return await ms.edit(f" Eʀʀᴏʀ {e}")
 
    await ms.delete() 
    os.remove(file_path) 
    if ph_path: os.remove(ph_path) 





