## 1. What is the full link of a social media post which is part of the malware campaign, and was unknowingly opened by Alonzo spire?
- check history browser in ***C:\Users\a\Desktop\detroitbecomehuman\Triage\C\Users\alonzo.spire\AppData\Local\Microsoft\Edge\User Data\Default\History***, then found suspicious facebook url for AI (using BrowingHistoryView or Autospy for automatically parsing)
- https://www.facebook.com/AI.ultra.new/posts/pfbid0BqpxXypMtY5dWGy2GDfpRD4cQRppdNEC9SSa72FmPVKqik9iWNa2mRkpx9xziAS1l
## 2. Can you confirm the timestamp in UTC when alonzo visited this post?
- 2024-03-19 04:30:00
## 3. Alonzo downloaded a file on the system thinking it was an AI Assistant tool. What is name of the archive file downloaded?
- After access facebook, maybe user download file by a redirect link to google drive: https://l.facebook.com/l.php?u=https%3A%2F%2Fdrive.usercontent.google.com%2Fu%2F2%2Fuc%3Fid%3D1z-SGnYJCPE0HA_Faz6N7mD5qf0E-A76H%26export%3Ddownload&h=AT2dsRb4dQeh4oPNOqp3eHhaSewnHh17zEIwZ18CVTFj5edI8V33q55EWDtVjXyMp3LQ5aaUwqq_ZtWpkTcAkWi9q9hzpI2JUJnZRl4io5nnOxgGHc8zB1e3lIXn6zJw9Agr73knOb4_acb9ZDFB&__tn__=-UK-R&c[0]=AT2pAxNrMkue5u710VTAYLmU_EsFxntsYANT148AzvKn8e_d8-lnf430pHC75tcwjB6fr7YWhA0N5FN3C0ojZ86fcSure9rJt1OGqeRq4y5q-bLgDmnLi7vugPXdNuZ511hTSoxa8vJ8dR-ak14a_4m_WAudOrCiudtoRPLo9mLdo7krRbqXEtIKydoSuioHjI5NVuMWVA
- Then check web downloads artifact from Autospy, found an entry download from google drive
- AI.Gemini Ultra For PC V1.0.1.rar
## 4. What was the full direct url from where the file was downloaded?
- Also in Autospy shows source of file
-  https://drive.usercontent.google.com/download?id=1z-SGnYJCPE0HA_Faz6N7mD5qf0E-A76H&export=download
## 5. Alonzo then proceeded to install the newly download app, thinking that its a legit AI tool. What is the true product version which was installed?
- Search for event 1033 in Application log, found the true version of msi installer (Google AI Gemini Ultra For PC V1.0.1.msi)
- 3.32.3
## 6. When was the malicious product/package successfully installed on the system?
- Also in the same event has the time that malicious is installed successfully
- 2024-03-19 04:31:33
## 7. The malware used a legitimate location to stage its file on the endpoint. Can you find out the Directory path of this location?
- Check window powershell logs, found some odd powershell command:
```bash
    HostName=ConsoleHost
	HostVersion=5.1.19041.3031
	HostId=13df80a7-4a3b-49f2-9f31-ec7ff38e6bc9
	HostApplication=powershell -ExecutionPolicy Bypass -File C:\Program Files (x86)\Google\Install\nmmhkkegccagdldgiimedpic/ru.ps1
	EngineVersion=5.1.19041.3031
	RunspaceId=4770b22a-1990-4e70-af50-0c659067edb9

```
- C:\Program Files (x86)\Google
## 8. The malware executed a command from a file. What is name of this file?
- Traverse through C:\Program Files (x86)\Google, I found a cmd file named install.cmd
## 9. What are the contents of the file from question 8? Remove whitespace to avoid format issues.
- Using mftexplorer to inspect content of file
- @echooffpowershell-ExecutionPolicyBypass-File"%~dp0nmmhkkegccagdldgiimedpic/ru.ps1"
## 10. What was the command executed from this file according to the logs?
- I discovered above about suspicious ps command
- powershell -ExecutionPolicy Bypass -File C:\Program Files (x86)\Google\Install\nmmhkkegccagdldgiimedpic/ru.ps1
## 11. Under malware staging Directory, a js file resides which is very small in size.What is the hex offset for this file on the filesystem?
- Based on MFT pasrsing, I found a content.js file with small size, which has entry number is 64067, calcuate offset by 64067*1024, then convert to hex
- 3E90C00
## 12. Recover the contents of this js file so we can forward this to our RE/MA team for further analysis and understanding of this infection chain. To sanitize the payload, remove whitespaces.
- Inspect content file from MFTexplorer, I got it
```js
varisContentScriptExecuted = localStorage.getItem('contentScriptExecuted');
if (!isContentScriptExecuted) {
    chrome.runtime.sendMessage({
        action: 'executeFunction'
    }, function(response) {
        localStorage.setItem('contentscriptExecuted', true);
    });
}
```
## 13. Upon seeing no AI Assistant app being run, alonzo tried searching it from file explorer. What keywords did he use to search?
- Use regripper with plugin 'WordWheelQuery' which will allow me to look throuh registry hives for the searches that user made
```powershell
C:\Users\a\Desktop\RegRipper4.0> .\rip.exe -r ..\detroitbecomehuman\Triage\C\Users\alonzo.spire\NTUSER.DAT -p wordwheelquery
Launching wordwheelquery v.20200916
wordwheelquery v.20200916
(NTUSER.DAT) Gets contents of user's WordWheelQuery key

Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery
LastWrite Time 2024-03-19 04:32:11Z

Searches listed in MRUListEx order

0    Google Ai Gemini tool
```
- Google Ai Gemini tool
## 14. When did alonzo searched it?
- 2024-03-19 04:32:11
## 15. After alonzo could not find any AI tool on the system, he became suspicious, contacted the security team and deleted the downloaded file. When was the file deleted by alonzo?
- Look in AutoSpy in Recycle Bin, there is a file named $R2MU60B.rar which is original from C:\Users\alonzo.spire\Downloads\AI.Gemini Ultra For PC V1.0.1.rar and deleted at 2024-03-19 04:34:16
- 2024-03-19 04:34:16
## 16. Looking back at the starting point of this infection, please find the md5 hash of the malicious installer.
- Search file installer on google, found BF17D7F8DAC7DF58B37582CEC39E609D
