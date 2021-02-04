from aiohttp import web
from pymongo.collection import Collection
import time
import smtplib

class CreationHandler:
    def __init__(self, db_collection : Collection, smtp_host : str, smtp_port: int):
        self.db_collection = db_collection
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_mail(self, email : str, message : str):
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as client:
            client.ehlo()
            client.sendmail('test@test.test', email, message)
            print("Sending mail to : " + email + ". Content : " + message + "\n")

    async def handle_creation(self, request):
        '''
            This coroutine handles the user registration process : inserts the user in the DB, sends the email and returns a response
        '''
        data = await request.post()

        try:
            username = data['username']
            password = data['password']
            email = data['email']
            verification_code = str(abs(hash(email)) % (10 ** 4))
            code_timestamp = time.time()

            #Look into the DB to see if the username of email address are already in use
            existing_user = self.db_collection.find_one(
                { 
                    "$or": [ { "email": email }, { "username": username } ]
                }
            )
            if existing_user is not None:
                response_obj = { 'status' : 'failed', 'reason': "Username or email already exists/is already linked to an account"}
                return web.json_response(response_obj, status=409)

            self.send_mail(email, "Your code is : " + verification_code)

            try:
                user_id = self.db_collection.insert_one(
                {
                    'username': username, 
                    'password' : password, 
                    'email' : email, 
                    'verification_code' : verification_code,
                    'code_timestamp' :  code_timestamp
                })
            except Exception as e:
                #If inserting the new user into the database fails, return a 500 error code
                response_obj = { 'status' : 'failed', 'reason': "bllllllla"}
                return web.json_response(e, status=500)

            response_obj = { 'status' : 'success', 'code' : verification_code}
            return web.json_response(response_obj, status=200)
        except KeyError as e:
            #If a field is missing in the HTTP POST content
            response_obj = { 'status' : 'failed', 'reason': "Bad request" }
            return web.json_response(response_obj, status=400)

        

        
