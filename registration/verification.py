from aiohttp import web


class VerificationHandler:
    def __init__(self, client : MongoClient):
        self.client = client

    async def handle_verification(self, request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name + ". This is the verification API\n"
        return web.Response(text=text)

