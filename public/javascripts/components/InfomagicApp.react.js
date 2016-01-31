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
    render: function(){
        return (
            <div>
                <AppHeader />
                {this.props.children}
            </div>
        );
    }
});

module.exports = InfomagicApp;
