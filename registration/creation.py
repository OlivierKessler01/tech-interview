from aiohttp import web
from pymongo import MongoClient
import time
import smtplib

class CreationHandler:
    def __init__(self, db_client : MongoClient, database_name: str, smtp_host : str, smtp_port: int):
        self.db_client = db_client
        self.database_name = database_name
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_mail(self, email : str, message : str):
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as client:
            client.ehlo()
            client.sendmail('test@test.test', email, message)
            print("Sending mail to : " + email + ". Content : " + message + "\n")

    async def handle_creation(self, request):
        '''
            This coroutine handles the user registration process : write in the DB, sends the email and returns a response
        '''
        data = await request.post()

        try:
            username = data['username']
            password = data['password']
            email = data['email']

            db = self.db_client[self.database_name]
            verification_code = '1233456789979'
            code_timestamp = time.time();

            self.send_mail(email, "Your code is : " + verification_code)

            user_id = db.users.insert_one(
                {
                    'username': username, 
                    'password' : password, 
                    'email' : email, 
                    'verification_code' : verification_code,
                    'code_timestamp' :  code_timestamp
                }
            ).inserted_id

            response_obj = { 'status' : 'success', 'code' : verification_code}
            return web.json_response(response_obj, status=200)
        except KeyError as e:
            response_obj = { 'status' : 'failed', 'reason': "Bad request" }
            return web.json_response(response_obj, status=400)

        

        
