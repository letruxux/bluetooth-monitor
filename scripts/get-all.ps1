Get-CimInstance Win32_PnPEntity |
Where-Object {
  $_.HardwareID -match 'BTHENUM|HID|USB'
} |
Select-Object -ExpandProperty Name |
Sort-Object -Unique
