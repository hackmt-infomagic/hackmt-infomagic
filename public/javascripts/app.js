/**
 * Created by rayde on 1/29/2016.
 */
var React = require('react');
var ReactDom = require('react-dom');
var InfomagicApp = require('./components/InfomagicApp.react');
var AppActions = require('./actions/AppActions');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var browserHistory = ReactRouter.browserHistory;
var IndexRoute = ReactRouter.IndexRoute;
var GraphComponent = require('./components/GraphComponent.react');
var Overview = require('./components/Overview.react');
var Focus = require('./components/Focus.react');

AppActions.getUser(222);

ReactDom.render((
    <Router history={browserHistory}>
        <Route path="/" component={InfomagicApp}>
            <IndexRoute component={Overview} />
            <Route path="/sessionTracker" component={Focus}/>
        </Route>
    </Router>
), document.getElementById('react-container'));

