$pattern = ($input | ForEach-Object { [regex]::Escape($_) }) -join '|'

foreach ($d in Get-PnpDevice | Where FriendlyName -match $pattern) {
  try {
    $p = Get-PnpDeviceProperty `
      -InstanceId $d.InstanceId `
      -KeyName '{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2' `
      -ErrorAction Stop

    if ($p.Type -ne 'Empty') {
      $d.InstanceId
      break
    }
  } catch {}
}
