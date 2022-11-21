"""Custom client handling, including traderaStream base class."""

import zeep


class TraderaClient:
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

        wsdl = "https://api.tradera.com/v3/SearchService.asmx?WSDL"
        self.client = zeep.Client(wsdl=wsdl)

    def search(self, query, category_id=0, order_by="EndDateAscending"):
        """Simple keyword search."""
        total_pages = 1
        current_page = 1
        search_items = []
        while current_page <= total_pages:
            search_result = self.client.service.Search(
                query=query,
                categoryId=category_id,
                pageNumber=current_page,
                orderBy=order_by,
                _soapheaders={
                    "AuthenticationHeader": {
                        "AppId": self.app_id,
                        "AppKey": self.app_key,
                    }
                },
            )
            search_items.extend(search_result.Items)
            total_pages = search_result.TotalNumberOfPages
            current_page += 1
        return search_items
