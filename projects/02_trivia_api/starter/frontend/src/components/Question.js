import React, { Component } from 'react';
import '../stylesheets/Question.css';

class Question extends Component {
  constructor(){
    super();
    this.state = {
      visibleAnswer: false
    }
  }

  flipVisibility() {
    this.setState({visibleAnswer: !this.state.visibleAnswer});
  }

  render() {
    const { question, answer, category, difficulty } = this.props;
    return (
      <div className="card " style={{margin:'10px'}}>
        <div className="card-header">
          <img className="category" src={`${category}.svg`}/> &nbsp;&nbsp;
          <a>Difficulty: {difficulty}</a></div>
        <div className="card-body">
        {question} 
        <br></br>
        <div className="show-answer btn btn-default btn-sm"
            onClick={() => this.flipVisibility()}>
            {this.state.visibleAnswer ? 'Hide' : 'Show'} Answer
          </div>
        <div className="answer-holder">
          <span style={{"visibility": this.state.visibleAnswer ? 'visible' : 'hidden'}}>Answer: {answer}</span>
        </div>
        </div>
        <div className="card-footer">
          <img src="delete.png" className="delete" onClick={() => this.props.questionAction('DELETE')}/>      
          </div>
      </div>
    );
  }
}

export default Question;
