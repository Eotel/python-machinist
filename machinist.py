""" machinist

"""
import json
from logging import NullHandler
from logging import getLogger
from typing import Any
from typing import TypedDict

import requests
from requests import Response

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Machinist:
    def __init__(
        self,
        url: str = "https://gw.machinist.iij.jp/endpoint",
        api_key: str = None,
        agent_name: str = None,
    ):

        if url is None:
            raise ValueError("url is None")

        if api_key is None:
            raise ValueError("api_key is None")

        if agent_name is None:
            raise ValueError("agent_name is None")

        self.url: str = url
        self.api_key: str = api_key
        self.agent_name: str = agent_name
        self.headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.metrics: list[Metric] = []
        self.body: Body = {"agent": f"{agent_name}", "metrics": self.metrics}

    def post_metrics(self) -> Response:
        result = requests.post(
            self.url, data=json.dumps(self.body), headers=self.headers
        )

        match result.status_code:
            case 200:
                logger.info("[OK] データの送信に成功しました")
            case 400:
                logger.info("[Bad Request] リクエストのフォーマットが不正です")
            case 401:
                logger.info("[Unauthorized Access] 認証に失敗しました")
            case 409:
                logger.info("[Conflict] リソース利用上限数に達しています")
            case 422:
                logger.info("[Unprocessable Entity] リクエストボディのパラメータに問題があります")
            case 429:
                logger.info("[Too Many Requests] 単位時間あたりの送信回数が規定値を超えています")
            case _:
                logger.info(result.status_code)

        return result


class DataPointRequired(TypedDict):
    value: int | float


class DataPoint(DataPointRequired, total=False):
    """
    timestamp : POSIX timestamp as float

    特殊なmetaプロパティ
    key (str) | value (str) | summary
    --------- | ----------- | -------
    latitude  | -90° ~ 90°  | 地図の表示 に用いる緯度の値
    longitude | -180° ~ 180°| 地図の表示 に用いる経度の値
    """

    timestamp: float
    meta: dict[str, Any]


class MetricRequired(TypedDict):
    """
    Required keys
    """

    name: str
    data_point: dict[str, str | int | float | bool | dict[str, Any]]


class Metric(MetricRequired, total=False):
    """
    Optional keys
    """

    namespace: str
    tags: dict[str, str]


class Body(TypedDict):
    agent: str
    metrics: list[Metric]
