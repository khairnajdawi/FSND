import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    # get categories list
    @app.route("/categories")
    def get_categories():
        # query categories
        categories_list = Category.query.all()
        # create list of categories formatted, then return json response
        categories = [cat.format() for cat in categories_list]
        return jsonify({
            'success': True,
            'categories': categories
        })

    # helper method to paginate questions
    def paginate_questions(request, selection):
        # get page number from request, default is 1
        page = request.args.get('page', 1, type=int)
        # set start and end based on page number
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        # get all questions from selection
        questions = [question.format() for question in selection]
        # get questions based on page number (start till end)
        current_questions = questions[start:end]
        return current_questions

    # this end point will read all questions, no category filter applied
    # for a specific category questions,
    # then /category/category_id/questions endpoint is used
    @app.route("/questions")
    def get_questions():
        # get all questions, ordered by id descending,
        # i.e the newest question is on top=+
        questions_list = Question.query.order_by(Question.id.desc()).all()
        # get selection based on page number
        current_questions = paginate_questions(request, questions_list)
        # if current page has no questions, then return 404 (not found) error
        if len(current_questions) == 0:
            abort(404)

        # get list of all categories
        categories_list = Category.query.all()
        categories = [cat.format() for cat in categories_list]

        # return json response
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': Question.query.count(),
            'current_category': None,
            'categories': categories
        })

    # end point to delete a question based on question id
    @app.route('/questions/<int:q_id>', methods=['DELETE'])
    def delete_question(q_id):
        try:
            # get the question to be deleted based on it's id
            question = Question.query.filter(Question.id == q_id).one_or_none()
            # if question exist, delete the question,
            # else return 422 (Unproccessable) error
            if(question):
                question.delete()
            else:
                abort(422)
            # return json response, in case of success
            return jsonify({
                'success': True,
                'deleted': q_id
            })
        except:
            abort(422)

    # end point to add new question, using http post
    @app.route('/questions', methods=['POST'])
    def add_questions():
        # read form data from post request
        body = request.get_json()
        # read post data
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)
        # check if all required data is available,
        # if so, then add the question
        if(question and answer and difficulty and category):
            # create Question instance using form data
            new_question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category)
            # add new question to db
            new_question.insert()
        else:
            # in case one or more of required fields are missing, return 422
            abort(422)

        # return json response for success
        return jsonify(
            {
                'success': True,
                'inserted': new_question.id,
            }
        )

    #  end point to search for a question
    @app.route('/search', methods=['POST'])
    def search_question():
        #  get search term from request
        term = request.get_json().get('searchTerm')
        # get all questions, ordered by id descending,
        # filtering by search term using ilike for case insensitive
        questions_list = Question.query.order_by(Question.id.desc())\
            .filter(Question.question.ilike('%{}%'.format(term))).all()
        current_questions = paginate_questions(request, questions_list)

        # return json response
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(current_questions)
        })

    # end point to get questions based on categories
    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        # get list of all questions filtered by category,
        # ordered by id descending,i.e the newest is on top
        questions_list = Question.query\
            .filter(Question.category == category_id)\
            .order_by(Question.id.desc())
        # create paginating for questions
        current_questions = paginate_questions(request, questions_list.all())
        # if current page does not have questions, return not found error
        if len(current_questions) == 0:
            abort(404)

        # return json response for success
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': questions_list.count(),
            'current_category': category_id,
        })

    # end point to get a question to play
    @app.route('/quizzes', methods=['POST'])
    def get_quize_questions():
        try:
            # get request data, to read category id and previous questions
            body = request.get_json()
            # get category if exist
            category = body.get('quiz_category', None)
            # get previous questions list
            previous_questions = body.get('previous_questions', None)
            # get all questions to choose from
            all_questions = Question.query
            # if there is previous questions,
            # then filter questions removing previous ones
            if(previous_questions):
                all_questions = all_questions\
                    .filter(~ Question.id.in_(previous_questions))

            # check if a category is choosen,
            # i.e category id is larger than 0 (0 for all categories)
            if(category['id'] > 0):
                # if category is choosen,
                # then filter question based on this category
                question = all_questions\
                    .filter(Question.category == category['id']).first()
            else:
                # no category is choosen, get first question
                question = all_questions.first()

            # return json response for selected question
            return jsonify(
                {
                    'success': True,
                    'question': question.format() if question else None
                }
            )
        except:
            abort(500)

    # error handler for 404 (Not Found)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    # error handler for 422 (unprocessable)
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    # error handler for 400 (bad request)
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    # error handler for 405 (method not allowed)
    @app.errorhandler(405)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    # error handler for 500
    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
