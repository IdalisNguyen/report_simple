# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.addons.biz_voucher_report_simple.report.share_func import get_name_company, get_company_address, get_date_str, convert_to_money, get_currency, amount_to_text, get_datetime_print, get_date_print, get_hours_print, get_journal, get_account_debit, get_amount_debit, get_account_credit, get_amount_credit

to_19 = ( u'không', u'một', u'hai', u'ba', u'bốn', u'năm', u'sáu',
          u'bảy', u'tám', u'chín', u'mười', u'mười một', u'mười hai', u'mười ba',
          u'mười bốn', u'mười lăm', u'mười sáu', u'mười bảy', u'mười tám', u'mười chín' )
tens  = ( u'hai mươi', u'ba mươi', u'bốn mươi', u'năm mươi', u'sáu mươi', u'bảy mươi', u'tám mươi', u'chín mươi')
denom = ( '',
          u'nghìn', u'triệu', u'tỷ', u'nghìn tỷ', u'trăm nghìn tỷ')

class ReportReceiptsPaySlip(models.AbstractModel):
    _name = 'report.biz_voucher_report_simple.print_receipts_pay_slip'
    _description = 'Print Receipts/Pay Slip'
    
    def get_lines(self, o):
        res = []
        stt = 0
        total_qty = 0
        amount_total = 0.0
        for line in o.move_ids_without_package:
            stt += 1
            debit_id = line.product_id.categ_id.property_stock_account_output_categ_id and line.product_id.categ_id.property_stock_account_output_categ_id.code or ''
            credit_id = line.product_id.categ_id.property_stock_valuation_account_id and line.product_id.categ_id.property_stock_valuation_account_id.code or ''
            res.append({
                        'stt': stt,
                        'name': line.product_id.name,
                        'default_code': line.product_id.default_code or '',
                        'product_uom': line.product_uom.name,
                        'qty_done': line.quantity_done,
                        'price_unit': convert_to_money(line.price_unit_extra),
                        'subtotal': convert_to_money(line.price_subtotal),
                        'location': o.picking_type_id.warehouse_id and o.picking_type_id.warehouse_id.code or line.location_id.display_name or '',
                        'debit_id': debit_id,
                        'credit_id': credit_id,
                        })
            total_qty += line.quantity_done
            amount_total += line.price_subtotal
        # self.total_qty = total_qty
        # self.amount_total = amount_total
        return res
    
    def get_print_name(self, docid):
        return docid.amount >= 0 and u'PHIẾU THU' or u'PHIẾU CHI'
    
    def get_person_title(self, docid):
        return docid.amount >= 0 and u'Họ tên người nộp tiền' or u'Họ tên người nhận tiền'
    
    def print_type(self, docid):
        return docid.amount >= 0 and 'inbound' or 'outbound'
    
    def bank_account_ids(self, docid):
        if docid.payment_id:
            if docid.payment_id.bank_account_ids:
                return docid.payment_id.bank_account_ids
        return []
    
    def get_account_debit(self, docid):
        name = ''
        debit = docid.move_id.line_ids.filtered(lambda x: x.account_id and x.debit > 0)
        if debit:
            name = ', '.join(debit.mapped('account_id').mapped('code'))
        
        return name
        
    def get_amount_debit(self, docid):
        if docid.payment_id:
            return get_amount_debit(self, docid.payment_id)
        return 0
        
    def get_account_credit(self, docid):
        name = ''
        credit = docid.move_id.line_ids.filtered(lambda x: x.account_id and x.credit > 0)
        if credit:
            name = ', '.join(credit.mapped('account_id').mapped('code'))
        
        return name
    
    def get_amount_credit(self, docid):
        if docid.payment_id:
            return get_amount_credit(self, docid.payment_id)
        return 0
    
    def get_journal(self, docid):
        if docid.payment_id:
            return docid.payment_id.journal_id and (docid.payment_id.journal_id.number_journal or docid.payment_id.journal_id.display_name)
        return ''
    
    def get_number(self,docid):
        if docid:
            return docid.number_sequence or ''
        return ''
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # self.total_qty = 0
        # self.amount_total = 0.0
        report = self.env['ir.actions.report']._get_report_from_name('biz_voucher_report_simple.print_receipts_pay_slip')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docids),
            'report_type': data.get('report_type') if data else '',
            'name_company': get_name_company,
            'address': get_company_address,
            'get_date_str': get_date_str,
            'convert_to_money': convert_to_money,
            'get_currency': get_currency,
            'amount_to_text': amount_to_text,
            'get_date_print': get_date_print,
            'get_hours_print': get_hours_print,
            'get_datetime_print': get_datetime_print,
            'get_journal': self.get_journal,
            'get_print_name': self.get_print_name,
            'get_person_title': self.get_person_title,
            'print_type': self.print_type,
            'bank_account_ids': self.bank_account_ids,
            'get_account_debit': self.get_account_debit,
            'get_amount_debit': self.get_amount_debit,
            'get_account_credit': self.get_account_credit,
            'get_amount_credit': self.get_amount_credit,
            'get_number': self.get_number,
            
        }
