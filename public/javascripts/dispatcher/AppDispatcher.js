/**
 * Created by rayde on 1/30/2016.
 */
var Dispatcher = require('flux').Dispatcher;

var AppDispatcher = new Dispatcher();

AppDispatcher.handleAction = function(action){
    this.dispatch({
        source: 'VIEW_ACTION',
        action: action
    });
};

module.exports = AppDispatcher;