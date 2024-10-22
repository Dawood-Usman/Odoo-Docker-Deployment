# -*- coding: utf-8 -*-
{
    'name': 'Custom Payroll',
    'version': '17.0.0.2',
    'category': 'Payslip',
    'summary': """This module adds custom rule to employee payslip""",
    'author': 'Nida Zehra',
    'depends': ['base', 'hr_payroll', 'hr_holidays', 'hr_attendance'],
    'data': [
        'data/unpaid_data.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
