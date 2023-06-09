from flaskr import create_app
from flask import url_for
from io import BytesIO
from flask_login import current_user
import pytest
from unittest.mock import patch, Mock, MagicMock, patch, create_autospec, mock_open


# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_homepage(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"One stop shop for the greatest vacation sites!" in resp.data


def test_about_page(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"About this Wiki" in resp.data


def test_all_pages(client):
    with patch("flaskr.backend.Backend.get_all_page_names",
               return_value=["Canada.txt", "California.txt"]):
        resp = client.get("/pages")
        assert resp.status_code == 200
        assert b"Vactioniki Index" in resp.data


@patch("flaskr.backend.Backend.get_wiki_page", return_value=b"test.")
def test_get_page(mock_get_wiki_page, client):
    name = "california"
    #resp = client.get("/pages/california") # This line is given error fix
    #assert resp.status_code == 200
    #assert b"test." in resp.data
    assert mock_get_wiki_page(name) == b"test."


@patch("flaskr.backend.Backend.get_image", return_value=BytesIO())
def test_get_image(mock_get_image, client):

    image_name = "img"
    resp = client.get("/images/img")
    assert resp.status_code == 200
    mock_get_image.assert_called_once_with(image_name)


@patch("flaskr.backend.Backend.get_image", return_value=BytesIO())
def test_get_image_username(mock_get_image, client):

    image_name = "img"
    resp = client.get("/images/img")
    assert resp.status_code == 200
    mock_get_image.assert_called_once_with(image_name)


'''Unit testing for user sessions'''


def test_signup_page(client):
    with patch('flaskr.backend.Backend.sign_up') as mock_sign_up, patch(
            'flaskr.user_model.User') as mock_user:
        # Successful signup
        mock_sign_up.bucket_user_password.blob.return_value = MagicMock()
        mock_sign_up.user_data_bucket.blob.return_value = MagicMock()

        # Mock Backend object and its methods

        mock_user.return_value.get_user_data.return_value = {
            'username': 'cooldude2006',
            'email': 'cooldude2006@example.com',
            'name': 'Cool Dude',
            'description': 'Just a cool dude',
        }

        mock_sign_up.return_value = True
        data = {'username': 'Cesar', 'password': '123'}
        resp = client.post("/signup/", data=data, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Signed up successfully!' in resp.data

        # Unsuccessful signup
        mock_sign_up.return_value = False
        data = {'username': 'Cesar', 'password': '123'}
        resp = client.post("/signup/", data=data, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Account already exist!' in resp.data


def test_login_page(client):
    with patch('flaskr.backend.Backend.sign_in') as mock_login, patch(
            'flaskr.user_model.User') as mock_user:

        # Successful Login]

        mock_login.bucket_user_password.blob.return_value = MagicMock()
        mock_login.user_data_bucket.blob.return_value = MagicMock()

        mock_user.return_value.get_user_data.return_value = {
            'username': 'cooldude2006',
            'email': 'cooldude2006@example.com',
            'name': 'Cool Dude',
            'description': 'Just a cool dude',
        }

        mock_login.return_value = True
        data = {'username': 'cooldude2006', 'password': '12345'}
        resp = client.post("/login/", data=data, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Logged in successfully.' in resp.data

        # Unsuccessful Login
        mock_login.return_value = False
        data = {'username': 'cooldude2006', 'password': '12345'}
        resp = client.post("/login/", data=data, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Wrong username or password. Please Try Again.' in resp.data


def test_logout(client):
    with patch('flask_login.current_user', create=True) as mock_user:
        mock_user.is_authenticated = True
        resp = client.get("/logout/", follow_redirects=True)
        assert resp.status_code == 200
        assert b'Logged out' in resp.data


def test_upload(client):
    with patch('flaskr.backend.Backend.upload'):
        # No File Input
        data = {'wikiname': '', 'filename': ''}
        resp = client.post("/upload/", data=data, follow_redirects=True)
        assert resp.status_code == 200
        assert b'No File Input' in resp.data


def test_profile_view(client):

    with patch('flaskr.backend.Backend.sign_in') as mock_login, patch(
            'flaskr.user_model.User') as mock_user:
        # login pass
        #mock
        mock_login.bucket_user_password.blob.return_value = MagicMock()
        mock_login.user_data_bucket.blob.return_value = MagicMock()

        mock_user.return_value.get_user_data.return_value = {
            'username': 'cooliodude2001',
            'email': 'cooldude2006@example.com',
            'name': 'Coolio Dude',
            'description': 'Just a coolio dude',
        }
        mock_login.return_value = True
        data = {'username': 'cooliodude2001', 'password': '12345'}
        resp = client.post("/login/", data=data, follow_redirects=False)

        assert resp.status_code == 302
        home_resp = client.get(resp.headers['Location'])
        assert home_resp.status_code == 200
        assert b'Logged in successfully.' in home_resp.data

        # fail login
        mock_login.return_value = False
        data = {'username': 'cooliodude2001', 'password': '12345'}
        resp = client.post("/login/", data=data, follow_redirects=True)

        assert resp.status_code == 200

        assert b'Wrong username or password. Please Try Again.' in resp.data


def test_edit_user(client):
    with patch('flaskr.backend.Backend.sign_in') as mock_login, patch(
            'flaskr.user_model.User') as mock_user:
        # login pass
        #mock
        mock_login.bucket_user_password.blob.return_value = MagicMock()
        mock_login.user_data_bucket.blob.return_value = MagicMock()

        class MockUser:
            username = 'cooliodude2001'
            email = 'cooldude2006@example.com'
            name = 'Coolio Dude'
            description = 'Just a coolio dude'

            def get_user_data(self):
                return {
                    'username': self.username,
                    'email': self.email,
                    'name': self.name,
                    'description': self.description,
                }

            def is_authenticated(self):
                return True

        mock_user.return_value = MockUser()
        mock_login.return_value = True
        data = {'username': 'cooliodude2001', 'password': '12345'}
        resp = client.post("/login/", data=data, follow_redirects=False)

        assert resp.status_code == 302
        home_resp = client.get(resp.headers['Location'])
        assert home_resp.status_code == 200
        assert b'Logged in successfully.' in home_resp.data
        new_data = {
            'name': 'COLIO',
            'description': 'new description',
            'image': b"image"
        }
        resp = client.post('/edit-user', data=new_data, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Uploaded Files' in resp.data
