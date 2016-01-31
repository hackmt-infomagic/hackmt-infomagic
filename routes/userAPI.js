/*
 * API for user interaction
 */


// Importing express and creating an http client.
var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.send('respond with a resource');
});


/*
 * An http request in the form:
 * http://localhost:3000/userAPI/getUser/(USER_ID)
 * will retrieve the mongodb document corresponding
 * to the user.
 */

router.get('/getUser/:userId', function(req, res, next) {
  var db = req.db;
  var userId = parseInt(req.params.userId, '10');
  db.get('Users').findOne({'user_id': userId}, function(err, document){
    res.send(document);
  });
});

/*
 *	This is a method that accepts an http request of the form
 *	http://localhost:3000/userAPI/getStats/(USER_ID)
 *	and returns a response containing an array corresponding to 
 *  the user's measured statistics.
 */

router.get('/getStats/:userId', function(req, res, next) {
  var db = req.db;
  var userId = parseInt(req.params.userId, '10');
  db.get('Users').findOne({'user_id': userId}, function(err, document){
    res.send(document.stats);
  });
});

/*
 * An http request in the form:
 * http://localhost:3000/userAPI/newSubject/(USER_ID)", json={'subject':'(SUBJECT_NAME)'}
 * will add a subject to a particular user document.
 * The response is a string notifying that the subjects array has been updated
 */
router.post('/newSubject/:userId', function(req, res, next){
	var db = req.db;
	var userId = parseInt(req.params.userId, '10');
	var subject = req.body.subject;
  db.get('Users').update(
  	{'user_id': userId},
  	{$push: {"subjects" : subject}}

   );
  res.send('Updated Subjects!');
});

/*
 *	An http request in the form:
 *  http://localhost:3000/userAPI/newSession/(USER_ID)/", json={'subject': '(SUBJECT_NAME)', 'start_time': '2077/7/7 12:34:56','end_time': '2088/8/8 10:09:08', 'tags': []}
 *  Will create a new session on the user. Input is of type string except for tags, which is an array of strings.
 */
 router.post('/newSession/:userId', function(req, res, next){
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