import json
import asyncio
from typing import Optional
from datetime import datetime

from fake_useragent import UserAgent
from playwright.async_api import async_playwright

from .schemas import Tweet
from core.logger import logger


class Twetter:
    def __init__(self, token: str | None, proxy: str = None):
        self.proxy = {
            "server": f"http://{proxy.split('@')[1]}",
            "username": proxy.split(":")[0],
            "password": proxy.split(":")[1].split("@")[0],
        }

        self.cookies_file_path = "cookies.json"
        self.token = token

    async def start(self):
        self.playwright = await async_playwright().start()
        await self._initialize_context()

    async def open(
        self,
        url: str,
        on: Optional[callable] = None,
        on_result: Optional[list] = None,
        timeout: Optional[int] = 2,
    ):
        page = await self._create_page()

        if on:
            page.on(
                "response",
                lambda response: asyncio.create_task(on(response, on_result)),
            )
        await page.goto(url, timeout=timeout * 1000000)
        await asyncio.sleep(timeout)

        return on_result

    async def get_posts(self, unfl: str, timeout=None) -> list[Tweet]:
        result = []
        await self.open(
            f"https://twitter.com/{unfl}",
            timeout=timeout,
            on_result=result,
            on=self.handle_response,
        )
        logger.info(f"Get Posts: {unfl}")

        return result

    async def get_butch_posts(
        self,
        unfls: list[str],
        posts_count: int | None = None,
    ) -> list[list[Tweet]]:
        logger.info("Get Butch Posts")
        posts = []
        tasks = [asyncio.create_task(self.get_posts(unfl, 5)) for unfl in unfls]

        results = await asyncio.gather(*tasks)

        for result in results:
            posts.append(result if posts_count is None else result[:posts_count])
        return posts

    async def handle_response(self, response, result: list):
        try:
            if "UserTweets" in response.url:
                response_body = await response.text()
                self.parse_posts(json.loads(response_body), result)
        except Exception as e:
            print(f"Error while processing response: {e}")

    def parse_posts(self, data, result: list):
        timelines = data["data"]["user"]["result"]["timeline_v2"]["timeline"]
        for instruction in timelines["instructions"]:
            if instruction["type"] == "TimelineAddEntries":
                for entry in instruction["entries"]:
                    try:
                        post = entry["content"]

                        if content := post.get("itemContent"):
                            legacy = content["tweet_results"]["result"]["legacy"]
                            result.append(
                                Tweet(
                                    id=int(legacy["id_str"]),
                                    text=legacy["full_text"],
                                    created_at=int(
                                        datetime.strptime(
                                            legacy["created_at"],
                                            "%a %b %d %H:%M:%S %z %Y",
                                        ).timestamp()
                                    ),
                                )
                            )
                    except Exception as e:
                        print(f"Error while parsing entry: {e}")

    async def _initialize_context(self):
        logger.info('_initialize_context')
        ua = UserAgent()
        browser = await self.playwright.chromium.launch(
            headless=True,
            proxy=self.proxy,
        )

        self.context = await browser.new_context(
            storage_state=self.cookies_file_path,
            user_agent=ua.chrome,
        )

        if self.token:
            await self.context.add_cookies([self._get_cookies()])

    async def _create_page(self):
        page = await self.context.new_page()
        s = """
            if (navigator.webdriver === false) {
                // Post Chrome 89.0.4339.0 and already good
            } else if (navigator.webdriver === undefined) {
                // Pre Chrome 89.0.4339.0 and already good
            } else {
                // Pre Chrome 88.0.4291.0 and needs patching
                delete Object.getPrototypeOf(navigator).webdriver
            }
            """

        await page.add_init_script(s)

        return page

    def _get_cookies(self):
        return {
            "name": "auth_token",
            "value": self.token,
            "path": "/",
            "domain": ".twitter.com",
            "expires": 1868720206.0,
            "httpOnly": True,
            "secure": True,
        }
