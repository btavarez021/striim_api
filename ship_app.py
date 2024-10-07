from flask import Flask, render_template, jsonify, request
from requests.exceptions import RequestException
import requests
import json
from requests import RequestException
import urllib.parse
from urllib.parse import urljoin
import os
import logging
from datetime import datetime
from creds import username, password

# print(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

logging.basicConfig(filename="./logs/striim_api_{:%Y-%m-%d_%H}.log".format(datetime.now()),
                    format='%(asctime)s %(message)s',
                    filemode='w', level=logging.INFO)

app = Flask(__name__)

striim_api_url = "http://localhost:5001/api/v1"
discovery_striim_api_url = 'http://10.65.61.154:9080/'
auth_path = 'security/authenticate'



# encoded_password = urllib.parse.quote(str(password))

# if password:
#     encoded_password = urllib.parse.quote(password)
# else:
#     print("Password not found in environmental variables.")

SHIP_API_MAP = {"Discovery":r"http://10.65.61.154:9080/api/v2/applications", 
                "Dawn":r"http://dawstriim01v.dawn.ncl.com:9080/api/v2/applications", "Epic":"http://epistriim01v.epic.ncl.com:9080/api/v2/applications", 
                "Encore":"http://encstriim01v.encore.ncl.com:9080/api/v2/applications", "Escape": r"http://escstriim01v.escape.ncl.com:9080/api/v2/applications",
                "Gem":"http://gemstriim01v.gem.ncl.com:9080/api/v2/applications", "Getaway":"http://getstriim01v.getaway.ncl.com:9080/api/v2/applications",
                "Bliss":"http://blistriim01v.bliss.ncl.com:9080/api/v2/applications", "Breakaway":"http://brestriim01v.breakaway.ncl.com:9080/api/v2/applications",
                "Sun":"http://sunstriim01v.sun.ncl.com:9080/api/v2/applications", "Jewel":"http://jewstriim01v.jewel.ncl.com:9080/api/v2/applications",
                "Spirit":"http://spistriim01v.spirit.ncl.com:9080/api/v2/applications", "Gem":"http://gemstriim01v.gem.ncl.com:9080/api/v2/applications",
                "Pearl":"http://peastriim01v.pearl.ncl.com:9080/api/v2/applications", "Sky":"http://skystriim01v.sky.ncl.com:9080/api/v2/applications",
                "Jade":"http://jadstriim01v.jade.ncl.com:9080/api/v2/applications", "Joy":"http://joystriim01v.joy.ncl.com:9080/api/v2/applications",
                "Viva":"http://vivstriim01v.viva.ncl.com:9080/api/v2/applications", "Prima":"http://pristriim01v.prima.ncl.com:9080/api/v2/applications",
                "Pride of America": "http://10.15.50.154:9080/api/v2/applications", "Star": "http://10.3.50.154:9080/api/v2/applications",             
                "Explorer":"http://10.31.50.154:9080/api/v2/applications",          "Grandeur":"http://10.75.50.154:9080/api/v2/applications",
                "Insignia":"http://10.16.50.154:9080/api/v2/applications", "Marina":"http://10.19.50.154:9080/api/v2/applications",
                "Mariner":"http://marstriim01v.mariner.rssc.com:9080/api/v2/applications", "Nautica":"http://10.18.50.154:9080/api/v2/applications",
                "Navigator":"http://navstriim01v.navigator.rssc.com:9080/api/v2/applications", "Regatta":"http://regstriim01v.regatta.oceaniacruises.com:9080/api/v2/applications",
                "Riviera":"http://10.20.50.154:9080/api/v2/applications", "Sirena":"http://10.68.50.154:9080/api/v2/applications",
                "Splendor":"http://10.71.50.154:9080/api/v2/applications", "Voyager":"http://voystriim01v.voyager.rssc.com:9080/api/v2/applications",
                "Vista":"http://visstriim01v.vista.ncl.com:9080/api/v2/applications", "Voyager":"http://voystriim01v.voyager.rssc.com:9080/api/v2/applications",
                
                }

@app.route('/')
def index():
    return render_template('index.html', active_page='interactive_cli')

