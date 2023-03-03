from notion_kit import kit as nkit
from notion_kit import object as nobj

from notion_pbar.push_api import PushProcess
from notion_pbar import gadget

from pprint import pprint

class ProcessBar:
    def __init__(self, 
                 page_object:nobj.Page,
                 total:int,
                 name:str, 
                 property_dict:dict[str, nobj.PropertyType],
                 request_method:PushProcess.request
                 ):
        self.page_object = page_object
        self.value = 0
        self.total = total
        self.name = name
        self.property_dict = property_dict
        # Get Status options dict
        self.STATUS_OPTIONS = {}
        for option in property_dict['Status'].Dict['status']['options']:
            self.STATUS_OPTIONS.update({option['name']: nobj.Option(**option)})
            
        self.__request_method = request_method
    
    def __status_check(self)->None:
        if self.value > self.total:
            self.change_status(status=self.STATUS_OPTIONS['Error'])
            
    def __request__(self)->None:
        self.__status_check()
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
    
    def change_status(self, status:nobj.Option)->None:
        nkit.Gadget.update_page_property(page_object=self.page_object,
                                         property_name="Status",
                                         status=status.Dict)

    def reset(self)->None:
        self.value = 0
        nkit.Gadget.update_page_property(page_object=self.page_object,
                                         property_name="Value",
                                         number=self.value)
        self.__request__()
    
    #-----------------[ Update property ]-----------------#
    def update_name(self, new_name:str)->None:
        self.page_object.update_title(nkit.Gadget.Object.get_rich_text(text=new_name))
        
    def update_property(self, **kwargs)->None:
        """
        Update the properties of the process bar.
        Only sūpport 'Rich Text', 'Select' and 'Checkbox' type.
        """
        if kwargs:
            for property_name, property_value in kwargs.items():
                # check property is exist or not
                if property_name in list(self.property_dict.keys()):
                    property_type = self.property_dict[property_name].Dict['type']
                    if property_type != 'checkbox':
                        property_value = gadget.get_object(value=property_value, type=property_type)
                    nkit.Gadget.update_page_property(self.page_object,
                                                     property_name,
                                                     **{property_type:property_value}
                                                     )
                else:
                    ValueError(f"Property {property_name} is not exist.")
            # Update the page
            self.__request__()

    def update_checkbox(self, name:str, check:bool)->None:
        if name in list(self.property_dict.keys()):
            nkit.Gadget.update_page_property(self.page_object,
                                            name,
                                            **{'checkbox':check}
                                            )
            # Update the page
            self.__request__()
        else:
            ValueError(f"Property {name} is not exist.")

    def update_rich_text(self, name:str, 
                         text:str="",
                         rich_text_object:nobj.RichText | None = None)->None:
        if name in list(self.property_dict.keys()):
            if rich_text_object is not None:
                rich_text_object = rich_text_object
            else:
                rich_text_object = nkit.Gadget.Object.get_rich_text(text=text)
            nkit.Gadget.update_page_property(self.page_object,
                                            name,
                                            **{'rich_text':[rich_text_object]}
                                            )
            # Update the page
            self.__request__()
        else:
            ValueError(f"Property {name} is not exist.")
            
    def update_select(self, name:str,
                      option:nobj.Option | str,
                      color:str="defalut")->None:
        if name in list(self.property_dict.keys()):
            if type(option) == str:
                option_object = nkit.Gadget.Object.get_option(name=option, color=color)
            else:
                option_object = option
            nkit.Gadget.update_page_property(self.page_object,
                                            name,
                                            **{'select':option_object}
                                            )
            # Update the page
            self.__request__()
        else:
            ValueError(f"Property {name} is not exist.")
    
    def update(self, value:int=1, **kwargs)->None:
        # Update
        self.value += value
        nkit.Gadget.update_page_property(page_object=self.page_object,
                                         property_name="Value",
                                         number=self.value)
        # Set status
        if self.value == self.total:
            self.change_status(status=self.STATUS_OPTIONS['Done'])
        elif self.value >= 1:
            self.change_status(status=self.STATUS_OPTIONS['In progress'])
        
        if kwargs:
            for name, value in kwargs.items():
                if name in list(self.property_dict.keys()):
                    nkit.Gadget.update_page_property(page_object=self.page_object,
                                                     property_name=name,
                                                     **{self.property_dict[name]: value}
                                                     )
        # Update the page
        self.__request__()

    #-----------------[ Add Block ]-----------------#
