from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
import unittest
import json

from creation import handle_creation

class CreationTest(AioHTTPTestCase):
    async def get_application(self):
        app = web.Application()
        app.add_routes([web.post('/register', handle_creation)])
        return app

    @unittest_run_loop
    async def test_handle_creation_ok(self):
        payload = {"email":"test", "password":"test", "username":"username"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 200
        json_response = await resp.json()
        assert "code" in json_response
        assert len(json_response["code"]) > 10

    @unittest_run_loop
    async def test_handle_creation_missing_parameter(self):
        payload = {"email":"test", "password":"test"}
        resp = await self.client.request("POST", "/register", data=payload)
        assert resp.status == 400
        json_response = await resp.json()
        assert "code" not in json_response
        assert "reason" in json_response
        assert json_response["reason"] == "Bad request"

        payload = {"email":"test", "username":"username"}
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