def build_url(selected_ship, endpoint_type='token', authToken=None):
   """Builds the correct URL based on the selected ship and endpoint type."""
   base_url = SHIP_API_MAP.get(selected_ship)
   if not base_url:
       logging.error(f"Error: Could not find URL for ship: {selected_ship}")
       return None
   parts = base_url.split("/")
   segment_to_keep = [0, 1, 2]  # Keeping the first three parts of the URL
   new_parts = [part for idx, part in enumerate(parts) if idx in segment_to_keep]
   if endpoint_type == 'token':
       endpoint = '/security/authenticate'
   elif endpoint_type == 'health':
       endpoint = f'/health?token={authToken}'
   else:
       logging.error(f"Error: Unknown endpoint type: {endpoint_type}")
       return None
   parsed_url = "/".join(new_parts) + endpoint
   logging.info(f"Built URL: {parsed_url}")
   return parsed_url

# def parse_token_url():
#             #Ensure data is provided in the request and extract the selected ship
#             data = request.json
#             logging.info(f"Data received from front end {data }")
#             print("DATA in parse token URL: ", data)
#             if 'ship' in data:
#                 selected_ship = data.get('ship')
#             elif 'selectedValue' in data:
#                 selected_ship = data.get('selectedValue')
#             print("SELECTED SHIP IN PARSE TOKEN URL: ", selected_ship)
#             logging.info(f"Selected ship for token authentication is: {selected_ship}")


#             #Parse STRIIM URL for the token endpoint
#             token_endpoint = '/security/authenticate' 
#             # health_endpoint = f'health?token={authToken}'
            
#             print("MY JSON: ", data)

#             if 'selectedValue' in data or 'ship' in data:
#                 url = SHIP_API_MAP.get(selected_ship)
#                 print("URL IN get creds: ", url)
#                 logging.info(f"Using STRIIM API URL: {url}")
#             else:
#                 logging.info("Could not find STRIIM URL from response.")
            
#             #Map the selectes hip to the correct URL
#             # url = SHIP_API_MAP.get('selected_ship')
#             parts = url.split("/")
#             logging.info(f"Split URL to append token endpoint: {parts}")\

#             segment_to_keep = [0,1,2]
#             new_parts = [part for idx, part in enumerate(parts) if idx in segment_to_keep]
#             print("NEW PARTS: ", new_parts)
#             parsed_url = "/".join(new_parts) + token_endpoint
#             logging.info(f"Using the following URL as the  {parsed_url}")
#             print("DAWN URL?: ", parsed_url)

#             return parsed_url
    
def get_credentials(selected_ship):
            
            data = request.json

            if not data:
                logging.error("Did not receieve any selections from the front end.")
                return jsonify({"error": "No data received from front end."})
            else:
                logging.info(f"Received the following from the frontend: {data}")
            
            # selected_ship = data.get('ship')
            logging.info(f"Retrieving credentials for {selected_ship}")

            print({selected_ship: password.get(selected_ship)})

            #fetch corresponding password based on the ship name
            # logging.info(password[selected_ship])
            ship_username = username.get('username')
            ship_password = password.get(selected_ship)

            if not ship_username:
                logging.error(f"Could not find username: {username}")
                return jsonify({"Error": "No username found."})
            else:
                logging.info(f"Username found!")

            if not ship_password:
                logging.error(f"Error: No password configured for {selected_ship}")
                return f"Error: No password configured for {selected_ship}"
            else:
                logging.info
            #Prepare the payload for the authentication request
            headers = {'username': ship_username, 'password': str(ship_password)}
            logging.info(f"Credentials found for {selected_ship}")

            return headers

def get_token(selected_ship, token_url):
   print("Attempting to get token for ship:", selected_ship)
   # Retrieve the credentials/headers for the selected ship
   headers = get_credentials(selected_ship)
   print("HEADERS IN TOKEN: ", headers)
   try:
       # Make the post request to retrieve the token for the ship
       resp = requests.post(token_url, data=headers)
       logging.info(f"Response from token request: {resp.text}")
       print("Response Status: ", resp.status_code)
       if resp.status_code != 200:
           logging.error(f"Failed to retrieve token. Status Code: {resp.status_code}")
           return None
       # Parse the JSON response and extract the token
       token_json = resp.json()
       token = token_json.get("token")
       if not token:
           logging.error("Token not found in response.")
           return None
       logging.info(f"Retrieved token for {selected_ship}: {token}")
       return token
   except requests.exceptions.RequestException as ex:
       logging.error(f"Request failed: {ex}")
       return None
   except Exception as e:
       logging.error(f"Error: {e}")

