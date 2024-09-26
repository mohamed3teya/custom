{
    'name': 'HUE Credit Hours',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 2,
    'summary': 'Horus Credit Hours',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base', 'openeducat_core', 'HUE_openeducat_core'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/course_assessment_degrees.xml',
        'views/student_accumlative_semesters.xml',
        'views/subject_ext.xml',
        'views/student_accumulative.xml',
        'views/subject_department.xml',
        'menus/credit_menu.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
