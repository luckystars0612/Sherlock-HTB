## 1. At What time did the compromised account first authenticate to the workstation? (UTC)
- 2024-10-22 15:25:57 ( arjun)
## 2. What protocol did the threat actor us to access the workstation?
- rdp (check terminal service log)
## 3. What logon type was logged when the threat actor accessed the workstation?
- 10 (rdp has logon type 10)
## 4. What was the IP address of the workstation the threat actor pivoted through to access the internal network?
- 10.10.0.81 ( also check rdp and 4624 logs)
## 5. At what time did the threat actor first attempt to bypass a feature of Windows Defender? (UTC)
- 
## 6. What is the name of the tool the threat actor used to enumerate the workstation for misconfigurations?
- On prefetch files, I found a suspicious file named Powerup.ps1, also check with powershell log and console history file, I confirm this is Powerup from Powersploit framework
- Powerup
## 7. What is the name of the executable the threat actor used to elevate their privileges?

## 8. At what time did the new user get created? (UTC)
- Event 4720 for new created user (chhupa)
- 2024-10-22 21:52:24
## 9. What was the SID of the user that created the new user?
- also in same event of created user 
- S-1-5-18
## 10. What is the original name of the exploit binary the threat actor used to bypass several Windows security features?

## 11. What time did the threat actor first run the exploit? (UTC)

## 12. Which account owns the files manipulated by the exploit?

## 13. The threat actor managed to exfiltrate some domain credentials, which Windows security feature did they bypass using the exploit?
- There's a dd.exe which is used for [WindowsDowndata](https://github.com/SafeBreach-Labs/WindowsDowndate/tree/main), found some tactics like:
```bash
<Configuration>
    <UpdateFilesList>
        <UpdateFile source="C:\Users\Chhupa\Desktop\test.exe" destination="C:\Windows\System32\securekernel.exe" />
    </UpdateFilesList>
</Configuration>

```
- This points me to VBS UEFI Lock, it is a gaurd method of window to protect credentials in a isolate memory region.
- Credential Guard
## 14. What is the NT hash of the domain administrator compromised by the Threat Actor?
- Because we need domain administrator, but unfortunately, lsass.dmp does not contain it. So I try to use secretdumps.py from impacket to dump SAM and SECURITY hives (note that SYSTEM hive has dirty transaction, so I use RegExplorer of Eric Zimmerman to clean it).
```bash
python3 dump.py -sam SAM -sytem SYSTEM_clean -security SECURITY_clean LOCAL
```
- After get the administrator hash,but it is not NT hash format, It's DC2 cache format, so we need to crack it into plaintext password, then use python to rebuild NT from this password
```bash
hashcat -m 2100 -a 0 adminhash.txt rockyou.txt
```
```bash
import hashlib

password = "P@ssw0rd1"  # Replace with the cracked password
nt_hash = hashlib.new('md4', password.encode('utf-16le')).hexdigest()
print(f"NT Hash: {nt_hash}")
```
- ae974876d974abd805a989ebead86846
## 15. What is the password set by the threat actor for their generated user?
- The generated user is chhupa. Use pypykatz to parse lsass.dmp file to get NT hash, then crack it using hash cat
```bash
hashcat -m 1000 -a 0 hash.txt rockyou.txt
```
- Password123
