from __future__ import unicode_literals

from django.contrib.auth.models import User

from reviewboard.reviews.models import DefaultReviewer
from reviewboard.scmtools.models import Repository, Tool
from reviewboard.site.models import LocalSite
from reviewboard.testing import TestCase


class DefaultReviewerTests(TestCase):
    fixtures = ['test_scmtools']

    def test_for_repository(self):
        """Testing DefaultReviewer.objects.for_repository"""
        tool = Tool.objects.get(name='CVS')

        default_reviewer1 = DefaultReviewer(name="Test", file_regex=".*")
        default_reviewer1.save()

        default_reviewer2 = DefaultReviewer(name="Bar", file_regex=".*")
        default_reviewer2.save()

        repo1 = Repository(name='Test1', path='path1', tool=tool)
        repo1.save()
        default_reviewer1.repository.add(repo1)

        repo2 = Repository(name='Test2', path='path2', tool=tool)
        repo2.save()

        default_reviewers = DefaultReviewer.objects.for_repository(repo1, None)
        self.assertEqual(len(default_reviewers), 2)
        self.assertIn(default_reviewer1, default_reviewers)
        self.assertIn(default_reviewer2, default_reviewers)

        default_reviewers = DefaultReviewer.objects.for_repository(repo2, None)
        self.assertEqual(len(default_reviewers), 1)
        self.assertIn(default_reviewer2, default_reviewers)

    def test_for_repository_with_localsite(self):
        """Testing DefaultReviewer.objects.for_repository with a LocalSite."""
        test_site = LocalSite.objects.create(name='test')

        default_reviewer1 = DefaultReviewer(name='Test 1', file_regex='.*',
                                            local_site=test_site)
        default_reviewer1.save()

        default_reviewer2 = DefaultReviewer(name='Test 2', file_regex='.*')
        default_reviewer2.save()

        default_reviewers = DefaultReviewer.objects.for_repository(
            None, test_site)
        self.assertEqual(len(default_reviewers), 1)
        self.assertIn(default_reviewer1, default_reviewers)

        default_reviewers = DefaultReviewer.objects.for_repository(None, None)
        self.assertEqual(len(default_reviewers), 1)
        self.assertIn(default_reviewer2, default_reviewers)

    def test_review_request_add_default_reviewer_with_inactive_user(self):
        """Testing adding default reviewer with inactive user to review request
        """
        tool = Tool.objects.get(name='CVS')

        default_reviewer1 = DefaultReviewer(name="Test", file_regex=".*")
        default_reviewer1.save()

        repo1 = Repository(name='Test1', path='path1', tool=tool)
        repo1.save()
        default_reviewer1.repository.add(repo1)

        user1 = User(username='User1')
        user1.save()
        default_reviewer1.people.add(user1)

        user2 = User(username='User2', is_active=False)
        user2.save()
        default_reviewer1.people.add(user2)

        review_request = self.create_review_request(repository=repo1,
                                                    submitter=user1)
        diffset = self.create_diffset(review_request)
        self.create_filediff(diffset)
        review_request.add_default_reviewers()
        self.assertIn(user1, review_request.target_people.all())
        self.assertNotIn(user2, review_request.target_people.all())