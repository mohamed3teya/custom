{
    'name': 'HUE Advising',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 2,
    'summary': 'Horus Credit Hours',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base',  'HUE_openeducat_core', 'hue_credit',],
    
    'data': [
        'security/ir.model.access.csv',
        'views/gpa_calculator_template.xml',
        'views/academic_direction.xml',
        'views/Academic_directions_core.xml',
        'views/student_without_advisor.xml',
        'views/transferred_advisor.xml',
        'views/gpa_calculator.xml',
        'views/advisor_students.xml',
        'menus/advising_menu.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
