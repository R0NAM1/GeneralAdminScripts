from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

## LOGIKS
# Check if an existing user exists in Google Workspace
    # If not, create user based on details.
    # If so, continue and change any details if different.

# Then reverse, go through Google OU's and check if student exists in above, if not then move to disabledStudents and suspend account.

def onerosterToGoogleWorkspaceLoop(dryrun, studentArray, emailDomain, adminUser, gradeMap, excludedOus, excludedAccounts, studentOu):
    # Iterate over all imported students and format name into email, check if email exists.
        # If not create account and fill in details with temp password. auto-gen include in log
        # If so check if details match, if not attempt update
        
    print("=== Syncing users from local RAM to Google Workspace API ===")
        
    generatedService = initConnection(adminUser)
    
    print("-- Service Authentication Built --")
        
    emailDomain = "@" + emailDomain
        
    studentCounter = 0
        
    for student in studentArray:
        
        startTime = time.time()
        
        # Create email based on details
        # Example, first name + first letter of last name @domain
        # In future provide templates & custom since there are MANY ways to format names with emails, including grad year and such
        # THAT will be fun to calculate :|
        
        localLastName = student.middleName + " " + student.familyName
        generatedEmail = (student.givenName + student.familyName[0] + emailDomain).lower()
        print("Processing entry " + studentCounter + " : " + student.givenName + " " + localLastName + " : " + generatedEmail)
        
        ##############        
        try:
            userDetails = getUser(generatedService, generatedEmail)
            # User exists!
            
            googleLastName = userDetails['name']['middleName'] + " " + userDetails['name']['familyName']
            
            # Change all users details to source
            # Relevent details retrieved are: primaryEmail, name, suspended, archived, orgUnitPath
            # name, orgunit are the only ones synced so far
            updateUserDetails(generatedService, student, userDetails, gradeMap, excludedOus, dryrun)
        
        except:
            # User does not exist! Create account.
            createNewUser(generatedService, onerosterStudent, gradeMap, excludedOus, dryrun, generatedEmail)
            
        studentCounter = studentCounter + 1
        
        diffTime = time.time() - startTime
        
        print("Done processing student, took " + diffTime + " seconds!")
    
    print("OneRoster --> Google Workspace sync completed, running reverse sync to check for deleted students!")
    # Logic flow: We find all OU's under the General Student OU and check each student, if they are excluded (Test accounts, other) 
    
    googleOus = generatedService.orgunits().list().execute()
    
    print(googleOus)
    
    # Logic I hope works!
    
    for org in googleOus['organizationUnits']:
        #   "kind": "admin#directory#orgUnit",
        #   "name": "sales_support",
        #   "description": "a description",
        #   "etag": "string",
        #   "blockInheritance": false,
        #   "orgUnitId": "string",
        #   "orgUnitPath": "/corp/support/sales_support",
        #   "parentOrgUnitId": "string",
        #   "parentOrgUnitPath": "string"
        # Need to use orgUnitPath? 
        
        print(org['name'])
        print(org['description'])
        print(org['blockInheritance'])

            
def initConnection(ADMIN_USER):
    
    # Path to the service account key file
    SERVICE_ACCOUNT_FILE = 'oneRosterSync_ServiceAccount.json'

    # Scopes required by this endpoint
    SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly'] # Need to update to all

    # Return built service request

    # return [SERVICE_ACCOUNT_FILE, ADMIN_USER, SCOPES]
    creds = service_account.Credentials.from_service_account_file(
        initConnectionArray[0],
        subject=initConnectionArray[1],
        scopes=initConnectionArray[2])

    service = build('admin', 'directory_v1', credentials=creds)
    return service



def getUser(generatedService, userAtDomain):
    # Retrieves details of a specific user

    user = generatedService.users().get(userKey=userAtDomain).execute()
    # print('User Details:')
    # print(user)
    return user



