import telegram
import requests

update_id = None


def run():
    global update_id
    bot = telegram.Bot('354930862:AAFoCXTgomrLfvCsvp4a7oOcZjWrm54pXlw')
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        for update in bot.getUpdates(offset=update_id, timeout=10):
            update_id = update.update_id + 1
            if update.message:
                try:
                    r = requests.post('https://aiaas.pandorabots.com/talk/1409614304594/alice',
                                     params={"user_key": "c70f5f260f515eb026675097239c19c9", "input": update.message.text})
                    resp_value = r.json()['responses'][0]
                    update.message.reply_text(resp_value)
                except:
                    pass

if __name__ == '__main__':
    run()
