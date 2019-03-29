import json
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from app import db
from app.models.product import Product
from app.models.user import User
from app.test.base import BaseTestCase
from app.test.test_auth import register_user, login_user
from app.util.dt_format_strings import DT_STR_FORMAT_ISO


def create_admin_user_and_sign_in(self):
    register_response = register_user(
        self,
        'admin@email.com',
        'admin',
        'test1234')
    register_data = register_response.get_json()
    self.assertEqual(register_data['status'], 'success')
    self.assertEqual(register_data['message'], 'Successfully registered.')
    self.assertIsNotNone(register_data['Authorization'])
    self.assertEqual(register_response.content_type, 'application/json')
    self.assertEqual(register_response.status_code, HTTPStatus.CREATED)

    user = User.find_by_email('admin@email.com')
    user.admin = True
    db.session.commit()

    login_response = login_user(self, 'admin@email.com', 'test1234')
    login_data = login_response.get_json()
    self.assertEqual(login_data['status'], 'success')
    self.assertEqual(login_data['message'], 'Successfully logged in.')
    self.assertIsNotNone(login_data['Authorization'])
    self.assertEqual(login_response.content_type, 'application/json')
    self.assertEqual(login_response.status_code, HTTPStatus.OK)
    return login_data['Authorization']

def create_regular_user_and_sign_in(self):
    register_response = register_user(
        self,
        'site_user@email.com',
        'site_user',
        'test5678')
    register_data = register_response.get_json()
    self.assertEqual(register_data['status'], 'success')
    self.assertEqual(register_data['message'], 'Successfully registered.')
    self.assertIsNotNone(register_data['Authorization'])
    self.assertEqual(register_response.content_type, 'application/json')
    self.assertEqual(register_response.status_code, HTTPStatus.CREATED)

    user = User.find_by_username('site_user')
    user.admin = False
    db.session.commit()

    login_response = login_user(self, 'site_user@email.com', 'test5678')
    login_data = login_response.get_json()
    self.assertEqual(login_data['status'], 'success')
    self.assertEqual(login_data['message'], 'Successfully logged in.')
    self.assertIsNotNone(login_data['Authorization'])
    self.assertEqual(login_response.content_type, 'application/json')
    self.assertEqual(login_response.status_code, HTTPStatus.OK)
    return login_data['Authorization']

def create_product_happy_path(
        self,
        product_name,
        release_info_url,
        xpath_version_number,
        xpath_download_url,
        jwt_auth):
    create_product_response = create_product(
        self,
        product_name,
        release_info_url,
        xpath_version_number,
        xpath_download_url,
        jwt_auth)
    create_product_data = create_product_response.get_json()
    self.assertEqual(create_product_data['status'], 'success')
    self.assertEqual(create_product_data['message'], f'New product added: {product_name}.')
    self.assertEqual(create_product_data['location'], f'/api/v1/product/{product_name}')
    self.assertEqual(create_product_response.content_type, 'application/json')
    self.assertEqual(create_product_response.status_code, HTTPStatus.CREATED)
    product = Product.find_by_name(product_name)
    self.assertIsNotNone(product)
    return product

def create_product_python(self, jwt_auth):
    product_name = 'python_v3_7'
    release_info_url = 'https://www.python.org/downloads/'
    xpath_download_url = '//p[@class="download-buttons"]/a/text()'
    xpath_version_number = '//p[@class="download-buttons"]/a/@href'
    product = create_product_happy_path(
        self,
        product_name,
        release_info_url,
        xpath_download_url,
        xpath_version_number,
        jwt_auth)
    newest_version = '3.7.2'
    download_url = 'https://www.python.org/ftp/python/3.7.2/python-3.7.2-macosx10.9.pkg'
    check_time = datetime.utcnow()
    update_time = datetime.utcnow() + timedelta(seconds=3)
    check_time_str = check_time.replace(tzinfo=timezone.utc).strftime(DT_STR_FORMAT_ISO)
    update_time_str = update_time.replace(tzinfo=timezone.utc).strftime(DT_STR_FORMAT_ISO)
    product.newest_version_number = newest_version
    product.download_url = download_url
    product.last_checked = check_time
    product.last_update = update_time
    db.session.commit()

    retrieve_product_response = retrieve_product(self, product_name)
    retrieve_product_data = retrieve_product_response.get_json()
    self.assertEqual(retrieve_product_data['product_name'], product_name)
    self.assertEqual(retrieve_product_data['newest_version_number'], newest_version)
    self.assertEqual(retrieve_product_data['download_url'], download_url)
    self.assertEqual(retrieve_product_data['last_checked_utc_iso'], check_time_str)
    self.assertEqual(retrieve_product_data['last_update_utc_iso'], update_time_str)
    self.assertEqual(retrieve_product_response.content_type, 'application/json')
    self.assertEqual(retrieve_product_response.status_code, HTTPStatus.OK)

    product = Product.find_by_name(product_name)
    product_repr = (
        f'Product<('
            f'id=1, '
            f'product_name={product_name}, '
            f'newest_version_number={newest_version})>')
    self.assertEqual(repr(product), product_repr)
    return product

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

