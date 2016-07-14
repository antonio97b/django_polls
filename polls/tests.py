import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Question

def create_question(question_text, days):
    """
    Creates a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        future_question = create_question(question_text="Future Question", days=3)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        past_question = create_question(question_text="Past Question", days=-3)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class QuestionViewTests(TestCase):

    def test_index_view_with_no_questions(self):
        """
        If no questions are present, a message should be displayed
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_index_view_with_a_past_question(self):
        create_question(question_text="Past Question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], ["<Question: Past Question>"])

    def test_index_view_with_a_future_question(self):
        create_question(question_text="Future Question", days=+30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_index_view_with_a_past_and_future_question(self):
        create_question(question_text="Future Question", days=+30)
        create_question(question_text="Past Question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], ["<Question: Past Question>"])

    def test_index_view_with_two_past_questions(self):
        create_question(question_text="Past Question 1", days=-30)
        create_question(question_text="Past Question 2", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], ["<Question: Past Question 2>", "<Question: Past Question 1>"])
      

class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return false for questions whose pub_date is older than 1 days
        """
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=thirty_days_ago)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)