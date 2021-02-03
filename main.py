from aiohttp import web
from registration.creation import handle_creation
from registration.verification import handle_verification

app = web.Application()
app.add_routes([web.post('/register', handle_creation),
                web.post('/verify', handle_verification)])

if __name__ == '__main__':
    web.run_app(app)
