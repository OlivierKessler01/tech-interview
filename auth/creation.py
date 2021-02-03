from aiohttp import web

async def handle_creation(request):
    data = await request.post()

    try:
        username = data['username']
        password = data['password']
        email = data['email']
        response_obj = { 'status' : 'success', 'code' :'1234'}
        return web.json_response(response_obj, status=200)
    except KeyError as e:
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.json_response(response_obj, status=400)

        

        