def updateUserDetails(generatedService, onerosterStudent, userDetails, gradeMap, excludedOus, dryrun):
    # Check if details are different then oneroster details!!!!! 
    
    # "name": {
    # "givenName": "John",
    # "familyName": "Doe",
    # "fullName": "John Doe"
    # }
    # "orgUnitPath": "/Students/X-Grade/" ONLY IF if not exluded_ous (For email blocking, printer blocking etc etc)
    # Reason I'm not syning Custom OU changes from anywhere else it's because people often use different things and I don't know them all so I'm just doing OneRoster for Now,
    # I'll make a commit adding Google -> AD OU Changes eventually, probably.
    # Define the new user's details
    
    finalGivenName = userDetails['name']['givenName']
    finalFamilyName = userDetails['name']['middleName'] + ' ' + userDetails['name']['familyName']
    localLastName = onerosterStudent.middleName + " " + onerosterStudent.familyName

    
    # Check diff from oneroster and user.get
    # If local first name is different then google first name
    if (onerosterStudent.givenName != userDetails['name']['givenName']):
        print("Changing givenName from " + userDetails['name']['givenName'] + " --> " + onerosterStudent.givenName)
        finalGivenName = onerosterStudent.givenName
        
    # If local last name is different then google last name
    if (localLastName != finalFamilyName):
        print("Changing familyName from " + finalFamilyName + " --> " + localLastName)
        finalFamilyName = localLastName

    # Calculate orgUnitPath from grade
    orgUnitPath = gradeMap[onerosterStudent.grades[0]]
    
    if (orgUnitPath != userDetails['orgUnitPath']):
                
        # Check if in excluded OU's
        for excludedOu in excludedOus:
            excludedOuNoWildcard = excludedOu.replace("/*", "")
            
            # Check if matches
            if excludedOuNoWildcard in userDetails['orgUnitPath']:
                print("User currently in excluded OU or sub OU, checking for wildcard...")
            
                # Wildcards supported!
                if excludedOu.endswith("/*"):
                    print("User in excluded OU by wildcard! : " + excludedOu + " : Not touching orgUnitPath!")
                    orgUnitPath = userDetails['orgUnitPath']
                elif (excludedOuNoWildcard == userDetails['orgUnitPath']):
                    print("User is directly in excluded OU! : "  + excludedOu + " : Not touching orgUnitPath!")
                    orgUnitPath = userDetails['orgUnitPath']
                    
        ## NO EXCLUDED OU's, go ahead and change!
            
        # Check orgUnitPath
        if orgUnitPath != userDetails['orgUnitPath']:
            print("Changing orgUnitPath from " + userDetails['orgUnitPath'] + " to " + orgUnitPath)

    user_details = {
        # If student is not already in exludedOu, then set based on gradeMap
        
        "name": {
            "familyName": finalFamilyName,
            "givenName": finalGivenName
        },
        "orgUnitPath": orgUnitPath
    }

    try:
        # Create the new user
        if dryrun == False:
            result = service.users().insert(body=user_details).execute()
            print("User processed! ---")
            return True
        
        print("Dryrun enabled! Not calling users().insert...")
        return True
    
    except Exception as e:
        print("Exception while updating Student details: " + onerosterStudent.givenName + ' ' + onerosterStudent.middleName + ' ' + onerosterStudent.familyName)
        print("Exception follows as: " + e)
        return False
    
    
    
def createNewUser(generatedService, onerosterStudent, gradeMap, excludedOus, dryrun, generatedEmail):
    print("Creating new user in Google Workspace!")
    localLastName = onerosterStudent.middleName + " " + onerosterStudent.familyName

    ## TEMP PASSWORD TEMPLATE
    newTempPassword = "tempPassword2024!"

    # Calculate orgUnitPath from grade
    orgUnitPath = gradeMap[onerosterStudent.grades[0]]
    
    print("Setting user details to the following:")
    print("givenName: " + onerosterStudent.givenName)
    print("familyName: " + localLastName)
    print("changePasswordAtNextLogin: True")
    print("password: " + newTempPassword)
    print("orgUnitPath: " + orgUnitPath)

    user_details = {
        # If student is not already in exludedOu, then set based on gradeMap
        
        "primaryEmail": generatedEmail,
        "name": {
            "familyName": localLastName,
            "givenName": onerosterStudent.givenName,
            "displayName": onerosterStudent.givenName + " " + onerosterStudent.familyName,
            "fullName": onerosterStudent.givenName + " " + localLastName
        },
        "changePasswordAtNextLogin": True,
        "password": newTempPassword,
        "orgUnitPath": orgUnitPath
    }

    try:
        # Create the new user
        if dryrun == False:
            result = service.users().insert(body=user_details).execute()
            print("User created! ---")
            return True
        
        print("Dryrun enabled! Not calling users().insert...")
        return True
    
    except Exception as e:
        print("Exception while creating Student: " + onerosterStudent.givenName + ' ' + onerosterStudent.middleName + ' ' + onerosterStudent.familyName)
        print("Exception follows as: " + e)
        return False