from dotenv import load_dotenv
from notion_client import Client
import os

load_dotenv()

source_notion_api_key = os.getenv("SOURCE_NOTION_API_KEY")
source_database_id = os.getenv("SOURCE_DATABASE_ID")

destination_notion_api_key = os.getenv("DESTINATION_NOTION_API_KEY")
destination_database_id = os.getenv("DESTINATION_DATABASE_ID")

source_client = Client(auth=source_notion_api_key)
destination_client = Client(auth=destination_notion_api_key)

properties_to_copy = [
    "Fecha de publicación",
    "Thumbnail",
    'Name',
    "Assets",
    "Video"
]

# Get all pages from the source database
results = source_client.databases.query(
    **{
        "database_id": source_database_id,
        "filter": {
            "property": "Estatus",
            "status": {
                
                "equals": "Publicado"
            },
        },  
        "sorts": [{"property": "Fecha de publicación", "direction": "ascending"}],
    }
).get("results")

for page in results[:4]:
    page_properties = { prop : page["properties"][prop] for prop in properties_to_copy}
    created = destination_client.pages.create(
        **{
            "parent": {"database_id": destination_database_id},
            "cover":{
                "type": "external",
                "external": {
                    "url": "https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1065&q=80"
                }
                },
            "properties": page_properties
        }
    )

# breakpoint()
# pass
