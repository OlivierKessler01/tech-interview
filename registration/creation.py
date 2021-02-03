from aiohttp import web

async def handle_creation(request):
    '''
        This coroutine handles the user registration process : write in the DB, sends the email and returns a response
    '''
    data = await request.post()

    try:
        username = data['username']
        password = data['password']
        email = data['email']
        response_obj = { 'status' : 'success', 'code' :'12345678910'}
        return web.json_response(response_obj, status=200)
    except KeyError as e:
        response_obj = { 'status' : 'failed', 'reason': "Bad request" }
        return web.json_response(response_obj, status=400)

        

        
