import praw
from kafka import KafkaProducer
from json import dumps

# Reddit credentials
reddit = praw.Reddit(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    user_agent='script by /u/YOUR_USERNAME',
    username='YOUR_USERNAME',
    password='PASSWORD'
)

# Kafka producer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: dumps(x).encode('utf-8'))

# Fetch new posts from the subreddit
subreddit = reddit.subreddit('news')  # replace 'news' with your subreddit of interest

for submission in subreddit.stream.submissions():
    try:
        data = {'title': submission.title, 'text': submission.selftext}
        producer.send('reddit_stream', value=data)
        producer.flush()
        print("Posted to Kafka:", data)
    except Exception as e:
        print(e)
