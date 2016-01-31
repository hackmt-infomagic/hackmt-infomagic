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
				<AppHeader />
				<GraphComponent />
				<div className="footer">
					<div className="small-12 start-button columns">
						<a href="#"><span></span>
							<h1>
								Start
							</h1>
						</a>
					</div>
					<div className="small-12 stop-button columns">
						<a href="#"><span></span>
							<h1>
								Stopping
							</h1>
						</a>
					</div>
				</div>
			</div>
        );
    }
});

module.exports = Overview;