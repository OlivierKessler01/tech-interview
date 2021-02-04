from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
import unittest
import json
from pymongo import MongoClient
import smtplib
import os

from creation import CreationHandler

class CreationTest(AioHTTPTestCase):
    async def get_application(self):
        '''
            Mocking mongoclient and injecting it in the handler so the test doesn't write in database
        '''
        db_client = MongoClient('mongodb://' + os.environ['MONGO_USERNAME']+ ':' + 
            os.environ['MONGO_PASSWORD'] + '@' + os.environ['MONGO_HOST'] + ':' 
            + os.environ['MONGO_PORT'] + '/')

        creation_handler = CreationHandler(db_client, database_name=os.environ['MONGO_PASSWORD'], 
        smtp_host=os.environ['SMTP_HOST'] ,smtp_port=os.environ['SMTP_PORT'])


        app = web.Application()
        app.add_routes([web.post('/register', creation_handler.handle_creation)])
        return app

    @unittest_run_loop
    async def test_handle_creation_ok(self):
        payload = {"email":"test@test.com", "password":"test", "username":"username"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 200
        json_response = await resp.json()
        assert "code" in json_response
        assert len(json_response["code"]) > 10

    @unittest_run_loop
    async def test_handle_creation_wrong_method(self):
        resp = await self.client.request("GET", "/register")
        assert resp.status == 405

    @unittest_run_loop
    async def test_handle_creation_missing_parameter(self):
        payload = {"email":"test@test.com", "password":"test"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 400
        json_response = await resp.json()
        assert "code" not in json_response
        assert "reason" in json_response
        assert json_response["reason"] == "Bad request"

        payload = {"email":"test@test.com", "username":"username"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 400
        json_response = await resp.json()
        assert "code" not in json_response
        assert "reason" in json_response
        assert json_response["reason"] == "Bad request"

        payload = {"username":"username", "password":"test"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 400
        json_response = await resp.json()
        assert "code" not in json_response
        assert "reason" in json_response
        assert json_response["reason"] == "Bad request"

if __name__ == "__main__":
    unittest.main()
