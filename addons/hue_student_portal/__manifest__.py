# -*- coding: utf-8 -*-
{
    'name': "HUE Student Portal",

    'summary': """
        HUE Student Portal""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HUE IT",
    'website': "http://www.hours.edu.eg",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HUE',
    'sequence': 2,
    'version': '17.0.1.0',
    'license': 'AGPL-3',
    'author': 'HUE IT',
    # any module necessary for this one to work correctly
    'depends': ['base'],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
            'hue_student_portal/static/front/plugins/iCheck/all.css',
            'hue_student_portal/static/src/js/jquery.js',
            'hue_student_portal/static/src/js/zoomodoo.js',
        ],
    },
    # always loaded
    'data': [
        'views/container.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}