import validators #for checking url and email 
from datetime import datetime
from flask import g
class Field(object):
    ''' object after parsing a tsv file '''
    
    
    def __init__(self, target_key, multiple, type_class, parent, metadata_block):
        ''' Constructor '''
        self.target_key = target_key
        self.controlled_vocabulary = []
        self.multiple = (multiple == 'TRUE')
        self.type_class = type_class
        self.parent = parent
        self.metadata_block = metadata_block
        
        
    def __repr__(self):
        return "{multiple: " + str(self.multiple) + ", type class: " + self.type_class + ", parent: " + str(self.parent) + ", metadata block: " + self.metadata_block + ", controlled Vocabulary: " + str(self.controlled_vocabulary) +"}"
        
        
    def set_controlled_vocabulary(self, controlled_vocabulary):
        self.controlled_vocabulary.append(controlled_vocabulary)


    def check_value(self, values):
        if(not isinstance(values, list)):
            values = [values]
        valid = True
        for value in values:
            if self.type_class == "url":
                valid = valid and validators.url(value)

            elif self.type_class == "email":
                valid = valid and validators.email(value)

            elif self.type_class == "date":
                format_d = "%d-%m-%Y"
                try:
                    res = bool(datetime.strptime(value, format))
                    valid = valid and True
                except ValueError:
                    res=False    
                    valid = False

            elif self.type_class == "int":
                valid = valid and isinstance(value, int)

            elif self.type_class == "float":
                valid = valid and isinstance(value, float)

            elif self.type_class == "none":
                valid = valid and value is None

            elif self.type_class == "text":
                if not isinstance(value, str):
                    valid = False
                else:
                    if '\n' in value:
                        value.replace('\n', ' ')
                    valid = valid and True
        return valid        
    
        
    def check_controlled_vocabulary(self, v):     
        """ Checks value v against controlled_vocabulary list. 
        
        Returns v if it is in controlled_vocabulary, else []. Ignores 'none' values.
        
        Parameters
        ---------
        v : str
        
        Returns
        ---------
        v : str or []
        """
        if len(v) > 1:      # case multiple values
            v_new = []
            for value_ in v:
                if value_ in self.controlled_vocabulary:
                    v_new.append(value_)
                elif value_ != 'none':
                    g.warnings.append(self.target_key + " has a controlled vocabulary. " + value_ + " is not part of it. It has been removed. Allowed values are: " + str(self.controlled_vocabulary))
                else:    
                    continue
            return v_new
        else:               
            v = v[0]
            if v in self.controlled_vocabulary:      
                return v
            elif v != 'none':
                g.warnings.append(self.target_key + " has a controlled vocabulary. " + v +" is not part of it. It has been removed. Allowed values are: " + str(self.controlled_vocabulary))
                return []
            else:
                return []
    