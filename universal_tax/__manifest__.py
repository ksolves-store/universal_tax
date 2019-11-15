# -*- coding: utf-8 -*-
{
    'name': "Universal Tax",

    'summary': """
        Universal Tax v13.0
        """,

    'description': """
        - Apply a field in Sales, Purchase and Invoice module to calculate tax after the order lines are inserted.
        - Can be enabled from (**Note** : Charts of Accounts must be installed)
            
            Settings -> General Settings -> invoice
        
        - Maintains the global tax entries in accounts specified by you (**Note** : To see journal entries in Invoicing:
         (in debug mode))
            
            Settings -> users -> select user -> Check "Show Full Accounting Features")
        
        - Label given to you will be used as name given to tax field.
        - Also update the report PDF printout with global tax value.
    """,

    'author': "Ksolves India Pvt. Ltd.",
    'website': "https://www.ksolves.com/",


    'category': 'Sales Management',
    'version': '1.1.1',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'purchase', 'account', 'sale_management'],

    'data': [
        'views/ks_account_account.xml',
        'views/ks_sale_order.xml',
        'views/ks_account_invoice.xml',
        'views/ks_purchase_order.xml',
        'views/ks_account_invoice_supplier_form.xml',
        'views/ks_report.xml',
        'views/assets.xml',

    ],

    'images': ['static/description/Universal-Tax-V13.jpg'],

}
