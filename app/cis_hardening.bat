@echo off
:: CIS Windows Hardening Script for Non-Admins
:: Run as Administrator
echo ----------------------------------------
echo Applying CIS Security Best Practices...
echo ----------------------------------------

:: 1.1.x - Password Policies
echo [+] Enforcing password history to 24
net accounts /uniquepw:24

echo [+] Setting max password age to 365 days
net accounts /maxpwage:365

echo [+] Setting min password age to 1 day
net accounts /minpwage:1

echo [+] Setting min password length to 14
net accounts /minpwlen:14

echo [+] Locking account after 10 invalid logins
net accounts /lockoutthreshold:10

echo [+] Lockout duration set to 15 minutes
net accounts /lockoutduration:15

echo [+] Reset account lockout counter after 15 minutes
net accounts /lockoutwindow:15

:: 1.5.x - Screen Lock
echo [+] Setting screen lock timeout to 15 minutes (AC power)
powercfg /change standby-timeout-ac 15

:: 2.3.7.1 - Disable Guest Account
echo [+] Disabling Guest account
net user guest /active:no

:: 18.3.x - Disable SMBv1
echo [+] Disabling SMBv1 (legacy file sharing)
dism /online /norestart /disable-feature /featurename:SMB1Protocol

:: 18.9.5.1 - Disable Remote Desktop
echo [+] Disabling Remote Desktop
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 1 /f

:: 1.2.x - Enable basic audit logging
echo [+] Enabling Logon Audit (Success/Failure)
auditpol /set /subcategory:"Logon" /success:enable /failure:enable

echo [+] Enabling Account Logon Audit (Success/Failure)
auditpol /set /subcategory:"Account Logon" /success:enable /failure:enable

echo ----------------------------------------
echo [✔] CIS Basic Hardening Complete!
echo Please restart your PC to apply all settings.
echo ----------------------------------------

pause
