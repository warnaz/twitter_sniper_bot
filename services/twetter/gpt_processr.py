import re
import time
import httpx
import requests
from openai import OpenAI

from core.logger import logger
from core.config import settings, PROXY
from services.crud import valid_tweets
from .intefaces import ITweetProcessor
from .schemas import ProcessedTweet, Tweet



_http_client = httpx.Client(proxy=PROXY)
openai = OpenAI(api_key=settings.API_KEY, http_client=_http_client)


class TweetProcessor(ITweetProcessor):
    def __init__(self):
        self.api_key = settings.API_KEY

    def _send_prompt(self, prompt: str):
        logger.info("Send prompt to GPT")
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI travel assistant. You will give advices about places to visit",
                },
                {"role": "user", "content": prompt[0]},
            ],
        )
        advice = response.choices[0].message.content
        return advice

    def old_send_prompt(self, prompt: str):
        model = "gpt-4o"
        old_model = "gpt-3.5-turbo-instruct"

        logger.info("Send prompt to GPT")
        # payload = {
        #     "model": model,
        #     "prompt": prompt,
        #     "max_tokens": 15,
        # }
        payload = {
            "model": "gpt-4o",
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON.",
                },
                {"role": "user", "content": (prompt)},
            ],
            "max_tokens": 300,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        time.sleep(5)
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers=headers,
            json=payload,
            proxies={
                "http": "http://dkhalidovstt:VBNsY2BRZW@185.248.51.166:59100",
                "https": "http://dkhalidovstt:VBNsY2BRZW@185.248.51.166:59100",
            },
        )
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["text"]
        else:
            print(f"Error: {response.json()}")

    def _get_tokens(self, text: str):
        prompt = (
            f"""Task: Identify and highlight all mentions of crypto tokens in the provided text. Make sure you find both popular and lesser known tokens.

            Steps:

            Read the entire text.
            Look for any words or phrases that could be crypto tokens.
            Highlight the found tokens in the text.
            If possible, include only the token abbreviation without extra text if it is present in the text. otherwise give [NULL]

            Example text and result:

            Text:
            "Bitcoin and Ethereum have risen significantly in price recently. Dogecoin has also attracted the attention of many investors."

            Result:
            [BTC ETH DOGE]

            Here is the text:
            {text}""",
        )

        response = self._send_prompt(prompt)
        if response:
            try:
                return self._process_porpt_result(response)
            except Exception:
                print(f"Error: {response}")
                return None
        else:
            return None

    def _process_porpt_result(self, text: str):
        tokens_str = text.split("[")[1].split("]")[0]
        tokens = tokens_str.split()
        tokens = self._clean_tokens(tokens)
        return tokens

    def _clean_tokens(self, tokens):
        delete_symbols = re.compile(r"[,\[\]\"'NULL\s]+")
        cleaned_tokens = [delete_symbols.sub("", token) for token in tokens]
        return list(filter(None, cleaned_tokens))

    def find_token_by_symbol(self, text: str, symbols: list[str]):
        tokens = []
        words = text.split()
        for word in words:
            for symbol in symbols:
                if word.startswith(symbol):
                    word = word[len(symbol) :]
                    if self.is_number(word):
                        continue
                    tokens.append(word)
        return tokens

    async def process(self, tweets: list[Tweet]) -> list[ProcessedTweet]:
        logger.info("Process Tweets")
        result = []
        tweets_valid = await valid_tweets(tweets)

        logger.info(f"Send new {len(tweets_valid)} tweets to GPT")
        for tweet in tweets_valid:
            tokens_by_gpt = self._get_tokens(tweet)
            tokens_by_symbol = self.find_token_by_symbol(tweet.text, ["$"])

            tokens = list(set(tokens_by_gpt + tokens_by_symbol))

            if not tokens:
                continue

            result.append(
                ProcessedTweet(
                    id=tweet.id,
                    text=tweet.text,
                    created_at=tweet.created_at,
                    mentions=tokens,
                )
            )
        return result

    def is_number(self, n):
        try:
            float(n)
            return True
        except ValueError:
            return False
