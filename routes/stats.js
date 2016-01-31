/*
 *	This is a method that accepts an http request of the form
 *	"http://localhost:3000/Users/(USER_ID)"
 *	and returns a response containing an array corresponding to 
 *  the user's measured statistics.
 */

var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.send('respond with a resource');
});

router.get('/:userId', function(req, res, next) {
  var db = req.db;
  var userId = parseInt(req.params.userId, '10');
  db.get('Users').findOne({'user_id': userId}, function(err, document){
    res.send(document.stats);
  });
});


module.exports = router;