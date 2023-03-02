from notion_kit import kit as nkit
from notion_kit import object as nobj

class ProcessBar:
    STATUS_OPTIONS = ["Error",
                      "Not started",
                      "In progress",
                      "Done"]
    
    def __init__(self, 
                 page_object:nobj.Page,
                 total:int, name:str, 
                 property_dict:dict,
                 request_method
                 ):
        self.page_object = page_object
        self.value = 0
        self.total = total
        self.name = name
        self.property_dict = property_dict
        self.__request_method = request_method
    
    def __request__(self)->None:
        self.__request_method(self.page_object)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.value < self.total:
            value = self.value
            self.value += 1
            self.update()
            return value
        else:
            raise StopIteration() 
    
    def change_status(self, status:str)->None:
        nkit.Gadget.update_page_property(page_object=self.page_object,
                                         property_name="Status",
                                         status={'name': status})

    def reset(self)->None:
        self.value = 0
    
    def update_property(self, **kwargs)->None:
        if kwargs:
            for name, value in kwargs.items():
                if name in list(self.property_dict.keys()):
                    nkit.Gadget.update_page_property(page_object=self.page_object,
                                                     property_name=name,
                                                     **{self.property_dict[name]: value}
                                                     )
            # Update the page
            self.__request__()
        
    def update(self, value:int=1, **kwargs)->None:
        # Update
        self.value += value
        nkit.Gadget.update_page_property(page_object=self.page_object,
                                         property_name="Value",
                                         number=self.value)
        # Set status
        if self.value >= 1:
            self.change_status(status=self.STATUS_OPTIONS[2])
        elif self.value >= self.total:
            self.change_status(status=self.STATUS_OPTIONS[3])
            
        if kwargs:
            for name, value in kwargs.items():
                if name in list(self.property_dict.keys()):
                    nkit.Gadget.update_page_property(page_object=self.page_object,
                                                     property_name=name,
                                                     **{self.property_dict[name]: value}
                                                     )
        # Update the page
        self.__request__()
       