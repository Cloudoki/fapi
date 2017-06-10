from flask import jsonify
from flask_restful import Resource
from flask_restful.utils import cors
#from models.user import User
from __init__ import db

class Users(Resource):
    @cors.crossdomain(origin='*')
    def get(self):

        return jsonify(db.query(User).all())

class SingleUser(Resource):
    @cors.crossdomain(origin='*')
    def get(self, userId):

        return jsonify(db.query(User).filter_by(id=userId).first())
