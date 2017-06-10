from flask import jsonify
from flask_restful import Resource, reqparse
from flask_restful.utils import cors
from models.document import Document
from models.account import Account
from models.tag import Tag
from __init__ import db

parser = reqparse.RequestParser()
parser.add_argument('tags', type=str, help='Tag-based filter with comma separation')
parser.add_argument('exclude', type=str, help='Tag-based exclusion filter with comma separation')

class Documents(Resource):
    @cors.crossdomain(origin='*')
    def get(self, accountId=None, tags=None):

        args = parser.parse_args()

        if accountId and args is None:
            return jsonify(db.query(Account).filter_by(id=accountId).first().documents)

        q = db.query(Document)

        # if args['tags']:
        #     tags = args['tags'].split(',')
        #     for tag in tags:
        #         q = q.filter(Document.tags.any(Tag.slug == tag))

        if args['tags']:
            tags = args['tags'].split(',')
            q = q.filter(Document.tags.any(Tag.slug.in_(tags)))


        if args['exclude']:
            tags = args['exclude'].split(',')
            for tag in tags:
                q = q.filter(~Document.tags.any(Tag.slug == tag))

        if accountId:
            q = q.filter(Document.account == db.query(Account).filter_by(id=accountId).first())

        return jsonify(q.order_by(Document.date).all())


class SingleDocument(Resource):
    @cors.crossdomain(origin='*')
    def get(self, documentId):

        return jsonify(db.query(Document).filter_by(id=documentId).first())
