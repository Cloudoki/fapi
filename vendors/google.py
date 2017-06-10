import json, base64
from datetime import datetime, timedelta
from vendors.googleapi import get_credentials, get_sheets_service, get_drive_service, sheettime
from vendors import harvest

from requests.auth import HTTPBasicAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models.base import Base
from models.account import Account
from models.document import Document
from models.partner import Partner
from models.tag import Tag
from __init__ import db, CustomJSONEncoder

due_time = 30

def parseGoogleSheet(sheet):

    service = get_sheets_service()

    meta = json.loads(sheet.meta)

    for tab in meta['tabs']:
        result = service.spreadsheets().values().get(spreadsheetId=sheet.uid, range=tab['range'], valueRenderOption='UNFORMATTED_VALUE').execute()
        values = result.get('values', [])

        if values:
            for row in values:
                if len(row) > 9 and isinstance(row[9], str):
                    if tab['type'] is 'payroll':
                        record = parse_payroll_record(row)
                    else:
                        record = parse_default_record(row)

                    parse_document(record, sheet.account, tab['type'])

def parse_document(record, account, typestring):
    document = db.query(Document).filter_by(uid=record['uid']).first()
    partner = get_or_create(Partner, name=record['meta']['client_name'])

    if document is None:
        document = Document(**record)
        document.account = account
        document.tags = [typetags[typestring]]
        db.add(document)
    else:
        u = list(set(document.tags).difference(set(tags.values())))
        if u: document.tags = u

        document.name = record['name']
        document.value = record['value']
        document.date = record['date']

    document.updated_at = datetime.now()
    document.meta = CustomJSONEncoder().encode(record['meta'])
    document.partner = partner
    document.tags.append(tags[record['meta']['state']])

    if record['meta']['state'] == 'open' and record['meta']['due_at'] < datetime.now():
        document.tags.append(tags['due'])



def get_or_create(model, **kwargs):
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        return instance

def parse_default_record(row):
    return {
        'uid': row[9],
        'name': row[6],
        'value': row[2],
        'date': sheettime(row[1]),
        'meta': {
            "number": row[5],
            "tax_amount": -row[3] if isinstance(row[3], int) else 0,
            "amount": -row[2],
            "subject": row[6],
            "state": "open" if not row[7] or int(row[7]) < int(row[2]) else "paid",
            "client_name": row[4],
            "due_at": sheettime(row[8]), #sheettime(row[1], due_time).strftime("%Y-%m-%d"),
            "currency": "Euro - EUR",
            "issued_at": sheettime(row[1]).strftime("%Y-%m-%d"),
            "due_amount": int(row[2]) - int(row[7]) if row[7] else row[2]
        }
    }

def parse_payroll_record(row):
    return {
        'uid': row[9],
        'name': '%s, %s' % (row[3], row[4]),
        'value': row[2],
        'date': sheettime(row[1]),
        'meta': {
            "amount": -row[2],
            "tax_amount": 0,
            "subject": row[4],
            "state": "open" if not row[6] or int(row[6]) < int(row[2]) else "paid",
            "client_name": row[3],
            "due_at": sheettime(row[8]), #sheettime(row[1]).strftime("%Y-%m-%d"),
            "currency": "Euro - EUR",
            "issued_at": sheettime(row[1]),
            "due_amount": int(row[2]) - int(row[6]) if row[6] else row[2]
        }
    }

typetags = {
    'invoice':  get_or_create(Tag, name="Invoice", slug="invoice"),
    'bill':     get_or_create(Tag, name="Bill", slug="bill"),
    'expense':  get_or_create(Tag, name="Expense", slug="expense"),
    'payroll':  get_or_create(Tag, name="Pay-roll", slug="payroll")
}
tags = {
    'draft':    get_or_create(Tag, name="Draft", slug="draft"),
    'open':     get_or_create(Tag, name="Open", slug="open"),
    'paid':     get_or_create(Tag, name="Paid", slug="paid"),
    'due':      get_or_create(Tag, name="Over Due", slug="due")
}

# def googleSheets():
#     service = get_sheets_service()
#
#     for tab in sheet['tabs']:
#         result = service.spreadsheets().values().get(spreadsheetId=sheet['file'], range=tab['range'], valueRenderOption='UNFORMATTED_VALUE').execute()
#         values = result.get('values', [])
#
#         if not values:
#             print('No data found.')
#         else:
#             for row in values:
#                 if len(row) and isinstance(row[0], int):
#                     if tab['type'] is 'bill':
#                         record = {
#                             'uid': tab['uid'] % row[0],
#                             'name': '%s - %s' % (row[4], row[6]),
#                             'value': row[2],
#                             'date': sheettime(row[1]),
#                             'meta': {
#                                 "number": row[5],
#                                 "tax_amount": -row[3] if isinstance(row[3], int) else 0,
#                                 "amount": -row[2],
#                                 "subject": row[6],
#                                 "state": "open" if len(row) < 8 or row[7] < row[2] else "paid",
#                                 "client_name": row[4],
#                                 "due_at": sheettime(row[1], due_time).strftime("%Y-%m-%d"),
#                                 "currency": "Euro - EUR",
#                                 "issued_at": sheettime(row[1]).strftime("%Y-%m-%d"),
#                                 "due_amount": row[2] - row[7] if len(row) >= 8 else row[2],
#                                 "from_file": sheet['name']
#                             }
#                         }
#                     if tab['type'] is 'payroll':
#                         record = {
#                             'uid': tab['uid'] % row[0],
#                             'name': '%s, %s' % (row[3], row[4]),
#                             'value': row[2],
#                             'date': sheettime(row[1]),
#                             'meta': {
#                                 "amount": -row[2],
#                                 "tax_amount": 0,
#                                 "subject": row[4],
#                                 "state": "open" if len(row) < 7 or row[6] < row[2] else "paid",
#                                 "client_name": row[3],
#                                 "due_at": sheettime(row[1]).strftime("%Y-%m-%d"),
#                                 "currency": "Euro - EUR",
#                                 "issued_at": sheettime(row[1]).strftime("%Y-%m-%d"),
#                                 "due_amount": row[2] - row[6] if len(row) >= 7 else row[2],
#                                 "from_file": sheet['name']
#                             }
#                         }
#                     if tab['type'] is 'expense':
#                         record = {
#                             'uid': tab['uid'] % row[0],
#                             'name': '%s, %s' % (row[4], row[6]),
#                             'value': row[2],
#                             'date': sheettime(row[1]),
#                             'meta': {
#                                 "number": row[5],
#                                 "amount": -row[2],
#                                 "tax_amount": -row[3] if isinstance(row[3], int) else 0,
#                                 "subject": row[6],
#                                 "state": "open" if len(row) < 8 or row[7] < row[2] else "paid",
#                                 "client_name": row[4],
#                                 "due_at": sheettime(row[1]).strftime("%Y-%m-%d"),
#                                 "currency": "Euro - EUR",
#                                 "issued_at": sheettime(row[1]).strftime("%Y-%m-%d"),
#                                 "due_amount": row[2] - row[7] if len(row) >= 8 else row[2],
#                                 "from_file": sheet['name']
#                             }
#                         }
#
#                     parse_document(record, sheet.account, tab['type'])
