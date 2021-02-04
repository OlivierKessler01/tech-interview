from aiohttp import web
from pymongo import MongoClient

class VerificationHandler:
    def __init__(self, db_client : MongoClient, database_name: str):
        self.db_client = db_client
        self.database_name = database_name

    async def handle_verification(self, request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name + ". This is the verification API\n"
        return web.Response(text=text)

