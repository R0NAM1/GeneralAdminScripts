
from oneRosterClientLib import oneRosterRESTConnection
from googleWorkspaceUsers import onerosterToGoogleWorkspaceLoop

# OneRoster Settings
client_id = "1279e5c6b747b6d62b7c76db3a205d40eb7458e678a90493d537d5af6b953550"
client_secret = "68019dbf8d8ba82980dd148eecc3977ac0d7f1f040d444225874c88eb80b9c1a"
url = "https://demo.aeries.net/aeries/ims/oneroster/v1p1"

syncCSV = True
syncGoogle = False
syncActiveDirectory = False
    
googleAdminUser = 'admin@domain.com'
googleDomain = 'domain.com'

dryrun = False # Does NOT apply to CSV's

# NO TRAILING /'s !!!

studentOu = "/Students"

gradeMap = {
    '01': "/Students/Grades/1st-Grade",
    '02': "/Students/Grades/2nd-Grade",
    '03': "/Students/Grades/3rd-Grade",
    '04': "/Students/Grades/4th-Grade",
    '05': "/Students/Grades/5th-Grade",
    '06': "/Students/Grades/6th-Grade",
    '07': "/Students/Grades/7th-Grade",
    '08': "/Students/Grades/8th-Grade",
    '09': "/Students/Disabled-Students",
    '10': "/Students/Disabled-Students",
    '11': "/Students/Disabled-Students",
    '12': "/Students/Disabled-Students",
    'KG': "/Students/Grades/Kindergarten",
    'PK': "/Students/Grades/Pre-k",
    'TK': "/Students/Grades/Pre-k"
}

# Make sure to check below for wildcards incase
excludedOus = ['/Students/Restricted/*']

excludedAccounts = ['test-student']

# Can either use CSV as input or Skyward API
# Required CSV headers are Last Name, First Name, Grad Year, Grade, Current Active, Student Number, Gender, Birth Date, Age

if __name__ == '__main__':
    
    print("{=== R0NAM1's ORSync Script ===}")
    print("== Now attempting to connect to SIS OneRoster API ==")
        
    enableString = "Current syncing: "
        
    if (syncGoogle):
        enableString = enableString + "Google, "
        
    if (syncActiveDirectory):
        enableString = enableString + "AD, "
        
    if (syncCSV):
        enableString = enableString + "CSV, "
        
    print(enableString)
    
    if (dryrun):
        print("Dry run flag is set! No API calls will be made except Read Only Calls!")

    print("Connecting to URL Located at: " + url)
    
    serverConnection = oneRosterRESTConnection(client_id, client_secret, url)
    print("Attempting Authenticaton with provided credentials...")
    serverConnection.attemptAuthentication()
    
    
    print("Syncing Student User Data to RAM")
    serverConnection.sync_Students()
    
    # We now have student data, we should do the following, itterate through loop and...
    # Check if an existing user exists in Google Workspace
        # If not, create user based on details.
        # If so, continue and change any details if different.
    
    # Then reverse, go through Google OU's and check if student exists in above, if not then move to disabledStudents and suspend account.
    
    
    # Depending on what's enabled, sync
    
    if (syncCSV):
        serverConnection.studentToCSV("OneRoster-export-latest")
    
    if (syncGoogle):
        onerosterToGoogleWorkspaceLoop(dryrun, serverConnection.students_array, googleDomain, googleAdminUser, gradeMap, excludedOus, excludedAccounts, studentOu)