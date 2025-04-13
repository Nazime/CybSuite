# ==================== #
# Script Configuration #
# ==================== #

# If property dont exists in object, raise error
Set-StrictMode -Version Latest

# Set culture to en-US to avoid issues with dates
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::CreateSpecificCulture("en-US")
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::CreateSpecificCulture("en-US")

# TODO: double check if dates are in UTC
# =============== #
# UTILS FUNCTIONS #
# =============== #

function print_info {
    param([string]$message)
    Write-Host "[i] " -NoNewline -ForegroundColor Green
    Write-Host $message
}

function print_error {
    param([string]$message)
    Write-Host "[ERROR] " -NoNewline -ForegroundColor Red
    Write-Host $message
}


function AsJson {
    # Same as using ConvertTo-Json -Array but compatible with lower powershell versions
    param (
        [Parameter(ValueFromPipeline = $true, Mandatory = $true)]
        $InputObject,

        [Parameter(Mandatory = $false)]
        [int]$Depth = 5
    )


    # Collect input objects into an array
    begin
    {
        $collectedInput = @()
    }


    process {
        $collectedInput += $InputObject
    }

    end {
        # Convert the collected objects to JSON
        $jsonOutput = $collectedInput | ConvertTo-Json -Depth $Depth

        if (-not $jsonOutput.StartsWith('[')) {
            $jsonOutput = "[`n$jsonOutput`n]"
        }

        # Output the JSON
        $jsonOutput
    }

}

# ================== #
# EXTRACTS FUNCTIONS #
# ================== #



# ================ #
# Global variables #
# ================ #


$hostname = $env:COMPUTERNAME
$currentDir = Get-Location
$dirExtracts = Join-Path $currentDir "extracts_$hostname"
$dirCommands = Join-Path $dirExtracts "commands"
$dirFiles = Join-Path $dirExtracts "files"
$infoJsonPath = Join-Path $dirExtracts "info.json"
$outputZip = Join-Path $currentDir "extracts_$hostname.zip"
$startTime = Get-Date
# ======================= #
# CLI PARAMETERS & CHECKS #
# ======================= #
# TODO: Fix CLI args --force
#param(
#    [switch]$Force
#)

# If force remove current folder
#if ($Force) {
#    if (Test-Path $dirExtracts) {
#        print_info "Forcing removal of existing 'cbs_extracts' folder ..."
#        Remove-Item -Path $dirExtracts -Recurse -Force
#    }
#}

# Check if base folder exists
if (Test-Path $dirExtracts) {
    print_error "Folder '$dirExtracts' already exists. Use --force to remove it."
    exit 1
}


# Create directories
print_info "Creating folders"
New-Item -ItemType Directory -Path $dirExtracts -Force | Out-Null
New-Item -ItemType Directory -Path $dirCommands -Force | Out-Null
New-Item -ItemType Directory -Path $dirFiles -Force | Out-Null

# Create info.json file
# ---------------------
print_info "Extracting metadata for review"
# Get the current universal time
$currentTime = (Get-Date).ToUniversalTime().ToString("o") # ISO 8601 format
# Create the JSON object
$info = @{
    type = "windows"
    name = $hostname
    datetime = $currentTime
}
# Convert to JSON and save to the specified file
$info | ConvertTo-Json -Depth 2 | Out-File -FilePath $infoJsonPath -Encoding UTF8



# ================ #
# EXTRACTING CONFS #
# ================ #

# Run systeminfo and save in commands
print_info "Extracting systeminfo"
systeminfo | Out-File -FilePath "$dirCommands\systeminfo.txt" -Encoding utf8

print_info "Extracting local users"
Get-LocalUser | AsJson | Out-File -FilePath "$dirCommands\local_users.json" -Encoding utf8
Get-LocalUser | ConvertTo-Csv  -NoTypeInformation | Out-File -FilePath  "$dirCommands\local_users.csv"  -Encoding utf8

print_info "Extracting local groups"
Get-LocalGroup | AsJson | Out-File -FilePath  "$dirCommands\local_groups.json" -Encoding utf8
Get-LocalGroup | ConvertTo-Csv -NoTypeInformation | Out-File -FilePath "$dirCommands\local_groups.csv" -Encoding utf8

print_info "Extracting local groups members for administrators"
$adminGroup = ([System.Security.Principal.SecurityIdentifier] "S-1-5-32-544").Translate([System.Security.Principal.NTAccount]).Value
$adminGroupName = ($adminGroup -split '\\')[-1]  # Extracts only the group name (e.g., "Administrateurs")
Get-LocalGroupMember -Group $adminGroupName | ConvertTo-Csv -NoTypeInformation | Out-File -FilePath  "$dirCommands\local_groups_members_administrators.csv" -Encoding utf8

