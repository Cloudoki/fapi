
import json
from datetime import datetime, timedelta

from vendors import harvest, google
from vendors.googleapi import get_drive_service
from models.document import Document
from models.tag import Tag
from __init__ import db



def googleLastUpdated(accountId = None):

    service = get_drive_service()

    query = db.query(Document).filter(
        Document.updated_at < datetime.now() - timedelta(seconds=15),
        Document.tags.any(Tag.slug == 'source'),
        Document.tags.any(Tag.slug == 'google_sheet'))

    if accountId is not None:
        query.filter(Document.account_id == accountId)

    sheets = query.all()
    amount = 0

    for sheet in sheets:
        results = service.files().get(fileId=sheet.uid, fields='name, modifiedTime').execute()

        if datetime.strptime(results['modifiedTime'], "%Y-%m-%dT%H:%M:%S.%fZ") > sheet.updated_at:
            print('This is what we fetched: %s.' % sheet.name)
            sheet.name = results['name']
            sheet.updated_at = datetime.now()
            google.parseGoogleSheet(sheet)
            amount+= 1

    ### Add Documents to DB
    if amount > 0:
        db.commit()

    return amount

def harvestLastUpdated(accountId = None):
    query = db.query(Document).filter(
        Document.updated_at < datetime.now() - timedelta(seconds=15),
        Document.tags.any(Tag.slug == 'source'),
        Document.tags.any(Tag.slug == 'harvest'))

    if accountId is not None:
        query.filter(Document.account_id == accountId)

    sources = query.all()
    amount = 0

    for source in sources:
        meta = json.loads(source.meta)

        r = harvest.get_request(meta['url'] % '/invoices?updated_since=%s' % source.updated_at)
        invoices = r.json()

        if len(invoices) > 0:
            print('About to parse %s invoices' % len(invoices))

            amount += 1
            source.updated_at = datetime.now()
            harvest.parse_invoices(invoices, source.account)

    if amount > 0:
        db.commit()

    return amount

### MySQL DB
# engine = create_engine('mysql+pymysql://cloudoki:hovering-rabbits-4455-sudoku@cloudoki.com:3306/cloudoki?charset=utf8')
# session = sessionmaker()
# session.configure(bind=engine)
# Base.metadata.create_all(engine)
# db = session()
