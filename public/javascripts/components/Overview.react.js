/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var AppHeader = require('./AppHeader.react');
var GraphComponent = require('./GraphComponent.react');

var Overview = React.createClass({
    render: function(){
        return(
			<div>
				<div className="spacer45"></div>
				<AppHeader />
				<GraphComponent />
				<div className="footer short">
					<div className="small-12 stop-button columns">
						<a href="#"><span></span>
							<h1>
								Start
							</h1>
						</a>
					</div>
				</div>
				<div className="spacer90"></div>
			</div>
        );
    }
});

module.exports = Overview;