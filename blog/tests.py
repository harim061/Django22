from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post


# Create your tests here.
class TestView(TestCase):

    def setUp(self):
        self.client = Client()

    def nav_test(self,soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('AboutMe', navbar.text)

    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code,200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual(soup.title.text, 'Blog')


        #navbar = soup.nav
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('AboutMe', navbar.text)
        self.nav_test(soup)

        self.assertEqual(Post.objects.count(),0)
        main_area = soup.find('div', id="main-area")
        self.assertIn('아무 게시물이 없습니다.',main_area.text)

        post_001 = Post.objects.create(title="첫번째 포스트",content="첫번째 포스트입니다.")
        post_002 = Post.objects.create(title="두번째 포스트",content="두번째 포스트입니다.")
        self.assertEqual(Post.objects.count(), 2)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div',id ="main-area")
        self.assertIn(post_001.title,main_area.text)
        self.assertIn(post_002.title,main_area.text)
        self.assertNotIn('아무 게시물이 없습니다.',main_area.text)

    def test_post_detail(self):
        post_001 = Post.objects.create(title="첫번째 포스트",content="첫번째 포스트입니다.")
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')

        #navbar = soup.nav
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('AboutMe', navbar.text)
        self.nav_test(soup)

        self.assertIn(post_001.title, soup.title.text)

        main_area =soup.find('div',id='main-area')
        post_area = main_area.find('div',id='post-area')
        self.assertIn(post_001.title,post_area.text)
        self.assertIn(post_001.content,post_area.text)