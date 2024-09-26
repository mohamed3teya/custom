{
    'name': 'HUE Alumni',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Horus Alumni',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base','openeducat_core','HUE_openeducat_core'],
    
    'data': [
        'views/alumni_students.xml',
        'views/intern_student.xml',
        'views/training_places.xml',
        'views/graduation_project.xml',
        'views/intern_department.xml',
        'menus/alumni_menu.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
