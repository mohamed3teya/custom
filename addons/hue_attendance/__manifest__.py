{
    'name': 'HUE Attendance',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 2,
    'summary': 'Horus Attendance',
    'complexity': "easy",
    'author': 'HUE',
    
    'depends': ['base','web','openeducat_core','openeducat_attendance', 'hr_attendance'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_sheet.xml',
        'views/global_leaves.xml',
        'views/student_leaves.xml',
        'views/student_disciplinary.xml',
        'report/attendance_pivot_report.xml',
        'menus/attendance_menu.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'hue_attendance/static/src/**/*',
            'hue_attendance/static/src/js/student_attendance.js',
        ],

        'hue_attendance.assets_public_attendance': [
            # Front-end libraries
            ('include', 'web._assets_helpers'),
            ('include', 'web._assets_frontend_helpers'),
            'web/static/lib/jquery/jquery.js',
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap_frontend'),
            ('include', 'web._assets_bootstrap_backend'),
            '/web/static/lib/odoo_ui_icons/*',
            '/web/static/lib/bootstrap/scss/_functions.scss',
            '/web/static/lib/bootstrap/scss/_mixins.scss',
            '/web/static/lib/bootstrap/scss/utilities/_api.scss',
            'web/static/src/libs/fontawesome/css/font-awesome.css',
            ('include', 'web._assets_core'),

            # Public Kiosk app and its components
            "hue_attendance/static/src/public_kiosk/**/*",
            "hue_attendance/static/src/hr_attendance.scss",
            'hue_attendance/static/src/components/**/*',
            'hue_attendance/static/src/js/barcode_template.xml',
            "web/static/src/views/fields/formatters.js",

            # Barcode reader utils
            "web/static/src/webclient/barcode/barcode_scanner.js",
            "web/static/src/webclient/barcode/barcode_scanner.xml",
            "web/static/src/webclient/barcode/barcode_scanner.scss",
            "web/static/src/webclient/barcode/crop_overlay.js",
            "web/static/src/webclient/webclient_layout.scss",
            "web/static/src/webclient/barcode/crop_overlay.xml",
            "web/static/src/webclient/barcode/crop_overlay.scss",
            "web/static/src/webclient/barcode/ZXingBarcodeDetector.js",
            "barcodes/static/src/components/barcode_scanner.js",
            "barcodes/static/src/components/barcode_scanner.xml",
            "barcodes/static/src/components/barcode_scanner.scss",
            "barcodes/static/src/barcode_service.js",

            # Kanban view mock
            "web/static/src/views/kanban/kanban_controller.scss",
            "web/static/src/search/search_panel/search_panel.scss",
            "web/static/src/search/control_panel/control_panel.scss",
        ],
    },
    
    'installable': True,
    'auto_install': False,
    'application': True,
}