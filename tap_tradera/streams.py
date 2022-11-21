"""Stream type classes for tap-tradera."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

import singer_sdk._singerlib as singer
import zeep
from singer_sdk.plugin_base import PluginBase as TapBaseClass
from singer_sdk.streams import Stream

from tap_tradera.client import TraderaClient

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class TraderaSearchStream(Stream):
    """Stream class for tradera streams."""

    schema_filepath = SCHEMAS_DIR / "search_items.json"

    def __init__(
        self,
        tap: TapBaseClass,
        client: TraderaClient,
        query: str,
        category_id: int = 0,
        order_by: str = "EndDateAscending",
        schema: str | PathLike | dict[str, Any] | singer.Schema | None = None,
        name: str | None = None,
    ):
        super().__init__(tap=tap, schema=schema, name=name)
        self.client = client
        self.query = query
        self.category_id = category_id
        self.order_by = order_by

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of record-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        yield from [
            zeep.helpers.serialize_object(search_item, dict)
            for search_item in self.client.search(
                query=self.query, category_id=self.category_id, order_by=self.order_by
            )
        ]
