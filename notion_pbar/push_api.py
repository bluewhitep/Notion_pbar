import time
from multiprocessing import Process, Lock, Value
from multiprocessing.managers import BaseManager

from notion_kit import kit as nkit
from notion_kit import object as nobj
from notion_kit.CONTENTS import NON_UPDATABLE_PROPERTIES_ITEMS

#-----------------[ Low-Level API ]-----------------#
#-----------------[ Multiprocessing custom manager ]-----------------#
class ObjectPush:
    def __init__(self):
        self.push_object = None
        self.lock = Lock()
        
    def set_object(self, object):
        self.lock.acquire()
        self.push_object = object
        self.lock.release()
        
    def clear_object(self):
        self.lock.acquire()
        self.push_object = None
        self.lock.release()
        
    def get_object(self):
        object = self.push_object
        if object is None:
            return None
        else:
            self.clear_object()
            return object

class BlockPush:
    def __init__(self):
        self.push_blocks = []
        self.lock = Lock()
        
    def add_block(self, id:str, block_object:nobj.Block):
        self.lock.acquire()
        self.push_blocks.append({'id':id, 'block':block_object})
        self.lock.release()
        
    def clear_block(self):
        self.lock.acquire()
        self.push_blocks = []
        self.lock.release()
    
    def get_block(self) -> list:
        blocks = self.push_blocks
        if len(blocks) == 0:
            return []
        
        # Merge the blocks
        id_list = []
        block_list = []
        for block in blocks:
            if block['id'] not in id_list:
                id_list.append(block['id'])
                block_list.append([])
            index = id_list.index(block['id'])
            block_list[index].append(block['block'])
        push_block_list = [{'id':id,'block':block} 
                           for id, block in zip(id_list, block_list)]
        
        self.clear_block()
        return push_block_list

class CustomManager(BaseManager):
    pass

CustomManager.register("PagePush", ObjectPush)
CustomManager.register("BlockPush", BlockPush)

#-----------------[ High-Level API ]-----------------#
class PushProcess:
    @staticmethod
    def push_method(token:str,
                    page_manager:ObjectPush,
                    block_manager:BlockPush, 
                    interval:int=1)->None:
        """
        Push the page object to the notion server.
        
        Parameters
            token:          (str)               - The token of the notion server.
            push_manager:   (PushStructManager) - The manager of the push object.
            interval:       (int)               - The interval of the push method. [default: 1 sec]
        """
        # Init
        nkit.Client(token=token)
        
        # While for push
        while True:
            # Get block_object
            block_objects = block_manager.get_block()
            if len(block_objects) > 0:
                # Push to notion server
                for block_object in block_objects:
                    nkit.Block.add_block(block_object['id'], block_object['block'])
                
            # Get page_object
            page_object = page_manager.get_object()
            if page_object is not None:
                # Push to notion server
                nkit.Page.update(page_object)
            
            time.sleep(interval)
        
    def __init__(self, token, interval:int=1):
        self.token = token
        self.interval = interval
        # Init manager
        
        self.manager = CustomManager()
        self.manager.start()
        
        self.page_manager = self.manager.PagePush()
        self.block_manager = self.manager.BlockPush()
        
        # Init process
        self.push_process = Process(target=PushProcess.push_method,
                                    args=(token,
                                          self.page_manager,
                                          self.block_manager,
                                          interval))
        self.push_process.daemon = True
        self.push_process.start()

    def page_request(self, page_object:nobj.Page)->None:
        self.page_manager.set_object(page_object)
        
    def block_request(self, id:str, block_object:nobj.Block)->None:
        self.block_manager.add_block(id, block_object)
        
    def close(self)->None:
        self.push_process.join(timeout=10)
        self.push_process.terminate()
        self.manager.shutdown() 
        self.push_process.join()
        
