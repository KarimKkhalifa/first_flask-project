import unittest
import os
from blog import app, db
from werkzeug.security import generate_password_hash

from models import User, Posts

app.config["TESTING"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'


class TestCase(unittest.TestCase):

    def setUp(self):
        db.create_all()
        self.user = User(login='test_user', password_hash=generate_password_hash('test_password'))
        db.session.add(self.user)
        db.session.commit()
        self.new_user = User.query.filter_by(login='test_user').first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_register_password_not_equal(self):
        tester = app.test_client(self)
        response1 = tester.post('/register',
                                data=dict(login='tests_user', password='test_password', password2='daadsa'),
                                follow_redirects=True)
        self.assertIn(b'passwords are not equal', response1.data)

    def test_register_fields_not_full(self):
        tester = app.test_client(self)
        response1 = tester.post('/register',
                                data=dict(login='tests_user'),
                                follow_redirects=True)
        self.assertIn(b'fill all fields', response1.data)

    def test_posts_page_sort(self):
        tester = app.test_client(self)
        response1 = tester.post('/posts_page', data=dict(newest='newest'))
        assert response1.status_code == 200
        response = tester.get('/posts_page', content_type='html/txt')
        assert response.status_code == 200

    def test_home_page_text(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/txt')
        self.assertTrue(b'hello' in response.data)
        assert response.status_code == 200

    def test_user_page(self):
        tester = app.test_client(self)
        response1 = tester.post(
            '/login',
            data=dict(
                login='test_user', password='test_password'
            ),
            follow_redirects=True
        )
        assert response1.status_code == 200
        response = tester.get('/user')
        assert response.status_code == 200

    def test_user_page_logout(self):
        tester = app.test_client(self)
        response1 = tester.post(
            '/login',
            data=dict(
                login='test_user', password='test_password'
            ),
            follow_redirects=True
        )
        assert response1.status_code == 200
        response = tester.post('/user', data=dict(login='test_user', password='test_password'),
                               follow_redirects=True)
        assert response.status_code == 200

    def test__login_is_not_full(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(password="wrong"),
            follow_redirects=True
        )
        self.assertIn(b'fill login and password fields', response.data)

    def test__login_is_not_correct(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(login='wrong', password="wrong"),
            follow_redirects=True
        )
        self.assertIn(b'Login or password is not correct', response.data)

    def test_user_page_del(self):
        tester = app.test_client(self)
        response1 = tester.post(
            '/login',
            data=dict(
                login='test_user', password='test_password'
            ),
            follow_redirects=True
        )
        assert response1.status_code == 200
        response = tester.get(f'/user/delete', follow_redirects=True)
        assert response.status_code == 200

    def test_register_user(self):
        tester = app.test_client(self)
        response1 = tester.get('/register', content_type='html/txt')
        assert response1.status_code == 200
        response = tester.post(
            '/register',
            data=dict(
                login='test_user1', password='test_password1', password2='test_password1'
            ),
            follow_redirects=True
        )
        assert response.status_code == 200

    def test_login_user(self):
        tester = app.test_client(self)
        response = tester.post('/login',
                               data=dict(login='test_user1', password='test_password1'),
                               follow_redirects=True
                               )
        assert response.status_code == 200

    def test_posts_page(self):
        tester = app.test_client(self)
        response = tester.get('/posts_page', content_type='html/txt')
        assert response.status_code == 200

    def test_create_post_get(self):
        tester = app.test_client(self)
        response1 = tester.post(
            '/login',
            data=dict(
                login='test_user', password='test_password'
            ),
            follow_redirects=True
        )
        assert response1.status_code == 200
        response = tester.get('/create', content_type='html/txt')
        assert response.status_code == 200

    def test_create_post(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data=dict(
                login='test_user', password='test_password'
            ),
            follow_redirects=True
        )
        tester.post('/create', data=dict(title='1_post_test', text='1_post_test_text', user_id=self.new_user),
                    follow_redirects=True)
        response = tester.get('/posts_page', follow_redirects=True)
        assert response.status_code == 200

    def test_post_detail(self):
        tester = app.test_client(self)
        post = Posts(
            title='test_post1',
            text='test_text1',
            user_id=1
        )
        db.session.add(post)
        db.session.commit()
        response = tester.get(f'/posts_page/{post.id}', content_type='html/txt')
        assert response.status_code == 200

    def test_post_delete(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data=dict(
                login='test_user', password='test_password'
            ),
            follow_redirects=True)
        post = Posts(
            title='test_post1',
            text='test_text1',
            user_id=1
        )
        db.session.add(post)
        db.session.commit()
        response = tester.get(f'/posts_page/{post.id}/delete', follow_redirects=True)
        assert response.status_code == 200

    def test_post_update_get(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data=dict(
                login='test_user', password='test_password'
            ),
            follow_redirects=True)
        post = Posts(
            title='test_post1',
            text='test_text1',
            user_id=1
        )
        db.session.add(post)
        db.session.commit()
        response1 = tester.get(f'/posts_page/{post.id}/update')
        assert response1.status_code == 200

    def test_post_update(self):
        tester = app.test_client(self)
        post = Posts(
            title='test_post1',
            text='test_text1',
            user_id=1
        )
        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)
        response1 = tester.post('/login', data=dict(login='test_user', password_hash='test_password'),
                                follow_redirects=True)
        assert response1.status_code == 200
        response = tester.post(
            f'/posts_page/{post.id}/update',
            data=dict(
                title='test_title', text='test_text',
                user_id=1
            ),
            follow_redirects=True
        )
        statuscode = response.status_code
        assert statuscode == 200


if __name__ == '__main__':
    unittest.main()  # pragma no cover
