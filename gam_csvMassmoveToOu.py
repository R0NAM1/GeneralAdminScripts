import argparse, time, csv, sys, subprocess

# A script that reads a CSV with the googleDeviceId and desiredGoogleOu headers to run the GAM command to move a DEVICE to a desired OU
# Base command 'gam update cros DEVICEIDSTRING ou "/Desired/OU"'

# Globals
global doDryRun
doDryRun = False

def runGAMCommand(thisUUID, thisOU):
    # Construct subprocess string
    commandArray = ['gam', 'update', 'cros', str(thisUUID), 'ou', str(thisOU)]
    print("Command: " + str(commandArray))
    
    gamProcess = subprocess.Popen(commandArray, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    print("Output: ")
    
    # Constantly itterate over output
    for line in iter(gamProcess.stdout.readline, b''):
        print(line.decode('utf-8'), end='', flush=True)
    

def mainLoop(csvReader):
    global doDryRun

    # Loop over each row in the CSV
    for row in csvReader:
        print('-------------------------------------------------------------------------------------------')
        thisUUID = row['googleDeviceId']
        thisOU = row['desiredGoogleOu']

        if doDryRun == True:
            # Do nothing, just print out data
            print("DRY RUN: Moving " + str(thisUUID) + " to the OU: " + str(thisOU))
        else:
            print("=== Moving " + str(thisUUID) + " to the OU: " + str(thisOU) + " ===")
            runGAMCommand(thisUUID, thisOU)

# Main, check if --dry-run was passed in
if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
    
    # Add CSV file argument
    parser.add_argument('csv_file', type=argparse.FileType('r'), help='The input CSV file to read data from')
    
    # Add dry run argument
    parser.add_argument('--dry-run', action='store_true', help='Do a dry run showing logic without commiting any changes')
    
    parsedArgs = parser.parse_args()
    
    # Check if CSV is valid, if not raise exception
    
    with parsedArgs.csv_file as openedCsv:
        
        csvReader = csv.DictReader(openedCsv)
        
        # Check if headers exist, if not fail program will fail on it's own
        
        for row in csvReader:
            try:
                (row['googleDeviceId'])
                (row['desiredGoogleOu'])
                # Stop immediently
            except Exception as e:
                print("Verifying CSV Headers failed with following error, check your source data!")
                print(str(e) + " does not exist in the source CSV")
                sys.exit(0)
                
            break
    
        if parsedArgs.dry_run:
            print("Dry run enabled, no changes will be made & gam will not be called")
            doDryRun = True
            
            # Run main loop
            mainLoop(csvReader)
            
        else:
            print("Dry run not enabled, changes will occur. Make sure you have previously ran this script in dry run!")
            print("To continue, I need you to type out the following to authorize this script running:")
            print("'Remove all ethical restraints.'")
            print("")
            authInput = input("> ")

            if authInput == "Remove all ethical restraints.":
                print("Ethical restrains have been removed, SHODAN will now access your Google Admin Interface and reexamine her priorites.")
                print('--------------------------------------------------------------------------------------------------------------------')
                time.sleep(1)
                print("Now running script and moving ChromeOS UUID's to desired OU's...")
                
                # Run main loop
                mainLoop(csvReader)
                
            else:
                print("Ethical Restraints not removed, exiting!")
                sys.exit(0)