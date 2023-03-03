import os, time

from notion_pbar.tool import NotionProcessBar as npbar
from notion_kit import kit as nkit
from notion_kit import object as nobj

# Simple example
if __name__ == "__main__":
    # 1. Recommend: use environment variable
    token = os.environ["NOTION_TOKEN"]
    # 2. Get database url from notion
    database_url = ""

    # 3. init a client
    npbar.Client(token=token, database_url=database_url)
    total = 10
    name = "quicky test"
    pbar = npbar.set_pbar(total=total, name=name)

    # 4. update exist property
    ## 'Rich Text', 'Select' and 'Checkbox'
    pbar.update_property(Text="Hello World!",
                         Select="Option 1",
                         Checkbox=True)
    
    for i in range(total):
        print(i)
        pbar.update()
        time.sleep(1)
        
    pbar.update_checkbox(name='Checkbox', check=True)
    pbar.update_select(name='Select', option='Option 2', color='red')
    pbar.update_rich_text(name='text', text='Done')
    npbar.close()
        
