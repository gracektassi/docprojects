# -*- coding: utf-8 -*-
{
    "name": "AV Project",
    "summary": "Virunga Alliance  Project",
    "version": "17.0.1.0.0",
    "description": "Virunga Alliance",
    "author": "Virunga Foundation",
    "license": "OPL-1",
    "depends": ["base", "project", "hr"],
    "application": False,
    "data": [
        # Security
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        # "security/ir_rules.xml",
        # Views
        "views/project_views.xml",
        # Data
        # menu
        "views/project_menu.xml",
    ],
    "installable": True,
}
