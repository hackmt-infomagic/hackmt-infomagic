/**
 * Created by rayde on 1/30/2016.
 */

var React = require('react');

var AppHeader = React.createClass({
    render: function(){
        return (
            <div className="fixed">

            <div id="loading" className="loading">Loading&#8230;</div>

  				  <nav id="page" className="nav-bar top-bar" data-topbar role="navigation">
  					<div className="row">
  					<div className="small-2 columns">
  						<a href="#">
  							<img src="../images/white-menu.png" width="35px" height="35px"></img>
  						</a>
  					</div>
  						<div className="small-8">
		    				<h1>
		    					Tracktion
		    				</h1>
    					</div>
					<div className="small-2 columns align-middle">
						<a href="#">
							<img src="../images/white-gear.png" width="35px" height="35px"></img>
						</a>
					</div>
					</div>
  				</nav>

			</div>

        );
    }
});

module.exports = AppHeader;