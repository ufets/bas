reg delete "HKEY_CURRENT_USER\Software\Microsoft\TerminalServer Client\Default" /va /f
reg delete "HKEY_CURRENT_USER\Software\Microsoft\TerminalServer Client\Servers" /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\TerminalServer Client\Servers"
attrib -s -h %userprofile%\documents\Default.rdp
del %userprofile%\documents\Default.rdp
del /f /s /q /a %AppData%\Microsoft\Windows\Recent\AutomaticDestinations