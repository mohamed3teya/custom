{
    'name': 'HUE Exam',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 2,
    'summary': 'Horus Exam',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base','openeducat_core','openeducat_exam'],
    
    'data': [
        'views/class_room.xml',
        'views/online_exam_result.xml',
        'views/student_online_exam_result.xml',
        'views/hue_exam.xml',
        'views/hue_exam_attendees.xml',
        'menus/exam_menu.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
