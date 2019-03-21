import json
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from app import db
from app.models.product import Product
from app.models.user import User
from app.test.base import BaseTestCase
from app.test.test_auth import register_user, login_user
from app.util.dt_format_strings import DT_FORMAT_ISO


def create_admin_user_and_sign_in(self):
    register_response = register_user(
        self,
        'admin@email.com',
        'admin',
        'test1234')
    register_data = register_response.get_json()
    self.assertTrue(register_data['status'] == 'success')
    self.assertTrue(
        register_data['message'] == 'Successfully registered.')
    self.assertTrue(register_data['Authorization'])
    self.assertTrue(register_response.content_type == 'application/json')
    self.assertEqual(register_response.status_code, HTTPStatus.CREATED)

    user = User.find_by_email('admin@email.com')
    user.admin = True
    db.session.commit()

    login_response = login_user(self, 'admin@email.com', 'test1234')
    login_data = login_response.get_json()
    self.assertTrue(login_data['status'] == 'success')
    self.assertTrue(login_data['message'] == 'Successfully logged in.')
    self.assertTrue(login_data['Authorization'])
    self.assertTrue(login_response.content_type == 'application/json')
    self.assertEqual(login_response.status_code, HTTPStatus.OK)
    return login_data['Authorization']

def create_regular_user_and_sign_in(self):
    register_response = register_user(
        self,
        'site_user@email.com',
        'site_user',
        'test5678')
    register_data = register_response.get_json()
    self.assertTrue(register_data['status'] == 'success')
    self.assertTrue(
        register_data['message'] == 'Successfully registered.')
    self.assertTrue(register_data['Authorization'])
    self.assertTrue(register_response.content_type == 'application/json')
    self.assertEqual(register_response.status_code, HTTPStatus.CREATED)

    user = User.find_by_username('site_user')
    user.admin = False
    db.session.commit()

    login_response = login_user(self, 'site_user@email.com', 'test5678')
    login_data = login_response.get_json()
    self.assertTrue(login_data['status'] == 'success')
    self.assertTrue(login_data['message'] == 'Successfully logged in.')
    self.assertTrue(login_data['Authorization'])
    self.assertTrue(login_response.content_type == 'application/json')
    self.assertEqual(login_response.status_code, HTTPStatus.OK)
    return login_data['Authorization']

def create_product_happy_path(self):
    jwt_auth = create_admin_user_and_sign_in(self)
    create_product_response = create_product(
        self,
        'python_v3_7',
        'https://www.python.org/downloads/',
        '//p[@class="download-buttons"]/a/text()',
        '//p[@class="download-buttons"]/a/@href',
        jwt_auth)
    create_product_data = create_product_response.get_json()
    self.assertTrue(create_product_data['status'] == 'success')
    self.assertTrue(create_product_data['message'] == 'New product added: python_v3_7.')
    self.assertTrue(create_product_data['location'] == '/api/product/python_v3_7')
    self.assertTrue(create_product_response.content_type == 'application/json')
    self.assertEqual(create_product_response.status_code, HTTPStatus.CREATED)
    product = Product.find_by_name('python_v3_7')
    self.assertIsNotNone(product)

    newest_version = '3.7.2'
    download_url = 'https://www.python.org/ftp/python/3.7.2/python-3.7.2-macosx10.9.pkg'
    check_time = datetime.utcnow()
    update_time = datetime.utcnow() + timedelta(seconds=3)
    check_time_str = check_time.replace(tzinfo=timezone.utc).strftime(DT_FORMAT_ISO)
    update_time_str = update_time.replace(tzinfo=timezone.utc).strftime(DT_FORMAT_ISO)
    product.newest_version_number = newest_version
    product.download_url = download_url
    product.last_checked = check_time
    product.last_update = update_time
    db.session.commit()

    retrieve_product_response = retrieve_product(self, 'python_v3_7')
    retrieve_product_data = retrieve_product_response.get_json()
    self.assertTrue(retrieve_product_data['product_name'] == 'python_v3_7')
    self.assertTrue(retrieve_product_data['newest_version_number'] == newest_version)
    self.assertTrue(retrieve_product_data['download_url'] == download_url)
    self.assertTrue(retrieve_product_data['last_checked_utc_iso'] == check_time_str)
    self.assertTrue(retrieve_product_data['last_update_utc_iso'] == update_time_str)
    self.assertTrue(retrieve_product_response.content_type == 'application/json')
    self.assertEqual(retrieve_product_response.status_code, HTTPStatus.OK)
    return product, jwt_auth

