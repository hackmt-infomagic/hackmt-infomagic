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

module.exports = router;
