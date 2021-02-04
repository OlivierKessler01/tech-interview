from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
import unittest
import json
from pymongo import MongoClient
import smtplib
import os
from unittest.mock import MagicMock

from creation import CreationHandler

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
        self.collection.insert_one = MagicMock(return_value={"inserted_id": "blabla"})
        self.collection.update_one = MagicMock(return_value={"inserted_id": "blabla"})
        creation_handler = CreationHandler(db_collection=self.collection, smtp_host=os.environ['SMTP_HOST'] ,smtp_port=os.environ['SMTP_PORT'])

        app = web.Application()
        app.add_routes([web.post('/register', creation_handler.handle_creation)])
        return app

    @unittest_run_loop
    async def test_handle_creation_ok(self):
        payload = {"email":"test@test.com", "password":"test", "username" :"username"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 200
        json_response = await resp.json()
        assert "code" in json_response
        assert len(json_response["code"]) == 4
        assert json_response["message"] == "The registration process has been recorded, here is your code (also sent via email)"

    @unittest_run_loop
    async def test_handle_creation_wrong_method(self):
        resp = await self.client.request("GET", "/register")
        assert resp.status == 405

    @unittest_run_loop
    async def test_handle_creation_user_already_exists(self):
        '''
            A verified account already exists, return 409
        '''
        self.collection.find_one = MagicMock(return_value={"_id" : "blabla", "verified" : True})
        payload = {"email":"test@test.com", "password":"test", "username" :"username"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 409
        json_response = await resp.json()
        assert json_response["message"] == "Username or email already exists/is already linked to a verified account"

    @unittest_run_loop
    async def test_handle_creation_user_already_exists_regenerate_code(self):
        '''
            An account already exists but has never been verified, regenerate code
        '''
        self.collection.find_one = MagicMock(return_value={"_id" : "blabla", "verified" : False})
        self.collection.update_one = MagicMock(return_value={"_id" : "blabla", "verified" : False})
        payload = {"email":"test@test.com", "password":"test", "username" :"username"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 200
        json_response = await resp.json()
        assert json_response["message"] == "The verification code has been regenerated"


    @unittest_run_loop
    async def test_handle_creation_missing_parameter(self):
        payload = {"email":"test@test.com", "password":"test"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 400
        json_response = await resp.json()
        assert "code" not in json_response
        assert "message" in json_response
        assert json_response["message"] == "Bad request"

        payload = {"email":"test@test.com", "username":"username"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 400
        json_response = await resp.json()
        assert "code" not in json_response
        assert "message" in json_response
        assert json_response["message"] == "Bad request"

        payload = {"username":"username", "password":"test"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 400
        json_response = await resp.json()
        assert "code" not in json_response
        assert "message" in json_response
        assert json_response["message"] == "Bad request"

if __name__ == "__main__":
    unittest.main()
