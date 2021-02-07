from aiohttp import web
from registration.creation import CreationHandler
from registration.verification import VerificationHandler
from pymongo import MongoClient
from passlib.context import CryptContext
import smtplib
import os
import logging

db_client = MongoClient(
    'mongodb://' 
    + os.environ['MONGO_USERNAME']+ ':' 
    + os.environ['MONGO_PASSWORD'] + '@' 
    + os.environ['MONGO_HOST'] + ':' 
    + os.environ['MONGO_PORT'] + '/'
)

database = db_client[os.environ['MONGO_DATABASE']]
collection = database.users

crypt_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)

creation_handler = CreationHandler(
    db_collection=collection, 
    crypt_context=crypt_context,
    smtp_host=os.environ['SMTP_HOST'], 
    smtp_port=os.environ['SMTP_PORT']
)

verification_handler = VerificationHandler(
    db_collection=collection, 
    crypt_context=crypt_context
)

app = web.Application()
app.add_routes(
    [
        web.post('/register', creation_handler.handle_creation),
        web.post('/verify', verification_handler.handle_verification)
    ]
)

if __name__ == '__main__':
    web.run_app(app)
