
New-Item -ItemType Directory -Force -Path "D:\test-assets"

$pngBytes = [Convert]::FromBase64String("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==")
[System.IO.File]::WriteAllBytes("D:\test-assets\test-avatar.png", $pngBytes)

dir "D:\test-assets\test-avatar.png"