def health_stats(authToken, appname=None):

    app_status = {}

    striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint=None)
    print("BENNY URLLL", striim_ship_api_url)

    health_url = build_url(selected_ship, endpoint_type='health', authToken=authToken)

    # parsed_url = parse_token_url()
    
    resp = requests.get(health_url)
    if resp.status_code == 200:
        print("HEALTH STATS: ", resp)
        logging.info("Application health API was retrieved successfully.")
        logging.info("Looking to see if application name was given...")
        data = json.loads(resp.text)
        # print(f"Health: {data}")
        if appname != None:
            logging.info("")
            for key , value in data.items():
                if key == 'healthRecords':
                    for inner_key, inner_value in value[0].items():
                        if inner_key =='appHealthMap':
                            for inner_inner_key, inner_inner_value in inner_value.items():
                                if appname in inner_inner_value["fqAppName"]:
                                    logging.info(f"Health stats for {appname} found.")
                                    app_status[inner_inner_value["fqAppName"]] = inner_inner_value["status"]
        else:
            logging.info("No specific application name given. Will display health stats for all applications.")
    else:                           
         logging.error(f"Error: {resp.status_code} - {resp.text} - {resp.url}")

    return data, app_status

@app.route('/striim/status-by-ship', methods=['POST', 'GET'])
def health_stats_by_ship(appname=None):
   data = request.get_json()
   if not data:
       logging.error("No selection from the drop down menu received.")
       return jsonify({"error": "No data received"}), 400
   else:
       logging.info(f"Received {data} from the drop down menu.")
   selected_ship = data.get('ship')
   logging.info(f"Going to use {selected_ship} to get API URL.")
   app_health = {}
   if selected_ship == 'All':
       for ship, url in SHIP_API_MAP.items():
           # Build the token URL for each ship
           token_url = build_url(ship, endpoint_type='token')
           # Get token for each ship
           authToken = get_token(ship, token_url)
           if not authToken:
               logging.error(f"Failed to retrieve token for {ship}. Skipping...")
               continue
           # Build the health URL with the token
           health_path = f'health?token={authToken}'
           parsed_url = "/".join(url.split("/")[:3]) + "/" + health_path
           logging.info(f"Final API URL for {ship}: {parsed_url}")
           headers = get_credentials(ship)
           response = requests.get(parsed_url, headers=headers)
           if response.status_code == 200:
               app_health[ship] = response.json()  # Store successful response
           else:
               logging.error(f"Failed to retrieve health stats for {ship}. Status Code: {response.status_code}")
               # Store blank values for ships with errors
               app_health[ship] = {
                   'healthRecords': [
                       {
                           'appHealthMap': {
                               'blankApp': {
                                   'fqAppName': '',
                                   'status': ''
                               }
                           }
                       }
                   ]
               }
       return render_template("ship_status_table.html", active_page='status', selected_ship='All', app_health=app_health)
   else:
       # Handle a single ship case
       url = SHIP_API_MAP.get(selected_ship)
       if not url:
           return jsonify({"error": "Invalid ship selected"}), 400
       token_url = build_url(selected_ship, endpoint_type='token')
       authToken = get_token(selected_ship, token_url)
       if not authToken:
           return jsonify({"error": "Failed to retrieve token"}), 502
       health_path = f'health?token={authToken}'
       parsed_url = "/".join(url.split("/")[:3]) + "/" + health_path
       logging.info(f"Final API URL for {selected_ship}: {parsed_url}")
       headers = get_credentials(selected_ship)
       response = requests.get(parsed_url, headers=headers)
       if response.status_code == 200:
           app_health = response.json()
       else:
           logging.error(f"Failed to retrieve health stats for {selected_ship}. Status Code: {response.status_code}")
           # Add blank values for a single ship with an error
           app_health = {
               'healthRecords': [
                   {
                       'appHealthMap': {
                           'blankApp': {
                               'fqAppName': '',
                               'status': ''
                           }
                       }
                   }
               ]
           }
       return render_template("ship_status_table.html", active_page='status', selected_ship=selected_ship.capitalize(), app_health=app_health)

