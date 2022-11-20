"""Custom client handling, including traderaStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk.streams import Stream


class traderaStream(Stream):
    """Stream class for tradera streams."""

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of record-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        # TODO: Write logic to extract data from the upstream source.
        # records = mysource.getall()
        # for record in records:
        #     yield record.to_dict()
        raise NotImplementedError("The method is not yet implemented (TODO)")
