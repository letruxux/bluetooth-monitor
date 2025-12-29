$input | ForEach-Object {
  Get-PnpDevice -FriendlyName "*$_*" | ForEach-Object {
    $test = $_ |
      Get-PnpDeviceProperty -KeyName '{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2' |
      Where Type -ne Empty

    if ($test) {
      $test.InstanceId
    }
  }
}
