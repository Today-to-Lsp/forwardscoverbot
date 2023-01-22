# ForwardsCoverBot - don't let people on telegram forward with your name on the forward label
# Copyright (C) 2017-2022  Dario <dariomsn@hotmail.it> (github.com/91DarioDev)
#
# ForwardsCoverBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ForwardsCoverBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with ForwardsCoverBot.  If not, see <http://www.gnu.org/licenses/>


from forwardscoverbot import utils
from forwardscoverbot import dbwrapper
from forwardscoverbot import keyboards
from forwardscoverbot import messages

from telegram import MessageEntity
from telegram.constants import ParseMode
from telegram.constants import MessageLimit
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup


async def help_command(update, context):
    keyboard = keyboards.github_link_kb()
    text = (
        "<b>你想向某人或群组发送消息, "
        "但是你想避免有人用你的名字在电报上传播它吗？这个机器人只是回复"
        "你的消息</b>.\n\n在这里发送您想要的内容，您将收到相同的消息，"
        "然后将消息转发到您想要的位置，转发标签将具有此机器人的名称。"
        "\n<i>如果您编辑消息或转发消息，它也适用。"
        "它还保持相同的文本格式样式。</i>\n\n"
        "<b>Supported commands:</b>\n"
        "/disablewebpagepreview\n"
        "/removecaption\n"
        "/addcaption\n"
        "/removebuttons\n"
        "/addbuttons\n"
        "/addspoiler\n"
        "/removespoiler\n"
    )
    await update.message.reply_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)



async def disable_web_page_preview(update, context):
    if not update.message.reply_to_message:
        text = ("此命令允许从消息中删除网页预览。"
                "\n\n使用它回复机器人已经显示的消息，并且您想使用此命令禁用预览。")
        await update.message.reply_text(text=text)
        return

    if not update.message.reply_to_message.text:
        text = "此消息没有网页预览"
        await update.message.reply_to_message.reply_text(text=text, quote=True)
        return

    entities_list = [MessageEntity.URL, MessageEntity.TEXT_LINK]
    entities = update.message.reply_to_message.parse_entities(entities_list)
    if len(entities) == 0:
        text = "此消息没有网页预览"
        await update.message.reply_to_message.reply_text(text=text, quote=True)
        return

    await messages.process_message(update=update, context=context, message=update.message.reply_to_message, disable_web_page_preview=True)



async def remove_caption(update, context):
    if not update.message.reply_to_message:
        text = (
            "此命令删除消息中标题。\n\n使用此命令回复要删除标题的消息。"
            "\n\n同时确保消息有标题。"
        )
        await update.message.reply_text(text=text)
        return

    if not update.message.reply_to_message.caption:
        text = "此消息没有标题，请将此命令用于带有标题的消息。"
        await context.bot.sendMessage(
            chat_id=update.message.from_user.id,
            text=text,
            reply_to_message_id=update.message.reply_to_message.message_id
        )
        return

    await messages.process_message(update=update, context=context, message=update.message.reply_to_message, remove_caption=True)



async def add_spoiler(update, context):
    await handle_spoiler(update, context, 'add')


async def remove_spoiler(update, context):
    await handle_spoiler(update, context, 'remove')


async def handle_spoiler(update, context, spoiler_action):
    if not update.message.reply_to_message:
        if spoiler_action == 'add':
            text = (
                "This command permits to add a spoiler to a message. Reply with this command to "
                "the message where you want to add the spoiler."
            )
        elif spoiler_action == 'remove':
            text = (
                "This command permits to remove the spoiler from a message. Reply with this command to "
                "the message where you want to remove the spoiler."
            )
        await update.message.reply_text(text=text)
        return

    
    if not (update.message.reply_to_message.photo or update.message.reply_to_message.video or update.message.reply_to_message.animation):
        text = "This message doesn't support spoilers."
        await context.bot.sendMessage(
            chat_id=update.message.from_user.id,
            text=text,
            reply_to_message_id=update.message.reply_to_message.message_id,
        )
        return

    await messages.process_message(update=update, context=context, message=update.message.reply_to_message, spoiler_action=spoiler_action)


async def remove_buttons(update, context):
    if not update.message.reply_to_message:
        text = (
            "此命令允许从消息中删除按钮。使用此命令回复要删除按钮的消息。"
            "确保消息有按钮。"
        )
        await update.message.reply_text(text=text)
        return

    if not update.message.reply_to_message.reply_markup:
        text = "此消息没有按钮，请将此命令用于带有按钮的消息。"
        await context.bot.sendMessage(
            chat_id=update.message.from_user.id,
            text=text,
            reply_to_message_id=update.message.reply_to_message.message_id
        )
        return

    await messages.process_message(update=update, context=context, message=update.message.reply_to_message, remove_buttons=True)    



async def add_caption(update, context):
    if not update.message.reply_to_message:
        text = (
            "<b>此命令允许向消息添加标题。使用此命令及其后的标题回复您要添加标题的消息。"
            "</b>\n\n<i>如果消息已有标题，此命令将用新标题覆盖当前标题。"
            "\n"
            "如果消息不支持标题，它就不会添加它，不会返回任何错误提示</i>\n\n\n"
            "<i>Note: 如果消息是由您发送的，您可以编辑它以添加标题."
            "此命令适用于您从频道转发一个您不想再次下载和上传的大文件.")
        await update.message.reply_text(text=text, parse_mode='HTML')
        return

    caption = " ".join(update.message.text.split(" ")[1:])
    caption_html = " ".join(update.message.text_html.split(" ")[1:])

    if len(caption) > MessageLimit.CAPTION_LENGTH:
        text = "This caption is too long. max allowed: {} chars. Please retry removing {} chars.".format(
            MessageLimit.CAPTION_LENGTH,
            len(caption) - MessageLimit.CAPTION_LENGTH 
        )
        await context.bot.sendMessage(
            chat_id=update.message.from_user.id,
            text=text,
            reply_to_message_id=update.message.reply_to_message.message_id
        )
        return

    await messages.process_message(update=update, context=context, message=update.message.reply_to_message, custom_caption=caption_html)



async def add_buttons(update, context):
    usage = (
        "<b>使用此命令，您可以向消息添加按钮。</b>\n使用此命令回复要添加按钮的消息。比如：\n\n"
        "<code>/addbuttons 第一个标题=https://telegram.org && 第二个标题=https://google.com &&& 第三个标题=https://t.me</code>"
        "\n\n按钮的格式是 [text]=[link]. 同一行上的按钮用 && 分隔，新一行由 &&& 分隔。"
    )
    if not update.message.reply_to_message or len(context.args) < 1:
        await update.message.reply_text(text=usage, parse_mode='HTML')
        return
    
    param = ' '.join(context.args)
    rows = param.split('&&&')
    lst = []
    for row in rows:
        try:
            row_lst = []
            row_buttons = row.split('&&')
            for button in row_buttons:
                text, link = button.split('=')
                text = text.strip()
                link = link.strip()
                button = InlineKeyboardButton(text=text, url=link)
                
                row_lst.append(button)
            lst.append(row_lst)
        except Exception as e:
            error = 'ERROR formatting the buttons'
            await update.message.reply_text(text=error, parse_mode='HTML')
    keyboard = InlineKeyboardMarkup(lst)
    await messages.process_message(update=update, context=context, message=update.message.reply_to_message, custom_reply_markup=keyboard)
    

@utils.only_admin
async def stats(update, context):
    await update.message.reply_text(text=await dbwrapper.stats_text(), parse_mode=ParseMode.HTML)



