$input | ForEach-Object {
    $val = Get-PnpDeviceProperty `
        -InstanceId $_ `
        -KeyName '{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2' |
        ForEach-Object { $_.Data }

    if ($null -eq $val) {
        Write-Error "battery property not found"
        exit 1
    }

    $val
}
