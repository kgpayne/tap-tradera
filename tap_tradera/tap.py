"""tradera tap class."""

import csv
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
            "items_file", th.StringType, description="File path to items list CSV."
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

        if self.config.get("items_file"):
            with open(self.config["items_file"]) as f:
                reader = csv.reader(f)
                item_ids = [i[0] for i in reader]
            if item_ids:
                streams.append(
                    TraderaItemsStream(tap=self, client=client, item_ids=item_ids)
                )

        return streams


if __name__ == "__main__":
    TapTradera.cli()
