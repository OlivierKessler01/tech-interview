from aiohttp import web
from pymongo.collection import Collection
from passlib.context import CryptContext
import time
import base64
import re

class VerificationHandler:
    '''
        Collection of function pointers (coroutines whose names are starting by 
        handle_*) to pass as route callback function to AIOHTTP server.
    '''

    def __init__(
        self, 
        db_collection : Collection, 
        crypt_context : CryptContext
    ):
        self.db_collection = db_collection
        self.crypt_context = crypt_context

    async def handle_verification(self, request : web.Request) -> web.Response:
        '''
            This co-routine handles the validation process 
            of the user registration.

            It takes a code that's been previously given to the user 
            and sets the account as verified if the code is right and not stale
            The delay beforing staling is of 1 minute.
        '''
        data = await request.post()
        headers = request.headers

        try:
            #Get email and password from the BASIC AUTH header
            basic_auth_header = re.sub(
                r'^.*?Basic ', '', 
                headers['Authorization']
            )

            email_password_encoded = base64.b64decode(
                basic_auth_header
            ).decode("utf-8")

            email = email_password_encoded[0:email_password_encoded.find(':')]
            password = email_password_encoded[
                email_password_encoded.find(':') + 1:
            ]
        except KeyError as e:
            #HTTP Basic Auth not set, send 401 Unauthorized code
            response_obj = { 
                'status' : 'failed', 
                'message': "Unauthorized : missing BASIC AUTH header"
            }

            return web.json_response(
                response_obj, 
                status=401, 
                headers={
                    "WWW-Authenticate": "Basic realm=\"Access to " \
                    "the verification API\""
                }
            )

        try:
            verification_code = data['verification_code']

            #Look into the DB to see if the email address are already in use
            existing_user = self.db_collection.find_one(
                { "email": email }
            )

            if existing_user is not None:
                if existing_user['verified'] == True:
                    #The user is already verified
                    response_obj = { 
                        'status' : 'failed', 
                        'message': "Email already exists/is already " \
                        "linked to a verified account"
                    }

                    return web.json_response(response_obj, status=409)
                elif existing_user['code_timestamp'] < time.time() - 60:
                    '''
                        If the code has expired 
                        (timestamp in second from epoch - 60 secondes)
                    '''
                    response_obj = { 
                        'status' : 'failed', 
                        'message': "The verification code is stale. " \
                        "Please retry calling /register to get a new code."
                    }

                    return web.json_response(response_obj, status=403)
                elif existing_user['verification_code'] != verification_code:
                    #The code provided is wrong
                    response_obj = { 
                        'status' : 'failed', 
                        'message': "Bad verification code."
                    }

                    return web.json_response(response_obj, status=403)
                else:
                    #The password provided in the HTTP call is right
                    if self.crypt_context.verify(
                        password, 
                        existing_user['password']
                    ):
                        try:
                            self.db_collection.update_one(
                                {'_id': existing_user['_id']},
                                {'$set': {'verified' : True}
                                }, upsert=False
                            )

                            response_obj = { 
                                'status' : 'success',
                                "message": "The account is now verified."
                            }

                            return web.json_response(response_obj, status=200)
                        except Exception as e:
                            response_obj = { 
                                'status' : 'failed', 
                                'message': e
                            }

                            return web.json_response(e, status=500)
                    #The password is wrong
                    else:
                        #HTTP Basic Auth not set, send 401 Unauthorized code
                        response_obj = { 
                            'status' : 'failed', 
                            'message': "Unauthorized, bad credentials"
                        }

                        return web.json_response(response_obj, status=401)
        except KeyError as e:
            #If a field is missing in the HTTP POST content
            response_obj = { 
                'status' : 'failed', 
                'message': "Bad request"
            }

            return web.json_response(response_obj, status=400)

