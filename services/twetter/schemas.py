from pydantic import BaseModel


class Tweet(BaseModel):
    id: int
    text: str
    created_at: int


class ProcessedTweet(Tweet):
    mentions: list
