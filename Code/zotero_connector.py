import os
from dotenv import load_dotenv
from pyzotero import zotero

# 1. Load .env into os.environ
load_dotenv()  

# 2. Grab credentials
USR_ID   = os.environ["ZOTERO_USER_ID"]
LIB_TYPE = os.environ.get("ZOTERO_LIBRARY_TYPE", "user")  # default to 'user'
API_KEY  = os.environ.get("ZOTERO_API_KEY")               # can be None if you only need local access

# 3. Instantiate the client
#    - For Web API access: local=False (default)
#    - For read-only local access via Zotero's built-in HTTP server: local=True
zot = zotero.Zotero(USR_ID, LIB_TYPE, API_KEY, local=True)

# 4. Quick test: fetch and print your latest 5 items
items = zot.items(sort="dateModified", order="desc")
for item in items:
    data = item["data"]
    print(f"{data.get('title','<no title>')}  —  {data.get('key')}")