def create_product(
    self,
    product_name,
    release_info_url,
    xpath_version_number,
    xpath_download_url,
    jwt_auth
):
    request_data = (
        f'product_name={product_name}&'
        f'release_info_url={release_info_url}&'
        f'xpath_version_number={xpath_version_number}&'
        f'xpath_download_url={xpath_download_url}')
    return self.client.post(
        'api/v1/product/',
        headers=dict(Authorization=f'Bearer {jwt_auth}'),
        data=request_data,
        content_type='application/x-www-form-urlencoded')

def retrieve_product(self, product_name):
    return self.client.get(f'api/v1/product/{product_name}')

def update_product(
    self,
    product_name,
    release_info_url,
    xpath_version_number,
    xpath_download_url,
    jwt_auth
):
    request_data = (
        f'release_info_url={release_info_url}&'
        f'xpath_version_number={xpath_version_number}&'
        f'xpath_download_url={xpath_download_url}')
    return self.client.put(
        f'api/v1/product/{product_name}',
        headers=dict(Authorization=f'Bearer {jwt_auth}'),
        data=request_data,
        content_type='application/x-www-form-urlencoded')

def delete_product(self, product_name, jwt_auth):
    return self.client.delete(
        f'api/v1/product/{product_name}',
        headers=dict(Authorization=f'Bearer {jwt_auth}'),
        content_type='application/x-www-form-urlencoded')


