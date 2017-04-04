import telegram
import requests
import boto3

update_id = None


def upload_to_s3(data, key_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('results')
    bucket.upload_fileobj(data, key_name)


def run():
    global update_id
    bot = telegram.Bot('TOKEN')
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        for update in bot.getUpdates(offset=update_id, timeout=10):
            update_id = update.update_id + 1
            if update.message:
                try:
                    r = requests.get('http://ec2-54-211-74-133.compute-1.amazonaws.com:5000',
                                     params={"q": update.message.text})
                    resp_value = r.json()[0]['value'][0]
                    update.message.reply_text(resp_value)

                    # Log conv

                except:
                    pass

if __name__ == '__main__':
    run()
