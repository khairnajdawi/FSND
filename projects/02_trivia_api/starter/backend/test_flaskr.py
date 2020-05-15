import os
import unittest
import json
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_user = "khairallah"
        self.database_user_pass = "Najdawi"
        self.database_path = "postgresql://{}:{}@{}/{}".\
            format(
                self.database_user,
                self.database_user_pass,
                'localhost:5432',
                self.database_name)
        setup_db(self.app, self.database_path)

        # create new question for add test
        self.new_question = {
            'question': 'Test Question',
            'answer': 'Test Answer',
            'category': 1,
            'difficulty': 1,
        }
        self.bad_new_question = {
            'question': 'Test Question',
            'answer': 'Test Answer',
        }

        #  binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            #  create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # test get all questions, should return http code 200,
    # success with questions list and total questions count.
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    # test if get questions request has page number beyond existing pages
    # should return 404 resource not found error
    def test_404_page_number_not_found(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # test for get categories list
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    #  test post to categories, return 405 not allowed
    def test_post_categories_405_not_allowed(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    # test get questions based on category
    def test_get_categories_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 1)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    # test error 404 not found
    # when try to get questions based on not exist category
    def test_get_categories_questions_not_found(self):
        res = self.client().get('/categories/11111/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # test add new question
    def test_add_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['inserted'])

    # test 422 for try to add question with not all fields provided
    def test_add_new_question_failure(self):
        res = self.client().post('/questions', json=self.bad_new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # test delete question
    def test_delete_question(self):
        # try to get last question, then try to delete
        question = Question.query.order_by(Question.id.desc()).first()
        res = self.client().delete('/questions/{}'.format(question.id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question.id)

    # test delete question failure,
    # must return 422 if question id does not exist
    def test_delete_question_failure(self):
        res = self.client().delete('/questions/11111')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # test get quiz question
    def test_get_quiz(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 1}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # test get quiz using get, return 405 not allowed
    def test_get_quiz_question_error_405(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    # test search questions
    def test_search_question(self):
        res = self.client().post('/search', json={'searchTerm': 'who'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # test search using get, return 405 not allowed
    def test_get_search_question_error_405(self):
        res = self.client().get('/search')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

#  Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
