from loguru import logger
from asyncio import sleep
from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.dispatcher.filters import Text
from os import remove as remove_file, environ
from pytube import YouTube, exceptions
from keep_alive import keep_alive
from random import choice

# Button keyboard
kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb1 = types.KeyboardButton('Помощь🚒')
kb2 = types.KeyboardButton('Легально?⚠')
kb3 = types.KeyboardButton('Свой бот🤖')
kb4 = types.KeyboardButton('Шар предсказания🎱')
kb.add(kb4).add(kb1, kb2, kb3)

# Configure logging
logger.add('logs.log',
           format='{time} {level} {message}',
           level='INFO',
           rotation='10 KB',
           compression='zip')

# Initialize bot and dispatcher
bot = Bot(token=environ['key'])
dp = Dispatcher(bot)

# Secret channels
channel_user = environ['Channel_user']
channel_music = environ['Channel_music']


# My func
def get_music_youtube(link):
  """Получение audio из youtube"""
  yt = YouTube(link)
  stream = yt.streams.get_audio_only()  # get_itag(140)

  if stream.filesize_mb > 50:
    raise utils.exceptions.NetworkError('Размер файлы превышает 50мб')

  obj = stream.download(filename=yt.title)

  return obj, yt.views, yt.publish_date.year, yt.thumbnail_url


# Выводит в консоль запуска бота
async def on_startup(_):
  print('Бот успешно запущен!')


# Обработка первого запуска бота
@dp.message_handler(commands=['start', 'info'])
async def start_command(message: types.Message) -> None:
  """/start - запускает бот"""
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
    await bot.send_message(
      channel_user,
      f'''{message.from_user.id} - ID пользователя\
          \n{message.from_user.first_name} - Имя пользователя\
          \n{message.from_user.last_name} - Фамилия или псевдоним пользователя\
          \n@{message.from_user.username} - Никнейм пользователя''')
  # Автоудаление через 180сек сообщения бота <answ>
  await sleep(180)
  await bot.delete_message(message.chat.id, answ.message_id)


# Обработка команды <help>
@dp.message_handler(Text(equals='Помощь🚒'))
async def helper(message: types.Message) -> None:
  await start_command(message)


# Обработка команды <legal>
@dp.message_handler(Text(equals='Легально?⚠'))
async def legal(message: types.Message) -> None:
  answ = f'''
Я создал BotMusic с идеей, что должен существовать легальный
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


# Обработка ответа на кнопку <Свой бот>
@dp.message_handler(Text(equals='Свой бот🤖'))
async def own_bot(message: types.Message) -> None:
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


# Обработчик запроса шар предсказания
@dp.message_handler(Text(equals='Шар предсказания🎱'))
async def help_user(message: types.Message) -> None:
  answers = [
    'Бесспорно', 'Мне кажется - да', 'Пока неясно, попробуй снова',
    'Даже не думай', 'Предрешено', 'Вероятнее всего', 'Спроси позже',
    'Мой ответ - нет', 'Никаких сомнений', 'Хорошие перспективы',
    'Лучше не рассказывать', 'По моим данным - нет', 'Определённо да',
    'Знаки говорят - да', 'Сейчас нельзя предсказать',
    'Перспективы не очень хорошие', 'Можешь быть уверен в этом', 'Да',
    'Сконцентрируйся и спроси опять', 'Весьма сомнительно'
  ]
  answ = await message.answer(choice(answers))
  await sleep(5)
  await bot.delete_message(message.chat.id, answ.message_id)
  await message.delete()


# main app download music from youtube
@dp.message_handler(
  Text(startswith=('https://youtu.be/', 'https://www.youtube.com/'),
       ignore_case=True))
async def send_song(message: types.Message) -> None:
  """Присылает пользователю аудио-файл"""

  await message.delete()
  bot_answ = await message.answer('<em><b>Скачиваю файл, подождите..</b></em>',
                                  parse_mode='HTML')
  try:
    obj, views, pub, url = get_music_youtube(message.text)
    description = \
        f'<em>Столько: {views:,d} людей прослушали</em>.\n' \
        f'<em>Дата публикации: {pub}г</em>.'
    with open(obj, 'rb') as file1:
      # С помощью переменной, можно узнать id сообщения и не только
      msg = await message.answer_audio(file1,
                                       caption=description,
                                       parse_mode='HTML',
                                       thumb=types.InputFile.from_url(url))
    remove_file(obj)
    await bot.forward_message(
      chat_id=channel_music,  # Указать конечный канал
      from_chat_id=message.chat.id,  # Указать начальный канал
      message_id=msg.message_id)  # Указать id сообщения

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
Пожалуйста, отправьте другую ссылку:
        
{'-' * 20}
<em>(Сообщение удалится автоматически)</em>'''
    answ = await message.answer(answ, parse_mode='HTML')
    # Автоудаление через 30сек сообщения бота <answ>
    await sleep(30)
    await bot.delete_message(message.chat.id, answ.message_id)
  except Exception as e:
    logger.error(e)
    msg1 = await message.answer(
      '<b>Не удалось скачать файл, работаем над этим..</b>', parse_mode='html')
    await sleep(5)
    await bot.delete_message(message.chat.id, msg1.message_id)
  finally:
    await bot.delete_message(message.chat.id, bot_answ.message_id)


if __name__ == '__main__':
  keep_alive()
  executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
