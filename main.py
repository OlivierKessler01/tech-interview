from aiohttp import web
from registration.creation import CreationHandler
from registration.verification import VerificationHandler
from pymongo import MongoClient
import smtplib
import os

db_client = MongoClient('mongodb://' + os.environ['MONGO_USERNAME']+ ':' + 
    os.environ['MONGO_PASSWORD'] + '@' + os.environ['MONGO_HOST'] + ':' 
    + os.environ['MONGO_PORT'] + '/')
database = db_client['MONGO_DATABASE']
collection = database.users

creation_handler = CreationHandler(db_collection=collection, smtp_host=os.environ['SMTP_HOST'] ,smtp_port=os.environ['SMTP_PORT'])
verification_handler = VerificationHandler(db_collection=collection)

app = web.Application()
app.add_routes([web.post('/register', creation_handler.handle_creation),
                web.post('/verify', verification_handler.handle_verification)])

if __name__ == '__main__':
    web.run_app(app)
