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
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
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
    #get page number from request, default is 1
    page = request.args.get('page', 1, type=int)
    #set start and end based on page number
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    #get all questions from selection
    questions = [question.format() for question in selection]
    #get questions based on page number (start till end)
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
  #this end point will read all questions, no category filter applied
  #for a specific category questions, then /category/category_id/questions endpoint is used
  @app.route("/questions")
  def get_questions():
    #get all questions, ordered by id descending, i.e the newest question is on top=+    
    questions_list = Question.query.order_by(Question.id.desc()).all()
    #get selection based on page number
    current_questions = paginate_questions(request,questions_list)
    #if current page has no questions, then return 404 (not found) error
    if len(current_questions) == 0:
      abort(404)

    #get list of all categories
    categories_list = Category.query.all()
    categories = [cat.format() for cat in categories_list]

    #return json response
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
  #end point to delete a question based on question id
  @app.route('/questions/<int:q_id>',methods=['DELETE'])
  def delete_question(q_id):
    try:
      #get the question to be deleted based on it's id
      question = Question.query.filter(Question.id==q_id).one_or_none()
      #if question exist, delete the question, else return 422 (Unproccessable) error
      if(question):
        question.delete()        
      else:
        abort(422)
      
      #return json response, in case of success
      return jsonify({
        'success': True,
        'deleted': q_id
      })
    except :
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
  #end point to add new question, using http post
  @app.route('/questions',methods=['POST'])
  def add_questions():
    #read form data from post request
    body = request.get_json()
    #read post data
    question = body.get('question',None)
    answer = body.get('answer',None)
    difficulty = body.get('difficulty',None)
    category = body.get('category',None)
    #check if all required data is available,
    #if so, then add the question
    if(question and answer and difficulty and category):
      #create Question instance using form data
      new_question = Question(
        question=question,
        answer=answer,
        difficulty=difficulty,
        category=category)
      #add new question to db
      new_question.insert()
    else:
      #in case one or more of required fields are missing, return 422  error
      abort(422)

    #return json response for success
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
  #end point to search for a question
  @app.route('/search',methods=['POST'])
  def search_question():
    #get search term from request
    term = request.get_json().get('searchTerm')
    #get all questions, ordered by id descending, filtering by search term using ilike for case insensitive
    questions_list = Question.query.order_by(Question.id.desc()).filter(Question.question.ilike('%{}%'.format(term))).all()
    current_questions = paginate_questions(request,questions_list)

    #return json response
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions)
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  #end point to get questions based on categories
  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    #get list of all questions filtered by category, ordered by id descending,i.e the newest is on top
    questions_list = Question.query.filter(Question.category==category_id).order_by(Question.id.desc())
    #create paginating for questions
    current_questions = paginate_questions(request,questions_list.all())
    #if current page does not have questions, return not found error
    if len(current_questions) == 0:
      abort(404)

    #return json response for success
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
  #end point to get a question to play
  @app.route('/quizzes',methods=['POST'])
  def get_quize_questions():
    try:
      #get request data, to read category id if exist and previous questions
      body = request.get_json()
      #get category if exist
      category = body.get('quiz_category',None)
      #get previous questions list
      previous_questions = body.get('previous_questions',None)
      #get all questions to choose from
      all_questions = Question.query
      #if there is previous questions, then filter questions removing previous ones
      if(previous_questions):
        all_questions = all_questions.filter(~Question.id.in_(previous_questions))

      #check if a category is choosen, i.e category id is larger than 0 (0 for all categories)
      if(category['id']>0):
        #if category is choosen, then filter question based on this category
        question = all_questions.filter(Question.category==category['id']).first()
      else:
        #no category is choosen, get first question
        question = all_questions.first()

      #return json response for selected question    
      return jsonify(
        {
          'success':True,
          'question':question.format() if question else None
        }
      )
    except:
      abort(500)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #error handler for 404 (Not Found)
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  #error handler for 422 (unprocessable)
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  #error handler for 400 (bad request)
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  
  #error handler for 405 (method not allowed)
  @app.errorhandler(405)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405
  
  # #error handler for 500 
  # @app.errorhandler(500)
  # def bad_request(error):
  #   return jsonify({
  #     "success": False, 
  #     "error": 500,
  #     "message": "internal server error"
  #     }), 500
      
  return app

    