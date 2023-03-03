from notion_kit import kit as nkit
from notion_kit import object as nobj

from notion_pbar.push_api import PushProcess
from notion_pbar.process_bar import ProcessBar

from pprint import pprint

class NotionProcessBar:
    @classmethod
    def Client(cls, token:str, database_url:str, interval:int=1)->None:
        cls.client = nkit.Client(token=token)
        cls.interval = interval
        
        # Get database data
        cls.database_id = nkit.get_id(database_url)
        database_object = nkit.Database.get_data(cls.database_id)
        ## Get database properties
        cls.property_dict = {} # {name:type}
        for name, property_type_object in database_object.properties.items():
            cls.property_dict.update({name: property_type_object})
        
        # Init push process
        cls.push_process = PushProcess(token=token, interval=interval)
     
    @classmethod
    def close(cls)->None:
        cls.push_process.close()
    
    @classmethod
    def set_pbar(cls, total:int, name:str="", **kwargs):
        """
        Set a process bar.
        
        Parameters
            total:  (int)   - The total of the process bar.
            name:   (str)   - The name of the process bar. [default: "Process Bar"]
            kwargs: (dict)  - The init properties of the process bar.
                              [default: {}]
        Return
            pbar:   (pbar) - The process bar object.
        """
        # Check total
        if type(total) == range or type(total) == list:
            total = len(total)
        elif type(total) == int:
            total = total
        else:
            raise TypeError("total should be range, list or int")
        
        # if name is "", will use "Process Bar"
        name = name if name else "Process Bar"
        
        # Check icon
        icon = None
        if 'icon' in kwargs:
            icon = kwargs.pop('icon')
            if type(kwargs['icon']) is nobj.Icon:
                icon = kwargs['icon']
            elif type(kwargs['icon']) is str:
                icon = nobj.Icon(emoji=kwargs['icon'])
            else:
                icon = None
        
        # Create page process
        init_properties_dict = {"Total": nobj.PropertyItem(type="number", number=total),
                                "Value": nobj.PropertyItem(type="number", number=0),
                                }
        
        ## Check init properties is in property_dict?
        if kwargs:
            for name, value in kwargs.items():
                if name in list(cls.property_dict.keys()):
                    init_properties_dict.update({name: nobj.PropertyItem(type=cls.property_dict[name],
                                                                        **{cls.property_dict[name]: value}
                                                                        )}
                                                )
        ## Create page
        page_object = nkit.Page.create_in_database(parent_database_id=cls.database_id,
                                                    title=nkit.Gadget.Object.get_rich_text(name),
                                                    properties_item_dict=init_properties_dict,
                                                    icon=icon
                                                    )
        # Return process bar class
        return ProcessBar(page_object=page_object,
                          total=total, name=name,
                          property_dict=cls.property_dict,
                          request_method=cls.push_process.request)
