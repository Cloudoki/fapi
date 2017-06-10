from flask import Flask
from flask_restful import Resource, Api


from controllers.accounts import Accounts, SingleAccount, AccountTotals, AccountRefresh
from controllers.documents import Documents, SingleDocument
from controllers.partners import Partners, SinglePartner
from controllers.tags import Tags, SingleTag
from controllers.users import Users, SingleUser
from __init__ import db, CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

api = Api(app)

class ApiVersion(Resource):
    def get(self):
        return {'version': 'v1'}

class ApiPing(Resource):
    def get(self):
        return ['success']

# basics
api.add_resource(ApiVersion, '/')
api.add_resource(ApiPing, '/v1')

# routing
api.add_resource(Accounts,          '/v1/accounts')
api.add_resource(SingleAccount,     '/v1/accounts/<int:accountId>')
api.add_resource(AccountTotals,     '/v1/accounts/<int:accountId>/totals')
api.add_resource(AccountRefresh,     '/v1/accounts/refresh')

api.add_resource(Documents,         '/v1/documents',
                                    '/v1/accounts/<int:accountId>/documents')
api.add_resource(SingleDocument,    '/v1/documents/<int:documentId>')

api.add_resource(Partners,          '/v1/partners')
api.add_resource(SinglePartner,     '/v1/partners/<int:partnerId>')

api.add_resource(Tags,              '/v1/tags')
api.add_resource(SingleTag,         '/v1/tags/<string:slug>')

api.add_resource(Users,             '/v1/users')
api.add_resource(SingleUser,        '/v1/users/<int:userId>')

if __name__ == '__main__':
    app.run(debug=True)
