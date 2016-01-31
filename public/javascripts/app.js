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

AppActions.getUser(2);

ReactDom.render((
    <Router history={browserHistory}>
        <Route path="/" component={InfomagicApp}>

        </Route>
    </Router>
), document.getElementById('react-container'));