def url_builder(endpoint=None):
    command = None
    selected_ship = None
    app_name = None

    if request.is_json:
        print("IS JSON")
        data = request.get_json()
        print("Benn2: ", data)
        selected_ship = data.get('ship')
        print("benny data: ", selected_ship)
        command = data.get('command')
        app_name = data.get('appName')
        print("app_name: ", app_name)
    else:
        selected_ship = request.form.get('ship')
        command = request.form.get('command')
        app_name = request.form.get('appName')
        print("app_name: ", app_name)
        print("REQUEST" , request)
        print("NOT JSON")
        print("Selected ship" ,selected_ship)

    # if not selected_ship:
    #     print("NO SHIP SELECTED?")
    #     logging.error("No ship selected")
    #     return jsonify({"error": "No ship selected"}), 400

    print("HIIDF")
    print(f"Selected Ship: {selected_ship}")
    ship_url = SHIP_API_MAP.get('Discovery')
    print(f"SHIP URL: {ship_url}")

    if not ship_url:
        logging.error(f"Could not find {ship_url}")
        return jsonify(f"Could not find {ship_url}"), 400
    
    if endpoint:
        striim_ship_api_url = f"{ship_url}/{app_name}/{endpoint}"
        logging.info(f"Built following URL: {striim_ship_api_url}")
    else:
        striim_ship_api_url = ship_url
    
    print("1: ", striim_ship_api_url)
    print("2", selected_ship)
    print("3", app_name)

    return striim_ship_api_url, selected_ship, command, app_name

# Route to check the deployment status (GET)
@app.route('/application/status', methods=['GET'])
def check_deployment_status():
    print("HIIIII")
    logging.info(f"Checking deployment status...")
    print("YES OK")

    ship = request.args.get('ship')
    app_name = request.args.get('appName')

    print(f"SHIPPP: {ship}, APPNAME: {app_name}")

    # Retrieve auth token
    auth_token = get_token()

    # Build the URL and other necessary info
    striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint='deployment')

    headers = {
        "Authorization": f"STRIIM-TOKEN {auth_token}",
        "Content-Type": "application/json"
    }
    try:
        # Make a GET request to check the current status of the application
        status_response = requests.get(f'{striim_ship_api_url}', headers=headers)
        print(f"RESPONSE CHECK DEPLOY: {status_response.status_response}")

        if status_response.status_code == 200:
            status_data = status_response.json()
            logging.info(f"Current deployment status: {status_data}")
            # Check if the application is already deployed
            if status_data.get('status') == 'DEPLOYED':
                logging.error(f"{app_name} on {selected_ship} is already deployed.")
                return jsonify({"message": f"{app_name} on {selected_ship} is already deployed."}), 200
            else:
                logging.info(f"{app_name} on {selected_ship} is not deployed.")
                return jsonify({"message": f"{app_name} on {selected_ship} is not deployed."}), 200
        else:
            logging.error(f"Failed to retrieve status. Status code: {status_response.status_code}")
            return jsonify({"error": "Failed to retrieve application status."}), status_response.status_code
    except requests.RequestException as e:
        print(f"Error retrieving status: {str(e)}")
        logging.error(f"Error retrieving status: {str(e)}")
        return jsonify({"error": str(e)}), 500
   
@app.route('/application/deploy', methods=['POST', 'GET'])
def deploy_app():
    auth_token = get_token()
    striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint='deployment')
    headers = {
        "Authorization": f"STRIIM-TOKEN {auth_token}",
        "Content-Type": "application/json"
    }
    logging.info(f"Starting deployment process for app: {app_name} on ship: {selected_ship}")
    try:
        # Proceed with deployment
       logging.info(f"Deploying {app_name} on {selected_ship}...")
       deploy_response = requests.post(f'{striim_ship_api_url}', headers=headers)
       if deploy_response.status_code == 200:
           deploy_data = deploy_response.json()
           logging.info(f"Deployment successful: {deploy_data}")
           return jsonify({"message": f"Successfully deployed {app_name} on {selected_ship}."}), 200
       else:
           logging.error(f"Failed to deploy {app_name} on {selected_ship}. Status code: {deploy_response.status_code}")
           return jsonify({"error": f"Failed to deploy {app_name} on {selected_ship}."}), deploy_response.status_code
    except requests.RequestException as e:
       logging.error(f"Error during deployment: {str(e)}")
       return jsonify({"error": str(e)}), 500   
    
