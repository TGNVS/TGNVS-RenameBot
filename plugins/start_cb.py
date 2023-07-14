import random
import requests
import re, os, time
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from helper.database import db
from helper.utils import b64_to_str, get_current_time, shorten_url, str_to_b64
from config import Config, Txt  
  

id_pattern = re.compile(r'^.\d+$')
ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5490240193').split()]
    
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await db.add_user(client, message)
    token = await db.get_token(message.from_user.id)
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton('🎛️ Aʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton('🛠️ Hᴇʟᴩ', callback_data='help')
    ]])
    uid = message.from_user.id
    if message.text.startswith("/start ") and len(message.text) > 7:
        user_id = message.from_user.id
        try:
            ad_msg = b64_to_str(message.text.split("/start ")[1])
            if int(user_id) != int(ad_msg.split(":")[0]):
                await message.reply_text("This Token Is Not For You")
                return
            if int(ad_msg.split(":")[1]) < get_current_time():
                await message.reply_text("Token Expired Regenerate A New Token")
                return
            if int(ad_msg.split(":")[1]) > int(get_current_time() + 3600):
                await message.reply_text("Dont Try To Be Over Smart")
                return
            if token == message.command[1]:
                await db.new_time(message.from_user.id, time=int(ad_msg.split(":")[1]))
                await db.new_token(message.from_user.id, token=None)
                await message.reply_text("Congratulations! Ads token refreshed successfully! \n\nIt will expire after `1 Hour`")
                return
        except Exception as e:
            print("error:", str(e))
            await message.reply_text("Invalid Token")
            return
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, caption=Txt.START_TXT.format(user.mention), reply_markup=button)       
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)
        
        
@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    if data == "start":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton('🎛️ Aʙᴏᴜᴛ', callback_data='about'),
                InlineKeyboardButton('🛠️ Hᴇʟᴩ', callback_data='help')
            ]])
        )
    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔒 Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("◀️ Bᴀᴄᴋ", callback_data = "start")
            ]])            
        )
    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT.format(client.mention),
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔒 Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("◀️ Bᴀᴄᴋ", callback_data = "start")
            ]])            
        )
    elif data == "dev":
        await query.message.edit_text(
            text=Txt.DEV_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔒 Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("◀️ Bᴀᴄᴋ", callback_data = "start")
            ]])          
        )
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()
