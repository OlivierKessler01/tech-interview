from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
import unittest
import json
from pymongo import MongoClient
from passlib.context import CryptContext
import os
from unittest.mock import MagicMock
import time
import base64

from verification import VerificationHandler

class CreationTest(AioHTTPTestCase):

    async def get_application(self):
        '''
            Mocking mongoclient and injecting it in the handler so the test doesn't write in database
        '''

        self.db_client = MongoClient('mongodb://' + os.environ['MONGO_USERNAME']+ ':' + 
            os.environ['MONGO_PASSWORD'] + '@' + os.environ['MONGO_HOST'] + ':' 
            + os.environ['MONGO_PORT'] + '/')
        database = self.db_client[os.environ['MONGO_DATABASE']]
        self.collection = database.users
        #We mock the collection so the database is not affected by the tests
        self.collection.find_one = MagicMock(return_value=None)
        self.collection.update_one = MagicMock(return_value={"inserted_id": "blabla"})
        self.crypt_context = CryptContext(
                        schemes=["pbkdf2_sha256"],
                        default="pbkdf2_sha256",
                        pbkdf2_sha256__default_rounds=30000
                    )

        verification_handler = VerificationHandler(db_collection=self.collection, crypt_context=self.crypt_context)

        app = web.Application()
        app.add_routes([web.post('/verify', verification_handler.handle_verification)])
        return app

    @unittest_run_loop
    async def test_handle_verification_ok(self):
        self.collection.find_one = MagicMock(
            return_value = {
                "password": self.crypt_context.hash("test"), 
                "verified": False, "code_timestamp" : time.time(), 
                "verification_code": "1234",
                "_id" : "dummyid"
            }
        )

        payload = {"verification_code" : "1234"}       
        headers = {"Authorization": "Basic " + base64.b64encode("test@test.com:test".encode("utf-8")).decode("utf-8")}
        resp = await self.client.request("POST", "/verify", data=payload, headers=headers)
        assert resp.status == 200
        json_response = await resp.json() 
        assert json_response["message"] == "The account is now verified."

    @unittest_run_loop
    async def test_handle_verification_stale_code(self):
        self.collection.find_one = MagicMock(
            return_value = {
                "password": self.crypt_context.hash("test"), 
                "verified": False, "code_timestamp" : time.time() - 61, 
                "verification_code": "1234",
                "_id" : "dummyid"
            }
        )

        payload = {"verification_code" : "1234"}
        headers = {"Authorization": "Basic " + base64.b64encode("test@test.com:test".encode("utf-8")).decode("utf-8")}
        resp = await self.client.request("POST", "/verify", data=payload, headers=headers)
        assert resp.status == 403
        json_response = await resp.json() 
        assert json_response["message"] == "The verification code is stale. Please retry calling /register to get a new code."

    @unittest_run_loop
    async def test_handle_verification_bad_password(self):
        self.collection.find_one = MagicMock(
            return_value = {
                "password": self.crypt_context.hash("test1"), 
                "verified": False, "code_timestamp" : time.time(), 
                "verification_code": "1234",
                "_id" : "dummyid"
            }
        )

        payload = {"verification_code" : "1234"}
        headers = {"Authorization": "Basic " + base64.b64encode("test@test.com:test2".encode("utf-8")).decode("utf-8")}
        resp = await self.client.request("POST", "/verify", data=payload, headers=headers)
        assert resp.status == 401
        json_response = await resp.json() 
        assert json_response["message"] == "Unauthorized, bad credentials"

    @unittest_run_loop
    async def test_handle_verification_no_auth_header(self):
        self.collection.find_one = MagicMock(
            return_value = {
                "password": self.crypt_context.hash("test"), 
                "verified": False, "code_timestamp" : time.time(), 
                "verification_code": "1234",
                "_id" : "dummyid"
            }
        )

        payload = {"verification_code" : "1234"}
        resp = await self.client.request("POST", "/verify", data=payload)
        assert resp.status == 401
        json_response = await resp.json() 
        assert "WWW-Authenticate" in resp.headers
        assert json_response["message"] == "Unauthorized : missing BASIC AUTH header"

    @unittest_run_loop
    async def test_handle_verification_bad_code(self):
        self.collection.find_one = MagicMock(
            return_value = {
                "password": self.crypt_context.hash("test"), 
                "verified": False, "code_timestamp" : time.time(), 
                "verification_code": "1234",
                "_id" : "dummyid"
            }
        )

        payload = {"verification_code" : "12345"}
        headers = {"Authorization": "Basic " + base64.b64encode("test@test.com:test".encode("utf-8")).decode("utf-8")}
        resp = await self.client.request("POST", "/verify", data=payload, headers=headers)
        assert resp.status == 403
        json_response = await resp.json() 
        assert json_response["message"] == "Bad verification code."

    @unittest_run_loop
    async def test_handle_verification_missing_code(self):
        payload = {"test" : "test"}
        headers = {"Authorization": "Basic " + base64.b64encode("test@test.com:test".encode("utf-8")).decode("utf-8")}
        resp = await self.client.request("POST", "/verify", data=payload, headers=headers)
        assert resp.status == 400
        json_response = await resp.json() 
        assert json_response["message"] == "Bad request"

    def tearDown(self):
        self.db_client.close()
        super().tearDown()


if __name__ == "__main__":
    unittest.main()
