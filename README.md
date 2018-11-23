# Universal Tax

This application provides Odoo users with the feature to calculate Universal Tax on sale or purchase order.

# Features

-   Calculate Total Tax value on sale/purchase order instead of doing the same on sale/purchase order lines as in regular Odoo process.
-   Application function can be easily Enabled/Disabled from Odoo Configuration.
-   Journal Entries are maintained with seperate line for Universal Tax values.
-   Refund entries are also maintained in Journal Entries.
-   Report printing of Sales, Purchase and Invoice are also maintained.
-   Compatible with Ksolves’ Universal  Discount Application. 

** Note: When both applications are installed together, Universal Tax will be applied on Universal Discount values.**

# Installation

-  There’s NO external library used.

# Configuration

After installing this module from Odoo Apps, follow these steps to activate this application:

-   To View Universal Tax Setting :

    > Settings → General Settings → Invoice

    **Note: In order to enable this application, please Ensure that Accounting of at least one country is installed and selected in Fiscal Localizations in Invoice Settings to view Universal Tax settings.**

-     At the top, there will be Universal Tax settings where you have to check the box to enable or disable Universal Tax.

-   After enabling the Universal Tax, you have to define accounts to be used to maintain Universal Tax values.

-   After the above step is done, a field will appear for Universal Tax value in Sales, Purchase and Invoice model view.

-   After creating and validating the order, Journal Entries are created with separate Universal Tax lines in them.

      ** Note: To see the Journal Entries, you have to give the current user access to "Show Full Accounting Features" through Odoo Settings → Users (in debug mode).**

# Authors

-   Developed and maintained by - [Ksolves India Pvt. Ltd.](https://www.ksolves.com/)