print_info "Extracting local groups members"
$allGroupMembers = @()
foreach ($groupInfo in Get-LocalGroup) {
    $members = Get-LocalGroupMember -Group $groupInfo.Name

    # Ensure members is always an array
    if ($members -isnot [Array]) {
        $members = @($members)
    }

    $allGroupMembers += [PSCustomObject]@{
        group  = $groupInfo
        members = $members
    }
}
# Use -Depth to have full info of members and not just name
$allGroupMembers | AsJson | Out-File -FilePath  "$dirCommands\local_groups_members.json"  -Encoding utf8


print_info "Extracting Bitlocker volumes"
Get-BitlockerVolume | AsJson | Out-File -FilePath "$dirCommands\bitlocker_volumes.json"  -Encoding utf8

# Require admin privileges
print_info "Extracting secedit"
secedit /export /cfg "$dirCommands/secedit.ini" > $null

print_info "Extracting auditpol"
auditpol /backup /file:"$dirCommands/auditpol.csv"

print_info "Extracting antivirus information"
$antivirus1 = Get-WmiObject -Namespace "root\SecurityCenter" -Query "SELECT * FROM AntiVirusProduct"
$antivirus2 = Get-WmiObject -Namespace "root\SecurityCenter2" -Query "SELECT * FROM AntiVirusProduct"
$antivirus = $antivirus1 + $antivirus2
$antivirus | AsJson | Out-File -FilePath "$dirCommands\antivirus.json" -Encoding utf8
$antivirus | ConvertTo-Csv -NoTypeInformation | Out-File -FilePath "$dirCommands\antivirus.csv" -Encoding utf8

print_info "Extracting installed applications"
$applications = Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
$applications | AsJson | Out-File -FilePath "$dirCommands\applications_registry.json" -Encoding utf8
$applications | ConvertTo-Csv -NoTypeInformation | Out-File -FilePath "$dirCommands\applications_registry.csv" -Encoding utf8

$applications2 = Get-WmiObject Win32_product | Select-Object name, version
$applications2 | AsJson | Out-File -FilePath "$dirCommands\applications_wmic.json" -Encoding utf8
$applications2 | ConvertTo-Csv -NoTypeInformation | Out-File -FilePath "$dirCommands\applications_wmic.csv" -Encoding utf8

print_info "Extracting HotFix"
Get-HotFix | ConvertTo-Csv -NoTypeInformation | Out-File -FilePath "$dirCommands\hotfix.csv"  -Encoding utf8
Get-HotFix | AsJson | Out-File -FilePath "$dirCommands\hotfix.json" -Encoding utf8


print_info "Extracting registries... This might take some time, grab a coffee!"

$hives = @(
    "HKLM",
    "HKCU",
    "HKCR",
    "HKU",
    "HKCC"
)

foreach ($hive in $hives) {
    print_info "  extracting hive as txt $hive..."
    reg.exe export $hive "$dirCommands\reg_$hive.txt" > $null 2>&1
}

# This takes 30 minutes .. so do the compute in post review
foreach ($hive in $hives) {
    print_info "  extracting hive as json $hive..."
    Get-ChildItem "$($hive):\" -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
        # Prepare an object to store key information
        $registryKeyData = @{
            path     = $_.Name
            properties = @{}
        }

        # Get registry values for each key
        $key = $_
        foreach ($valueName in $key.GetValueNames()) {
                $valueData = $key.GetValue($valueName)
                # Add each registry value to the properties hashtable
                $registryKeyData.properties[$valueName] = $valueData
            }

        # Convert the object to JSON and compress it
        $registryKeyData | ConvertTo-Json -Compress
    } | Out-File -FilePath "$dirCommands\reg_$hive.json" -Encoding utf8
}

if ($false) {
    # not working for the moment => takes muuuch time
    print_info "Extracting ACLs... This might take some time, grab a coffee!"
    Get-ChildItem / -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
        try{
            if (-Not (Test-Path "$($_.FullName)")) { return }

            $acl = Get-acl "$($_.FullName)"
            $sddl = $acl.GetSecurityDescriptorSddlForm('All')
            if ($sddl) {
                [PSCustomObject]@{
                    filename = $_.FullName
                    sddl = $sddl
                } | ConvertTo-Json -Compress
            }
        }catch   {
            echo "Skipping $_"
        }
    }  | Out-File -FilePath  -Encoding utf8 "$dirCommands\acls.json"
}
# ==================== #
# COMPRESS EXTRACTIONS #
# ==================== #

if (Test-Path $outputZip) { Remove-Item $outputZip }
Compress-Archive -Path $dirExtracts -DestinationPath $outputZip

# Remove the original extraction directory after compression
print_info "Removing original extraction directory"
Remove-Item -Path $dirExtracts -Recurse -Force

print_info "Extracted and compressed to: $outputZip"

$endTime = Get-Date
$elapsedTime = $endTime - $startTime
print_info "Script execution time: $($elapsedTime.TotalSeconds) seconds /  $($elapsedTime.TotalMinutes) minutes"
