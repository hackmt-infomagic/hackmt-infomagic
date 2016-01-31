/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var UserStore = require('../stores/UserStore');
var AppHeader = require('./AppHeader.react');

function getAppState(){
    return {
        user: UserStore.getUser(),
        stats: UserStore.getStats()
    }
}

var InfomagicApp = React.createClass({
    getInitialState: function(){
      return getAppState();
    },
    componentDidMount: function(){
        $(document).foundation();
        UserStore.addChangeListener(this._onChange);
    },
    componentDidUpdate: function(){
        $(document).foundation();
        UserStore.removeChangeListener(this._onChange);
    },
    render: function(){
        return (
            <div>
                <AppHeader />
            </div>
        );
    },
    _onChange: function(){
        this.setState(getAppState());
    }
});

module.exports = InfomagicApp;
