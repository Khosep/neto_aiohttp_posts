import requests

API_URL = 'http://127.0.0.1:8080'


def test_get_nonexistent_posts():
    resp = requests.get(f'{API_URL}/posts/')
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_user(create_user):
    new_user = create_user
    resp = requests.get(f'{API_URL}/users/{new_user["id"]}')
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data['username'] == new_user['username']


def test_get_post(create_user, create_post):
    new_post = create_post
    resp = requests.get(f'{API_URL}/posts/{new_post["id"]}')
    assert resp.status_code == 200


def test_get_nonexistent_post():
    resp = requests.get(f'{API_URL}/posts/5555')
    assert resp.status_code == 404
    json_data = resp.json()
    assert json_data['message'] == 'post not found'


def test_get_posts(create_post2):
    resp = requests.get(f'{API_URL}/posts/')
    assert resp.status_code == 200


def test_get_user_not_exist():
    resp = requests.get(f'{API_URL}/users/5555')
    assert resp.status_code == 404
    json_data = resp.json()
    assert json_data['message'] == 'user not found'


def test_create_user():
    resp = requests.post(f'{API_URL}/users/', json={'username': 'Ali',
                                                    'email': 'Ab@sultan.org',
                                                    'password': 'p123'})
    assert resp.status_code == 200
    json_data = resp.json()
    assert 'id' in json_data
    assert json_data['email'] == 'Ab@sultan.org'


def test_create_user_with_same_email():
    requests.post(f'{API_URL}/users/', json={'username': 'Sam',
                                             'email': 'Khleb@head.org',
                                             'password': 'psw123321'})
    resp = requests.post(f'{API_URL}/users/', json={'username': 'Otto',
                                                    'email': 'Khleb@head.org',
                                                    'password': 'p'})
    assert resp.status_code == 400
    json_data = resp.json()
    assert json_data['message'] == 'field is not unique'


def test_create_post():
    resp = requests.post(f'{API_URL}/posts/', auth=('Ali', 'p123'), json={'title': 'Немного о себе',
                                                                          'content': 'Красив, чертяга',
                                                                          'user_id': 3})

    assert resp.status_code == 200
    json_data = resp.json()
    assert 'id' in json_data
    assert json_data['content'] == 'Красив, чертяга'


def test_create_post_with_nonexistent_user_id():
    resp = requests.post(f'{API_URL}/posts/', auth=('Ali', 'p123'), json={'title': 'Меня нет',
                                                                          'content': 'Я без user_id',
                                                                          'user_id': 6666})
    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'you are not allowed to set non-your user_id'


def test_create_user_without_required_field():
    resp = requests.post(f'{API_URL}/users/', json={'username': 'Kongo',
                                                    'password': 'qwerty'})
    assert resp.status_code == 400
    json_data = resp.json()
    assert json_data['message'] == {'loc': ['email'], 'msg': 'field required', 'type': 'value_error.missing'}


def test_create_post_without_required_field():
    resp = requests.post(f'{API_URL}/posts/', auth=('Ali', 'p123'), json={'title': 'Validation',
                                                                          'content': 'Create post without user_id',
                                                                          })
    assert resp.status_code == 400
    json_data = resp.json()
    assert json_data['message'] == {'loc': ['user_id'], 'msg': 'field required', 'type': 'value_error.missing'}


def test_create_post_without_permission():
    resp = requests.post(f'{API_URL}/posts/', json={'title': 'Validation',
                                                    'content': 'Create post without user_id',
                                                    'user_id': 3
                                                    })
    assert resp.status_code == 401
    json_data = resp.json()
    assert json_data['message'] == 'authentication data has not been received'


def test_create_post_wrong_username():
    resp = requests.post(f'{API_URL}/posts/', auth=('ali', 'p123'), json={'title': 'Немного о себе',
                                                                          'content': 'Красив, чертяга',
                                                                          'user_id': 3})

    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'wrong username'


def test_create_post_wrong_password():
    resp = requests.post(f'{API_URL}/posts/', auth=('Ali', 'p1234'), json={'title': 'Немного о себе',
                                                                           'content': 'Красив, чертяга',
                                                                           'user_id': 3})

    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'wrong password'


def test_create_post_wrong_user():
    resp = requests.post(f'{API_URL}/posts/', auth=('Ali', 'p123'), json={'title': 'Немного о себе',
                                                                          'content': 'Красив, чертяга',
                                                                          'user_id': 1})

    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'you are not allowed to set non-your user_id'


def test_update_post():
    resp = requests.patch(f'{API_URL}/posts/3', auth=('Ali', 'p123'), json={'title': 'Patch'})
    assert resp.status_code == 200
    json_data = resp.json()
    assert json_data['title'] == 'Patch'


def test_update_post_with_nonexistent_post_id():
    resp = requests.patch(f'{API_URL}/posts/8888', auth=('Ali', 'p123'), json={'title': 'Wrong post_id in http'})
    assert resp.status_code == 404
    json_data = resp.json()
    assert json_data['message'] == 'post not found'


def test_update_post_without_permission():
    resp = requests.patch(f'{API_URL}/posts/3', json={'title': 'Patch'})
    assert resp.status_code == 401
    json_data = resp.json()
    assert json_data['message'] == 'authentication data has not been received'


def test_update_post_wrong_user():
    resp = requests.patch(f'{API_URL}/posts/2', auth=('Ali', 'p123'), json={'title': 'Patch'})
    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'you do not have access rights to change this post'


def test_update_post_nonexistent_user_id():
    resp = requests.patch(f'{API_URL}/posts/3', auth=('Ali', 'p123'), json={'user_id': 6666})
    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'you are not allowed to change user_id'


def test_update_post_wrong_username():
    resp = requests.patch(f'{API_URL}/posts/3', auth=('ali', 'p123'), json={'title': 'Wrong username in auth'})
    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'wrong username'


def test_update_post_wrong_password():
    resp = requests.patch(f'{API_URL}/posts/3', auth=('Ali', 'p1234'), json={'title': 'Wrong password in auth'})
    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'wrong password'


def test_delete_nonexistent_post():
    resp = requests.delete(f'{API_URL}/posts/8888', auth=('Ali', 'p123'))
    assert resp.status_code == 404
    json_data = resp.json()
    assert json_data['message'] == 'post not found'


def test_delete_post_without_permission():
    resp = requests.delete(f'{API_URL}/posts/3')
    assert resp.status_code == 401
    json_data = resp.json()
    assert json_data['message'] == 'authentication data has not been received'


def test_delete_post_wrong_user():
    resp = requests.delete(f'{API_URL}/posts/2', auth=('Ali', 'p123'))
    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'you do not have access rights to delete this post'


def test_delete_post_wrong_username():
    resp = requests.delete(f'{API_URL}/posts/3', auth=('ali', 'p123'))
    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'wrong username'


def test_delete_post_wrong_password():
    resp = requests.delete(f'{API_URL}/posts/3', auth=('Ali', 'p1234'))
    assert resp.status_code == 403
    json_data = resp.json()
    assert json_data['message'] == 'wrong password'


def test_delete_post():
    resp = requests.delete(f'{API_URL}/posts/3', auth=('Ali', 'p123'))
    assert resp.status_code == 200
    assert resp.json() == {'status': 'post deleted'}
