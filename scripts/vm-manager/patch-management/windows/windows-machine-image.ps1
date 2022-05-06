Set-StrictMode -Version Latest;
$ErrorActionPreference = "Stop";

<#
    .SYNOPSIS
        This function calls the gcloud binary

    .PARAMETER Arguments
        Array of arguments to be passed to gcloud

    .OUTPUTS
        PSCustomObject {StandardOutput, StandardError, ExitCode}

    .EXAMPLE
        Invoke-Gcloud -Arguments @("compute", "instances", "list");
#>
function Invoke-Gcloud
{
    param
    (
        [string[]] $Arguments
    );

    process
    {
        $info = New-Object System.Diagnostics.ProcessStartInfo;
        $info.FileName = "cmd.exe";
        $info.RedirectStandardError = $true;
        $info.RedirectStandardOutput = $true;
        $info.UseShellExecute = $false;
        $info.LoadUserProfile = $true;
        $info.Arguments = "/C gcloud.cmd $($Arguments -join " ")";

        $process = New-Object System.Diagnostics.Process;
        $process.StartInfo = $info;
        $process.Start() | Out-Null;

        [PSCustomObject] @{
            StandardOutput = $process.StandardOutput.ReadToEnd()
            StandardError = $process.StandardError.ReadToEnd()
            ExitCode = $process.ExitCode
        };

        $process.WaitForExit();
    }
}


<#
    .SYNOPSIS
        This function returns the project from a given resource URI

    .PARAMETER Uri
        GCP resource URI

    .OUTPUTS
        Project

    .EXAMPLE
        ConvertTo-Project -Uri "https://www.googleapis.com/compute/v1/projects/test/zones/europe-west4-a/disks/test";
#>
function ConvertTo-Project
{
    param
    (
        [string] $Uri
    );

    process
    {
        $start = $Uri.IndexOf("projects/") + 9;
        $end = $Uri.IndexOf("/", $start);

        if($end -eq -1)
        {
            $end = $Uri.Length - $start;
        }

        return $Uri.Substring($start, $end);
    }
}

<#
    .SYNOPSIS
        This function returns the zone from a given resource URI

    .PARAMETER Uri
        GCP resource URI

    .OUTPUTS
        Zone

    .EXAMPLE
        ConvertTo-Zone -Uri "https://www.googleapis.com/compute/v1/projects/test/zones/europe-west4-a/disks/test";
#>
function ConvertTo-Zone
{
    param
    (
        [string] $Uri
    );

    process
    {
        $start = $Uri.IndexOf("zones/") + 6;
        $end = $Uri.IndexOf("/", $start);

        if($end -eq -1)
        {
            $end = $Uri.Length - $start;
        }

        return $Uri.Substring($start, $end);
    }
}

<#
    .SYNOPSIS
        Returns instance metadata queried from the GCE metadata endpoint

    .PARAMETER Entry
        Metadata entry to query for

    .OUTPUTS
        Metadata value for the entry

    .EXAMPLE
        Get-InstanceMetadata -Entry "name";

    .LINK
        https://cloud.google.com/compute/docs/storing-retrieving-metadata#project-instance-metadata
#>
function Get-InstanceMetadata
{
    param
    (
        [string] $Entry
    );

    process
    {
        return Invoke-RestMethod `
            -Headers @{"Metadata-Flavor" = "Google"} `
            -Uri "http://metadata/computeMetadata/v1/instance/$($Entry)";
    }
}
<#
    .SYNOPSIS
        Gets the name of the current VM from metadata

    .OUTPUTS
        Name of the VM

    .EXAMPLE
        Get-VmName;
#>
function Get-VmName
{
    param
    (
    );

    process
    {
        return Get-InstanceMetadata -Entry "name";
    }
}

<#
    .SYNOPSIS
        Gets the zone of the current VM from metadata

    .OUTPUTS
        Zone of the VM

    .EXAMPLE
        Get-Zone;
#>
function Get-Zone
{
    param
    (
    );

    process
    {
        $zone = Get-InstanceMetadata -Entry "zone";
        return ConvertTo-Zone -Uri $zone;
    }
}


<#
    .SYNOPSIS
        Creates machine image for VM

    .PARAMETER VmName
        Name of the current VM

    .PARAMETER PachJobId
        Id of the patch job

    .EXAMPLE
        Machine_Image  -VmName $vmName -PatchJobId $jobId -Zone $zone;
#>

function Machine_Image
{
    param
    (
        [string] $vmName,
        [string] $zone
    );

    process
    {
            $zone = Get-Zone;
            $Tdate=Get-Date -UFormat "%m%d%Y%H%M%S"

            $arguments = @(
                "compute",
		"machine-images",
                "create",
                "$vmName-$Tdate",
                "--source-instance $vmName",
		"--source-instance-zone $zone"
            );
            
            $process = Invoke-Gcloud -Arguments $arguments;
            if($process.ExitCode -ne 0)
            {
                return $false;
            }

        return $true;
    }
}

$vmName = Get-VmName;
$zone = Get-Zone;

Write-Host -NoNewline "Creating Machine Image: ";
$result = Machine_Image  -VmName $vmName  -Zone $zone;

if($result)
{
    Write-Host "done";
}
else
{
    Write-Host "failed";
    
    # Return non-zero exit code to stop patching
    [System.Environment]::Exit(1);
}
