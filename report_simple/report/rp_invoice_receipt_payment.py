# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.addons.biz_voucher_report_simple.report.share_func import get_name_company, get_company_address, get_person_title, get_date_str, convert_to_money, get_currency, amount_to_text, get_datetime_print, get_date_print, get_hours_print, get_journal, get_account_debit, get_amount_debit, get_account_credit, get_amount_credit
from odoo.exceptions import ValidationError, UserError
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    is_html_empty,
    sql
)

class rp_invoice_payment(models.AbstractModel):
    _name = 'report.biz_voucher_report_simple.rp_invoice_payment'
    _description = 'rp_invoice_payment'

    move_ids = fields.Many2many('account.move','rel_report_move_ids','report_id','move_id')
    
    def get_print_name(self, docid):
        if docid._name  ==  'account.bank.statement.line':
            return docid.amount >= 0 and u'PHIẾU THU' or u'PHIẾU CHI'
        if docid._name == 'account.payment':
            print_name = docid.payment_type == 'inbound' and u'PHIẾU THU' or docid.payment_type == 'outbound' and u'PHIẾU CHI'
            return print_name
        return ''

    def get_journal(self, docid):
        if docid._name == 'account.bank.statement.line':
            if docid.payment_id:
                return docid.payment_id.journal_id and (docid.payment_id.journal_id.number_journal or docid.payment_id.journal_id.display_name)
            return ''

        if docid._name == 'account.payment':
            return  get_journal(docid)

    def get_account_debit(self, docid):
        context = self._context
        if docid._name == 'account.payment':
            move_id = self.env['account.move'].browse(context['move_id'])
            if move_id.move_type  in ['in_invoice','out_refund']:
                name = ''
                debit = move_id.line_ids.filtered(lambda x: x.account_id and x.debit > 0)
                if debit:
                    name = ', '.join(debit.mapped('account_id').mapped('code'))
                return name
            else:
                account_debit = get_account_debit(self, docid)
                return account_debit

        if docid._name == 'account.bank.statement.line':
            if docid.payment_id:
                return get_account_debit(self, docid.payment_id)
            return 0

    def get_amount_debit(self, docid):
        if docid._name == 'account.payment':
            amount_debit = get_amount_debit(self, docid)
            return amount_debit
        if docid._name == 'account.bank.statement.line':
            if docid.payment_id:
                return get_amount_debit(self, docid.payment_id)
            return 0

    def get_account_credit(self, docid):
        context = self._context
        if docid._name == 'account.payment':
            move_id = self.env['account.move'].browse(context['move_id'])
            if move_id.move_type in  ['in_refund','out_invoice']:
                name = ''
                credit = move_id.line_ids.filtered(lambda x: x.account_id and x.credit > 0)
                if credit:
                    name = ', '.join(credit.mapped('account_id').mapped('code'))

                return name
            else:
                return get_account_credit(self, docid)

        if docid._name == 'account.bank.statement.line':
            if docid.payment_id:
                return get_account_credit(self, docid.payment_id)
            return 0

    def get_amount_credit(self, docid):
        if docid._name == 'account.payment':
            return get_amount_credit(self, docid)
        if docid._name == 'account.bank.statement.line':
            if docid.payment_id:
                return get_amount_credit(self, docid.payment_id)
            return 0

    def get_person_title(self, docid):
        return docid.amount >= 0 and u'Họ tên người nộp tiền' or u'Họ tên người nhận tiền'

    def bank_account_ids(self, docid):
        if docid.payment_id:
            if docid.payment_id.bank_account_ids:
                return docid.payment_id.bank_account_ids
        return []

    def print_type(self, docid):
        return docid.amount >= 0 and 'inbound' or 'outbound'

    def get_number(self,docid):
        if docid:
            return docid.number_sequence or ''
        return ''

    def _get_reconciled_info_JSON_values(self, move):
        reconciled_vals = []
        reconciled_partials = move._get_all_reconciled_invoice_partials()
        for reconciled_partial in reconciled_partials:
            counterpart_line = reconciled_partial['aml']
            if counterpart_line.move_id.ref:
                reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
            else:
                reconciliation_ref = counterpart_line.move_id.name
            if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
                foreign_currency = counterpart_line.currency_id
            else:
                foreign_currency = False

            reconciled_vals.append({
                'name': counterpart_line.name,
                'journal_name': counterpart_line.journal_id.name,
                'amount': reconciled_partial['amount'],
                'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else reconciled_partial['currency'].id,
                'date': counterpart_line.date,
                'partial_id': reconciled_partial['partial_id'],
                'account_payment_id': counterpart_line.payment_id.id,
                'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
                'move_id': counterpart_line.move_id.id,
                'ref': reconciliation_ref,
                # these are necessary for the views to change depending on the values
                'is_exchange': reconciled_partial['is_exchange'],
                'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance), currency_obj=counterpart_line.company_id.currency_id),
                'amount_foreign_currency': foreign_currency and formatLang(self.env, abs(counterpart_line.amount_currency), currency_obj=foreign_currency)
            })
        return reconciled_vals

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        print("============doc.payment_state", docs.mapped('payment_state'))

        if any(doc.payment_state not in ['in_payment','paid'] for doc in docs):
            raise ValidationError(_('The invoice has not been recorded as payment, please check again!'))

        list_payment = []
        list_move = []

        for move in docs:
            contents = self._get_reconciled_info_JSON_values(move)

            for content in contents:
                if content.get("account_payment_id", False):
                    payment_id = self.env['account.payment'].browse(content['account_payment_id'])
                    if payment_id and payment_id.journal_id.type == 'cash':
                        list_payment.append(payment_id)

                elif content.get("move_id", False):
                    move_id = self.env['account.move'].browse(content['move_id'])
                    if move_id.statement_line_id:
                        list_move.append(move_id.statement_line_id)

        if not list_move and not list_payment:
            raise ValidationError(_('Nothing to print!'))

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(docids),
            'list_payment': list_payment,
            'person_title': get_person_title,
            'get_person_title': self.get_person_title,
            'list_move': list_move,
            'name_company': get_name_company,
            'address': get_company_address,
            'get_date_str': get_date_str,
            'convert_to_money': convert_to_money,
            'get_currency': get_currency,
            'amount_to_text': amount_to_text,
            'get_date_print': get_date_print,
            'get_hours_print': get_hours_print,
            'get_journal': self.get_journal,
            'get_account_debit': self.with_context(move_id=docs.id).get_account_debit,
            'get_amount_debit': self.get_amount_debit,
            'get_account_credit': self.with_context(move_id=docs.id).get_account_credit,
            'get_amount_credit': self.get_amount_credit,
            'get_print_name': self.get_print_name,
            'bank_account_ids': self.bank_account_ids,
            'print_type': self.print_type,
            'get_number': self.get_number,
        }