class TestProductBlueprint(BaseTestCase):

    def test_create_product(self):
        with self.client:
            create_product_happy_path(self)

    def test_create_product_already_exists(self):
        product = Product(
            product_name='python_v3_7',
            release_info_url='https://www.python.org/downloads/',
            xpath_version_number='//p[@class="download-buttons"]/a/text()',
            xpath_download_url='//p[@class="download-buttons"]/a/@href')
        db.session.add(product)
        db.session.commit()
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            create_product_response = create_product(
                self,
                'python_v3_7',
                'https://www.python.org/downloads/',
                '//p[@class="download-buttons"]/a/text()',
                '//p[@class="download-buttons"]/a/@href',
                jwt_auth)
            create_product_data = create_product_response.get_json()
            self.assertTrue(create_product_data['status'] == 'fail')
            self.assertTrue(create_product_data['message'] == 'Product name: python_v3_7 already exists, must be unique.')
            self.assertTrue(create_product_response.content_type == 'application/json')
            self.assertEqual(create_product_response.status_code, HTTPStatus.CONFLICT)

    def test_create_product_invalid_product_name(self):
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            create_product_response = create_product(
                self,
                'python v3.6',
                'https://www.python.org/downloads/',
                '//p[@class="download-buttons"]/a/text()',
                '//p[@class="download-buttons"]/a/@href',
                jwt_auth)
            create_product_data = create_product_response.get_json()
            self.assertTrue('errors' in create_product_data)
            self.assertTrue('product_name' in create_product_data['errors'])
            self.assertTrue('contains one or more invalid characters' in create_product_data['errors']['product_name'])
            self.assertTrue(create_product_data['message'] == 'Input payload validation failed')
            self.assertEqual(create_product_response.status_code, HTTPStatus.BAD_REQUEST)

    def test_retrieve_product_does_not_exist(self):
        with self.client:
            retrieve_product_response = retrieve_product(self, 'python_v3_7')
            retrieve_product_data = retrieve_product_response.get_json()
            self.assertTrue(retrieve_product_data['status'] == 'fail')
            self.assertTrue(retrieve_product_data['message'].startswith('python_v3_7 not found in database.'))
            self.assertTrue(retrieve_product_response.content_type == 'application/json')
            self.assertEqual(retrieve_product_response.status_code, HTTPStatus.NOT_FOUND)

    def test_update_product(self):
        with self.client:
            product, jwt_auth = create_product_happy_path(self)
            updated_url = 'http://www.test.com'
            updated_xpath_1 = '//table/tr//td/text()'
            updated_xpath_2 = '//div//a/@href'

            update_product_response = update_product(
                self,
                product.product_name,
                updated_url,
                updated_xpath_1,
                updated_xpath_2,
                jwt_auth)
            update_product_data = update_product_response.get_json()
            self.assertTrue(update_product_data['status'] == 'success')
            self.assertTrue(update_product_data['data']['release_info_url'] == updated_url)
            self.assertTrue(update_product_data['data']['xpath_version_number'] == updated_xpath_1)
            self.assertTrue(update_product_data['data']['xpath_download_url'] == updated_xpath_2)
            self.assertTrue(update_product_response.content_type == 'application/json')
            self.assertEqual(update_product_response.status_code, HTTPStatus.OK)

    def test_update_product_does_not_exist(self):
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            update_product_response = update_product(
                self,
                'python_v3_7',
                'https://www.python.org/downloads/',
                '//p[@class="download-buttons"]/a/text()',
                '//p[@class="download-buttons"]/a/@href',
                jwt_auth)
            update_product_data = update_product_response.get_json()
            self.assertTrue(update_product_data['status'] == 'success')
            self.assertTrue(update_product_data['message'] == 'New product added: python_v3_7.')
            self.assertTrue(update_product_data['location'] == '/api/product/python_v3_7')
            self.assertTrue(update_product_response.content_type == 'application/json')
            self.assertEqual(update_product_response.status_code, HTTPStatus.CREATED)

    def test_delete_product(self):
        with self.client:
            product, jwt_auth = create_product_happy_path(self)
            delete_product_response = delete_product(
                self,
                product.product_name,
                jwt_auth)
            self.assertTrue(delete_product_response.content_type == 'application/json')
            self.assertEqual(delete_product_response.status_code, HTTPStatus.NO_CONTENT)

    def test_delete_product_does_not_exist(self):
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            delete_product_response = delete_product(
                self,
                'python_v3_7',
                jwt_auth)
            self.assertTrue(delete_product_response.content_type == 'application/json')
            self.assertEqual(delete_product_response.status_code, HTTPStatus.NO_CONTENT)

    def test_create_product_admin_token_requred(self):
        with self.client:
            jwt_auth = create_regular_user_and_sign_in(self)
            create_product_response = create_product(
                self,
                'python_v3_7',
                'https://www.python.org/downloads/',
                '//p[@class="download-buttons"]/a/text()',
                '//p[@class="download-buttons"]/a/@href',
                jwt_auth)
            create_product_data = create_product_response.get_json()
            self.assertTrue(create_product_data['status'] == 'fail')
            self.assertTrue(create_product_data['message'] == 'You do not have administrator access.')
            self.assertTrue(create_product_response.content_type == 'application/json')
            self.assertEqual(create_product_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_update_product_admin_token_requred(self):
        with self.client:
            product, jwt_auth = create_product_happy_path(self)
            logout_response = self.client.post(
                'api/v1/auth/logout',
                headers=dict(Authorization=f'Bearer {jwt_auth}'))
            logout_data = json.loads(logout_response.data.decode())
            self.assertTrue(logout_data['status'] == 'success')
            self.assertTrue(logout_data['message'] == 'Successfully logged out.')
            self.assertEqual(logout_response.status_code, HTTPStatus.OK)

            jwt_auth = create_regular_user_and_sign_in(self)
            updated_url = 'http://www.test.com'
            updated_xpath_1 = '//table/tr//td/text()'
            updated_xpath_2 = '//div//a/@href'

            update_product_response = update_product(
                self,
                product.product_name,
                updated_url,
                updated_xpath_1,
                updated_xpath_2,
                jwt_auth)
            update_product_data = update_product_response.get_json()
            self.assertTrue(update_product_data['status'] == 'fail')
            self.assertTrue(update_product_data['message'] == 'You do not have administrator access.')
            self.assertTrue(update_product_response.content_type == 'application/json')
            self.assertEqual(update_product_response.status_code, HTTPStatus.UNAUTHORIZED)

        def test_delete_product_admin_token_requred(self):
            with self.client:
                product, jwt_auth = create_product_happy_path(self)
                logout_response = self.client.post(
                    'api/v1/auth/logout',
                    headers=dict(Authorization=f'Bearer {jwt_auth}'))
                logout_data = json.loads(logout_response.data.decode())
                self.assertTrue(logout_data['status'] == 'success')
                self.assertTrue(logout_data['message'] == 'Successfully logged out.')
                self.assertEqual(logout_response.status_code, HTTPStatus.OK)

                jwt_auth = create_regular_user_and_sign_in(self)
                delete_product_response = delete_product(
                    self,
                    product.product_name,
                    jwt_auth)
                delete_product_data = delete_product_response.get_json()
                self.assertTrue(delete_product_data['status'] == 'fail')
                self.assertTrue(delete_product_data['message'] == 'You do not have administrator access.')
                self.assertTrue(delete_product_response.content_type == 'application/json')
                self.assertEqual(delete_product_response.status_code, HTTPStatus.UNAUTHORIZED)