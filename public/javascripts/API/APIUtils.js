/**
 * Created by rayde on 1/30/2016.
 */
var request = require('superagent');

module.exports = {
    getUser: function (userId, AppActions) {
        request
            .get('/users/'+userId)
            .end(function(err, res){
                if(res.ok){
                    AppActions.receiveUser(res.body.results)
                } else {
                    alert('API call failed.');
                }
            });
    }
};
