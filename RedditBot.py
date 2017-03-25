import telegram
import requests
import boto3

update_id = None


def run():
    global update_id
    bot = telegram.Bot('360545018:AAHcH68WE-QP5RjcP_Zu7ZYwMW6BuV6TeQ8')
    s3 = boto3.resource('s3')
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None
    conversations = {}
    while True:
        for update in bot.getUpdates(offset=update_id, timeout=10):
            update_id = update.update_id + 1
            if update.message:
                if update.message.text == "Exit":
                    with open(update.message.from_user.name+".txt", "w+") as f:
                        f.writelines(conversations.get(update.message.from_user.name, []))
                    s3.meta.client.upload_file(update.message.from_user.name+'.txt', 'cabota', update.message.from_user.name+'.txt')

                else:
                    r = requests.get('http://ec2-54-211-74-133.compute-1.amazonaws.com:5000',
                                     params={"q": update.message.text})
                    resp_value = r.json()[0]['value']
                    if resp_value:
                        update.message.reply_text(resp_value[0])
                    try:
                        conversations[update.message.from_user.name] += [str(update.message.date) + " - User - " + str(update.message.text) + "\n"]
                        conversations[update.message.from_user.name] += [str(update.message.date) + " - Bot - " + str(resp_value[0]) + "\n"]
                    except KeyError:
                        conversations[update.message.from_user.name] = [str(update.message.date) + " - User - " + str(update.message.text) + "\n"]
                        conversations[update.message.from_user.name] += [str(update.message.date) + " - Bot - " + str(resp_value[0]) + "\n"]


if __name__ == '__main__':
    run()
