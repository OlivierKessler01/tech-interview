from aiohttp import web
from pymongo import MongoClient
import os 
import time

class CreationHandler:
    def __init__(self, client : MongoClient):
        self.client = client

    async def handle_creation(self, request):
        '''
            This coroutine handles the user registration process : write in the DB, sends the email and returns a response
        '''
        data = await request.post()

        try:
            username = data['username']
            password = data['password']
            email = data['email']

            db = self.client[os.environ['MONGO_DATABASE']]
            verification_code = '1233456789979'
            code_timestamp = time.time();

            user_id = db.users.insert_one(
                {
                    'username': username, 
                    'password' : password, 
                    'email' : email, 
                    'verification_code' : verification_code,
                    'code_timestamp' :  code_timestamp
                }
            ).inserted_id
            print(user_id)

            response_obj = { 'status' : 'success', 'code' : verification_code}
            return web.json_response(response_obj, status=200)
        except KeyError as e:
            response_obj = { 'status' : 'failed', 'reason': "Bad request" }
            return web.json_response(response_obj, status=400)

        

        
