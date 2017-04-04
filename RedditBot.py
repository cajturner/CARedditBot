from io import StringIO

import boto3
import datetime
import requests
import telegram

update_id = None
bot_name = "Alice"
convs = {}


def upload_to_s3(data, key_name):
    global bot_name
    s3 = boto3.resource('s3')
    s = StringIO()
    s.write(str("\n".join(str(d) +"    "+ t for d,t in data)))
    s3.Object('redditbot', key_name + "_" + str(datetime.datetime.now()) + "_" + bot_name + ".txt").put(
        Body=s.getvalue())
    print("Exported to s3")


def add_to_log(username, request, response):
    global convs
    try:
        convs[username].append(request)
        convs[username].append(response)
    except KeyError:
        convs[username] = [request, response]


def run():
    global update_id
    global convs
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
                    username = update.message.from_user.username
                    if username == "":
                        username = update.message.from_user.first_name + update.message.from_user.last_name
                    if update.message.text != "EXIT":

                        r = requests.post('https://aiaas.pandorabots.com/talk/1409614304594/alice',
                                          params={"user_key": "c70f5f260f515eb026675097239c19c9",
                                                  "input": update.message.text})
                        resp_value = r.json()['responses'][0]
                        update.message.reply_text(resp_value)
                        log_request = (update.message.date, update.message.text)
                        log_response = (datetime.datetime.now().replace(microsecond=0), resp_value)
                        add_to_log(username, log_request, log_response)
                    else:  # Log conv
                        resp_value = "Thanks for chatting to me! Goodbye."
                        update.message.reply_text(resp_value)
                        log_request = (update.message.date, update.message.text)
                        log_response = (datetime.datetime.now().replace(microsecond=0), resp_value)
                        add_to_log(username, log_request, log_response)
                        upload_to_s3(convs[username], username)
                        convs.pop(username)
                except Exception as e:
                    print(e)
        to_remove = []
        for username, conversations in convs.items():
            if (datetime.datetime.now().replace(microsecond=0) - conversations[-1][0]).total_seconds() > 60:
                upload_to_s3(convs[username], username)
                to_remove.append(username)
        for username in to_remove:
            convs.pop(username)


if __name__ == '__main__':
    run()
