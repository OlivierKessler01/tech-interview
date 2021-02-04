from aiohttp import web
from registration.creation import CreationHandler
from registration.verification import VerificationHandler
from pymongo import MongoClient
import smtplib
import os

db_client = MongoClient('mongodb://' + os.environ['MONGO_USERNAME']+ ':' + 
    os.environ['MONGO_PASSWORD'] + '@' + os.environ['MONGO_HOST'] + ':' 
    + os.environ['MONGO_PORT'] + '/')

creation_handler = CreationHandler(db_client=db_client, database_name=os.environ['MONGO_PASSWORD'], 
smtp_host=os.environ['SMTP_HOST'] ,smtp_port=os.environ['SMTP_PORT'])
verification_handler = VerificationHandler(db_client=db_client, database_name=os.environ['MONGO_DATABASE'])

app = web.Application()
app.add_routes([web.post('/register', creation_handler.handle_creation),
                web.post('/verify', verification_handler.handle_verification)])

if __name__ == '__main__':
    web.run_app(app)
