from notion_kit import kit as nkit

def get_object(value:str | bool, type:str):
    """
    Get the object
    Support 'Rich Text', 'Select' type.
    
    Parameters
        value:      (str | bool)    - The value of the object.
        type:       (str)           - The type of the object.
        
    Returns
        notion_object:  (NotionObject) - The object.
    """
    
    if type == 'rich_text':
        return [nkit.Gadget.Object.get_rich_text(text=value)]
    elif type == 'select':
        return nkit.Gadget.Object.get_option(name=value)
    else:
        ValueError(f"Type {type} is not supported.")