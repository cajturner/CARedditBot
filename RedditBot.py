from io import StringIO

import boto3
import datetime
import requests
import telegram

update_id = None
bot_name = "Reddit"
convs = {}


def upload_to_s3(data, key_name):
    global bot_name
    s3 = boto3.resource('s3')
    s = StringIO()
    s.write(str("\n".join(data)))
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
    bot = telegram.Bot('360545018:AAHcH68WE-QP5RjcP_Zu7ZYwMW6BuV6TeQ8')
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
                    if update.message.text != "EXIT":

                        r = requests.get('http://ec2-54-211-74-133.compute-1.amazonaws.com:5000',
                                         params={"q": update.message.text})
                        resp_value = r.json()[0]['value'][0]
                        update.message.reply_text(resp_value)
                        log_request = str(update.message.date) + "    " + update.message.text
                        log_response = str(datetime.datetime.now().replace(microsecond=0)) + "    " + resp_value
                        add_to_log(username, log_request, log_response)
                    else:  # Log conv
                        resp_value = "Thanks for chatting to me! Goodbye."
                        update.message.reply_text(resp_value)
                        log_request = str(update.message.date) + "    " + update.message.text
                        log_response = str(datetime.datetime.now().replace(microsecond=0)) + "    " + resp_value
                        add_to_log(username, log_request, log_response)
                        upload_to_s3(convs[username], username)
                        convs.pop(username)
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    run()
