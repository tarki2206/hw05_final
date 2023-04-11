from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Post, Group

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test-user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/profile.html': f'/profile/{self.user}/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_auth(self):
        html1 = 'create_post.html'
        templates_url_names = {
            'posts/create_post.html': f'/posts/{self.post.id}/edit/',
            f'posts/{html1}': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_non_exist_url(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_anonimus_user_redirect_from_edit_post_page(self):
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_template_for_author_on_edit_post(self):
        response = self.authorized_client_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_authuser_notauthor_redirect_from_edit(self):
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, '/posts/1/')
