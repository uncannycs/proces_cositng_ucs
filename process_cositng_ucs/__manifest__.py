# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing Process Costing UCS | MRP Process Costing | Advanced Manufacturing Costing | Production Costing | Work Center Costing | Direct Material Costing | Overhead Costing',
    'version': '18.0.1.0.0',
    'summary': 'Process Costing in Manufacturing, BOM Costing, Operation Costing',
    'description': """
Manufacturing Process Costing
=============================
Optimize your manufacturing costs by tracking and allocating material costs, labor costs, and overhead costs across production and manufacturing orders.

Key Features:
- Manually or automatically add material, labor, and overhead costs on BOM.
- Compute estimated vs actual costs on Manufacturing Orders.
- Work center-based automatic cost calculation.
    """,
    'author': 'Uncanny Consulting Services LLP',
    'company': 'Uncanny Consulting Services LLP',
    'maintainer': 'Uncanny Consulting Services LLP',
    'website': 'https://www.uncannycs.com',
    'category': 'Manufacturing',
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/mrp_workcenter_views.xml',
        'views/mrp_bom_views.xml',
        'views/mrp_production_views.xml',
        'report/mrp_production_report.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': '80',
    'currency': 'USD',
    'license': 'Other proprietary',
}
