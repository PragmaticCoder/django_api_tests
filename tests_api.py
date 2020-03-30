from unittest.mock import patch

import requests
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status

from backend.posts.models import Post, Page
from backend.posts.tests import FACEBOOK_PAGE_ID, FACEBOOK_PAGE_NAME, MESSAGE, TEST_URL


class TestCreatePosts(TestCase):

    def setUp(self):
        self.URL_ENDPOINT = reverse('api-posts:create', kwargs={'version': 1})
        self.user = mommy.make('GrowthUser', is_api_user=True, _fill_optional=True)
        self.user_profile = mommy.make('UserProfile', user=self.user, _fill_optional=True)

        self.json = {
            'token': self.user.login_token,
            'page_id': FACEBOOK_PAGE_ID,
            'page_name': FACEBOOK_PAGE_NAME,
            'message': MESSAGE,
            'zapier_url': TEST_URL,
        }

    @patch('backend.posts.api.create_facebook_post', spec=requests.Response)
    @patch('backend.posts.api.get_page_image', return_value=TEST_URL)
    def test_success(self, mock_create_facebook_post, mock_get_page_image):
        response = self.client.post(self.URL_ENDPOINT, self.json)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.assertTrue(mock_create_facebook_post.called)
        self.assertTrue(mock_get_page_image.called)

        self.assertTrue(mock_create_facebook_post.return_value, requests.Response)
        self.assertTrue(mock_get_page_image.return_value, requests.Response)

    @patch('backend.posts.api.create_facebook_post', spec=requests.Response)
    @patch('backend.posts.api.get_page_image', return_value=TEST_URL)
    def test_success_on_existing_page(self, mock_create_facebook_post, mock_get_page_image):
        page = mommy.make('Page', _fill_optional=True)
        self.json['page_id'] = page.facebook_id
        response = self.client.post(self.URL_ENDPOINT, self.json)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Post.objects.count(), 1)

    @patch('backend.posts.api.create_facebook_post', spec=requests.Response)
    @patch('backend.posts.api.get_page_image', return_value=TEST_URL)
    def test_creates_new_post(self, mock_create_facebook_post, mock_get_page_image):
        response = self.client.post(self.URL_ENDPOINT, self.json)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Page.objects.count(), 1)

    @patch('backend.posts.api.create_facebook_post', spec=requests.Response)
    @patch('backend.posts.api.get_page_image', return_value=TEST_URL)
    def test_creates_new_page(self, mock_create_facebook_post, mock_get_page_image):
        response = self.client.post(self.URL_ENDPOINT, self.json)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Page.objects.count(), 1)

    @patch('backend.posts.api.create_facebook_post', spec=requests.Response)
    @patch('backend.posts.api.get_page_image', return_value=TEST_URL)
    def test_success_when_page_zapier_url_set(self, mock_create_facebook_post, mock_get_page_image):
        response = self.client.post(self.URL_ENDPOINT, self.json)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Page.objects.count(), 1)

    @patch('backend.posts.api.create_facebook_post', spec=requests.Response)
    @patch('backend.posts.api.get_page_image', return_value=TEST_URL)
    def test_updates_page_zapier_url(self, mock_create_facebook_post, mock_get_page_image):
        self.json['zapier_url'] = 'new-url.com'
        response = self.client.post(self.URL_ENDPOINT, self.json)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Page.objects.first().zapier_url, self.json['zapier_url'])

    @patch('backend.posts.api.create_facebook_post', spec=requests.Response)
    @patch('backend.posts.api.get_page_image', return_value=TEST_URL)
    def test_returns_400_when_page_zapier_url_not_set(self, mock_create_facebook_post, mock_get_page_image):
        del self.json['zapier_url']
        response = self.client.post(self.URL_ENDPOINT, self.json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('backend.posts.api.create_facebook_post', spec=requests.Response)
    @patch('backend.posts.api.get_page_image', return_value=None)
    def test_returns_400_when_page_zapier_url_not_set(self, mock_create_facebook_post, mock_get_page_image):
        del self.json['zapier_url']
        response = self.client.post(self.URL_ENDPOINT, self.json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_param(self):
        del self.json['page_id']

        response = self.client.post(self.URL_ENDPOINT, self.json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_access_returns_404(self):
        del self.json['token']

        response = self.client.post(self.URL_ENDPOINT, self.json)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
