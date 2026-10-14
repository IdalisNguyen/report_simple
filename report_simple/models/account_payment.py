# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountPaymentBank(models.Model):
    _name = 'account.payment.bank'
    _description = 'Account payment bank'
    
    debit = fields.Integer(string="Debit")
    credit = fields.Integer(string="Credit")
    account_id = fields.Integer(string="Account")
    account_payment_id  = fields.Integer(string="account_payment_id")

    
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    @api.depends('journal_id', 'journal_id.is_print')
    def compute_is_print(self):
        for res in self:
            res.is_print = res.journal_id.is_print
    
    is_print = fields.Boolean(compute='compute_is_print', string='Print cash receipt & payment voucher', store=True)
    bank_account_ids = fields.One2many('account.payment.bank','account_payment_id','bank_account_ids')
    number_sequence = fields.Char('Number')
    payer = fields.Char(string="Payer")
    including = fields.Char("Including")

    def _get_printed_report_name(self):
        self.ensure_one()
        return self.payment_type == 'inbound' and _('PHIEUTHU_%s' %(self.number_sequence)) or \
               self.payment_type == 'outbound' and _('PHIEUCHI_%s') % (self.number_sequence) or 'Cash Receipt &amp; Payment Voucher'
                
    def print_vourcher(self):
        self.ensure_one()
        if self.journal_id.type != 'cash':
            raise UserError(_('There is nothing to print. Please check again!'))
        return self.env.ref('biz_voucher_report_simple.account_report_voucher_payment').report_action(self)


    def action_post(self):
        number = ''
        for res in self:
            if res.payment_type =='inbound' and res.journal_id.type == "cash" and res.journal_id.sequence_receipt_id:
                number = res.journal_id.sequence_receipt_id.next_by_id()
            if res.payment_type == 'outbound' and res.journal_id.type == "cash" and res.journal_id.sequence_payment_id:
                number = res.journal_id.sequence_payment_id.next_by_id()
            res.with_context(pass_synchronize_to_moves=True).number_sequence = number
        return super(AccountPayment,self).action_post()
