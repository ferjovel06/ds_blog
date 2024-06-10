from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from blog.models import Post, Comment


# Create your tests here.
# Models test
class PostModelTest(TestCase):
    def setUp(self):
        # Create a new user as author
        self.author = User.objects.create_user(username='testuser', password='12345')

    def test_post_creation(self):
        # Create a new post instance
        post = Post.objects.create(
            author=self.author,
            title='Test Post',
            slug='test-post',
            body='This is a test post body.',
            publish=timezone.now(),
            status='published'
        )

        # Check if the post was created successfully
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.status, 'published')
        self.assertEqual(str(post), 'Test Post')


class CommentModelTest(TestCase):
    def setUp(self):
        # Create a new user as author
        self.author = User.objects.create_user(username='testuser', password='12345')
        # Create a new post instance
        self.post = Post.objects.create(
            author=self.author,
            title='Test Post',
            slug='test-post',
            body='This is a test post body.',
            publish=timezone.now(),
            status='published'
        )

    def test_comment_creation(self):
        # Create a new comment instance associated to the post created before
        comment = Comment.objects.create(
            post=self.post,
            name='Test User',
            email='test@example.com',
            body='This is a test comment body.'
        )
        # Check if the comment was created successfully
        self.assertEqual(comment.name, 'Test User')
        self.assertEqual(comment.post, self.post)
        self.assertTrue(comment.active)
        self.assertEqual(str(comment), f"Comentario de {comment.name} en {comment.post}")
