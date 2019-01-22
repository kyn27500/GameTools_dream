var express = require('express')
var router = express.Router()

var resp;

var lock = 0

var tab =' '

var gameList = [];

/* GET home page. */
router.get('/', function(req, res, next) {

	// 获取ID
	var id = req.query.id;

	// 配置文件,通过gamename选择相应的配置
	var config=require("./config.json");


	resp = res;
	console.log("点击ID：",id)
	if(id==1){
		//svn更新
		var scriptPath = process.cwd()+ "/routes/svnupdate.sh"
		var cmd = scriptPath+" "+config.configSvn
		execShell(cmd)
	}
	else if(id==2){
		// 热更新
		var scriptPath = "./routes/gitPull.sh"
		var cmd = scriptPath +" "+config.workPath_hotfix+" "+config.hotUpdateShell
		execShell(cmd,"热更开发服 完毕！")
	}
	else if (id==3){
		var scriptPath = process.cwd()+ "/routes/protoTool.py"
		var cmd = scriptPath+' '+config.protoPath+' '+config.pbPath
		execPy(cmd)
	}
	else if(id==4){

		// 检查相同文件
		var scriptPath = process.cwd()+ "/routes/createRoute.py"
		var cmd = scriptPath+' '+config.fishRouteExcel
		execPy(cmd)

	}
	else if(id==5){
		// 测试svn
		var scriptPath = process.cwd()+ "/routes/svn.py"
		var cmd = scriptPath+" "+config.svntest+" 2"
		execPy(cmd)
	}
	else{
		
		printToHtml('欢迎使用在线工具，如有建议，请联系作者！')
	}

});

// 执行python 文件
function execPy(pCmd,pCallback){

	var exec = require('child_process').exec;

	exec('python '+pCmd,function(error,stdout,stderr){
	    if(stdout.length >1){
	        printToHtml(stdout);
	    } else {
	        console.log('you don\'t offer args');
	    }
	    if(error) {
	        printToHtml("\nerror:"+stderr);
	    }
	});
}

// 执行shell文件
function execShell(pCmd,sText){

	var exec = require('child_process').exec;

	exec('sh '+pCmd,function(error,stdout,stderr){
	    if(stdout.length >1){
	        printToHtml(sText||"程序执行完毕！");
	    } else {
	        console.log('you don\'t offer args');
	    }
	    if(error) {
	        printToHtml("\nerror:"+stderr);
	    }
	}); 
}
// 打印
function printToHtml(ptext){
	resp.render('index', {text:ptext});
}
module.exports = router;
