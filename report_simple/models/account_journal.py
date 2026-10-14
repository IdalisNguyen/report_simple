# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    #=== FIELDS ===#
    
    is_print = fields.Boolean(string='Print cash receipt & payment voucher')
    rule_by = fields.Selection([('determination_15','Determination 15'), ('curcular_200','Circulars 200'),('curcular_133','Circulars 133'),('determination_48','Determination 48')], string='By Rule', default='determination_15')
    number_journal = fields.Char('Number Journal', default='1')
    sequence_receipt_id = fields.Many2one('ir.sequence', string='Cash Receipt voucher code')
    sequence_payment_id = fields.Many2one('ir.sequence', string='Cash Payment voucher code')
    director = fields.Many2one("res.users","Director")
    accountant = fields.Many2one("res.users","Accountant")
    repaired_by = fields.Many2one("res.users","Repaired By")
    cashier = fields.Many2one('res.users',"Cashier")


    #=== ONCHANGE ===#
    
    @api.onchange('is_print')
    def onchange_is_print(self):
        if self.is_print:
            try:
                self.journal_user = False
            except:
                pass
            
    @api.onchange('journal_user')
    def onchange_journal_user(self):
        try:
            if self.journal_user:
                self.is_print = False
        except:
            pass
