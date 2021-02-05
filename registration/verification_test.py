from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
import unittest
import json
from pymongo import MongoClient
from passlib.context import CryptContext
import os
from unittest.mock import MagicMock

from verification import VerificationHandler

class CreationTest(AioHTTPTestCase):

    async def get_application(self):
        '''
            Mocking mongoclient and injecting it in the handler so the test doesn't write in database
        '''

        db_client = MongoClient('mongodb://' + os.environ['MONGO_USERNAME']+ ':' + 
            os.environ['MONGO_PASSWORD'] + '@' + os.environ['MONGO_HOST'] + ':' 
            + os.environ['MONGO_PORT'] + '/')
        database = db_client[os.environ['MONGO_DATABASE']]
        self.collection = database.users
        #We mock the collection so the database is not affected by the tests
        self.collection.find_one = MagicMock(return_value=None)
        self.collection.update_one = MagicMock(return_value={"inserted_id": "blabla"})

        crypt_context = CryptContext(
                        schemes=["pbkdf2_sha256"],
                        default="pbkdf2_sha256",
                        pbkdf2_sha256__default_rounds=30000
                    )

        creation_handler = VerificationHandler(db_collection=self.collection, crypt_context=crypt_context)

        app = web.Application()
        app.add_routes([web.post('/verify', VerificationHandler.handle_verification)])
        return app

    @unittest_run_loop
    async def test_handle_creation_ok(self):
        payload = {"email":"test@test.com", "password":"test"}
        resp = await self.client.request("POST", "/verify", data=payload)
        assert resp.status == 200
        json_response = await resp.json()
        assert "code" in json_response
        assert len(json_response["code"]) == 4
        assert json_response["message"] == "The registration process has been recorded, here is your code (also sent via email)"


if __name__ == "__main__":
    unittest.main()
