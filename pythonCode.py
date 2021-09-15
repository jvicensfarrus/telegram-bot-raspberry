import telepot
import picamera
import RPi.GPIO as GPIO
import time
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import Adafruit_DHT as ADA_DHT
 
def handle(msg): #Function currently not in use
    global sendPhoto
    global chat_id
 
    chat_id = msg['chat']['id']
    command = msg['text']
 
    print('Message received from ' + str(chat_id) + ' which was saying: ' + str(command))
 
    if command == '/start':
        bot.sendMessage(chat_id, 'Welcome to Casa Notification')
 
    elif command == '/photo':
        sendPhoto = True
 
    elif command == '/more':
        bot.sendMessage(chat_id, 'More stuff could be done..')
    else:
        bot.sendMessage(chat_id, 'Invalid command!')
 
def capture(chat_id):
    print('Capturing photo...')
    try:
        camera = picamera.PiCamera()
 
        camera.framerate = 15
        camera.awb_mode= 'auto'
        camera.start_preview()
        camera.capture('./photo-darker.png')
        time.sleep(5)
        camera.capture('./photo-ligther.png')
        camera.stop_preview()
 
        camera.close()
 
        bot.sendPhoto(chat_id, photo=open('./photo-darker.png', 'rb'))
        bot.sendPhoto(chat_id, photo=open('./photo-ligther.png', 'rb'))
 
    except:
        bot.sendMessage(chat_id, 'An error ocurred while processing this command. Check with you administrator.')
 
def weather_capture(chat_id):
    print('Capturing temperature and humidty..')
    #Defining where the weather sensor is located based on my Raspberry pins(photos attached in the project and can also be found in the README file)
    DHT_SENSOR = ADA_DHT.DHT22
    DHT_PIN = 20
 
    h, t = ADA_DHT.read(DHT_SENSOR, DHT_PIN)
    if h is not None and t is not None:
 
        bot.sendMessage(chat_id, 'Temp={0:0.1f}C Humidity={1:0.1f}C'.format(t, h))
    else:
        bot.sendMessage(chat_id, 'Sensor Failure')
 
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
 
    if chat_type == 'private':
        bot.sendMessage(chat_id, "You are using me in a private chat... Are you sure you don't wanna share me in a group?")
 
    #Setting up buttons on screen and callback data sent upon click
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Temperature and Humidity', callback_data='weather_humidity')],
                   [InlineKeyboardButton(text='Take a photo', callback_data='photo')],
               ])
 
    bot.sendMessage(chat_id, 'Using inline keyboard. Select one of the options below.', reply_markup=keyboard)
 
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    #Decision making depending on button clicked
    if query_data == 'photo':
        bot.sendMessage(from_id, 'Taking a photo for you..')
        capture(from_id)
    if query_data == 'weather_humidity':
        bot.sendMessage(from_id, 'Mesuring temperature and humidity for you...')
        weather_capture(from_id)
 

bot = telepot.Bot('your-telegram-bot-key')
#bot.message_loop(handle) #If you wanna set manual commands instead of inline keyboard
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Bot Initialised')

 
while 1:
    time.sleep(10)