from kafka import KafkaConsumer
import json

topic_name = 'reddit_stream'

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

try:
    for message in consumer:
        # Assuming data contains 'title' and 'text'
        print("Title:", message.value['title'])
        print("Text:", message.value['text'])
except Exception as e:
    print(f"Error: {e}")
