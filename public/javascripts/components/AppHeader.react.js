/**
 * Created by rayde on 1/30/2016.
 */

var React = require('react');

var AppHeader = React.createClass({
    render: function(){
        return (
            <div className="fixed">
  				<nav className="nav-bar top-bar" data-topbar role="navigation">
  					<div className="row">
  					<div className="small-2 columns">
  						<a href="#">
  							<img src="../images/white-menu.png" width="35px" height="35px"></img>
  						</a>
  					</div>
  						<div className="small-8">
		    				<h1>
		    					Overview
		    				</h1>
    					</div>
					<div className="small-2 columns align-middle">
						<a href="#">
							<img src="../images/white-gear.png" width="35px" height="35px"></img>
						</a>
					</div>
					</div>
  				</nav>


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
								Stop
							</h1>
						</a>
  					</div>
  				</div>


			</div>

        );
    }
});

module.exports = AppHeader;