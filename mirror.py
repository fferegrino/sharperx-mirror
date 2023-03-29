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

DEFAULT_PAGE_COVER = "https://ik.imagekit.io/thatcsharpguy/video/thumbnails/default-thumbnail.png?updatedAt=1680120443520"

def clear_database(database_id):
    results = destination_client.databases.query(
        **{
            "database_id": database_id,
            "sorts": [{"property": "Fecha de publicación", "direction": "ascending"}],
        }
    ).get("results")

    for page in results:
        page["page_id"] = page["id"]
        page["archived"] = True
        destination_client.pages.update(
            **page
        )

clear_database(destination_database_id)

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
                    "url": page_properties["Thumbnail"]["url"] or DEFAULT_PAGE_COVER
                }
                },
            "properties": page_properties
        }
    )

    old_page_id = page["id"]
    new_page_id = created['id']

    blocks = source_client.blocks.children.list(block_id=old_page_id).get("results")

    new_blocks = []
    for block in blocks:
        block["parent"] = {"page_id": new_page_id, 'type': 'page_id'} 
        block["archived"] = False

        properties_to_remove = ["id", "created_by", "created_time", "last_edited_by", "last_edited_time"]
        for prop in properties_to_remove:
            block.pop(prop)

        new_blocks.append(block)

    destination_client.blocks.children.append(block_id=new_page_id, children=new_blocks)
