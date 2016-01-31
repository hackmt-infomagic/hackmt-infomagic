/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var FocusCounter = require('./FocusCounter.react');
var FocusDetail = require('./FocusDetail.react');
var UserStore = require('../stores/UserStore');

function getAppState(){
    return {
        user: UserStore.getUser(),
        stats: UserStore.getStats(),
        currentSession: UserStore.getSession()
    }
}

var Focus = React.createClass({
    getInitialState: function(){
        return getAppState();
    },
    componentDidMount: function(){
        $(document).foundation();
        UserStore.addChangeListener(this._onChange);
    },
    componentDidUpdate: function(){
        $(document).foundation();
    },
    componentWillUnmount: function(){
        UserStore.removeChangeListener(this._onChange);
    },
    renderButtons: function(){
      if(this.state.currentSession.hasOwnProperty('start')){
          return(
              <div className="row">
                  <div className="large-12 columns">
                      <button type="button" value="stop" >Stop</button>
                      <button type="button" value="stop">Pause</button>
                  </div>

              </div>
          );
      }
        else {
          return (
              <div className="row">

                  <div className="large-12 columns">
                      <button type="button" value="start" >Start</button>
                      <button type="button" value="home">Home</button>
                  </div>

              </div>
          );
      }
    },
    render: function(){
        return(
            <div>
                <FocusCounter start={Date.now()}/>
                <FocusDetail />
                {this.renderButtons()}
            </div>
        );
    },
    _onChange: function(){
        this.setState(getAppState());
    }
});

module.exports = Focus;