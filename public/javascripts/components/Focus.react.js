/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var FocusCounter = require('./FocusCounter.react');
var FocusDetail = require('./FocusDetail.react');

var Focus = React.createClass({
    render: function(){
        return(
            <div>
                <FocusCounter />
                <FocusDetail />
            </div>
        );
    }
});

module.exports = Focus;