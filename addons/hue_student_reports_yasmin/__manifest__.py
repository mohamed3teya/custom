{
    'name': 'HUE Student Reports y',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Generate Student Reports',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base','HUE_openeducat_core'],
    
    'data': [
        'wizard/military_education_students.xml',
        'wizard/military_recruitment_data_wizard.xml',
        'wizard/student_password_wizard.xml',
        'report/military_education_student_view.xml',
        'report/military_recruitment_data_view.xml',
        'report/student_password_view.xml',
        'menu/report_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': True,
}
