# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import float_is_zero, pycompat
from odoo.tools import float_compare, float_round, float_repr
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError, ValidationError

import time
import math
import copy

import logging
_logger = logging.getLogger(__name__)

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    _sql_constraints = [
        ('number_sequence_uniq', 'unique (number_sequence)', _('The number_sequence must be unique !')),
    ]
        
    #=== FIELDS ===#

    payment_id = fields.Many2one('account.payment', compute='_compute_payment', string="Payment")
    payment_ids = fields.Many2many('account.payment', 'account_bank_statement_payment_rel', 'statement_line_id', 'payment_id', string='Payments')
    payer = fields.Char(string="Payer")
    show_print = fields.Boolean(string="Show print", compute='_compute_show_print', default=False)
    number_sequence = fields.Char('Number')
    number_is_enter = fields.Boolean('Number', default=True)

    #=== COMPUTE ===#

    def _compute_payment(self):
        for res in self:
            res.payment_id = False
    
    @api.depends('journal_id')
    def _compute_show_print(self):
        for res in self:
            if res.journal_id and res.journal_id.type == 'cash':
                res.show_print = True
            else:
                res.show_print = False

    def print_receipts_pay_slip(self):
        return self.env.ref('biz_voucher_report_simple.account_print_receipts_pay_slip').report_action(self)
    
    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        res = super(AccountBankStatementLine, self).process_reconciliation(counterpart_aml_dicts, payment_aml_rec, new_aml_dicts)
        
        if self.journal_id.is_print:

            if not self.number_sequence:
                sequence_id = self.amount < 0 and self.journal_id.sequence_payment_id or self.journal_id.sequence_receipt_id
                if not sequence_id:
                    raise UserError(_('Journal have not sequence number. Please check again!!!'))
                self.number_sequence = sequence_id.next_by_id()
            
            for move in res:
                for ml in move.line_ids:
                    if ml.account_id == move.journal_id.default_debit_account_id or  ml.account_id == move.journal_id.default_credit_account_id:
                        ml.write({'ref': self.number_sequence})
                        if ml.payment_id and ml.statement_line_id:
                            ml.payment_id.write({'number_sequence': ml.statement_line_id.number_sequence,'payer': ml.statement_line_id.payer})
        
        return res
    def _get_printed_report_name(self):
        self.ensure_one()
        print(self.payment_id.payment_type)
        return self.payment_id.payment_type == 'inbound' and _('PHIEUTHU_%s' %(self.number_sequence)) or \
               self.payment_id.payment_type == 'outbound' and _('PHIEUCHI_%s') % (self.number_sequence) or 'Cash Receipt &amp; Payment Voucher'
