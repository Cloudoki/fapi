from flask import jsonify
from flask_restful import Resource
from flask_restful.utils import cors
from models.partner import Partner
from __init__ import db

class Partners(Resource):
    @cors.crossdomain(origin='*')
    def get(self):

        return jsonify(db.query(Partner).all())

class SinglePartner(Resource):
    @cors.crossdomain(origin='*')
    def get(self, partnerId):

        return jsonify(db.query(Partner).filter_by(id=partnerId).first())
