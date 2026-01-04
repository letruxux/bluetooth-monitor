Get-PnpDevice |
Where-Object {
    $_.InstanceId -like 'BTHENUM*'
} |
ForEach-Object {
    $conn = Get-PnpDeviceProperty `
        -InstanceId $_.InstanceId `
        -KeyName 'DEVPKEY_Device_IsConnected' `
        -ErrorAction SilentlyContinue

    if ($conn.Data -eq $true) {
        $_.FriendlyName
    }
}
