# -*- coding: utf-8 -*-
{
    "name": "AV Purchase",
    "summary": "Virunga Alliance  Project",
    "version": "17.0.1.0.0",
    "description": "Virunga Alliance",
    "author": "Virunga Foundation",
    "license": "OPL-1",
    "depends": ["base", "purchase", "hr","av_project"],
    "application": False,
    "data": [
        # Security
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        # "security/ir_rules.xml",
        # Views
        "views/purchase_views.xml",
        # Data
        # menu
        "views/purchase_menu.xml",
    ],
    "installable": True,
}
