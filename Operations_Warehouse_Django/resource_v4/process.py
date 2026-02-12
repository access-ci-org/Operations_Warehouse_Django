import json
from typing import Iterable, List, Tuple, Any

import globus_sdk
import requests
from .documents import ResourceV4Index

from django.conf import settings
from globus_sdk.scopes import SearchScopes


class GlobusProcess():
    def __init__(self, *args, **kwargs):
        self.app = globus_sdk.ClientApp(
            "ACCESS-CI Operations Warehouse Globus Service Client",
            client_id=settings.GLOBUS_CLIENT_ID,
            client_secret=settings.GLOBUS_CLIENT_SECRET
        )

        # Add scope requirements for the Authorizer
        self.app.add_scope_requirements({
            "search.api.globus.org": [SearchScopes.all]
        })

        # Get the authorization header for the Search PUT requests
        authorizer = self.app.get_authorizer("search.api.globus.org")
        self.authorization_header = authorizer.get_authorization_header()

        # Initialize the SearchClient with the app and required scopes
        self.search_client = globus_sdk.SearchClient(
            app=self.app, app_scopes=[SearchScopes.all]
        )
        self.search_endpoint = settings.GLOBUS_SEARCH_INDEX_ID

    def ingest(self, gmeta_list):
        for i, (batch, size_bytes) in enumerate(
            self.chunk_by_size(
                gmeta_list["ingest_data"]["gmeta"],
                max_chunk_kb=8000,
                safety_ratio=0.9
            )
        ):
            print(
                f"Batch {i}: "
                f"{len(batch)} items | "
                f"{size_bytes} bytes | "
            )
            try:
                self.search_client.ingest(
                    self.search_endpoint,
                    {
                        "ingest_type": "GMetaList",
                        "ingest_data": {
                            "gmeta": batch
                        }
                    }
                )
            except globus_sdk.SearchAPIError as err:
                print({"error": str(err), "status": "400"})
                return {"error": str(err), "status": "400"}

    def delete_by_query(self, local_ids):
        print(local_ids)
        try:
            self.search_client.delete_by_query(
                self.search_endpoint,
                {
                    "@version": "delete_by_query#1.0.0",
                    "filters": [
                        {
                            "type": "match_any",
                            "field_name": "LocalID",
                            "values": local_ids,
                        }
                    ],
                }
            )
        except globus_sdk.SearchAPIError as err:
            print({"error": str(err), "status": "400"})
            return {"error": str(err), "status": "400"}
        return {}

    def update_by_subject(self, gmeta_list):
        headers = {
            "Authorization": self.authorization_header,
            "Content-Type": "application/json"
        }
        url = f"https://search.api.globus.org/v1/index/{self.search_endpoint}/entry"

        for gmeta_entry in gmeta_list["ingest_data"]["gmeta"]:
            payload = {
                "subject": gmeta_entry["subject"],
                "visible_to": gmeta_entry["visible_to"],
                "content": gmeta_entry["content"]
            }

            response = requests.put(url, json=payload, headers=headers)
            response.raise_for_status()
            print(response.json())

    # Utility functions
    def chunk_by_size(
        self,
        items: Iterable[Any],
        max_chunk_kb: int = 10000,
        safety_ratio: float = 1.0,
    ) -> Iterable[Tuple[List[Any], int]]:
        """
        Yield (chunk, size_bytes) where each chunk's serialized JSON size
        does not exceed max_chunk_kb * safety_ratio.

        Args:
            items: Iterable of JSON-serializable objects
            max_chunk_kb: Maximum chunk size in kilobytes (default 10,000 KB)
            safety_ratio: Optional safety factor (e.g. 0.8 for 80%)

        Yields:
            Tuple of:
                - List of items
                - Serialized size in bytes
        """
        max_bytes = int(max_chunk_kb * 1024 * safety_ratio)

        chunk: List[Any] = []
        current_size = 2  # accounts for opening + closing brackets []

        for item in items:
            item_bytes = json.dumps(
                item,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")

            item_size = len(item_bytes)

            if item_size > max_bytes:
                raise ValueError(
                    f"Single item size ({item_size} bytes) exceeds max chunk size ({max_bytes} bytes)"
                )

            additional_size = item_size
            if chunk:
                additional_size += 1  # comma separator

            if chunk and current_size + additional_size > max_bytes:
                yield chunk, current_size
                chunk = []
                current_size = 2
                additional_size = item_size

            chunk.append(item)
            current_size += additional_size

        if chunk:
            yield chunk, current_size

    def put_search_entry(self, payload):
        pass

class ResourceV4Process():

    def index(self, relations=None):
        newRels = []
        if relations:
            for i in relations:
                newRels.append({'RelatedID': i, 'RelationType': relations[i]})
        obj = ResourceV4Index(
                meta = {'id': self.ID},
                ID = self.ID,
                Affiliation = self.Affiliation,
                LocalID = self.LocalID,
                QualityLevel = self.QualityLevel,
                Name = self.Name,
                ResourceGroup = self.ResourceGroup,
                Type = self.Type,
                ShortDescription = self.ShortDescription,
                ProviderID = self.ProviderID,
                Description = self.Description,
                Topics = self.Topics,
                Keywords = self.Keywords,
                Audience = self.Audience,
                Relations = newRels,
                StartDateTime = self.StartDateTime,
                EndDateTime = self.EndDateTime
            )
        obj.save()
        return obj.to_dict(include_meta=True)

    def delete(self):
        obj = ResourceV4Index.get(self.ID).delete()
        return
