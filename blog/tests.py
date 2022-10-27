from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.contrib.auth.models import User

# Create your tests here.
class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_kim = User.objects.create_user(username="kim",password="somepassword")
        self.user_lee = User.objects.create_user(username="lee",password="somepassword")

        self.category_com = Category.objects.create(name="computer",slug="computer")
        self.category_cul = Category.objects.create(name="culture", slug="culture")

        self.post_001 = Post.objects.create(title="첫번째 포스트", content="첫번째 포스트입니다.", author=self.user_kim,category=self.category_com)
        self.post_002 = Post.objects.create(title="두번째 포스트",content="두번째 포스트입니다.",author=self.user_lee,category=self.category_cul)
        self.post_003 = Post.objects.create(title="세번째 포스트", content="세번째 포스트입니다.", author=self.user_lee)

    def nav_test(self,soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('AboutMe', navbar.text)

        home_btn = navbar.find('a',text="Home")
        self.assertEqual(home_btn.attrs['href'], "/")

        blog_btn = navbar.find('a',text="Blog")
        self.assertEqual(blog_btn.attrs['href'], "/blog/")

        about_btn = navbar.find('a',text="AboutMe")
        self.assertEqual(about_btn.attrs['href'], "/about_me/")

    def category_test(self,soup):
        category_card = soup.find('div',id='category-card')
        self.assertIn('Categories',category_card.text)
        self.assertIn(f'{self.category_com} ({self.category_com.post_set.count()})', category_card.text)
        self.assertIn(f'{self.category_cul} ({self.category_cul.post_set.count()})', category_card.text)
        self.assertIn(f'미분류 (1)', category_card.text)


    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code,200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual(soup.title.text, 'Blog')


        #navbar = soup.nav
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('AboutMe', navbar.text)
        self.nav_test(soup)

        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id="main-area")
        self.assertIn(self.post_001.title, main_area.text)
        self.assertIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_001.author.username.upper(), main_area.text)
        self.assertIn(self.post_002.author.username.upper(), main_area.text)
        self.assertNotIn('아무 게시물이 없습니다.', main_area.text)

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id="main-area")
        self.assertIn('아무 게시물이 없습니다.',main_area.text)

        #post_001 = Post.objects.create(title="첫번째 포스트",content="첫번째 포스트입니다.",author=self.user_kim)
        #post_002 = Post.objects.create(title="두번째 포스트",content="두번째 포스트입니다.",author=self.user_lee)


    def test_post_detail(self):
        #post_001 = Post.objects.create(title="첫번째 포스트",content="첫번째 포스트입니다.",author=self.user_kim)
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')

        #navbar = soup.nav
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('AboutMe', navbar.text)
        self.nav_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        main_area =soup.find('div',id='main-area')
        post_area = main_area.find('div',id='post-area')
        self.assertIn(self.post_001.title,post_area.text)
        self.assertIn(self.post_001.content,post_area.text)
        self.assertIn(self.post_001.author.username.upper(),main_area.text)