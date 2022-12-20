from typing import Type
from aiohttp import web
from errors import raise_http_error
from models import Session, User, Post
from validate import validate, UserCreateValidate, PostCreateValidate
from auth import hash_password, total_check_authentication
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        return await handler(request)


async def get_item(item_class: Type[User] | Type[Post], item_id: int, session: Session):
    item = await session.get(item_class, item_id)
    if item is None:
        raise raise_http_error(web.HTTPNotFound, f'{item_class.__name__.lower()} not found')
    return item


def user_dict(user: User):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def post_dict(post: Post):
    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        # 'created': post.created.isoformat(),
        'user_id': post.user_id
    }


class UserView(web.View):

    @property
    def session(self):
        return self.request['session']

    async def get(self):
        user_id = int(self.request.match_info['user_id'])
        user = await get_item(User, user_id, self.session)
        return web.json_response(user_dict(user))

    async def post(self):
        user_data_init = await self.request.json()
        user_data = await validate(user_data_init, UserCreateValidate)
        user_data['password'] = hash_password(user_data['password'])
        new_user = User(**user_data)
        self.session.add(new_user)
        try:
            await self.session.commit()
        except IntegrityError:
            raise raise_http_error(web.HTTPBadRequest, 'field is not unique')

        return web.json_response({
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
        })



class PostView(web.View):
    @property
    def session(self):
        return self.request['session']

    async def get(self):
        post_id = self.request.match_info.get('post_id')
        if post_id:
            post = await get_item(Post, int(post_id), self.session)
            return web.json_response(post_dict(post))
        else:
            posts_query = await self.session.execute(select(Post))
            posts = []
            for p in posts_query:
                post = {'id': p[0].id,
                        'title': p[0].title,
                        'content': p[0].content,
                        'created': p[0].created.isoformat(),
                        'user_id': p[0].user_id}
                posts.append(post)
            return web.json_response(posts)

    async def post(self):
        auth_from_headers = self.request.headers.get('Authorization')
        if auth_from_headers:
            user_id = await total_check_authentication(auth_from_headers)
            post_data_init = await self.request.json()
            post_data = await validate(post_data_init, PostCreateValidate)
            if post_data.get('user_id') != user_id:
                raise raise_http_error(web.HTTPForbidden, 'you are not allowed to set non-your user_id')
            new_post = Post(**post_data)
            self.session.add(new_post)
            await self.session.commit()
            return web.json_response(post_dict(new_post))
        else:
            raise raise_http_error(web.HTTPUnauthorized, 'authentication data has not been received')

    async def patch(self):
        auth_from_headers = self.request.headers.get('Authorization')
        if auth_from_headers:
            user_id = await total_check_authentication(auth_from_headers)

            post_id = int(self.request.match_info['post_id'])
            post_patch_data = await self.request.json()
            post = await get_item(Post, int(post_id), self.session)
            if user_id == post.user_id:
                for field, value in post_patch_data.items():
                    if field == 'user_id' and value != user_id:
                        raise raise_http_error(web.HTTPForbidden, 'you are not allowed to change user_id')
                    setattr(post, field, value)
                self.session.add(post)
                await self.session.commit()
                return web.json_response(post_dict(post))
            else:
                raise raise_http_error(web.HTTPForbidden, 'you do not have access rights to change this post')
        else:
            raise raise_http_error(web.HTTPUnauthorized, 'authentication data has not been received')

    async def delete(self):
        auth_from_headers = self.request.headers.get('Authorization')
        if auth_from_headers:
            user_id = await total_check_authentication(auth_from_headers)

            post_id = int(self.request.match_info['post_id'])
            post = await get_item(Post, int(post_id), self.session)
            if user_id == post.user_id:
                await self.session.delete(post)
                await self.session.commit()
                return web.json_response({'status': 'post deleted'})
            else:
                raise raise_http_error(web.HTTPForbidden, 'you do not have access rights to delete this post')
        else:
            raise raise_http_error(web.HTTPUnauthorized, 'authentication data has not been received')
