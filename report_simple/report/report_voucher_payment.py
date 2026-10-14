# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.addons.biz_voucher_report_simple.report.share_func import get_name_company, get_company_address, get_date_str, get_person_title, convert_to_money, get_currency, amount_to_text, get_datetime_print, get_date_print, get_hours_print, get_journal, get_account_debit, get_amount_debit, get_account_credit, get_amount_credit 

class ReportVoucherPayment(models.AbstractModel):
    _name = 'report.biz_voucher_report_simple.report_voucher_payment'
    _description = 'Receipts/Vouchers'
    
    def get_account_debit(self, o):
        account_debit = get_account_debit(self, o)
        return account_debit
    
    def get_amount_debit(self, o):
        amount_debit = get_amount_debit(self, o)
        return amount_debit
    
    def get_account_credit(self, o):
        account_credit = get_account_credit(self, o)
        return account_credit
    
    def get_amount_credit(self, o):
        amount_credit = get_amount_credit(self, o)
        return amount_credit
    
    def get_print_name(self, docid):
        print_name = docid.payment_type == 'inbound' and u'PHIẾU THU' or \
               docid.payment_type == 'outbound' and u'PHIẾU CHI'
        return print_name
    
    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('biz_voucher_report_simple.report_voucher_payment')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docids),
            'report_type': data.get('report_type') if data else '',
            'name_company': get_name_company,
            'address': get_company_address,
            'get_date_str': get_date_str,
            'person_title': get_person_title,
            'convert_to_money': convert_to_money,
            'get_currency': get_currency,
            'amount_to_text': amount_to_text,
            'get_datetime_print': get_datetime_print,
            'get_date_print': get_date_print,
            'get_hours_print': get_hours_print,
            'get_journal': get_journal,
            'get_account_debit': self.get_account_debit,
            'get_amount_debit': self.get_amount_debit,
            'get_account_credit': self.get_account_credit,
            'get_amount_credit': self.get_amount_credit,
            'get_print_name': self.get_print_name,
        }