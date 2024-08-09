import requests, time, csv
from requests.auth import HTTPBasicAuth
# Light implementation of OneRoster v1.1 REST Api for grabbing Student Data, will be good test for eventual full feature complient library

# Workflow:
# Client creates instance of onerosterRESTConnection using client_id and client_secret env vars, valid for x seconds.
# Then queries can be made pythonically

class Student():
    def __init__(self):
        # https://www.imsglobal.org/oneroster-v11-final-specification#_Toc480452019
        self.sourceId = None
        self.status = None
        self.dateLastModified = None
        self.metadata = None
        self.username = None
        self.userIds = None
        self.enabledUser = None
        self.givenName = None
        self.familyName = None
        self.middleName = None
        self.role = None
        self.identifier = None
        self.email = None
        self.sms = None
        self.phone = None
        self.agents = None
        self.orgs = None
        self.grades = None
        self.password = None
        

class oneRosterRESTConnection():
    
    def __init__(self, client_id, client_secret, apiUri):
        super().__init__() # Init Class
        self.client_id = client_id
        self.client_secret = client_secret
        self.apiUrl = apiUri # Must end with ims/oneroster/v1p1, for instance, Aeries Demo is https://demo.aeries.net/aeries/ims/oneroster/v1p1
        self.client_token = False # Init to false to show not authenticated yet
        self.ttl_seconds = False # Seconds until token expires
        self.time_authenticated = False # Time authentication happened, so we know when expires.
        self.students_json = None
        self.students_array = []
        
    def attemptAuthentication(self):
        # Attempt HTTP Basic Auth to get a token to use as authorization: Bearer <access_token>
        basicAuthCreds = HTTPBasicAuth(self.client_id, self.client_secret)
        
        # Construct token uri
        tokenUrl = (self.apiUrl).replace('ims/oneroster/v1p1', 'token')
        
        response = (requests.post(tokenUrl, auth=basicAuthCreds)).json()
                
        self.client_token = response.get("access_token")
        self.ttl_seconds = response.get("expires_in")
        self.time_authenticated = time.time()
        
        print("Authentication Sucessful!")
            
            
    def convert_students(self):
        if len(self.students_json) == None:
            print("Cannot run, sync_students has not ran.")
        else:
            # Grab array object
            userArray = self.students_json["users"]
            
            for student in userArray:
                newStudent = Student()
                                
                # Load values
                newStudent.sourceId = student.get("sourceId")
                newStudent.status = student.get("status")
                newStudent.dateLastModified = student.get("dateLastModified")
                newStudent.metadata = student.get("metadata")
                newStudent.username = student.get("username")
                newStudent.userIds = student.get("userIds")
                newStudent.enabledUser = student.get("enabledUser")
                newStudent.givenName = student.get("givenName")
                newStudent.familyName = student.get("familyName")
                newStudent.middleName = student.get("middleName")
                newStudent.role = student.get("role")
                newStudent.identifier = student.get("identifier")
                newStudent.email = student.get("email")
                newStudent.sms = student.get("sms")
                newStudent.phone = student.get("phone")
                newStudent.agents = student.get("agents")
                newStudent.orgs = student.get("orgs")
                newStudent.grades = student.get("grades")
                newStudent.password = student.get("password")
                
                # Append newStudent to self.students_array
                self.students_array.append(newStudent)
                studentName = newStudent.givenName + " " + newStudent.familyName

            print("Student import sync finished! Imported " + str(len(self.students_array)) + " students.")

    def sync_Students(self):
        # Do a GET request to the server to get a JSON array of all the latest Student data
        self.students_json = (requests.get((self.apiUrl + "/students"), headers={'authorization': ('Bearer ' + self.client_token)})).json()
        self.convert_students()
        

    def studentToCSV(self, csvName):
        # Process to CSV:
        with open(csvName + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            field = [                
                    "sourceId",
                    "status",
                    "dateLastModified",
                    "metadata",
                    "username",
                    "userIds",
                    "enabledUser",
                    "givenName",
                    "familyName",
                    "middleName",
                    "role",
                    "identifier",
                    "email",
                    "sms",
                    "phone",
                    "agents",
                    "orgs",
                    "grades",
                    "password"
            ]
            
            writer.writerow(field)

            for student in self.students_array:
                dimArray = [
                    student.sourceId,        
                    student.status,
                    student.dateLastModified,
                    student.metadata,
                    student.username,
                    student.userIds,
                    student.enabledUser,
                    student.givenName,
                    student.familyName,
                    student.middleName,
                    student.role,
                    student.identifier,
                    student.email,
                    student.sms,
                    student.phone,
                    student.agents,
                    student.orgs,
                    student.grades,
                    student.password
                ]
                writer.writerow(dimArray)