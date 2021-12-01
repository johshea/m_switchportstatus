#Simple Switch Prt status check to return switch ports enabled but currently down
# Requirements
# Python 3.8 or >, Meraki SDK (pip(3) install meraki)
#dashboard API key with at least read access
#this application polls all switches in an org and collects port status. Reports are
#generated based on ports in an enabled state but showing currently disconneccted.
#The application will create a folder titled switchport_data and store timestamped versions.
#output can be selected as Json or CSV at runtime.
#
#******Running the APP******
#python main.py
#provide your api key and and org name when prompted

import meraki
import sys, datetime, json, time
from pathlib import Path

def main(argv):
    #function for resolving orgname to org ID
    def get_org(arg_orgname):
        org_response = dashboard.organizations.getOrganizations()
        for org in org_response:
            if org['name'].lower() == arg_orgname.lower():
                orgid = org['id']
                # print(orgid)
                #print("Org" + " " + orgid + " " + "found.")
                return(orgid)

            else:
                print("No Org Found!")
                sys.exit(0)

    def get_networks(orgid):
        networks = dashboard.organizations.getOrganizationNetworks(orgid, total_pages='all')
        return(networks)

    def get_devices(orgid):
        devices = dashboard.organizations.getOrganizationDevices(orgid, total_pages='all')
        return(devices)


    #Function for creating output as CSV
    def output_csv(data, flag, filename):
        # Create and write the CSV file (Windows, linux, macos)
        if len(data) > 0:
            keys = data[0].keys()
            Path(flag).mkdir(parents=True, exist_ok=True)
            inpath = Path.cwd() / flag / filename
            # print(inpath)
            with inpath.open(mode='w+', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(data)
        return ('success')

    #Function for creating output as json
    def output_json(data, flag, filename):
        if len(data) > 0:
            Path(flag).mkdir(parents=True, exist_ok=True)
            inpath = Path.cwd() / flag / filename
            with inpath.open('w') as jsonFile:
                json.dump(data, jsonFile, indent=4, sort_keys=True)
        return ('success')


    #Collect User Input
    #get API Key
    arg_apikey = input("Please enter your Meraki API Key: ")
    if arg_apikey != '':
        API_KEY = arg_apikey
        dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

    arg_orgname = input("Please enter your Organization name: ")
    #resolve the org name to an ID
    if arg_orgname.lower() != '':
        orgid = get_org(arg_orgname)
        devices = get_devices(orgid)
        #print(devices) #Test for device data return

    print("**Format**")
    print("json")
    print("csv")
    arg_filetype = input("Please enter a format (default json): ")
    if arg_filetype == '':
        arg_filetype = 'json'

    else:
        sys.exit(0)

    # set and format the time object
    timenow = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")


    #get all serial #s and fileter to MS serials only
    #create a dataset with relevant data

    try:
        portdata = []
        for serial in devices:
            if serial["productType"] == "switch":
                 switch = dashboard.switch.getDeviceSwitchPortsStatuses(serial['serial'])

                 for switchports in switch:
                    if switchports['enabled'] and switchports['status'] == 'Disconnected':
                        port_df = {'Port #': switchports['portId'], 'enabled': switchports['enabled'], 'Status': switchports['status']}
                        portdata.append(port_df)
                        #print(port_df) # validate the data

                    time.sleep(1)

                    #send to function for formatting
                    # Set Variables and send to the CSV report function
                    data = portdata
                    flag = 'switchport_data'
                    filename = serial['name'] + str(timenow) + '.' + arg_filetype

                    if arg_filetype == 'csv':
                        output = output_csv(data, flag, filename)
                    elif arg_filetype == 'json':
                        output = output_json(data, flag, filename)


    except Exception as e:
        print(e)

    print("All Done. Have a nice day!")


if __name__ == '__main__':
    main(sys.argv[1:])

