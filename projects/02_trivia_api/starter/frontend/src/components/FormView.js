import React, { Component } from 'react';
import $ from 'jquery';

import '../stylesheets/FormView.css';

class FormView extends Component {
  constructor(props){
    super();
    this.state = {
      question: "",
      answer: "",
      difficulty: 1,
      category: 1,
      categories: {}
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


  submitQuestion = (event) => {
    event.preventDefault();
    $.ajax({
      url: '/questions', 
      type: "POST",
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        question: this.state.question,
        answer: this.state.answer,
        difficulty: this.state.difficulty,
        category: this.state.category
      }),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true,
      success: (result) => {
        document.getElementById("add-question-form").reset();
        return;
      },
      error: (error) => {
        alert('Unable to add question. Please try your request again')
        return;
      }
    })
  }

  handleChange = (event) => {
    this.setState({[event.target.name]: event.target.value})
  }

  render() {
    return (
      <div id="add-form">
        <h2>Add a New Trivia Question</h2>
        <form className="form-view col-md-6" id="add-question-form" onSubmit={this.submitQuestion}>
        <div class="input-group mb-3">
          <div class="input-group-prepend">
            <span class="input-group-text" id="span1">Question</span>
          </div>
          <textarea  name="question"  required onChange={this.handleChange} style={{resize:'vertical'}} class="form-control" placeholder="enter question" aria-label="Question" aria-describedby="span1"></textarea>
        </div>
        <div class="input-group mb-3">
          <div class="input-group-prepend">
            <span class="input-group-text" id="span2">Answer</span>
          </div>
          <input type="text"  name="answer" required onChange={this.handleChange} class="form-control" placeholder="Answer" aria-label="Answer" aria-describedby="span2"></input>
        </div>
        <div class="input-group mb-3">
          <div class="input-group-prepend">
            <span class="input-group-text" id="span2">Difficulty</span>
          </div>
          <select name="difficulty" onChange={this.handleChange}  class="form-control" >
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
        </div>
        <div class="input-group mb-3">
          <div class="input-group-prepend">
            <span class="input-group-text" id="span2">Difficulty</span>
          </div>
          <select name="category" onChange={this.handleChange}  class="form-control">
            {Object.keys(this.state.categories).map(id => {
                return (
                  <option key={id} value={this.state.categories[id].id}>{this.state.categories[id].type}</option>
                )
              })}
          </select>
        </div>
          <input type="submit" className="btn btn-primary" value="Add Question" />
        </form>
      </div>
    );
  }
}

export default FormView;
