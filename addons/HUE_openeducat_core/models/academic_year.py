from odoo import models, fields
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AcademicYear(models.Model):
    _inherit = 'op.academic.year'
    _order = "year desc"
    
    join_year = fields.Many2one('hue.joining.years', string="Join Year")
    faculty = fields.Many2one('hue.faculties', string="Faculties")
    course_id = fields.Many2one('op.course', string="Course")
    student_id = fields.Many2one('op.student', string="Students")
    year = fields.Selection([(str(num), str(num)) for num in range(2015, (datetime.now().year)+1 )])
    sequence = fields.Integer(default=False)
    current = fields.Boolean(default=False)
    timetable_current = fields.Boolean(string="Timetable Current")
    gpa_current = fields.Boolean(string="GPA Current",default=False)
    run_semester_gpa = fields.Boolean(string="Run semester gpa",default=False)
    year_code = fields.Integer(string="year code")
    active_year = fields.Boolean(string='Active Year')
    invoice_date = fields.Date()
    
    
    def generate_invoices_discount(self):
        product = self.env['product.product']
        
        inv_product = product.sudo().search([('id', '=', 9954)])
        account_id = False
        if inv_product.id:
            account_id = inv_product.property_account_income_id.id
        if not account_id:
            account_id = inv_product.categ_id.property_account_income_categ_id.id
        sql = ("select distinct aa.id inv_id , bb.price_unit price , aa.partner_id from account_invoice aa inner join account_invoice_line bb \n"
                + " on aa.id = bb.invoice_id \n"
                + " where aa.academic_year = 69536 and aa.academic_term in (26,27)  \n"
                + " and aa.invoice_type = 'regular' and aa.move_type = 'out_invoice' and aa.state != 'cancel' \n"
                + " and bb.name = 'الزيادة السنوية لعام 2023/2024' and aa.faculty = 12 ")
        
        self.env.cr.execute(sql)
        allinvoices = self.env.cr.dictfetchall()
        students = []
        print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')
        count = 0
        for invoice in allinvoices:
            count = count+1
            print(count)
            print('count................................')
            _logger.info('--------------------------------------------------')
            _logger.info(count)
            _logger.info('--------------------------------------------------')
            student = self.env['op.student'].search([('partner_id','=', invoice['partner_id'] )])
            print(invoice['inv_id'])
            students_invoices = self.env['account.move'].search([('id','=', invoice['inv_id'] )])
            # print(invoice['inv_id'])
            credit_note_data = self.env['account.move'].sudo().create({
                            'academic_term':students_invoices.academic_term.id,
                            'origin':students_invoices.number,
                            'notes': 'Increase Discount 2024',
                            'invoice_type':'regular',
                            'currency_id' : students_invoices.currency_id.id,
                            'id' : students_invoices.id,
                            'move_type': 'out_refund',
                            # 'account_id': partner_id.property_account_receivable_id.id,
                            'ref': False,
                            'faculty':student.faculty.id,
                            'student_code':student.student_code,
                            'academic_year':students_invoices.academic_year.id,
                            'invoice_date_due': students_invoices.date_due,
                            'date_invoice':students_invoices.date_due,
                            'partner_id':student.partner_id.id,
                            'state': 'draft'
                            })
            
            if students_invoices:
                print('11111111111111111111111111111111')
                print(student.scholarship)
                if student.scholarship == 100:
                    continue
                if student.scholarship:
                    print('2222222222222222222222')
                    price_unit = invoice['price'] / 2
                    percent = 100 - int(student.scholarship)
                    price_unit = price_unit * percent  / 100
                else:
                    print('333333333333333333333')
                    price_unit = invoice['price'] / 2
                    
                invoice_line_data = self.env['account.move.line'].sudo().create({
                'name': inv_product.name,
                'account_id': account_id,
                'price_unit': price_unit,
                'quantity': 1,
                'move_id': credit_note_data.id,
                'product_id': inv_product.id
                })
                
            students_invoices.write({'name':inv_product.name})
            credit_note_data.action_post()
            
            credit_notes = self.env['account.move'].search([('origin', '=', students_invoices.number)])
            credit_note_ids = []
            for cr in credit_notes:
                credit_note_ids.append(cr.id)
                
            domain = [('id', 'in', credit_note_ids),('account_id', '=', students_invoices.account_id.id), ('partner_id', '=', students_invoices.env['res.partner']._find_accounting_partner(students_invoices.partner_id).id), ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0)]
            if students_invoices.move_type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': students_invoices.id}
            lines = students_invoices.env['account.move.line'].search(domain)
            currency_id = students_invoices.currency_id
            
            if len(lines) != 0:
                for line in lines:
                    self.assign_outstanding_credit(line.id,students_invoices)
    
    
    def generate_invoices_gpa(self):
        financial_years = self.env['hue.years']
        hue_installments = self.env['hue.installments']
        product = self.env['product.product']		
        invoice = self.env['account.move']
        invoice_line = self.env['account.move.line']
        student_status = self.env['hue.student.status']
        terms = self.env['op.academic.term']
        increase_years = self.env['hue.years.increase']
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        jointerm2 = self.env['op.student'].search([('join_year', '=', 69533),('join_term', '=', 2)]).ids
        print('jointerm2jointerm2jointerm2jointerm2')
        print(jointerm2)
        students_gpa = self.env['op.student.accumlative.semesters'].search([('course_id','!=',15),('student_id','not in',jointerm2)
            # ,('student_id','in',(6330,3260,3302,3452,5069,5839,5569,3925,2899,5696,2570,3195,3152,2491,3661,2810,4439,4460,3935,2586,2889,2670,2777,2372,2746,2628,3074,2936,3084,2784,3202,2854,2388,3844,2337,2376,2355,2338,2381,2395,2368,2366,2349,2392,2390,2504,2493,2498,2706,2357,2954,3151,3139,2540,2553,2542,2555,2557,2580,2572,2596,2585,2600,2588,2627,2619,2641,2634,2645,2680,2683,2698,3986,2682,2719,2725,2734,2715,2360,3163,2928,2749,2738,2742,2745,2773,2781,2743,2785,2793,2801,2803,2808,2812,2825,2827,2844,3879,2850,2849,4849,2859,2320,3117,2945,5830,6054,3043,3359,2704,2720,2515,4635,2875,3101,3045,4104,3300,2883,2888,3123,4892,3495,2897,2821,2901,5122,4704,4808,2903,2904,2314,5118,3427,2914,3467,4584,3936,2917,4802,4938,3247,3509,2831,3843,5000,2921,3407,4008,2922,5248,2571,5087,5877,2929,5097,5921,2930,5304,3782,4924,5526,2296,2613,2310,2306,4581,4785,2934,2778,4455,4887,3454,2819,4868,3271,5035,2624,3313,3239,4903,6165,5895,5583,3307,4273,4640,5916,4038,2332,4690,3397,3569,3403,2939,4429,4410,2327,4850,2961,2940,2958,2963,3923,5186,2973,2971,4153,2988,3009,3004,4872,3458,5713,5036,3956,4783,3056,4661,5126,3065,3061,3066,3067,5030,5235,5534,3068,4786,2335,4962,5023,3069,3071,3078,3077,3098,3072,3091,3093,3109,3095,3097,3114,3178,3168,3177,3171,3228,3182,3193,3223,3246,3255,3250,3261,3270,3243,3285,3235,3282,3298,2633,3319,3350,2871,3297,5059,2995,3357,2527,5896,2947,3614,2519,2599,4796,3413,5019,3515,2607,3739,3516,4446,4934,4772,2911,5827,3517,3544,3561,3425,3805,4680,3702,3821,3679,3845,3812,3824,3291,4370,5110,2305,4058,3954,3881,4259,3960,3969,3941,3149,2533,2661,3466,3447,4070,6148,5922,4406,4223,4260,4481,4412,2329,4463,2322,3818,5929,4985,2333,2545,2518,2601,2731,4313,2782,2758,3142,2838,3281,3258,3269,3402,3322,4878,5085,3484,3430,2318,3808,3489,3533,3928,5075,3958,3967,3119,3580,4034,2324,3415,5038,2552,3277,4844,4278,4419,3197,4679,4686,3232,4713,3283,4023,4851,4879,5240,5810,6084,4729,2517,5084,3717,5037,5127,3103,3200,2783,4682,3367,4980,5520,4108,2711,4078,2705,4130,3146,2344,3111,2399,4816,4928,2979,2721,2595,2671,2393,6179,2676,5533,3189,2369,5787,2593,3948,2942,2779,5708,3154,3274,5950,4797,5941,4855,3977,2754,4182,3934,3817,5368,5674,3480,3395,4538,5081,3826,3125,4964,3538,4756,6224,3040,2924,5799,5604,4810,3263,3344,4712,5956,4699,3337,4731,4992,4009,5086,2689,2608,2330,2334,3021,3381,4624,4559,6354,6011,3073,2830,3315,4571,2640,4829,3001,5041,4035,4312,3872,3947,2814,5749,5090,2513,4705,2441,2437,5539,2811,3488,3135,4911,3377,5039,3873,6183,5490,5182,5614,5901,4599,5935,5278,5184,4724,5421,5013,4912,4753,5070,5663,4801,5169,4994,5881,4737,4691,4586,4747,5364,5103,5688,5834,4798,5617,5913,5281,4563,5261,4906,5620,5570,5217,5846,5412,5134,5721,5003,6081,5878,4758,5710,5185,4920,5778,5844,4545,6031,5605,5740,5042,4628,5876,5297,5602,6118,5818,5564,5159,5794,4852,5919,5647,5298,4820,5861,5202,5691,5594,4626,4905,5823,5874,5271,5287,5781,5584,5237,4623,5931,5927,5616,4549,5123,4605,4740,5632,6329,4936,5249,5029,3469,2880,3133,5032,3391,5686,4125,5676,2952,5678,3267,5130,3320,3968,5745,2766,3299,4256,4570,2957,3950,4537,6045,4503,2822,5094,3309,3272,2420,3041,2728,3248,3325,2520,3863,3705,4280,3828,3434,3514,3227,2796,3971,3394,4398,3335,3187,4055,3330,2427,3208,3816,2868,3479,2638,3980,2445,2413,3400,3374,3328,3156,2727,4103,3058,3428,3356,2780,3160,3052,3505,3440,3100,2775,3063,3191,3090,3866,2885,2955,2510,4414,3406,2804,3362,2525,2959,3500,2526,3387,4594,2818,4018,3099,3943,3390,2894,3473,3965,4804,2616,2707,3275,3278,3450,2665,2584,2446,3310,2559,2693,2631,2768,6217,4662,3961,4706,2386,4733,4762,4961,5560,3306,5599,5693,5754,2864,5772,3106,3924,4677,4697,2431,2722,3438,2450,2953,4908,4720,4660,4806,5254,5697,4799,4719,2753,5829,5143))
            ,('student_id','in',(9372,9127,9012,9320,9209,9054,9376,8945,9833,9279,9908,9043,9032,9619,8762,10140))
            ,('current_gpa','>=',3.5),('academicyear_id', '=', 69533),('semester_id', '=', 2),('semester_status', '=', 2),('transferred', '=', False)])
        
        # print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
        print(len(students_gpa))
        print("ddddddddddd22222222222222222222222222222222222222")
        #print(students)
        for student in students_gpa:
            print("ddddddddddd22222222222222222222222222222222222222")
            std_join_year = student.student_id.join_year.id
            std_year = student.student_id.year
            std_faculty_id = student.student_id.faculty.id
            std_course_id = student.student_id.course_id.id
            std_id = student.student_id.id
            std_code = student.student_id.student_code
            partner_id =  student.student_id.partner_id
            join_year  = student.student_id.join_year.id
            student_data_status_id  = student.student_id.student_status.id
            student_student_nationality_id  = student.student_id.student_nationality.id
            student_scholarship  = student.student_id.scholarship
            brother_discount = student.student_id.brother_discount
            print("TTTTTTTTTTTTTTTTTT")
            print(student.student_id.student_nationality.foreign_nationality)
            
            students_invoices = invoice.search([('partner_id','=',partner_id.id)
                ,('academic_year', '=', 69535),('academic_term', '=', 24)
                ,('move_type','=','out_invoice'),('invoice_type','=','regular')],limit=1)
            credit_n = invoice.search([('partner_id','=',partner_id.id)
                ,('academic_year', '=', 69535),('move_type','=','out_refund'),('invoice_type','=','regular')],limit=1)
            print("TTTTTTTTccccccccccccccccccccccccTTTTTTTTTT")
            print(credit_n)
            # and not credit_n
            if student.current_gpa >= 3.5 and student.current_gpa < 4.1  :
                discounts = self.env['hue.discounts'].sudo().search([('cgpa_from', '<=', student.current_gpa),
                    ('cgpa_to', '>=',student.current_gpa)])
                print('AAAAAAAAAAACCCCCCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDDD')
                print(students_invoices.id)
                print(discounts.id)
                print('AAAAAAAAAAACCCCCCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDDD')
                inv_product = product.sudo().search([('discount_id', '=', discounts.id)],limit=1)
                print(inv_product)
                print('111111222223333333344444444445555555555')
                account_id = False
                if inv_product.id:
                    account_id = inv_product.property_account_income_id.id
                if not account_id:
                    account_id = inv_product.categ_id.property_account_income_categ_id.id
                if not account_id:
                    continue
                    raise UserError(
                        _('There is no income account defined for this product: "%s". \
                            You may have to install a chart of account from Accounting \
                            app, settings menu.') % (std_id,))
                
                if account_id != False:
                    financial_year = financial_years.search([('join_year', '=', join_year),('scholarship', '=', False),('course_id', '=',student.student_id.course_id.id), ('faculty', '=', std_faculty_id)],limit=1)
                    if not financial_year:
                        financial_year = financial_years.search(
                            [('join_year', '=', join_year), ('course_id', '=', False),('scholarship', '=', False),
                                ('faculty', '=', std_faculty_id)], limit=1)
                    total_amount = 0
                    if financial_year:
                        #check student nationality
                        if student.student_id.student_nationality.foreign_nationality :
                            total_amount = financial_year.total_dollar
                        else:
                            total_amount = financial_year.total
                            
                    price_unit = total_amount * (discounts.discount_rate/100)
                    print('AAAAAAAAAAQQQQQQQQQQQQEEEEEEEEEEEEERRRRRRRRRRRRRRRRR')
                    if student_data_status_id == 2 and student_scholarship == False : #and brother_discount == False
                        print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
                        print(students_invoices.id)
                        
                        credit_note_data = invoice.sudo().create({
                            'academic_term':students_invoices.academic_term.id,
                            'origin':students_invoices.number,
                            'notes': 'GPA Discount 2023',
                            'invoice_type':'regular',
                            'currency_id' : students_invoices.currency_id.id,
                            'id' : students_invoices.id,
                            'move_type': 'out_refund',
                            'account_id': partner_id.property_account_receivable_id.id,
                            'ref': False,
                            'faculty':std_faculty_id,
                            'student_code':std_code,
                            'academic_year':students_invoices.academic_year.id,
                            'invoice_date_due': students_invoices.date_due,
                            'date_invoice':students_invoices.date_due,
                            'partner_id':partner_id.id,
                            'state': 'draft'
                            })
                        if students_invoices:
                            # price_unit = product_data.list_price / invoices_data_count
                            invoice_line_data = invoice_line.sudo().create({
                            'name': inv_product.name,
                            'account_id': account_id,
                            'price_unit': price_unit,
                            'quantity': 1,
                            'move_id': credit_note_data.id,
                            'product_id': inv_product.id
                            })
                            
                        students_invoices.write({'name':inv_product.name})
                        
                        credit_note_data.action_post()
                        
                        credit_notes = self.env['account.move'].search([('origin', '=', students_invoices.number)])
                        credit_note_ids = []
                        for cr in credit_notes:
                            credit_note_ids.append(cr.id)
                            
                        domain = [('id', 'in', credit_note_ids),('account_id', '=', students_invoices.account_id.id), ('partner_id', '=', students_invoices.env['res.partner']._find_accounting_partner(students_invoices.partner_id).id), ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0)]
                        if students_invoices.move_type in ('out_invoice', 'in_refund'):
                            domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                            type_payment = _('Outstanding credits')
                        else:
                            domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                            type_payment = _('Outstanding debits')
                        info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': students_invoices.id}
                        lines = students_invoices.env['account.move.line'].search(domain)
                        currency_id = students_invoices.currency_id
                        
                        if len(lines) != 0:
                            for line in lines:
                                self.assign_outstanding_credit(line.id,students_invoices)
                                
    def register_payment(self, payment_line ,inv_id = False, writeoff_acc_id=False, writeoff_journal_id=False ):
        """ Reconcile payable/receivable lines from the invoice with payment_line """
        line_to_reconcile = inv_id.env['account.move.line']
        for inv in inv_id:
            line_to_reconcile += inv.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)
    
    
    def assign_outstanding_credit(self, credit_aml_id , inv_id):
        inv_id.ensure_one()
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        if not credit_aml.currency_id and inv_id.currency_id != inv_id.company_id.currency_id:
            credit_aml.with_context(allow_amount_currency=True, check_move_validity=False).write({
                'amount_currency': inv_id.company_id.currency_id.with_context(date=credit_aml.date).compute(credit_aml.balance, inv_id.currency_id),
                'currency_id': inv_id.currency_id.id})
        if credit_aml.payment_id:
            credit_aml.payment_id.write({'invoice_line_ids': [(4, inv_id.id, None)]})
        return self.register_payment(credit_aml,inv_id)
    
    
    def generate_invoices(self):
        print('11111111111111122222222222222222223333333333333333')
        financial_years = self.env['hue.years']
        hue_installments = self.env['hue.installments']
        product = self.env['product.product']		
        invoice = self.env['account.move']
        invoice_line = self.env['account.move.line']
        student_status = self.env['hue.student.status']
        terms = self.env['op.academic.term']
        increase_years = self.env['hue.years.increase']
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        course_id = self.course_id.id
        faculty = self.faculty.id
        std = self.student_id
        joinyear = self.join_year.id
        print(joinyear)
        if joinyear:
            students = self.env['op.student'].search([('student_status','in',status_ids),('year', '<', self.year),('faculty', '=', faculty),('join_year', '=', joinyear)])
        elif std:
            students = self.env['op.student'].search([('id', '=', self.student_id.id)])
        elif course_id:
            students = self.env['op.student'].search([('student_status','in',status_ids),('year', '<', self.year),('course_id', '=', course_id)])
        elif faculty:
            students = self.env['op.student'].search([('student_status','in',status_ids),('year', '<', self.year),('faculty', '=', faculty)])
        else:
            students = self.env['op.student'].search([('student_status','in',status_ids),('year', '<', self.year)])
        print('13333333333333333344444444444444444444999999999999')
        for student in students:
            _logger.info('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            _logger.info(student.student_code)
            std_join_year = student.join_year.id
            std_year = student.year
            std_faculty_id = student.faculty.id
            std_course_id = student.course_id.id
            std_id = student.id
            std_code = student.student_code
            partner_id =  student.partner_id
            join_year  = student.join_year.id
            scholarship = student.scholarship
            student_data_status_id  = student.student_status.id
            mc = student.mc
            staff_dis = student.father_discount
            sibling_dis = student.brother_discount
            martyrs_dis = student.martyrs_discount
            syndicate_dis = student.syndicate_discount
            student_student_nationality_id  = student.student_nationality.id
            CertificatePercentage = student.percentage
            Certificate_id = student.student_certificates.id
            faculty_id_data = student.faculty.id
            NationalityID = student.student_nationality.id
            if scholarship == False:
                print('F1111111111111111')
                financial_year = financial_years.search([('join_year', '=', join_year), ('course_id', '=', student.course_id.id),('scholarship','=',False)], limit=1)
                if not financial_year:
                    financial_year = financial_years.search([('join_year', '=', join_year), ('faculty', '=', student.faculty.id),('scholarship','=',False)], limit=1)
            else:
                print('F22222222222222222')
                print(join_year)
                print(student.faculty.id)
                financial_year = financial_years.search([('join_year', '=', join_year), ('course_id', '=', student.course_id.id),('scholarship','=',True)], limit=1)
                if not financial_year:
                    print('F22222222222222222**************')
                    financial_year = financial_years.search([('join_year', '=', join_year), ('faculty', '=', student.faculty.id),('scholarship','=',True)], limit=1)
            print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
            print(financial_year)
            if financial_year:
                #check student nationality
                print(financial_year)
                if student.student_nationality.foreign_nationality :
                    installments = hue_installments.sudo().search([('years_id', '=', financial_year.id),('extra_inv', '=', True),('one_time', '=', False),('foreign_nationality','=',True)])
                    incease = increase_years.sudo().search([('year_id', '=', financial_year.id),('foreign_nationality','=',True)])
                else:
                    installments = hue_installments.sudo().search([('years_id', '=', financial_year.id),('extra_inv', '=', True),('one_time', '=', False),('foreign_nationality','=',False)])
                    incease = increase_years.sudo().search([('year_id', '=', financial_year.id),('foreign_nationality','=',False)])
                print('###########################wwwwwwwwwwwwwwwwqqqqqq###############')
                print(installments)
                for installment in installments:
                    print('##########################################')
                    print(installment)
                    global_term_id = installment.term_id.id
                    term_data = terms.sudo().search([('term_id','=',self.id), ('global_term_id','=', global_term_id)],limit=1)
                    from_date = term_data.from_date
                    to_date = term_data.from_date
                    name = term_data.name
                    currency = installment.currency
                    invoice_exist = invoice.sudo().search([
                        ('academic_term','=',term_data.id),
                        ('invoice_type','=','regular'),
                        ('move_type','=','out_invoice'),
                        ('faculty','=',std_faculty_id),
                        ('academic_year','=',self.id),
                        ('partner_id','=',partner_id.id),
                        ])
                    if invoice_exist:
                        break;
                    invoice_data = invoice.sudo().create({
                        'academic_term':term_data.id,
                        'notes':financial_year.notes,
                        'invoice_type':'regular',
                        'currency_id' : currency.id,
                        'account_id': partner_id.property_account_receivable_id.id,
                        'move_type': 'out_invoice',
                        'ref': False,
                        'faculty':std_faculty_id,
                        'student_code':std_code,
                        'academic_year':self.id,
                        'invoice_date_due':to_date,
                        'date_invoice':from_date,
                        'partner_id':partner_id.id,
                        'state': 'draft',
                        'dis_inv': installment.extra_inv
                        })
                    
                    inv_product = product.sudo().search([('installments_id', '=', installment.id)])
                    account_id = False
                    if inv_product.id:
                        account_id = inv_product.property_account_income_id.id
                    if not account_id:
                        account_id = inv_product.categ_id.property_account_income_categ_id.id
                    if not account_id:
                        raise UserError(
                            _('There is no income account defined for this product: "%s". \
                                You may have to install a chart of account from Accounting \
                                app, settings menu.') % (product.name,))                                
                    invoice_line_data = invoice_line.sudo().create({
                        'name':inv_product.name,
                        'account_id':account_id,
                        'price_unit':inv_product.list_price,
                        'quantity':1,
                        'move_id':invoice_data.id,
                        'product_id':inv_product.id
                        })
                    account_id = False
                    if incease:
                        for increase in incease:
                            if increase.id:
                                account_id = increase.property_account_income_id.id
                            if not account_id:
                                account_id = increase.categ_id.property_account_income_categ_id.id
                            if not account_id:
                                raise UserError(
                                    _('There is no income account defined for this product: "%s". \
                                        You may have to install a chart of account from Accounting \
                                        app, settings menu.') % (product.name,))                                
                            invoice_line_data = invoice_line.sudo().create({
                                'name':increase.name,
                                'account_id':account_id,
                                'price_unit':increase.list_price,
                                'quantity':1,
                                'move_id':invoice_data.id,
                                'product_id':increase.product_id.id
                                })
                            
                    invoice_data.action_post()
                    
                discounts_data = []
                print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
                print(joinyear)
                print(scholarship)
                if scholarship:
                    print('11111111111111111111')
                    discounts = self.env['hue.discounts'].sudo().search(
                    [('percentage_from', '<=', CertificatePercentage),
                     ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                     ('certificate_id', '=', Certificate_id),
                     ('join_year_id', '=', join_year), ('course_id', '=', student.course_id.id),
                     ('faculty_ids', '=', faculty_id_data),('scholarship','=',scholarship)])
                    print(discounts)
                    print('11111111111111111111')
                else:
                    print('22222222222222222222')
                    print(staff_dis)
                    print('mccccccccccccccccccccccccccccccc')
                    if mc:
                        print('11-----------------')
                        print(CertificatePercentage)
                        print(NationalityID)
                        print(Certificate_id)
                        print(joinyear)
                        print(student.course_id.id)
                        print(faculty_id_data)
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('mc', '=', 1), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', join_year), ('course_id', '=', student.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    elif staff_dis:
                        print('2-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('staff_discount', '=', True), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', join_year), ('course_id', '=', student.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    elif sibling_dis:
                        print('3-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('sibling_discount', '=', True), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', join_year), ('course_id', '=', student.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    elif martyrs_dis:
                        print('4-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('martyrs_discount', '=', True), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', join_year), ('course_id', '=', student.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    elif syndicate_dis:
                        print('5-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('syndicate_discount', '=', True), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', join_year), ('course_id', '=', student.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    else:
                        print('6-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('syndicate_discount', '=', False),('martyrs_discount', '=', False),('sibling_discount', '=', False),('staff_discount', '=', False),('mc', '=', 0),
                             ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', join_year), ('course_id', '=', student.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    print(discounts)
                    print('22222222222222222222')
                for dis in discounts:
                    discounts_data.append(dis)
                if not discounts:
                    discounts = self.env['hue.discounts'].sudo().search(
                        [('percentage_from', '<=', student.percentage),
                         ('percentage_to', '>=',student.percentage),('nationality_id', '=',student.student_nationality.id),
                         ('certificate_id', '=',student.student_certificates.id), ('course_id', '=', False) ,
                         ('join_year_id', '=',std_join_year), ('faculty_ids', '=',std_faculty_id), ('scholarship', '=',student.scholarship)])
                    for dis in discounts:
                        discounts_data.append(dis)
                for discount in discounts_data:
                    print('wadood')
                    
                    product_data = product.sudo().search([('discount_id', '=', discount.id)])
                    print(discount.id)
                    print(product_data)
                    invoices_data_count = len(invoice.sudo().search(
                        [('state', '=', 'open'), ('partner_id', '=', partner_id.id), ('invoice_type', '=', 'regular'),
                         ('academic_year', '=', self.id) , ('dis_inv', '=', True) ],limit = 2)._ids)
                    invoices_data = invoice.sudo().search(
                        [('state', '=', 'open'), ('partner_id', '=', partner_id.id), ('invoice_type', '=', 'regular'),
                         ('academic_year', '=', self.id), ('dis_inv', '=', True)],limit = 2)
                    print(invoices_data)
                    print(invoices_data_count)
                    account_id = False
                    if product_data.id:
                        account_id = product_data.property_account_income_id.id
                    if not account_id:
                        account_id = product_data.categ_id.property_account_income_categ_id.id
                    if not account_id:
                        raise UserError(
                            _('There is no income account defined for this product: "%s". \
                               You may have to install a chart of account from Accounting \
                               app, settings menu.') % (product.name,))                   
                    if invoices_data:
                        for invoice_data in invoices_data:
                            print(product_data.list_price)
                            print(invoices_data_count)
                            price_unit = product_data.list_price / invoices_data_count
                            credit_note_data = invoice.sudo().create({
                                'academic_term':invoice_data.academic_term.id,
                                'origin':invoice_data.number,
                                'notes':financial_year.notes,
                                'invoice_type':'regular',
                                'currency_id' : currency.id,
                                'move_type': 'out_refund',
                                'account_id': partner_id.property_account_receivable_id.id,
                                'ref': False,
                                'faculty':std_faculty_id,
                                'student_code':std_code,
                                'academic_year':invoice_data.academic_year.id,
                                'invoice_date_due':invoice_data.date_invoice,
                                'date_invoice':invoice_data.date_invoice,
                                'partner_id':partner_id.id,
                                'state': 'draft'
                                })
                            
                            if invoices_data:
                                dis_increase = 0
                                invoice_line_data = invoice_line.sudo().create({
                                'name': product_data.name,
                                'account_id': account_id,
                                'price_unit': price_unit + dis_increase,
                                'quantity': 1,
                                'move_id': credit_note_data.id,
                                'product_id': product_data.id
                                })
                                
                            credit_note_data.action_post()
                            
                            credit_notes = self.env['account.move'].search([('origin', '=', invoice_data.number)])
                            credit_note_ids = []
                            for cr in credit_notes:
                                credit_note_ids.append(cr.id)
                                
                            domain = [('id', 'in', credit_note_ids),('account_id', '=', invoice_data.account_id.id), ('partner_id', '=', invoice_data.env['res.partner']._find_accounting_partner(invoice_data.partner_id).id), ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0)]
                            if invoice_data.move_type in ('out_invoice', 'in_refund'):
                                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                                type_payment = _('Outstanding credits')
                            else:
                                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                                type_payment = _('Outstanding debits')
                            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': invoice_data.id}
                            lines = invoice_data.env['account.move.line'].search(domain)
                            currency_id = invoice_data.currency_id
                            
                            if len(lines) != 0:
                                for line in lines:
                                    self.assign_outstanding_credit(line.id,invoice_data)