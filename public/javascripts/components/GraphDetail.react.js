/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var GraphComponent = require('./GraphComponent.react');
var GraphDetailText = require('./GraphDetailText.react');

var GraphDetail = React.createClass({
    render: function(){
        return(
            <div>
                <GraphComponent />
                <GraphDetailText />
            </div>
        );
    }
});

module.exports = GraphDetail;