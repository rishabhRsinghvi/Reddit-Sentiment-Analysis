import praw
from kafka import KafkaProducer
from json import dumps

# Reddit credentials
reddit = praw.Reddit(
    client_id='zcMm_aEoHjaAelidRCsyjA',
    client_secret='m8G_BXOnsDGtW0-sshU5YykAl519Bw',
    user_agent='script by /u/Dogemuskelon',
    username='Dogemuskelon',
    password='sentiment@analysis'
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