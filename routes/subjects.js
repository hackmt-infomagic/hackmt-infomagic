/*
 *	This is a method that accepts an http request of the form
 *	"http://localhost:3000/Subjects/(USER_ID)/(SUBJECT))"
 *  and appends a subject to the subjects array contained
 *  in the mongodb user document.
 */

var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.send('respond with a resource');
});

router.get('/:userId/:subject', function(req, res, next) {
  var db = req.db;
  var userId = parseInt(req.params.userId, '10');
  var subject = req.params.subject;
  db.get('Users').update(
  	{'user_id': userId},
  	{
  	 	$push: {"subjects" : subject}

  	}

   );
});

module.exports = router;