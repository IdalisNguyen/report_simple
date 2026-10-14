# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    #=== FIELDS ===#
    
    payment_count = fields.Integer(compute='_get_payment_count', string='Payments')
    payment_ids = fields.Many2many('account.payment', 'account_invoice_payment_rel', 'invoice_id', 'payment_id', string="Payments", copy=False, readonly=True)
    
    def _get_payment_count(self):
        for invoice in self:
            invoice.payment_count = invoice.payment_ids and len(invoice.payment_ids.ids) or 0
    
    def button_payments(self):
        context = dict(self._context or {})
        print("aâ",self._context)
        if context.get('default_type') == 'in_invoice':
            result = self.env.ref('account.action_account_payments_payable').read()[0]
        else:
            result = self.env.ref('account.action_account_payments').read()[0]
        result['domain'] = [('id', 'in', self.mapped('payment_ids').ids)]
        return result
    
    def _get_printed_report_name(self):
        self.ensure_one()
        payment_ids = [payment for payment in self.payment_ids if payment.journal_id.type == 'cash' and payment.journal_id.is_print]
        payment_type = 'transfer'
        name_thu = ''
        name_chi = ''
        for payment in payment_ids:
            if payment.payment_type == 'inbound':
                payment_type = 'inbound'
                name_thu+= u'_%s'%payment.number_sequence
            if payment.payment_type == 'outbound':
                payment_type = 'outbound'
                name_chi+= u'_%s'%payment.number_sequence
        return payment_type == 'inbound' and _('PHIEUTHU%s' %(name_thu)) or \
            payment_type == 'outbound' and _('PHIEUCHI%s') % (name_chi) or 'Cash Receipt &amp; Payment Voucher'
    
    def print_vourcher(self):
        self.ensure_one()
        journal_cash_ids = self.payment_ids.filtered(lambda r: r.journal_id.type == 'cash' and r.journal_id.is_print)
        if not journal_cash_ids:
            raise UserError(_('There is nothing to print. Please check again!'))
        return self.env.ref('biz_voucher_report_simple.account_report_voucher_invoice').report_action(self)
