from flask import jsonify
from flask_restful import Resource
from flask_restful.utils import cors
from models.tag import Tag
from __init__ import db

class Tags(Resource):
    @cors.crossdomain(origin='*')
    def get(self):

        return jsonify(db.query(Tag).all())

class SingleTag(Resource):
    @cors.crossdomain(origin='*')
    def get(self, slug):

        return jsonify(db.query(Tag).filter_by(slug=slug).first())
