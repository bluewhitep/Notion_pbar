import os, time

from notion_pbar.tool import NotionProcessBar as npbar
from notion_kit import kit as nkit
from notion_kit import object as nobj

# Simple example
if __name__ == "__main__":
    # 1. Recommend: use environment variable
    token = os.environ["NOTION_TOKEN"]
    # 2. Get database url from notion
    database_url = "https://www.notion.so/8641044a06c8471a8c67629d60b8996a?v=bc27b6158c6b417aab3a47c8b129f249&pvs=4"

    # 3. init a client
    npbar.Client(token=token, database_url=database_url)
    total = 20
    name = "quicky test"
    pbar = npbar.set_pbar(total=total, name=name)

    for i in range(total):
        print(i)
        pbar.update()
        time.sleep(1)

    npbar.close()
        
