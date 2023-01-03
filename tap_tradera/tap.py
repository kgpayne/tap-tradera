"""tradera tap class."""

import csv
import glob
from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_tradera.streams import (
    TraderaCategoriesStream,
    TraderaClient,
    TraderaItemsStream,
    TraderaSearchStream,
)


class TapTradera(Tap):
    """tradera tap class."""

    name = "tap-tradera"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "app_id",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The Tradera.com developer app ID",
        ),
        th.Property(
            "app_key",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The Tradera.com developer app key",
        ),
        th.Property(
            "searches",
            th.ArrayType(
                th.ObjectType(
                    th.Property(
                        "name", th.StringType, required=True, description="Stream name"
                    ),
                    th.Property(
                        "query",
                        th.StringType,
                        required=True,
                        description="Search query",
                    ),
                    th.Property(
                        "category_id",
                        th.IntegerType,
                        required=False,
                        default=0,
                        description="Category to search. Default 0 (all categories)",
                    ),
                    th.Property(
                        "order_by",
                        th.StringType,
                        allowed_values=[
                            "Relevance",
                            "BidsAscending",
                            "BidsDescending",
                            "PriceAscending",
                            "PriceDescending",
                            "EndDateAscending",
                            "EndDateDescending",
                        ],
                        required=False,
                        default="EndDateAscending",
                    ),
                ),
            ),
            required=False,
            description="Simple Search",
        ),
        th.Property(
            "items_file_path",
            th.StringType,
            description="Path to items list CSV.",
            required=False,
        ),
        th.Property(
            "items_file_pattern",
            th.StringType,
            description="File glob pattern to items list CSV.",
            required=False,
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        client = TraderaClient(
            app_id=self.config["app_id"], app_key=self.config["app_key"]
        )
        streams = [TraderaCategoriesStream(tap=self, client=client)]

        if self.config.get("searches", []):
            streams.append(
                TraderaSearchStream(
                    tap=self, client=client, searches=self.config.get("searches")
                )
            )

        item_ids = []
        if "items_file_path" in self.config:
            with open(self.config["items_file"]) as f:
                reader = csv.reader(f)
                item_ids = [i[0] for i in list(reader)[1:]]

        if "items_file_pattern" in self.config:
            files = glob.glob(
                self.config["items_file_pattern"],
            )
            for file in files:
                with open(file) as f:
                    records = csv.reader(f)
                    item_ids.extend([i[0] for i in list(records)[1:]])

        if item_ids:
            streams.append(
                TraderaItemsStream(
                    tap=self, client=client, item_ids=list(set(item_ids))
                )
            )

        return streams


if __name__ == "__main__":
    TapTradera.cli()