@app.route('/application/undeploy', methods=['DELETE'])
def undeploy_app():

    auth_token = get_token()

    striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint='deployment')

    headers = {
        "Authorization": f"STRIIM-TOKEN {auth_token}", 
        "Content-Type": "application/json"
    }
    try:
        logging.info(f"Trying to undeploy app: {app_name} on ship {selected_ship}")
        response = requests.delete(f'{striim_ship_api_url}', headers=headers)
        print(f"RESPONSE: {response.status_code}")
        print(f"FINAL URL {response.url}")

        if response.status_code == 200:
            logging.info(f"{app_name} undeployed successfully!")
            status_data = response.json()
            print(f"JSONNN: {status_data}")
            return jsonify({"message":f"Succesfully undeployed {app_name} on {selected_ship}"}), 200
        else:
            print(f"failed with statuscode {response.status_code}")
            logging.error(f"Failed to undeploy {app_name} on {selected_ship}")
            logging.error(f"failed with statuscode {response.status_code}")
            print("HIII UNDEPLOY")
            return jsonify({"error": f"Failed to undeploy {app_name} on {selected_ship}"})
    except requests.RequestException as e:
        print(f'RequestException: {str(e)}')
        logging.error("Error trying to undeploy applications")
        logging.error(str(e), response.status_code)
        return jsonify({"error": str(e)}), 500
    


@app.route('/striim/status-all', methods=['POST', 'GET'])   
def check_status_by_ship():

    striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint='deployment')


    try:
        if request.method == 'GET':
            return render_template('all_status.html')
        elif request.method == 'POST':
            print("REQUEST", request)
            data = request.get_json()
            print("data", data)
            print("HIIII")
            if not data:
                return jsonify({"error": "No data received"}), 400
            
            selected_ship = data.get('ship')

            if selected_ship is None:
                return jsonify({"error":"selectedValue is required"}),400

            return jsonify({"selected_ship":selected_ship})
    except ValueError as ve:
        print(str(ve))
        return jsonify({"error": str(ve)}), 400
    except requests.RequestException as re:
        print(str(re))
        return jsonify({"error": "Failed to fetch data from the external service"}), 502
    except Exception as e:
        print(str(e))
        return jsonify({"error": " An unexpected error occurred. Please try again later"}), 500

@app.route("/get_applications", methods=["POST"])                             
def get_applications():

    try:
        print("YES??")
        auth_token = get_token()
        print("AUTH TOKEN2222: ", auth_token)
        if not auth_token:
            raise ValueError("Authorization token is missing")
        app_health, app_status = health_stats(auth_token)
        print("HELLO UNDER", app_health)


        applications = []

        if app_health and 'healthRecords' in app_health:
            for record in app_health['healthRecords']:
                if 'appHealthMap' in record:
                        app_health_map = record['appHealthMap']
                        for app_key, app_value in app_health_map.items():
                            applications.append(app_value["fqAppName"])
        # print(applications)
        return jsonify({"applications":applications})
    except Exception as e:
        return jsonify({f"error": str(e)}), 500

@app.route('/striim/status', methods=['POST'])
def check_status():

    striim_ship_api_url, selected_ship, command, app_name= url_builder()

    print(f"SHIP URL {striim_ship_api_url} and {selected_ship}")

    try:
        response = requests.get(f'{ship_url}/server/status')
        print(f"RESPONSE: {response}")
        if response.status_code == 200:
            status_data = response.json()
            print(f"JSONNN: {status_data}")
            return jsonify({"message":f"{selected_ship} is {status_data.get('status')}"}), 200

        else:
            print(f"failed with statuscode {response.status_code}")
            return jsonify({"error": f"Failed to send command(s) to {selected_ship}"}), response.status_code
    except requests.RequestException as e:
        print(f'RequestException: {str(e)}')
        return jsonify({"error": str(e)}), 500


@app.route('/striim/sendcommands', methods=['POST'])
def send_commands_to_ship():

    striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint="deployment")

    ship_url = SHIP_API_MAP.get(selected_ship)
    print(SHIP_API_MAP[selected_ship] )

    print(f"This is the ship chosen: {selected_ship}")
    print(f"This command was received:{command}")

    if not command or not selected_ship:
        return jsonify({"error": "Commands and ship(s) must be provided"}), 400

    if not ship_url:
        return jsonify({"error": f"Could not find {selected_ship}"}), 404
    
    if len(command) <= 5:
        return jsonify({"error": f"Please enter a longer command."}), 404
    
    payload = {
        "ship": selected_ship, 
        "command": command}
    
    print(f"PAYLOAD: {payload}")
    
    try:
        response = requests.post(f'{ship_url}/server/restart', json=payload)
        if response.status_code == 200:
            # return jsonify(response.json()), 200
            return jsonify({"message": f"Sent command(s) to {selected_ship}"}), 200

        else:
            print(f"failed with statuscode {response.status_code}")
            return jsonify({"error": f"Failed to send command(s) to {selected_ship}"}), response.status_code
    except requests.RequestException as e:
        print(f'RequestException: {str(e)}')
        return jsonify({"error": str(e)}), 500


