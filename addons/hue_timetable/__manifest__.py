{
    'name': 'HUE Timetable',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Adding Horus Timetable ',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base', 'web', 'openeducat_timetable', 'HUE_openeducat_core', 'calendar'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/op_session.xml',
        'views/gen_timetable.xml',
        'views/op_session_registration.xml',
        'views/op_session_registration_enrollment.xml',
        'views/timetable_student_ext.xml',
        'views/timing.xml',
        'menus/timetable_menu.xml',
        'wizard/timetable_wizard_view.xml',
        'report/timetable_report_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hue_timetable/static/src/js/red_text_js_action.js',
            'hue_timetable/static/src/js/red_text_js_action_template.xml',
        ],
        # 'hue_timetable.assets_public_timetable': [
            
        # ],
    },

    'installable': True,
    'auto_install': False,
    'application': True,
}
