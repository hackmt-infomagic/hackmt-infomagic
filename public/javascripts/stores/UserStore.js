/**
 * Created by rayde on 1/30/2016.
 */

var AppDispatcher = require('../dispatcher/AppDispatcher');
var EventEmitter = require('events').EventEmitter;
var AppConstants = require('../constants/AppConstants');
var _ = require('underscore');

var _user = {};

var _stats = {};

function loadUserData(data){
    _user = _.omit(data, 'stats');
    _stats = data['stats'];
}

var UserStore = _.extend({}, EventEmitter.prototype, {
    getUser: function(){
        return _user;
    },
    getStats: function(){
        return _stats;
    },
    emitChange: function() {
        this.emit('change');
    },
    addChangeListener: function(callback){
        this.on('change', callback);
    },
    removeChangeListener: function(callback){
        this.removeListener('change', callback)
    }
});

AppDispatcher.register(function(payload){
    var action = payload.action;

    switch (action.actionType){
        case AppConstants.RECEIVE_USER:
            loadUserData(action.user);
            console.log('I recieved stuff.');
            break;
        default:
            return true;
    }

    UserStore.emitChange();

    return true;
});

module.exports = UserStore;