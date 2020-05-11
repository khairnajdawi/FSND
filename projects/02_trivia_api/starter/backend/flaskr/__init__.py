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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app,resources={r"/*":{"origins":"*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories")
  def get_categories():
    categories_list = Category.query.all()
    categories = [cat.format() for cat in categories_list]
    return jsonify({
      'success': True,
      'categories':categories
    })


  #helper method to paginate questions
  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route("/questions")
  def get_questions():
    questions_list = Question.query.order_by(Question.id.desc()).all()
    current_questions = paginate_questions(request,questions_list)
    if len(current_questions) == 0:
      abort(404)

    categories_list = Category.query.all()
    categories = [cat.format() for cat in categories_list]

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': Question.query.count(),
      'current_category':None,
      'categories':categories
    })



  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>',methods=['DELETE'])
  def delete_question(q_id):
    try:
      question = Question.query.filter(Question.id == q_id).one_or_none()
      if(question):
        question.delete()
      else:
        abort(404)
      
      return jsonify({
        'success': True,
        'deleted': q_id
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def add_questions():
    body = request.get_json()
    question = body.get('question',None)
    answer = body.get('answer',None)
    difficulty = body.get('difficulty',None)
    category = body.get('category',None)
    if(question and answer and difficulty and category):
      new_question = Question(
        question=question,
        answer=answer,
        difficulty=difficulty,
        category=category)
      new_question.insert()
    else:
      abort(400)

    return jsonify(
      {
        'success':True,
        'inserted':new_question.id,
      }
    )

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search',methods=['POST'])
  def search_question():
    term = request.get_json().get('searchTerm')
    questions_list = Question.query.order_by(Question.id.desc()).filter(Question.question.ilike('%{}%'.format(term))).all()
    current_questions = paginate_questions(request,questions_list)
   

    categories_list = Category.query.all()
    categories = [cat.format() for cat in categories_list]

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions),
      'current_category':"All",
      'categories':categories
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    questions_list = Question.query.filter(Question.category==category_id).order_by(Question.id.desc())
    current_questions = paginate_questions(request,questions_list.all())
    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': questions_list.count(),
      'current_category':category_id,
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def get_quize_questions():
    body = request.get_json()
    category = body.get('quiz_category',None)
    previous_questions = body.get('previous_questions',None)
    all_questions = Question.query
    if(previous_questions):
      all_questions = all_questions.filter(~Question.id.in_(previous_questions))
    if(category['id']>0):
      question = all_questions.filter(Question.category==category['id']).first()
    else:
      question = all_questions.first()

    
    return jsonify(
      {
        'success':True,
        'question':question.format() if question else None
      }
    )
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  
  
  return app

    