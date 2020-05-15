import React, { Component } from 'react';
import $ from 'jquery';

import '../stylesheets/QuizView.css';

const questionsPerPlay = 5; 

class QuizView extends Component {
  constructor(props){
    super();
    this.state = {
        quizCategory: null,
        previousQuestions: [], 
        showAnswer: false,
        categories: {},
        numCorrect: 0,
        currentQuestion: {},
        guess: '',
        forceEnd: false
    }
  }

  componentDidMount(){
    $.ajax({
      url: `/categories`, 
      type: "GET",
      success: (result) => {
        this.setState({ categories: result.categories })
        return;
      },
      error: (error) => {
        alert('Unable to load categories. Please try your request again')
        return;
      }
    })
  }

  selectCategory = ({type, id=0}) => {
    this.setState({quizCategory: {type, id}}, this.getNextQuestion)
  }

  handleChange = (event) => {
    this.setState({[event.target.name]: event.target.value})
  }

  getNextQuestion = () => {
    const previousQuestions = [...this.state.previousQuestions]
    if(this.state.currentQuestion.id) { previousQuestions.push(this.state.currentQuestion.id) }

    $.ajax({
      url: '/quizzes', 
      type: "POST",
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        previous_questions: previousQuestions,
        quiz_category: this.state.quizCategory
      }),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true,
      success: (result) => {
        this.setState({
          showAnswer: false,
          previousQuestions: previousQuestions,
          currentQuestion: result.question,
          guess: '',
          forceEnd: result.question ? false : true
        })
        return;
      },
      error: (error) => {
        alert('Unable to load question. Please try your request again')
        return;
      }
    })
  }

  submitGuess = (event) => {
    event.preventDefault();
    const formatGuess = this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    let evaluate =  this.evaluateAnswer()
    this.setState({
      numCorrect: !evaluate ? this.state.numCorrect : this.state.numCorrect + 1,
      showAnswer: true,
    })
  }

  restartGame = () => {
    this.setState({
      quizCategory: null,
      previousQuestions: [], 
      showAnswer: false,
      numCorrect: 0,
      currentQuestion: {},
      guess: '',
      forceEnd: false
    })
  }

  renderPrePlay(){
      return (
          <div className="quiz-play-holder">
              <div className="choose-header d-flex justify-content-center">Choose Category</div>
                  <div className="row  d-flex justify-content-center">
                  <div className="col col-md-4 mb-4">
                  <div className="card">
                    <div className="play-category" onClick={this.selectCategory}>ALL</div>
                  </div>
                  </div>
                  </div>
                <div className="row row-cols-2 row-cols-md-3">
                  {Object.keys(this.state.categories).map(index => {
                    return (
                      <div className="col col-md-4 mb-4"
                        key={this.state.categories[index].id}
                        value={this.state.categories[index].id}
                        onClick={() => this.selectCategory({type:this.state.categories[index].type, id:this.state.categories[index].id})}
                        >
                      <div className="card">
                      <div className="play-category card-body">                      
                        <img className="category" src={`${this.state.categories[index].id}.svg`}/> &nbsp;&nbsp;
                        {this.state.categories[index].type}
                      </div>
                      </div>
                      </div>
                    )
                  })}
              </div>
          </div>
      )
  }

  renderFinalScore(){
    return(
      <div className="quiz-play-holder">
        <div className="final-header"> Your Final Score is {this.state.numCorrect}</div>
        <div className="play-again button btn btn-primary" onClick={this.restartGame}> Play Again? </div>
      </div>
    )
  }

  evaluateAnswer = () => {
    const formatGuess = this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    const answerArray = this.state.currentQuestion.answer.toLowerCase().split(' ');
    return answerArray.includes(formatGuess)
  }

  renderCorrectAnswer(){
    const formatGuess = this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    let evaluate =  this.evaluateAnswer()
    return(
      <div className="quiz-play-holder">
        <div className="quiz-question">{this.state.currentQuestion.question}</div>
        <div className={`${evaluate ? 'correct' : 'wrong'}`}>{evaluate ? "You were correct!" : "You were incorrect"}</div>
        <div className="quiz-answer">{this.state.currentQuestion.answer}</div>
        <div className="next-question button btn btn-primary" onClick={this.getNextQuestion}> Next Question </div>
      </div>
    )
  }

  renderPlay(){
    return this.state.previousQuestions.length === questionsPerPlay || this.state.forceEnd
      ? this.renderFinalScore()
      : this.state.showAnswer 
        ? this.renderCorrectAnswer()
        : (
          <div className="quiz-play-holder">
            <div className="quiz-question">{this.state.currentQuestion.question}</div>
            <form onSubmit={this.submitGuess}>
              <input type="text" name="guess" onChange={this.handleChange}/>
              <input className="submit-guess button btn btn-primary" type="submit" value="Submit Answer" />
            </form>
          </div>
        )
  }


  render() {
    return this.state.quizCategory
        ? this.renderPlay()
        : this.renderPrePlay()
  }
}

export default QuizView;
