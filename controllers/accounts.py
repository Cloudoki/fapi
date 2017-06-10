import json, collector
from flask import jsonify
from flask_restful import Resource
from flask_restful.utils import cors
from models.account import Account
from models.document import Document
from models.tag import Tag
from datetime import datetime
from dateutil.relativedelta import relativedelta
from __init__ import db

class Accounts(Resource):
    @cors.crossdomain(origin='*')
    def get(self):

        return jsonify(db.query(Account).all())

class SingleAccount(Resource):
    @cors.crossdomain(origin='*')
    def get(self, accountId):

        return jsonify(db.query(Account).filter_by(id=accountId).first())

class AccountTotals(Resource):
    @cors.crossdomain(origin='*')
    def get(self, accountId):

        balance = self.parseBalance()

        # !HACK!
        # Combining accounts Lab Gent, CloudokiLX and Savvy if id == 1

        if accountId == 1:
            turnover, expected = self.parseTotals(1)
            turnover3, expected3 = self.parseTotals(3)
            turnover += turnover3
            expected += expected3
        else:
            turnover, expected = self.parseTotals(accountId)

        return jsonify({
            'balance': balance,
            'balance_eu': '€{:,.2f}'.format(balance),
            'turnover': turnover,
            'turnover_eu': '€{:,.2f}'.format(turnover),
            'expected': expected,
            'expected_eu': '€{:,.2f}'.format(expected)})

    def parseTotals(self, accountId):

        account  = db.query(Account).filter_by(id=accountId).first()
        turnover = 0
        expected = 0

        # Turn-over 12 months
        invoices = db.query(Document).filter(
            Document.date >= datetime.now() - relativedelta(years=1),
            Document.tags.any(Tag.slug.in_(['open', 'paid'])),
            Document.tags.any(Tag.slug == 'invoice'),
            Document.account == account).all()

        for document in invoices:
            meta = json.loads(document.meta)
            turnover += meta['amount'] - meta['tax_amount']

        # Expected
        invoices = db.query(Document).filter(
            Document.tags.any(Tag.slug.in_(['open', 'draft'])),
            Document.tags.any(Tag.slug == 'invoice'),
            Document.account == account).all()

        for document in invoices:
            meta = json.loads(document.meta)
            expected += meta['amount'] - meta['tax_amount']

        return turnover, expected

    def parseBalance(self):
        documents = db.query(Document).filter(Document.tags.any(Tag.slug.in_(['invoice', 'bill', 'expense', 'payroll']))).all()

        balance = 0

        # Balance
        for document in documents:
            meta = json.loads(document.meta)
            balance += meta['amount']
            if 'tax_amount' in meta:
                balance -= meta['tax_amount']

        return balance

class AccountRefresh(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        trigger = 0
        trigger += collector.googleLastUpdated()
        trigger += collector.harvestLastUpdated()

        return jsonify({ 'update': True if trigger > 0 else False })
