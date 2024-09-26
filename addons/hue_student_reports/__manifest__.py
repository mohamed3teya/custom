{
    'name': 'HUE Student Reports',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Generate Student Reports',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base','HUE_openeducat_core'],
    
    'data': [
        'views/student_progress_report_stu_template.xml',
        'views/transcript_report_template.xml',
        'views/transcript_report2_template.xml',
        'views/report_student_level_statistics_template.xml',
        'views/report_regular_students_template.xml',
        'views/student_gpa_debug_reports_template.xml',
        'views/student_registration_reports_template.xml',
        'views/student_exam_report_template.xml',
        'views/subject_result_report_template.xml',
        'views/student_attendance_report.xml',
        'views/report_actions.xml',
        'views/advisor_students.xml',
        'views/student_internal_buttons_action.xml',
        'views/transcript_action.xml',
        'wizard/transcript_wizard.xml',
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
