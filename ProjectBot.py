import logging
from asyncio import sleep
from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from os import remove as remove_file, environ
from pytube import YouTube, exceptions
from keep_alive import keep_alive
from random import choice


#Button keyboard
kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb1 = KeyboardButton('Помощь🚒')
kb2 = KeyboardButton('Легально?⚠')
kb3 = KeyboardButton('Свой бот🤖')
kb4 = KeyboardButton('Шар предсказания🎱')
kb.add(kb4).add(kb1, kb2, kb3)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
channel_user = environ['Channel_user']
channel_music = environ['Channel_music']
bot = Bot(token=environ['key'])
dp = Dispatcher(bot)


# My func
def GetMusicYoutube(link):
  '''Получение audio из youtube'''
  yt = YouTube(link)
  stream = yt.streams.get_audio_only()           #get_itag(140)
  if stream.filesize_mb > 50:
    raise utils.exceptions.NetworkError('Размер файлы превышает 50мб')
  obj = stream.download(filename=yt.title)
  return obj, yt.views, str(yt.publish_date).split('-')[0], \
  yt.thumbnail_url


async def on_startup(_):
  print('Бот успешно запущен!')


@dp.message_handler(commands=['start', 'info'])
async def start_command(message: types.Message) -> None:
  '''/start - запускает бот'''
  desc = f"""
Привет, <b>{message.from_user.first_name}</b>🤚
  
Я помогу найти аудио в YouTube Music и по возможности отправлю тебе его!
  • Просто перешли мне музыкальный клип с youtube.
  • Я ищу только оригиналы треков, без фанатских ремиксов и записи с диктофона!
  • Формат треков — M4A AAC 128 Kbps. Это оригинальный формат аудио на YouTube.
  • Обложки альбомов прилагаются!
Большинства треков присылаются не дольше 10секунд.


Нужен свой личный бот с блекджеками и девушками? Пиши - @mac_loves

{'-' * 20}
<em>(Сообщение удалится автоматически)</em>"""
  answ = await message.answer(desc, parse_mode='HTML', reply_markup=kb)
  await message.delete()
  if message.text == r'/start':
    await bot.send_message(channel_user,f'''
{message.from_user.id} - ID пользователя
{message.from_user.first_name} - Имя пользователя
{message.from_user.last_name} - Фамилия или псевдоним пользователя
@{message.from_user.username} - Никнейм пользователя''')
  # Автоудаление через 180сек сообщения бота <answ>
  await sleep(180)
  await bot.delete_message(message.chat.id, answ.message_id)


@dp.message_handler(Text(equals='Помощь🚒'))
async def helper(message: types.Message) -> None:
  await start_command(message)


@dp.message_handler(Text(equals='Легально?⚠'))
async def Legal(message: types.Message) -> None:
  answ = f'''Я создал BotMusic с идеей, что должен существовать легальный
инструмент для записи потоковой передачи в Интернете, который был бы чистым,
простым и не содержал спама. Согласно EFF.org, «в законе ясно,
что простоепредоставление общественности инструмента для копирования
цифровых носителей не влечет за собой ответственности за авторские права».

{'-' * 20}
<em>(Сообщение удалится автоматически)</em>'''
  answ = await message.answer(answ, parse_mode='HTML')
  await message.delete()
  # Автоудаление через 30сек сообщения бота <answ>
  await sleep(30)
  await bot.delete_message(message.chat.id, answ.message_id)


@dp.message_handler(Text(equals='Свой бот🤖'))
async def OwnBot(message: types.Message) -> None:
  answ = f'''
<em><b>Хочешь своего бота?</b></em>
Пиши - @mac_loves

{'-' * 20}
<em>(Сообщение удалится автоматически)</em>'''
  answ = await message.answer(answ, parse_mode='HTML')
  await message.delete()
  # Автоудаление через 30сек сообщения бота <answ>
  await sleep(30)
  await bot.delete_message(message.chat.id, answ.message_id)


@dp.message_handler(Text(equals='Шар предсказания🎱'))
async def HelpUser(message: types.Message) -> None:
  answers = ['Бесспорно', 'Мне кажется - да', 'Пока неясно, попробуй снова',
             'Даже не думай', 'Предрешено', 'Вероятнее всего', 'Спроси позже',
             'Мой ответ - нет', 'Никаких сомнений', 'Хорошие перспективы',
             'Лучше не рассказывать', 'По моим данным - нет', 'Определённо да',
             'Знаки говорят - да', 'Сейчас нельзя предсказать',
             'Перспективы не очень хорошие', 'Можешь быть уверен в этом', 'Да',
             'Сконцентрируйся и спроси опять', 'Весьма сомнительно']
  answ = await message.answer(choice(answers))
  await sleep(5)
  await bot.delete_message(message.chat.id, answ.message_id)
  await message.delete()


@dp.message_handler(Text(startswith=('https://youtu.be/',
                                     'https://www.youtube.com/'),
                         ignore_case=True))

async def send_song(message: types.Message) -> None:
  """Присылает пользователю аудио-файл"""
  
  await message.delete()
  bot_answ = await message.answer('<em><b>Ждите...</b></em>',
                                  parse_mode='HTML')
  try:
    obj, views, pub, URL = [i for i in GetMusicYoutube(message.text)]
    description = \
        f'<em>Столько: {views:,d} людей прослушали</em>.\n' \
        f'<em>Дата публикации: {pub}г</em>.'
    with open(obj, 'rb') as file1:
      # С помощью переменной, можно узнать id сообщения и не только
      msg = await message.answer_audio(
        file1,
        caption=description,
        parse_mode='HTML',
        thumb=types.InputFile.from_url(URL))
    remove_file(obj)
    await bot.forward_message(
      chat_id=channel_music,            # Указать конечный канал
      from_chat_id=message.chat.id,  # Указать начальный канал
      message_id=msg.message_id)      # Указать id сообщения
    
  except exceptions.VideoUnavailable:   
    answ = f'''
Отклонено правами автора.
Пожалуйста, отправить другую ссылку:

{'-' * 20}
<em>(Сообщение удалится автоматически)</em>'''
    answ = await message.answer(answ, parse_mode='HTML')
    # Автоудаление через 30сек сообщения бота <answ>
    await sleep(30)
    await bot.delete_message(message.chat.id, answ.message_id)
    
  except utils.exceptions.NetworkError:
    answ = f'''
Отклонено, размер файла превышает 50мб.
Пожалуйста, отправить другую ссылку:

{'-' * 20}
<em>(Сообщение удалится автоматически)</em>'''
    answ = await message.answer(answ, parse_mode='HTML')
    # Автоудаление через 30сек сообщения бота <answ>
    await sleep(30)
    await bot.delete_message(message.chat.id, answ.message_id)
  finally:
    await bot.delete_message(message.chat.id, bot_answ.message_id)


if __name__ == '__main__':
  keep_alive()
  executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
