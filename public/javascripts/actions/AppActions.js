/**
 * Created by rayde on 1/30/2016.
 */
var AppConstants = require('../constants/AppConstants');
var AppDispatcher = require('../dispatcher/AppDispatcher');
var api = require('../API/APIUtils');

var AppActions = {
    getUser: function(userId) {
        var localthis = this;
        api.getUser(userId, localthis);
    },
    receiveUser: function(data){
        AppDispatcher.handleAction({
            actionType: AppConstants.RECEIVE_USER,
            user: data
        });
    }
};

module.exports = AppActions;
