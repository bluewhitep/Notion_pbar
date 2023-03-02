import time
from multiprocessing import Process, Lock, Value
from multiprocessing.managers import BaseManager

from notion_kit import kit as nkit
from notion_kit import object as nobj
from notion_kit.CONTENTS import NON_UPDATABLE_PROPERTIES_ITEMS

#-----------------[ Low-Level API ]-----------------#
#-----------------[ Multiprocessing custom manager ]-----------------#
class PushStructManager(BaseManager):
    def __init__(self):
        super().__init__()
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

PushStructManager.register("PushManager", PushStructManager)

#-----------------[ High-Level API ]-----------------#
class PushProcess:
    @staticmethod
    def push_method(token:str, push_manager:PushStructManager, 
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
            # Get page_object
            page_object = push_manager.get_object()
            if page_object is not None:
                # Push to notion server
                nkit.Page.update(page_object)
            time.sleep(interval)
        
    def __init__(self, token, interval:int=1):
        self.token = token
        self.interval = interval
        # Init manager
        
        self.manager = PushStructManager()
        self.manager.start()
        
        self.push_manager = self.manager.PushManager()
        
        # Init process
        self.push_process = Process(target=PushProcess.push_method,
                                    args=(token, self.push_manager, interval))
        self.push_process.daemon = True
        self.push_process.start()

    def request(self, page_object:nobj.Page)->None:
        self.push_manager.set_object(page_object)
        
    def close(self)->None:
        self.push_process.terminate()
        self.manager.shutdown() 
        self.push_process.join()
        
