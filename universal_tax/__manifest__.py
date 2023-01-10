# -*- coding: utf-8 -*-
{
    'name': "Universal Tax",

    'summary': """
        Universal Tax v15.0
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

    'author': "Ksolves India Ltd.",
    'website': "https://store.ksolves.com/",


    'category': 'Sales Management',
    'version': '15.1.0.2',
    'license': 'LGPL-3',
    'currency': 'EUR',
    'price': '0.0',
    'depends': ['base', 'sale', 'purchase', 'account', 'sale_management'],

    'data': [
        'views/ks_account_account.xml',
        'views/ks_sale_order.xml',
        'views/ks_account_invoice.xml',
        'views/ks_purchase_order.xml',
        'views/ks_account_invoice_supplier_form.xml',
        'views/ks_report.xml',
        # 'views/assets.xml',

    ],

    'images': ['static/description/Universal_Tax_V15.jpg'],
    'assets': {
            'web.assets_backend': [
                '/universal_tax/static/css/ks_stylesheet.css',
            ],
        },

}
