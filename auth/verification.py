from aiohttp import web

async def handle_verification(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name + ". This is the verification API\n"
    return web.Response(text=text)

