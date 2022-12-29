"""Stream type classes for tap-tradera."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any, Iterable, List, Optional

import singer_sdk._singerlib as singer
from singer_sdk.plugin_base import PluginBase as TapBaseClass
from singer_sdk.streams import Stream

from tap_tradera.client import TraderaClient

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class TraderaSearchStream(Stream):
    """Stream class for tradera streams."""

    name = "search_items"
    schema_filepath = SCHEMAS_DIR / "search_item.json"

    def __init__(
        self,
        tap: TapBaseClass,
        client: TraderaClient,
        searches: List[dict],
        schema: str | PathLike | dict[str, Any] | singer.Schema | None = None,
        name: str | None = None,
    ):
        super().__init__(tap=tap, schema=schema, name=name)
        self.client = client
        self.searches = searches

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of record-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        for search in self.searches:
            for search_item in self.client.search(
                query=search["query"],
                category_id=search.get("category_id", 0),
                order_by=search.get("order_by", "EndDateAscending"),
            ):
                search_item["search_id"] = search["name"]
                yield search_item


class TraderaCategoriesStream(Stream):
    """Stream class for tradera streams."""

    name = "categories"
    schema_filepath = SCHEMAS_DIR / "category.json"

    def __init__(
        self,
        tap: TapBaseClass,
        client: TraderaClient,
        schema: str | PathLike | dict[str, Any] | singer.Schema | None = None,
        name: str | None = None,
    ):
        super().__init__(tap=tap, schema=schema, name=name)
        self.client = client

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of record-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        for category in self.client.get_categories():
            yield category


class TraderaItemsStream(Stream):
    """Tradera items."""

    name = "items"
    schema_filepath = SCHEMAS_DIR / "item.json"

    def __init__(
        self,
        tap: TapBaseClass,
        client: TraderaClient,
        item_ids: List[str],
        schema: str | PathLike | dict[str, Any] | singer.Schema | None = None,
        name: str | None = None,
    ):
        super().__init__(tap=tap, schema=schema, name=name)
        self.client = client
        self.item_ids = item_ids

    def get_records(self, context: dict | None) -> Iterable[dict | tuple[dict, dict]]:
        for item_id in self.item_ids:
            item = self.client.get_item(item_id)
            yield item
