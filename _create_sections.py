import json

import math

def HSS(height:float, width:float,element_id:int):
    '''
    we start with just a recntular secntion
    '''

    schema = {"element_id":element_id,
                "polygon" : [{"x":-width/2,"y": height/2},
                            {"x":width/2,"y": height/2},
                            {"x":width/2,"y": -height/2},
                            {"x":-width/2,"y": -height/2}
                            ],
                "type": "HSS"
            } 
    return schema

def CHS(radius: float, element_id: int):
    '''
    Create a circular section
    '''

    schema = {
        "element_id": element_id,
        "polygon": [],
        "type": "CHS"
    }

    num_points = 100  # Number of points to approximate the circle

    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        schema["polygon"].append({"x": x, "y": y})

    return schema

def I_section(height:float, width:float, flange_thick:float, web_thick:float, element_id:int):
    '''
    Create an I section
    '''

    schema = {"element_id":element_id,
                "polygon" : [{"x":-width/2,"y": height/2},
                            {"x":width/2,"y": height/2},
                            {"x":width/2,"y": height/2 - flange_thick},
                            {"x":web_thick/2, "y": height/2 - flange_thick},
                            {"x":web_thick/2, "y": -height/2 + flange_thick},
                            {"x":width/2, "y": -height/2 + flange_thick},
                            {"x":width/2, "y": -height/2},
                            {"x":-width/2,"y": -height/2}
                            ],
                "type": "I_section"  
            } 
    return schema

list_of_sections = [
    HSS(101.6, 101.6, 1), 
    HSS(101.6, 101.6, 2)    ,
    CHS(355/2, 3),
    I_section(180, 180, 12, 12, 4),
    I_section(350, 350, 12, 12, 5)

]

with open('data/cross_section.json', 'w') as file:
    json.dump(list_of_sections, file)