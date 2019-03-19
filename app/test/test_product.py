import json
import unittest

from app import db
from app.models.product import Product
from app.models.user import User
from app.test.base import BaseTestCase
from app.test.test_auth import register_user, login_user


def create_admin_user_and_sign_in(self):
    register_response = register_user(
        self,
        'new_user@email.com',
        'new_user',
        'test1234')
    register_data = register_response.get_json()
    self.assertTrue(register_data['status'] == 'success')
    self.assertTrue(
        register_data['message'] == 'Successfully registered.')
    self.assertTrue(register_data['Authorization'])
    self.assertTrue(register_response.content_type == 'application/json')
    self.assertEqual(register_response.status_code, 201)

    user = User.find_by_email('new_user@email.com')
    user.admin = True
    db.session.commit()

    login_response = login_user(self, 'new_user@email.com', 'test1234')
    login_data = login_response.get_json()
    self.assertTrue(login_data['status'] == 'success')
    self.assertTrue(login_data['message'] == 'Successfully logged in.')
    self.assertTrue(login_data['Authorization'])
    self.assertTrue(login_response.content_type == 'application/json')
    self.assertEqual(login_response.status_code, 200)
    return login_data['Authorization']

def create_product_happy_path(self):
    jwt_auth = create_admin_user_and_sign_in(self)
    create_product_response = create_product(
        self,
        'python_v3_6',
        'https://www.python.org/downloads/',
        '//p[@class="download-buttons"]/a/text()',
        '//p[@class="download-buttons"]/a/@href',
        jwt_auth)
    create_product_data = create_product_response.get_json()
    return (create_product_response, create_product_data)

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

def update_product(
    self,
    product_name,
    release_info_url,
    xpath_version_number,
    xpath_download_url,
    jwt_auth
):
    request_data = dict(
        product_name=product_name,
        release_info_url=release_info_url,
        xpath_version_number=xpath_version_number,
        xpath_download_url=xpath_download_url)
    return self.client.put(
        f'api/v1/product/{product_name}',
        headers=dict(Authorization=f'Bearer {jwt_auth}'),
        data=json.dumps(request_data),
        content_type='application/x-www-form-urlencoded')

def delete_product(self, product_name, jwt_auth):
    return self.client.delete(
        f'api/v1/product/{product_name}',
        headers=dict(Authorization=f'Bearer {jwt_auth}'),
        content_type='application/x-www-form-urlencoded')


class TestProductBlueprint(BaseTestCase):

    def test_create_product(self):
        with self.client:
            (create_product_response, create_product_data) = create_product_happy_path(self)
            self.assertTrue(create_product_data['status'] == 'success')
            self.assertTrue(create_product_data['message'] == 'New product added: python_v3_6.')
            self.assertTrue(create_product_data['location'] == '/api/product/python_v3_6')
            self.assertTrue(create_product_response.content_type == 'application/json')
            self.assertEqual(create_product_response.status_code, 201)

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
            self.assertEqual(create_product_response.status_code, 400)