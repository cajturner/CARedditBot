FROM python:latest

ADD RedditBot.py .
ADD requirements.txt .

RUN pip install -r requirements.txt

CMD python RedditBot.py
