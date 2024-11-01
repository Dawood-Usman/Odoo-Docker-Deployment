# -*- coding: utf-8 -*-
{
    'name': "Prixite Employment Offer",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Ameer Hamza Khan",
    'website': "hamzaniazi777@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment', 'hr_contract', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/report_paper_format.xml',
        'views/views.xml',
        'views/templates.xml',

        'views/hr_recruitment.xml',
        'reports/offer_letter.xml',
        'reports/increment_letter.xml',
        'data/mail_template_data.xml',
        'views/hr_contract.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
