import tempfile
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Test group',
            slug='group_test'
        )
        cls.group_2 = Group.objects.create(
            title='Test group2',
            slug='group_test_2'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Post1',
            author=self.user,
            group=self.group)

    def test_create_post_form(self):

        post_count = Post.objects.all().count()
        form_data = {
            'text': 'Post2',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(
            Post.objects.all().count(),
            post_count + 1,
            "Post didn't save"
        )
        self.assertTrue(
            Post.objects.filter(
                text='Post1',
                group=self.group
            ).exists())
        self.assertTrue(
            Post.objects.filter(
                text='Post1',
                author=self.user
            ).exists())

    def test_edit_post_form(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new post',
            'group': self.group_2.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True)
        modified_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, reverse('posts:post_detail', args=(1,)))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(
            modified_post.text,
            self.post.text,
            "text didn't change"
        )
        self.assertNotEqual(
            modified_post.group,
            self.post.group,
            "Group didn't change"
        )
        self.assertEqual(modified_post.group.title,
                         'Test group2')

    def test_create_post_form_guest(self):

        form_data = {
            'text': 'Post2',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_post_form_guest(self):
        form_data = {
            'text': 'new post',
            'group': self.group_2.id
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_form_with_wrong_data(self):
        form_data = {
            'text': ' ',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_form_edit_with_wrong_data(self):
        form_data = {
            'text': ' ',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='group',
            slug='group_1'
        )
        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.gif,
            content_type='image/gif'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_saving_post_with_image_in_db(self):
        form_data = {
            'text': 'Test top6',
            'author': self.user,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user}))
        self.assertTrue(Post.objects.filter(text='Test top6').exists())

    def test_upload_non_image_file(self):
        text = 'Test post555'
        file = SimpleUploadedFile(
            'test.txt',
            b'1234',
            content_type='text/plain'
        )
        response = self.authorized_client.post(reverse('posts:post_create'), {
            'text': text,
            'image': file
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(text=text).exists())
