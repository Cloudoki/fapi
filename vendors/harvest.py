import os, requests, json, base64
from requests.auth import HTTPBasicAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models.base import Base
from models.account import Account
from models.document import Document
from models.partner import Partner
from models.tag import Tag
from __init__ import db

### API Headers
auth = base64.b64encode(os.environ.get("HARVEST_CREDS"))
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': "Basic " + auth.decode("utf-8")}

# ### MySQL DB
# engine = create_engine('mysql+pymysql://cloudoki:hovering-rabbits-4455-sudoku@cloudoki.com:3306/cloudoki?charset=utf8')
# session = sessionmaker()
# session.configure(bind=engine)
# Base.metadata.create_all(engine)
# s = session()

def parse_partners(entries):
    for entry in entries:
        c = entry['client']
        partner = db.query(Partner).filter_by(uid=c['id']).first()
        if partner is None:
            partner = Partner(uid=c['id'])
            db.add(partner)

        partner.name = c['name']
        partner.meta = json.dumps(c)

def parse_invoices(entries, account):
    for entry in entries:
        i = entry['invoices']
        invoice = db.query(Document).filter_by(uid=i['id']).first()
        partner = db.query(Partner).filter_by(uid=i['client_id']).first()

        if invoice is None:
            invoice = Document(uid=i['id'], account=account, tags=[typetags['invoice']])
            db.add(invoice)
        else:
            u = list(set(invoice.tags).difference(set(tags.values())))
            if u: invoice.tags = u

        invoice.name = i['subject']
        invoice.value = i['amount']
        invoice.date = datetime.strptime(i['issued_at'], '%Y-%m-%d')
        invoice.updated_at = datetime.strptime(i['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        invoice.meta = json.dumps(i)
        invoice.partner = partner
        invoice.tags.append(tags[i['state']])

        if i['state'] == 'open' and datetime.strptime(i['due_at'], '%Y-%m-%d') < datetime.now():
            invoice.tags.append(tags['due'])

def get_request(url):
    return requests.get(url, headers=headers)

def get_or_create(model, **kwargs):
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        return instance

### Tags
typetags = {
    'invoice':  get_or_create(Tag, name="Invoice", slug="invoice"),
    'bill':     get_or_create(Tag, name="Bill", slug="bill"),
    'expense':  get_or_create(Tag, name="Expense", slug="expense")
}
tags = {
    'draft':    get_or_create(Tag, name="Draft", slug="draft"),
    'open':     get_or_create(Tag, name="Open", slug="open"),
    'paid':     get_or_create(Tag, name="Paid", slug="paid"),
    'due':      get_or_create(Tag, name="Over Due", slug="due")
}

if __name__ == '__main__':

    ## CLOUDOKILX
    url = 'https://cloudokilx.harvestapp.com%s'
    cloudokilx = get_or_create(s, Account, name="Cloudoki LX")

    ### Add Harvest Clients
    r = requests.get(url % '/clients', headers=headers)
    parse_partners(r.json(), s)

    ### Add Harvest invoices
    r = requests.get(url % '/invoices', headers=headers)
    parse_invoices(r.json(), cloudokilx, s)

    ## CLOUDOKI
    url = 'https://cloudoki.harvestapp.com%s'
    cloudoki = get_or_create(s, Account, name="Cloudoki")

    ### Add Harvest Clients
    r = requests.get(url % '/clients', headers=headers)
    parse_partners(r.json(), s)

    ### Add Harvest invoices
    r = requests.get(url % '/invoices', headers=headers) #?page=6
    parse_invoices(r.json(), cloudoki, s)

    ## SAVVY
    url = 'https://savvy.harvestapp.com%s'
    savvy = get_or_create(s, Account, name="Savvy")

    ### Add Harvest Clients
    r = requests.get(url % '/clients', headers=headers)
    parse_partners(r.json(), s)

    ### Add Harvest invoices
    r = requests.get(url % '/invoices', headers=headers)
    parse_invoices(r.json(), savvy, s)

    db.commit()
