/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var AppHeader = require('./AppHeader.react');
var AppFooter = require('./AppFooter.react');

var InfomagicApp = React.createClass({
    componentDidMount: function(){
        $(document).foundation();
    },
    componentDidUpdate: function(){
        $(document).foundation();
    },
    render: function(){
        return (
            <div>
                <AppHeader />
                <h1>
                    Hellow World! New Test. Hell yeah. Test
                </h1>
                <AppFooter />
            </div>
        );
    }
});

module.exports = InfomagicApp;
