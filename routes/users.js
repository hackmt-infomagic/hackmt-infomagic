/*
 *	This is a method that accepts an http get request of the form:
 *  "http://localhost:3000/Users/(USER_ID)"
 *  and returns a response containing the mongodb document
 *  corresponding to the user
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
    res.send(document);
  });
});

router.post('/:userId/subjects', function(req, res, next){
	var db = req.db;
	var userId = parseInt(req.params.userId, '10');
	var subject = req.body.subject;
  db.get('Users').update(
  	{'user_id': userId},
  	{$push: {"subjects" : subject}}

   );
  res.send('Updated Subjects!');
});

 router.post('/:userId/session', function(req, res, next){
 	var db = req.db;
 	var userId = parseInt(req.params.userId,'10');

 	var subject = req.body.subject;
 	var tags = req.body.tags;
 	var start_time = req.body.start_time;
 	var end_time = req.body.end_time;


 	db.get('Users').update(
 		{'user_id' : userId},
 		{
 			$push: {"sessions" : {start_time,tags,end_time,subject}}

 		}
 	);
 	res.send('Created New Session!');
});

module.exports = router;