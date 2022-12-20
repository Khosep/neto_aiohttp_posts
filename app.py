from aiohttp import web
from models import engine, Base
from views import session_middleware
from views import PostView, UserView

app = web.Application(middlewares=[session_middleware])


async def orm_context(app: web.Application):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    await engine.dispose()

app.cleanup_ctx.append(orm_context)


app.add_routes([
    web.get('/users/{user_id:\d+}', UserView),
    web.post('/users/', UserView),
    web.get('/posts/', PostView),
    web.get('/posts/{post_id:\d+}', PostView),
    web.post('/posts/', PostView),
    web.patch('/posts/{post_id:\d+}', PostView),
    web.delete('/posts/{post_id:\d+}', PostView),
])

# app.middlewares.append(session_middleware)

if __name__ == '__main__':
    web.run_app(app)