@app.route('/striim/stop', methods=['DELETE'])
def stop_server():

    striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint='sprint')

    auth_token = get_token()
    data, app_status = health_stats(auth_token, app_name)

    headers = {
        "Authorization": f"STRIIM-TOKEN {auth_token}",
        "Content-Type": "application/json"
    }


    try:
        logging.info(f"Trying to stop app: {app_name} on ship {selected_ship}")
        print(f'STOP {striim_ship_api_url}')
        response = requests.delete(f'{striim_ship_api_url}', headers=headers)
        try:
            resp = response.json()
            logging.info(f"Received: {resp}")
        except ValueError as json_error:
            return jsonify({"error":"Failed to parse response JSON", "details":str(json_error)}), 500
        logging.info(f"Checking to see if {app_name} is deployed")
        if resp.get('status') == 'DEPLOYED':
            logging.info(f"{app_name} is in deployed status. Will continue...")
            print("HI Inside")
            if response.status_code == 200:
                logging.info(f"{app_name} on {selected_ship} stopped successfully!")
                return jsonify({"message":f"{app_name} on {selected_ship} was stopped", "status":"stopped"}), 200
            elif response.status_code == 202:
                logging.info(f"{app_name} is trying to stop...")
                return jsonify({"message":f"{app_name} on {selected_ship} is stopping", "status":"stopping"}), 202
            else:
                logging.info(f"Failed to stop {app_name} on {selected_ship}. Please try again later.")
                return jsonify({"error": f"Failed to stop {app_name} on {selected_ship}. Please try again later."}), response.status_code
        else:
            logging.error(f"{app_name} on {selected_ship} is not deployed or started. Please deploy/start app before continuing.")
            logging.error(f"Current status: {app_name}: {app_status}")
            return jsonify({"error": f"{app_name} on {selected_ship} is not deployed or started. Please deploy/start app before continuing."}), 400
    except requests.RequestException as e:
        return jsonify({"error": f"{e}"}), 500

        
@app.route('/striim/start', methods=['POST'])
def start_server():

    striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint='sprint')

    auth_token = get_token()

    data, app_status = health_stats(auth_token, app_name)

    headers = {
        "Authorization": f"STRIIM-TOKEN {auth_token}",
        "Content-Type": "application/json"
    }

    try:
        logging.info(f"Trying to start app: {app_name} on ship {selected_ship}")        
        response = requests.post(f'{striim_ship_api_url}', headers=headers)
        print("RESPONSE ME", response)
        print(f'START FUNCTION {striim_ship_api_url}')
        try:
            resp = response.json()
            logging.info(f"Received: {resp}")
            print("RESPPP: ", resp)
        except ValueError as json_error:
            print("NOT RESPPP") 
            return jsonify({"error":"Failed to parse response JSON", "details":str(json_error)}), 500
        
        logging.info(f"Checking to see if {app_name} is deployed")
        if resp.get('status') == 'DEPLOYED':
            logging.info(f"{app_name} is in deployed status. Will continue...")
            if response.status_code == 200:
                print("Nada 1")
                logging.info(f"{app_name} on {selected_ship} started successfully!")
                return jsonify({"message":f"Successfully started {app_name} on {selected_ship}", "status":"running"}), 200
            elif response.status_code == 202:
                print("Nada 2")
                logging.info(f"{app_name} is trying to start...")
                return jsonify({"message":f"{app_name} on {selected_ship} is starting", "status":"pending"}), 202
            else:
                print("Nada 3")
                logging.error(f"Failed to start {app_name} on {selected_ship}. Response Code: {response.status_code}. Please try again later.")
                return jsonify({"error": f"Failed to start {app_name} on {selected_ship}. Please try again later."}), response.status_code
        else:
            print("Nada 4")
            logging.error(f"{app_name} on {selected_ship} is not deployed.")
            logging.error(f"Current status: {app_name}: {app_status}")
            return jsonify({"error": f"{app_name} on {selected_ship} is not deployed. {app_name}: {app_status}"}), 400
    except requests.RequestException as e:
        print("Nada 5")
        logging.error(f"Reponse Status Code: {response.status_code}. {str(e)}")
        return jsonify({"error": f"{e}"}), 500


@app.after_request    
def add_header(response):
    response.headers['Cache-Control'] ='no-store, no-chache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    
    app.run(debug=True, port=5000)