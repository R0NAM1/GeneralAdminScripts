A reposiotry for storing general use scripts, for example Google Admin Manager (GAM) update scripts, Windows Powershell Setup Scripts, and anything else that probably should be just a GIST but I'd rather it be a repo.

## Existing Scripts
### gam_csvMassmoveToOu.py
### REDUNDANT, USE gam csv spreadsheet.csv gam update cros ~deviceID ou ~desiredOu

A python script that reads a CSV and itterates over its rows to run the GAM command 'gam update cros DEVICEIDSTRING ou /Desired/OU' as a subprocess, includes a dry run option to make sure data is fed in properly along with an "Are you sure?" prompt. Also includes a STEP option for you to make sure each itteration runs correctly.

CSV must contain the Google Device ID under the header 'googleDeviceId' and the desired OU to move it into under 'desiredGoogleOu'.

python3 gam_csvMassmoveToOu.py --dry-run --step template.csv


### googleWorkspace_SkywardDbSyncToGoogleUsers.py

Takes a skyward database dump of students taking name, birthday, gender, (Grade?), and other info and put into a custom Student object, and then using created object changed desired info of found student object in GW, if student is not found create, if a student if found in GW but not in Skyward then somehow disable. All in steps:
1. Create Student Objects and put into array while taking Skyward dump.
2. Itterate over Student Object Array, with each object attempt to find a student account.
2a. If no student account if found, create one and set a temporary password env var
2b. If an account is found, update all details that can be, and calculate OU to use based on details (Grade or Birthday).
3. Run reverse, look through all user accounts under specific OU recursively to see if they are in Skyward.
3a. If so, do nothing.
3b. If not, move to Students-Disabled since they are not an active student and disable account.
4. With everything logged on disk, email if desired.
5. End program, run again using cronjob setting environment variables using googleWorkspace_SkywardDbSyncToGoogleUsers-envvar.sh
