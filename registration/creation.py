from aiohttp import web
from pymongo.collection import Collection
from passlib.context import CryptContext
import time
import smtplib
import hashlib
import random
import string

class CreationHandler:
    '''
        Collection of function pointers (coroutines whose names are starting
         by handle_*) to pass as route callback function to AIOHTTP server.
    '''
    def __init__(
        self, 
        db_collection : Collection, 
        smtp_host : str, 
        smtp_port: int, 
        crypt_context : CryptContext
    ):
        self.db_collection = db_collection
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.crypt_context = crypt_context

    def send_mail(self, email : str, message : str):
        '''
            As the name entails, this method sends an email 
            with the verification code.
            You will see the output to stdout when executing unit tests.
        '''
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as client:
            client.ehlo()
            client.sendmail('test@test.test', email, message)

    async def handle_creation(self, request) -> web.Response:
        '''
            This coroutine handles the user registration process : 
            Inserts the user in the DB, sends the email and returns a response.

            3 MAIN CASES :
                - No account previously registered : 
                    Create a new one and send the verification code
                - An account exists but has never been verified : 
                    Regenerate the code and send the new one
                - An verified account exists : 
                    Raise a 409 HTTP code
        '''
        data = await request.post()

        try:
            password = data['password']
            email = data['email']
            verification_code = str(
                int(
                    hashlib.sha256(
                        (
                            email + random.choice(string.ascii_letters)
                        ).encode('utf-8')
                    ).hexdigest(), 16
                ) % 10**4
            )

            '''
            Using hash or hashlib sometimes returns 3-digit verification code,
             probably due to a leading 0 in the hash
            '''
            if len(verification_code) == 3:
                verification_code = verification_code + str(
                    random.randint(0, 10)
                )

            if len(verification_code) != 4:
                response_obj = { 'status' : 'failed', 'message': 'Server error'}
                return web.json_response(e, status=500)
           
            code_timestamp = time.time()
            message = "The registration process has been recorded, " \
             "here is your code (also sent via email)"

            #Look into the DB to see if the email address are already in use
            existing_user = self.db_collection.find_one(
                {  "email": email }
            )

            if existing_user is not None:
                #A verified used already exists
                if existing_user['verified'] == True:
                    message = "Email already exists/is already " \
                     "linked to a verified account"
                    response_obj = { 'status' : 'failed', 'message': message}
                    return web.json_response(response_obj, status=409)
                else:
                    '''
                        A user already exists but it has not been verified, 
                        regenerate a code and override the record
                    '''
                    try:
                        self.db_collection.update_one({
                                '_id': existing_user['_id']
                            },
                            {
                                '$set': {
                                    'verification_code' : verification_code,
                                    'code_timestamp' :  code_timestamp,
                                }
                            }, upsert=False)

                        message = "The verification code has been regenerated"
                        self.send_mail(
                            email, "Your code is : " + 
                            verification_code
                        )
                    except Exception as e:
                        response_obj = { 'status' : 'failed', 'message': e}
                        return web.json_response(e, status=500)

            #No user exists, generate one
            else:
                try:
                    user_id = self.db_collection.insert_one(
                    {
                        'password' : self.crypt_context.hash(password), 
                        'email' : email, 
                        'verification_code' : verification_code,
                        'code_timestamp' :  code_timestamp,
                        'verified' : False
                    })
                    self.send_mail(email, "Your code is : " + verification_code)
                except Exception as e:
                    '''
                    If inserting the new user into the database fails, 
                    return a 500 error code
                    '''
                    response_obj = { 'status' : 'failed', 'message': e}
                    return web.json_response(e, status=500)

            response_obj = { 
                'status' : 'success', 
                "message": message,  
                'code' : verification_code
            }
            return web.json_response(response_obj, status=200)
        except KeyError as e:
            #If a field is missing in the HTTP POST content
            response_obj = { 
                'status' : 'failed', 
                'message': "Bad request : field missing" 
            }
            return web.json_response(response_obj, status=400)

        

        
