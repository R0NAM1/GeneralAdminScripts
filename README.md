A reposiotry for storing general use scripts, for example Google Admin Manager (GAM) update scripts, Windows Powershell Setup Scripts, and anything else that probably should be just a GIST but I'd rather it be a repo.

## Existing Scripts
### gam_csvMassmoveToOu.py
A python script that reads a CSV and itterates over its rows to run the GAM command 'gam update cros DEVICEIDSTRING ou /Desired/OU' as a subprocess, includes a dry run option to make sure data is fed in properly along with an "Are you sure?" prompt. Also includes a STEP option for you to make sure each itteration runs correctly.

CSV must contain the Google Device ID under the header 'googleDeviceId' and the desired OU to move it into under 'desiredGoogleOu'.

python3 gam_csvMassmoveToOu.py --dry-run --step template.csv