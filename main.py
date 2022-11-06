import argparse
import json
import logging
from tweepy import StreamRule, StreamingClient
from google.cloud import pubsub_v1

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bearer_token", type=str, required=True)
    parser.add_argument("--stream_rule", type=str, required=True)
    parser.add_argument("--project_id", type=str, required=True)
    parser.add_argument("--topic", type=str, required=True)

    return parser.parse_args()

def write_to_pubsub_topic(data, stream_rule):
    data["stream_rule"] = stream_rule
    data_formatted = json.dumps(data).encode("utf-8")
    id = data["id"].encode("utf-8")
    author_id = data["author_id"].encode("utf-8")

    future = publisher.publish(
        topic_path, data_formatted, id=id, author_id=author_id
    )
    print(future.result())

class TweetStreamer(StreamingClient):
    def __init__(self, bearer_token, stream_rule):
        super().__init__(bearer_token)
        self.stream_rule = stream_rule
    
    def on_response(self, response):
        tweet_data = response.data.data
        user_data = response.includes['users'][0].data
        result = tweet_data
        result['user'] = user_data
        write_to_pubsub_topic(result, self.stream_rule)
        with open("tweets.json", "a") as f:
            f.write(json.dumps(result))
    
    def on_errors(self, errors):
        logging.error("Error : {}".format(str(errors)))

if __name__ == "__main__":
    tweet_fields=['id', 'text', 'author_id', 'created_at', 'lang', 'non_public_metrics', 'organic_metrics', 'possibly_sensitive']
    user_fields = ['username', 'description', 'location', 'public_metrics', 'verified']
    expansions = ['referenced_tweets.id', 'author_id']

    logging.basicConfig(level=logging.DEBUG, filename='tweet.log', 
        format='%(asctime)s-%(levelname)s: %(message)s',
        datefmt='%d-%b-%y %H:%M:%S')

    args = parse_args()
    streamer = TweetStreamer(args.bearer_token, args.stream_rule)
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(args.project_id, args.topic)

    # Remove existing rules
    rules = streamer.get_rules().data
    if rules is not None:
        existing_rules = [rule.id for rule in rules]
        streamer.delete_rules(existing_rules)
    
    # add new rules and run stream
    streamer.add_rules([StreamRule(args.stream_rule)])
    streamer.filter(
        tweet_fields=tweet_fields, user_fields=user_fields, expansions=expansions
        )
