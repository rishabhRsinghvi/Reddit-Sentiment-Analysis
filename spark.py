from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StringType, StructType, StructField, FloatType
import re
from textblob import TextBlob

def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'\n', ' ', text)
    return text.strip()

def get_subjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def get_polarity(text):
    return TextBlob(text).sentiment.polarity

def get_sentiment(polarity):
    if polarity < 0:
        return 'Negative'
    elif polarity == 0:
        return 'Neutral'
    else:
        return 'Positive'

def main():
    spark = SparkSession \
        .builder \
        .appName("RedditSentimentAnalysis") \
        .getOrCreate()
    spark.sparkContext.setLogLevel('WARN')

    schema = StructType([
        StructField("title", StringType(), True),
        StructField("text", StringType(), True)
    ])

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "reddit_stream") \
        .option("startingOffsets", "earliest") \
        .load()
    df = df.selectExpr("CAST(value AS STRING) as json")
    df = df.select(from_json("json", schema).alias("data")).select("data.*")

    df = df.withColumn("combined_text", col("title") + " " + col("text"))
    clean_text_udf = F.udf(clean_text, StringType())
    df = df.withColumn("processed_text", clean_text_udf(col("combined_text")))

    subjectivity_udf = F.udf(get_subjectivity, FloatType())
    polarity_udf = F.udf(get_polarity, FloatType())
    sentiment_udf = F.udf(get_sentiment, StringType())

    sentiment_data = df \
        .withColumn('subjectivity', subjectivity_udf(col("processed_text"))) \
        .withColumn('polarity', polarity_udf(col("processed_text"))) \
        .withColumn('sentiment', sentiment_udf(col('polarity')))

    query = sentiment_data \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    query.awaitTermination()

if __name__ == '__main__':
    main()
