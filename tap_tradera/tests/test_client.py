import json
import os

from tap_tradera.client import TraderaClient


def test_search():
    client = TraderaClient(
        app_id=os.getenv("TAP_TRADERA_APP_ID"), app_key=os.getenv("TAP_TRADERA_APP_KEY")
    )
    search_items = client.search("optimus")
    assert search_items
