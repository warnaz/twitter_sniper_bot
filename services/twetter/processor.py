import re
import json
from twetter.intefaces import ITweetProcessor
from multiprocessing import Pool, cpu_count


class TweetProcessor(ITweetProcessor):
    def __init__(self):
        self.tokens = self.get_tokens()
        print(f"Найдено {len(self.tokens)} токенов.")

    def get_tokens(self):
        with open("tokens.json", "r") as file:
            tokens = json.load(file)
        return tokens

    def find_token_mentions(self, tweet_data):
        text, tokens = tweet_data
        mentions = []
        for token in tokens:
            if re.search(r"\b" + re.escape(token) + r"\b", text):
                mentions.append(token)
        return (text, mentions)

    def process(self):
        tweet_data = [(tweet.text, self.tokens) for tweet in self.tweets]

        with Pool(cpu_count()) as pool:
            results = pool.map(self.find_token_mentions, tweet_data)

        filtered_tweets = [result for result in results if result[1]]
        return filtered_tweets

    def display_results(self, filtered_tweets):
        print(f"Найдено {len(filtered_tweets)} твитов с упоминаниями токенов.")
        for tweet, mentions in filtered_tweets:
            print(f"Упоминания: {', '.join(mentions)}")
            print("\n\n")
