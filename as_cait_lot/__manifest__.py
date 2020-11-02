{
    "name": "Customizaciones para CAIT",
    "summary": "Cait",
    "category": "stock",
    "images": [],
    "version": "1.0.2",
    "application": True,
    "author": "TPCO",
    "support": "tpco@tpco.cl",
    "website": "www.tpco.cl",
    "depends": [
        "stock",
        "sale",
        'base',
   
    ],
    'data': [
        'views/as_lot.xml',
        'views/as_stock_picking.xml',
        # 'security/ir.model.access.csv',
    ],
    "auto_install": False,
    "installable": True,

}