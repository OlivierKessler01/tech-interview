from aiohttp import web
from pymongo.collection import Collection

class VerificationHandler:
    def __init__(self, db_collection : Collection):
        self.db_collection = db_collection

    async def handle_verification(self, request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name + ". This is the verification API\n"
        return web.Response(text=text)

