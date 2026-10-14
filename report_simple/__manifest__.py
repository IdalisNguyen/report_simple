# -*- coding: utf-8 -*-
{
    'name': 'Bizapps - Vietnam Cash Receipt & Payment Voucher',
    'version': '17.0.0.1',
    'category': 'Accounting',
    'summary': 'Print cash receipt and payment vouchers directly from Odoo invoices, payments and bank statements, with configurable journal codes.',
    'summary_vi_VN': 'In phiếu thu và phiếu chi từ hóa đơn, thanh toán và sao kê ngân hàng, cấu hình mã phiếu theo sổ nhật ký.',
    'description': """
Configure receipt and payment voucher codes on cash journals and print vouchers from invoices, customer or vendor payments, and bank statements.
""",
    'description_vi_VN': """
In phiếu thu và phiếu chi trực tiếp từ Odoo Accounting.
Cấu hình mã phiếu thu/phiếu chi theo sổ nhật ký tiền mặt và in từ hóa đơn, thanh toán khách hàng/nhà cung cấp và sao kê ngân hàng.
""",
    'author': 'support@bizapps.vn',
    'website': 'https://bizapps.vn/ung-dung',
    'price': 149.0,
    'currency': 'USD',
    'images': [
        'static/description/Theme.png',
        'static/description/icon.png',
    ],
    'depends': ['base', 'account', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/assets.xml',
        'report/rp_invoice_receipt_payment_view.xml',
        'report/report_extension.xml',
        'report/report_voucher_payment_view.xml',
        'report/report_voucher_invoice_view.xml',
        'report/report_receipts_pay_slip_view.xml',
        'views/account_journal_view.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/account_bank_statement_view.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            '/biz_voucher_report_simple/static/src/css/style_report.css',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
