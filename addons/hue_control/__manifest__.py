{
    'name': 'HUE Control',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 2,
    'summary': 'Horus Control Management',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base','openeducat_core','HUE_openeducat_core', 'hue_advising'],
    
    'data': [
        'views/subjects_control_security.xml',
        'views/subject_control.xml',
        'views/student_semesters_subjects.xml',
        'views/students_subject_control.xml',
        'menus/control_menu.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
