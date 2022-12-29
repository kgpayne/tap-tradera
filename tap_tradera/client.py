"""Custom client handling, including traderaStream base class."""

import zeep


def flatten_category(category, parent=None):
    flat_categories = []
    # add current node
    this_category = {k: v for k, v in category.items() if k in {"Id", "Name"}}
    if parent:
        this_category["ParentId"] = parent["Id"]
    else:
        this_category["ParentId"] = 0
    flat_categories.append(this_category)
    # add child nodes
    if category["Category"]:
        for child_category in category["Category"]:
            flat_categories.extend(
                flatten_category(category=child_category, parent=category)
            )
    return flat_categories


class TraderaClient:
    def __init__(self, app_id: int, app_key: str):
        self.app_id: int = app_id
        self.app_key: str = app_key

    @property
    def search_service(self):
        wsdl = "https://api.tradera.com/v3/SearchService.asmx?WSDL"
        return zeep.Client(wsdl=wsdl)

    def search(self, query, category_id=0, order_by="EndDateAscending"):
        """Simple keyword search."""
        total_pages = 1
        current_page = 1
        search_items = []
        while current_page <= total_pages:
            search_result = self.search_service.service.Search(
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
            search_items.extend(
                [
                    zeep.helpers.serialize_object(search_item, dict)
                    for search_item in search_result.Items
                ]
            )
            total_pages = search_result.TotalNumberOfPages
            current_page += 1
        return search_items

    @property
    def public_service(self):
        wsdl = "https://api.tradera.com/v3/publicservice.asmx?WSDL"
        return zeep.Client(wsdl=wsdl)

    def get_categories(self):
        """Returns Tradera.com Categories.

        Names are in Swedish.
        """
        soap_categories = self.public_service.service.GetCategories(
            _soapheaders={
                "AuthenticationHeader": {
                    "AppId": int(self.app_id),
                    "AppKey": self.app_key,
                }
            }
        )
        categories = zeep.helpers.serialize_object(soap_categories, dict)
        flat_categories = []
        for category in categories:
            flat_categories.extend(flatten_category(category))
        return flat_categories

    def get_item(self, item_id):
        soap_item = self.public_service.service.GetItem(
            _soapheaders={
                "AuthenticationHeader": {
                    "AppId": int(self.app_id),
                    "AppKey": self.app_key,
                }
            },
            itemId=item_id,
        )
        item = zeep.helpers.serialize_object(soap_item, dict)
        return item
