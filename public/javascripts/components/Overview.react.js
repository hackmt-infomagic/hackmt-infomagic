/**
 * Created by rayde on 1/30/2016.
 */
var React = require('react');
var AppHeader = require('./AppHeader.react');
var GraphComponent = require('./GraphComponent.react');



function onReady(callback) {
    var intervalID = window.setInterval(checkReady, 1000);
    function checkReady() {
        if (document.getElementsByTagName('body')[0] !== undefined) {
            window.clearInterval(intervalID);
            callback.call(this);
        }
    }
}

function show(id, value) {
    document.getElementById(id).style.display = value ? 'block' : 'none';
}



var Overview = React.createClass({
	componentDidMount: function(){
		onReady(function () {
		    show('page', true);
		    show('loading', false);
		});
	},

    render: function(){

        return(
			<div >
				<div className="spacer45"></div>
				<AppHeader />
				<GraphComponent />
				<div id="loading" className="footer short">
					<div className="small-12 stop-button columns">
						<a href="#"><span></span>
							<h1>
								Start Session
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