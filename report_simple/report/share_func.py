# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

to_19 = ( u'không', u'một', u'hai', u'ba', u'bốn', u'năm', u'sáu',
          u'bảy', u'tám', u'chín', u'mười', u'mười một', u'mười hai', u'mười ba',
          u'mười bốn', u'mười lăm', u'mười sáu', u'mười bảy', u'mười tám', u'mười chín' )
tens  = ( u'hai mươi', u'ba mươi', u'bốn mươi', u'năm mươi', u'sáu mươi', u'bảy mươi', u'tám mươi', u'chín mươi')
denom = ( '',
          u'nghìn', u'triệu', u'tỷ', u'nghìn tỷ', u'trăm nghìn tỷ')

def get_name_company(company):
    print("~~company", company)
    name = company.name or ''
    return name.upper()

def get_company_address(company_id):
    address = ''
    street = company_id.street and company_id.street or ''
    city = company_id.city and company_id.city or ''
    street2 = company_id.street2 and company_id.street2 or ''
    state = company_id.state_id and company_id.state_id.name or ''
    country = company_id.country_id and company_id.country_id.name or ''
    if street:
        address = street
    if street2:
        address += len(address) > 0 and ', ' + street2 or street2
    if city:
        address += len(address) > 0 and ', ' + city or city
    if state:
        address += len(address) > 0 and ', ' + state or state
    if country:
        address += len(address) > 0 and ', ' + country or country
    return address

def get_date_str(date):
    if date:
        day = str(date.day).zfill(2)
        month = str(date.month).zfill(2)
        year = str(date.year).zfill(4)
        return u'Ngày %s tháng %s năm %s' %(day, month, year)
    return u'Ngày .... tháng .... năm ....'

def get_person_title(payment_type):
    title = ''
    if payment_type == 'inbound':
        title = u'Họ tên người nộp tiền'
    elif payment_type == 'outbound':
        title = u'Họ tên người nhận tiền'
    return title

def get_journal(o):
    return o.journal_id.number_journal or o.journal_id.display_name

def get_currency(company_id, journal_id):
    if journal_id.currency_id:
        currency = journal_id.currency_id.name
    else:
        currency = company_id.currency_id and company_id.currency_id.name or ''
    return currency

def _convert_nn(val):
    if val>0 and val <= 9:
        return '' + to_19[val]
    if (val > 9 and val < 20) or val==0:
        return  to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                a = u'lăm'
                if to_19[val % 10] == u'một':
                    a = u'mốt'
                else:
                    a = to_19[val % 10]
                return dcap + ' ' + a
            return dcap

def vietnam_number(val):
    if val < 100:
        return _convert_nn(val)
    if val < 1000:
        return _convert_nnn(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l) + ' ' + denom[didx]
            tmp = u''
            if r > 0:
                if r < 100:
                    tmp = u'lẻ '
                ret = ret + ' ' + tmp + vietnam_number(r)
            return ret

def _convert_nnn(val):
    word = ''
    tmp = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = to_19[rem] + u' trăm'
        if mod > 0:
            word = word + ' '
        if mod < 10:
            tmp = u'lẻ '
    if mod > 0:
        word = word + tmp + _convert_nn(mod)
    return word

def amount_to_text(number):
    number = abs(number)
    number = '%.2f' % number
    list = str(number).split('.')
    start_word = vietnam_number(int(list[0]))
    final_result = start_word[0].upper()+ start_word[1:] + u' đồng'
    return final_result

def convert_to_money(number):
    str_tmp = '{:20,.0f}'.format(number)
    str = str_tmp.replace(',','.')
    return u'%s '%str.strip()

def get_date_print():
    date_now = datetime.now()
    day = str(date_now.day).zfill(2)
    month = str(date_now.month).zfill(2)
    year = str(date_now.year).zfill(4)
    return u'Ngày %s tháng %s năm %s' %(day, month, year)

def get_hours_print():
    date_now = datetime.now() + timedelta(hours=7)
    return date_now.strftime("%I:%M:%S %p")

def get_datetime_print():
    date_now = datetime.now() + timedelta(hours=7)
    return date_now.strftime("%d/%m/%Y %I:%M:%S %p")

def get_account_debit(self, o):
    account_debit = ''
    entries = self.env['account.move.line'].search([('payment_id','=',o.id)])
    for entry in entries:
        if entry.debit:
            account_debit += len(account_debit) > 0 and ', ' + entry.account_id.code or entry.account_id.code
    return account_debit

def get_amount_debit(self, o):
    amount_debit = 0
    entries = self.env['account.move.line'].search([('payment_id','=',o.id)])
    for entry in entries:
        if entry.debit:
            amount_debit += entry.debit
    return convert_to_money(amount_debit)

def get_account_credit(self, o):
    account_credit = ''
    entries = self.env['account.move.line'].search([('payment_id','=',o.id)])
    for entry in entries:
        if entry.credit:
            account_credit += len(account_credit) > 0 and ', ' + entry.account_id.code or entry.account_id.code
    return account_credit

def get_amount_credit(self, o):
    amount_credit = 0
    entries = self.env['account.move.line'].search([('payment_id','=',o.id)])
    for entry in entries:
        if entry.credit:
            amount_credit += entry.credit
    return convert_to_money(amount_credit)
    
def view_date(date):
    if date:
        date = u'%s'%date
        try:
            date_tmp = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=7)
        except:
            date_tmp = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        day = str(date_tmp.day).zfill(2)
        month = str(date_tmp.month).zfill(2)
        year = str(date_tmp.year).zfill(4)
        return '%s/%s/%s' % (day, month, year)
    return ''
