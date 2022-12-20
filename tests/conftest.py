from random import randint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Post, User
from pytest import fixture
from datetime import datetime
from auth import hash_password

engine = create_engine('postgresql://sss:sss@127.0.0.1:5431/neto_aiohttp_posts')
Session = sessionmaker(engine)


@fixture(scope='session', autouse=True)
def prepare_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    print('\nTESTING COMPLETED')
    engine.dispose()


@fixture()
def create_user():
    with Session() as session:
        new_user = User(username=f'Eden{randint(1, 99999)}', email=f'{datetime.now()}@mail.org',
                        password=hash_password(f'p{datetime.now()}'))
        session.add(new_user)
        session.commit()
        return {'id': new_user.id, 'username': new_user.username,
                'email': new_user.email, 'password': new_user.password}


@fixture()
def create_post():
    with Session() as session:
        new_post = Post(title='TITLE', content='This is content', user_id=1)
        session.add(new_post)
        session.commit()
        return {'id': new_post.id, 'title': new_post.title, 'content': new_post.content,
                'created': new_post.created, 'user_id': new_post.user_id}


@fixture()
def create_post2():
    with Session() as session:
        new_post = Post(title='HEADER', content='Content only', user_id=1)
        session.add(new_post)
        session.commit()
        return {'id': new_post.id, 'title': new_post.title, 'content': new_post.content,
                'created': new_post.created, 'user_id': new_post.user_id}
