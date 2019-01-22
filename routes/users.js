var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {

	var rf=require("fs");  
	var data=rf.readFileSync("public/version.html","utf-8");
	res.send(data); 
 
});

module.exports = router;
