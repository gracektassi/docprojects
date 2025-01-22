# -*- coding: utf-8 -*- 
{
    "name":"AV Project",
    "summary":"Virunga Alliance  Project",
    "version":"17.0.1.0.0",
    'description': 'Virunga Alliance Trip log',
    'author': 'Virunga Foundation',
    "license":"OPL-1",
    "depends":["base", "project", "purchase","hr" ],
    "application":False,
    "data": [
     # Security
       "security/res_groups.xml",
       "security/ir.model.access.csv",
     # "security/ir_rules.xml",

     #Views
        "views/docproject_project_views.xml",
        "views/docpurchase_order_views.xml",

        #Data    
        #menu 
        "views/docproject_menu.xml",
    ],



    "installable": True
}