def retrieve_all_products(self, page_num, per_page):
    query = f'page={page_num}&per_page={per_page}'
    return self.client.get(f'api/v1/product/?{query}')

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
            jwt_auth = create_admin_user_and_sign_in(self)
            create_product_python(self, jwt_auth)

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
            self.assertEqual(create_product_data['status'], 'fail')
            self.assertEqual(
                create_product_data['message'],
                'Product name: python_v3_7 already exists, must be unique.')
            self.assertEqual(create_product_response.content_type, 'application/json')
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
            self.assertEqual(create_product_data['message'], 'Input payload validation failed')
            self.assertEqual(create_product_response.status_code, HTTPStatus.BAD_REQUEST)

    def test_create_product_invalid_xpath(self):
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            product_name = 'python_v3_7'
            release_info_url = 'https://www.python.org/downloads/'
            xpath_version_number = '      '
            request_data = (
                f'product_name={product_name}&'
                f'release_info_url={release_info_url}&'
                f'xpath_version_number={xpath_version_number}')
            create_product_response =  self.client.post(
                'api/v1/product/',
                headers=dict(Authorization=f'Bearer {jwt_auth}'),
                data=request_data,
                content_type='application/x-www-form-urlencoded')
            create_product_data = create_product_response.get_json()
            self.assertTrue('errors' in create_product_data)
            self.assertTrue('xpath_version_number' in create_product_data['errors'])
            self.assertTrue('xpath_download_url' in create_product_data['errors'])
            self.assertTrue('XPath query must not be null or empty string.',
                create_product_data['errors']['xpath_version_number'])
            self.assertEqual('Missing required parameter in the post body',
                create_product_data['errors']['xpath_download_url'])
            self.assertEqual(create_product_data['message'], 'Input payload validation failed')
            self.assertEqual(create_product_response.status_code, HTTPStatus.BAD_REQUEST)

    def test_retrieve_all_products(self):
        jwt_auth = create_admin_user_and_sign_in(self)
        product_python = create_product_python(self, jwt_auth)
        product_1 = create_product_happy_path(
            self,
            'product_1',
            'https://www.prod1.com',
            '//prod[1]/text()',
            '//prod[1]/@href',
            jwt_auth)
        product_2 = create_product_happy_path(
            self,
            'product_2',
            'https://www.prod2.com',
            '//prod[2]/text()',
            '//prod[2]/@href',
            jwt_auth)
        product_3 = create_product_happy_path(
            self,
            'product_3',
            'https://www.prod3.com',
            '//prod[3]/text()',
            '//prod[3]/@href',
            jwt_auth)
        product_4 = create_product_happy_path(
            self,
            'product_4',
            'https://www.prod4.com',
            '//prod[4]/text()',
            '//prod[4]/@href',
            jwt_auth)
        product_5 = create_product_happy_path(
            self,
            'product_5',
            'https://www.prod5.com',
            '//prod[5]/text()',
            '//prod[5]/@href',
            jwt_auth)
        product_6 = create_product_happy_path(
            self,
            'product_6',
            'https://www.prod6.com',
            '//prod[6]/text()',
            '//prod[6]/@href',
            jwt_auth)
        retrive_products_response = retrieve_all_products(self, 1, 5)
        retrive_products_data = retrive_products_response.get_json()
        self.assertEqual(retrive_products_data['page'], 1)
        self.assertEqual(retrive_products_data['total_pages'], 2)
        self.assertEqual(retrive_products_data['items_per_page'], 5)
        self.assertEqual(retrive_products_data['total_items'], 7)
        self.assertEqual(retrive_products_data['items'][0]['product_name'], 'python_v3_7')
        self.assertEqual(retrive_products_data['items'][1]['product_name'], 'product_1')
        self.assertEqual(retrive_products_data['items'][2]['product_name'], 'product_2')
        self.assertEqual(retrive_products_data['items'][3]['product_name'], 'product_3')
        self.assertEqual(retrive_products_data['items'][4]['product_name'], 'product_4')

        retrive_products_response = retrieve_all_products(self, 2, 5)
        retrive_products_data = retrive_products_response.get_json()
        self.assertEqual(retrive_products_data['page'], 2)
        self.assertEqual(retrive_products_data['total_pages'], 2)
        self.assertEqual(retrive_products_data['items_per_page'], 5)
        self.assertEqual(retrive_products_data['total_items'], 7)
        self.assertEqual(retrive_products_data['items'][0]['product_name'], 'product_5')
        self.assertEqual(retrive_products_data['items'][1]['product_name'], 'product_6')

        retrive_products_response = retrieve_all_products(self, 1, 10)
        retrive_products_data = retrive_products_response.get_json()
        self.assertEqual(retrive_products_data['page'], 1)
        self.assertEqual(retrive_products_data['total_pages'], 1)
        self.assertEqual(retrive_products_data['items_per_page'], 10)
        self.assertEqual(retrive_products_data['total_items'], 7)
        self.assertEqual(retrive_products_data['items'][0]['product_name'], 'python_v3_7')
        self.assertEqual(retrive_products_data['items'][1]['product_name'], 'product_1')
        self.assertEqual(retrive_products_data['items'][2]['product_name'], 'product_2')
        self.assertEqual(retrive_products_data['items'][3]['product_name'], 'product_3')
        self.assertEqual(retrive_products_data['items'][4]['product_name'], 'product_4')
        self.assertEqual(retrive_products_data['items'][5]['product_name'], 'product_5')
        self.assertEqual(retrive_products_data['items'][6]['product_name'], 'product_6')


    def test_retrieve_product_does_not_exist(self):
        with self.client:
            retrieve_product_response = retrieve_product(self, 'python_v3_7')
            retrieve_product_data = retrieve_product_response.get_json()
            self.assertEqual(retrieve_product_data['status'], 'fail')
            self.assertTrue(
                retrieve_product_data['message'].startswith('python_v3_7 not found in database.'))
            self.assertEqual(retrieve_product_response.content_type, 'application/json')
            self.assertEqual(retrieve_product_response.status_code, HTTPStatus.NOT_FOUND)

    def test_update_product(self):
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            product = create_product_python(self, jwt_auth)
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
            self.assertEqual(update_product_data['status'],'success')
            self.assertEqual(update_product_data['data']['release_info_url'], updated_url)
            self.assertEqual(update_product_data['data']['xpath_version_number'], updated_xpath_1)
            self.assertEqual(update_product_data['data']['xpath_download_url'], updated_xpath_2)
            self.assertEqual(update_product_response.content_type, 'application/json')
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
            self.assertEqual(update_product_data['status'], 'success')
            self.assertEqual(update_product_data['message'], 'New product added: python_v3_7.')
            self.assertEqual(update_product_data['location'], '/api/v1/product/python_v3_7')
            self.assertEqual(update_product_response.content_type , 'application/json')
            self.assertEqual(update_product_response.status_code, HTTPStatus.CREATED)

    def test_delete_product(self):
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            product = create_product_python(self, jwt_auth)
            delete_product_response = delete_product(
                self,
                product.product_name,
                jwt_auth)
            self.assertEqual(delete_product_response.content_type, 'application/json')
            self.assertEqual(delete_product_response.status_code, HTTPStatus.NO_CONTENT)

    def test_delete_product_does_not_exist(self):
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            delete_product_response = delete_product(
                self,
                'python_v3_7',
                jwt_auth)
            self.assertEqual(delete_product_response.content_type, 'application/json')
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
            self.assertEqual(create_product_data['status'], 'fail')
            self.assertEqual(
                create_product_data['message'],
                'You are not authorized to perform the requested action.')
            self.assertEqual(create_product_response.content_type, 'application/json')
            self.assertEqual(create_product_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_update_product_admin_token_requred(self):
        with self.client:
            jwt_auth = create_admin_user_and_sign_in(self)
            product = create_product_python(self, jwt_auth)
            logout_response = self.client.post(
                'api/v1/auth/logout',
                headers=dict(Authorization=f'Bearer {jwt_auth}'))
            logout_data = json.loads(logout_response.data.decode())
            self.assertEqual(logout_data['status'], 'success')
            self.assertEqual(logout_data['message'], 'Successfully logged out.')
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
            self.assertEqual(update_product_data['status'], 'fail')
            self.assertEqual(
                update_product_data['message'],
                'You are not authorized to perform the requested action.')
            self.assertEqual(update_product_response.content_type, 'application/json')
            self.assertEqual(update_product_response.status_code, HTTPStatus.UNAUTHORIZED)

        def test_delete_product_admin_token_requred(self):
            with self.client:
                jwt_auth = create_admin_user_and_sign_in(self)
                product = create_product_python(self, jwt_auth)
                logout_response = self.client.post(
                    'api/v1/auth/logout',
                    headers=dict(Authorization=f'Bearer {jwt_auth}'))
                logout_data = json.loads(logout_response.data.decode())
                self.assertEqual(logout_data['status'], 'success')
                self.assertEqual(logout_data['message'], 'Successfully logged out.')
                self.assertEqual(logout_response.status_code, HTTPStatus.OK)

                jwt_auth = create_regular_user_and_sign_in(self)
                delete_product_response = delete_product(
                    self,
                    product.product_name,
                    jwt_auth)
                delete_product_data = delete_product_response.get_json()
                self.assertEqual(delete_product_data['status'], 'fail')
                self.assertEqual(
                    delete_product_data['message'],
                    'You are not authorized to perform the requested action.')
                self.assertEqual(delete_product_response.content_type, 'application/json')
                self.assertEqual(delete_product_response.status_code, HTTPStatus.UNAUTHORIZED)