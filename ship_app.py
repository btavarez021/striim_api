from requests.exceptions import RequestException
import requests
import json
from requests import RequestException
import urllib.parse
from urllib.parse import urljoin
import logging
from datetime import datetime
from creds import username, password, odp_sql_server_creds, striim_linux_server
import httpx
import asyncio
from dotenv import load_dotenv
from asyncio import Semaphore
from flask_cors import CORS
from quart import Quart, request, jsonify, render_template, abort
from quart_cors import cors
from cachetools import TTLCache
import asyncio
import aioodbc
import paramiko
from itertools import zip_longest
from concurrent.futures import ThreadPoolExecutor

# from db_connections import get_fidelio_odp_data

app = Quart(__name__)
cors(app)

load_dotenv()
timeout = httpx.Timeout(60.0)

global_app_health = {}

logging.basicConfig(filename="./logs/striim_api_{:%Y-%m-%d_%H}.log".format(datetime.now()),
                    format='%(asctime)s %(message)s',
                    filemode='w', level=logging.DEBUG)


# Create a console handler to log to stdout
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Capture debug logs
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console_handler.setFormatter(formatter)
# Add console handler to the root logger
logging.getLogger().addHandler(console_handler)
# Configure httpx logger
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.DEBUG)  # Capture all httpx debug messages
httpx_logger.addHandler(console_handler)  # Optional: Add the console handler for httpx too



striim_api_url = "http://localhost:5001/api/v1"
discovery_striim_api_url = 'http://10.65.61.154:9080/'
auth_path = 'security/authenticate'



SHIP_API_MAP = {"Discovery":"http://10.65.61.154:9080/api/v2/applications", 
                "Dawn":"http://dawstriim01v.dawn.ncl.com:9080/api/v2/applications", "Epic":"http://epistriim01v.epic.ncl.com:9080/api/v2/applications", 
                "Encore":"http://encstriim01v.encore.ncl.com:9080/api/v2/applications", "Escape": "http://escstriim01v.escape.ncl.com:9080/api/v2/applications",
                "Gem":"http://gemstriim01v.gem.ncl.com:9080/api/v2/applications", "Getaway":"http://getstriim01v.getaway.ncl.com:9080/api/v2/applications",
                "Bliss":"http://blistriim01v.bliss.ncl.com:9080/api/v2/applications", "Breakaway":"http://brestriim01v.breakaway.ncl.com:9080/api/v2/applications",
                "Sun":"http://sunstriim01v.sun.ncl.com:9080/api/v2/applications", "Jewel":"http://jewstriim01v.jewel.ncl.com:9080/api/v2/applications",
                "Spirit":"http://spistriim01v.spirit.ncl.com:9080/api/v2/applications", "Pearl":"http://peastriim01v.pearl.ncl.com:9080/api/v2/applications", 
                "Sky":"http://skystriim01v.sky.ncl.com:9080/api/v2/applications",
                "Jade":"http://jadstriim01v.jade.ncl.com:9080/api/v2/applications", "Joy":"http://joystriim01v.joy.ncl.com:9080/api/v2/applications",
                "Viva":"http://vivstriim01v.viva.ncl.com:9080/api/v2/applications", "Prima":"http://pristriim01v.prima.ncl.com:9080/api/v2/applications",
                "PrideOfAmerica": "http://10.15.50.154:9080/api/v2/applications", "Star": "http://10.3.50.154:9080/api/v2/applications",             
                "Explorer":"http://10.31.50.154:9080/api/v2/applications",          "Grandeur":"http://10.75.50.154:9080/api/v2/applications",
                "Insignia":"http://10.16.50.154:9080/api/v2/applications", "Marina":"http://10.19.50.154:9080/api/v2/applications",
                "Mariner":"http://marstriim01v.mariner.rssc.com:9080/api/v2/applications", "Nautica":"http://10.18.50.154:9080/api/v2/applications",
                "Navigator":"http://navstriim01v.navigator.rssc.com:9080/api/v2/applications", "Regatta":"http://regstriim01v.regatta.oceaniacruises.com:9080/api/v2/applications",
                "Riviera":"http://10.20.50.154:9080/api/v2/applications", "Sirena":"http://10.68.50.154:9080/api/v2/applications",
                "Splendor":"http://10.71.50.154:9080/api/v2/applications", "Voyager":"http://voystriim01v.voyager.rssc.com:9080/api/v2/applications",
                "Vista":"http://visstriim01v.vista.ncl.com:9080/api/v2/applications", "Voyager":"http://voystriim01v.voyager.rssc.com:9080/api/v2/applications"
                
                }


@app.route('/')
async def index():
    return await render_template('index.html', active_page='interactive_cli')

async def build_url(selected_ship, endpoint_type='token', authToken=None):
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
    elif endpoint_type == 'applications':
        endpoint = '/api/v2/applications'
    else:
        logging.error(f"Error: Unknown endpoint type: {endpoint_type}")
        return None
    parsed_url = "/".join(new_parts) + endpoint
    print(f"Parsed URL from BUILD URL: {parsed_url}")
    logging.info(f"Built URL: {parsed_url}")
    return parsed_url

    
async def get_credentials(selected_ship):
   logging.info(f"Retrieving credentials for {selected_ship}")
   # Fetch corresponding password based on the ship name
   ship_username = username.get('username')
   ship_password = password.get(selected_ship, {}).get('striim_password')  # Use get for safer access
   if not ship_username:
       logging.error(f"Could not find username for {selected_ship}: {username}")
       abort(400, description="No username found.")  # Return a 400 error
   if not ship_password:
       logging.error(f"Error: No password configured for {selected_ship}")
       abort(400, description=f"No password configured for {selected_ship}.")  # Return a 400 error
   # Prepare the payload for the authentication request
   headers = {
       'username': ship_username,
       'password': str(ship_password)
   }
   logging.info(f"Credentials found for {selected_ship}")
   return headers

# Create an in-memory cache with a TTL of 3 minutes (180 seconds)
# and a maximum size of 100 tokens (adjustable based on your use case).
token_cache = TTLCache(maxsize=50, ttl=180)
async def get_token(ship, token_url):

   # First, check if the token is already cached
   if ship in token_cache:
       # If token exists in cache, return it
       logging.info(f"Using cached token for {ship}")
       return token_cache[ship]
   # If not cached, fetch the token from the external service
   logging.info(f"No cached token for {ship}, fetching new token.")
   async with httpx.AsyncClient(timeout=timeout) as client:
       try:
           headers = await get_credentials(ship)
           response = await client.post(token_url, data=headers)
           response.raise_for_status()  # Raise an error for bad HTTP status codes
           token_data = response.json()
           new_token = token_data.get('token')
           if new_token:
               # Cache the new token in the local cache
               token_cache[ship] = new_token
               logging.info(f"New token cached for {ship}")
               return new_token
           else:
               logging.error(f"Failed to get token for {ship}, no token in response.")
               return None
       except Exception as e:
           logging.error(f"Error fetching token for {ship}: {e}")
           return None

# async def get_token(selected_ship, token_url):
#    ship_username = username.get('username')
#    ship_password = password.get(selected_ship, {}).get('striim_password')  # Use get for safer access
#    # Retrieve the credentials/headers for the selected ship
#    headers = await get_credentials(selected_ship)
#    if not headers:
#        return None  # Handle case where credentials could not be retrieved
#    try:
#        # Make the post request to retrieve the token for the ship
#        async with httpx.AsyncClient(timeout=timeout) as client:
#            logging.info("I am here")
#            logging.info(f"T:{token_url} ")
#            logging.info("h: ", headers)
#            resp = await client.post(token_url, data=headers)
#            logging.info(f"Response from token request: {resp.text}")
#            if resp.status_code != 200:
#                logging.error(f"Failed to retrieve token. Status Code: {resp.status_code}")
#                return None
#            # Parse the JSON response and extract the token
#            token_json = resp.json()
#            token = token_json.get("token")
#            if not token:
#                logging.error("Token not found in response.")
#                return None
#            logging.info(f"Retrieved token for {selected_ship}: {token}")
#            return token
#    except Exception as e:
#        logging.error(f"Error: {e}")
#        return None
   
async def get_dropdown_values():
   # Get JSON data from the request
   data = await request.get_json()
   if data is None:
       logging.error("No JSON data received in the request.")
       abort(400, description="No JSON data provided.")
   # Validate 'ship' and 'appName'
   selected_ship = data.get('ship')
   app_name = data.get('appName')
   if not selected_ship:
       logging.error("No 'ship' key found in the provided JSON.")
       abort(400, description="'ship' key is required in the JSON payload.")
   if not app_name:
       logging.warning("No 'appName' key found, proceeding with only 'ship'.")
   try:
       # Await the async build_url function for the selected ship
       parsed_url = await build_url(selected_ship)
       # Assuming get_token is also async
       auth_token = await get_token(selected_ship, parsed_url)
       if not auth_token:
           logging.error(f"Failed to retrieve token for {selected_ship}.")
           abort(502, description="Authentication token retrieval failed.")
       # Return the values to be used in the deployment
       return selected_ship, app_name, parsed_url, auth_token
   except (httpx.TimeoutException, httpx.RequestError) as e:
       logging.error(f"HTTP request error in get_dropdown_values: {str(e)}", exc_info=True)
       abort(502, description="HTTP error occurred while fetching the token or URL.")
   except Exception as e:
       logging.error(f"Unexpected error in get_dropdown_values: {str(e)}", exc_info=True)
       abort(500, description="An unexpected error occurred while processing the request.")

async def health_stats(authToken, appname=None):

    app_status = {}

    striim_ship_api_url, selected_ship, command, app_name = await url_builder(endpoint=None)

    health_url = await build_url(selected_ship, endpoint_type='health', authToken=authToken)

    # parsed_url = parse_token_url()
    
    resp = requests.get(health_url)
    if resp.status_code == 200:
        logging.info("Application health API was retrieved successfully.")
        logging.info("Looking to see if application name was given...")
        data = json.loads(resp.text)
        if appname != None:
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

# Function to create a blank health response
async def blank_health_response():
   return {
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

# Function to execute command on Linux box synchronously
def execute_command_on_linux_box(host, username, password, command, timeout=30):
   client = paramiko.SSHClient()
   client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   try:
       client.connect(hostname=host, username=username, password=password, timeout=timeout)
       logging.info(f"Successfully connected to {host}")
       stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
       output = stdout.read().decode('utf-8').strip().splitlines()
       error = stderr.read().decode('utf-8').strip().splitlines()
       logging.info(f"Command execution finished on {host}. Output: {output}, Errors: {error}")
       return {"host": host, "output": output, "error": error}
   except Exception as e:
       logging.error(f"Error executing command on {host}: {e}")
       return {"host": host, "output": [], "error": [str(e)]}  # Ensure error is a list
   finally:
       client.close()

@app.route('/execute-command-form')
async def command_form():
    return await render_template('execute_command.html', active_page='linux-cli')

# Function to load ships from a JSON file
@app.route("/load_ships")
def load_ships_from_json():
   with open('ship_names.json') as f:  # Update this path as needed
       data = json.load(f)
   return jsonify({"ships": data['ships']})

@app.route('/execute-command', methods=['POST'])
async def execute_command():
   try:
       data = await request.json
       if not data or 'hosts' not in data or 'command' not in data:
           return jsonify({"error": "Missing required fields: 'hosts' and 'command'"}), 400
       selected_hosts = data['hosts']
       command = data['command']
       # Handle the case when 'All Ships' is selected
       if 'All' in selected_hosts:
           selected_hosts = load_ships_from_json()  # Load all ships from JSON
       if not isinstance(selected_hosts, list):
           return jsonify({"error": "'hosts' should be a list"}), 400
       results = []
       loop = asyncio.get_running_loop()
       with ThreadPoolExecutor() as executor:
           futures = []
           for host in selected_hosts:
               logging.info(f"Processing host: {host}")
               ship_info = striim_linux_server.get(host, {})
               server = ship_info.get('server')
               username = ship_info.get('username')
               password = ship_info.get('password')
               if username and password:
                   future = loop.run_in_executor(executor, execute_command_on_linux_box, server, username, password, command)
                   futures.append(future)
               else:
                   logging.warning(f"Credentials missing for host {host}")
                   results.append({
                       "host": host,
                       "output": [],
                       "error": [f"Credentials missing for host {host}"]
                   })
           # Collect results
           for future in asyncio.as_completed(futures):
               result = await future  # Await the result of the future
               results.append(result)
       # Return the results in a format that your frontend can process
       return jsonify({"results": results, "ship":selected_hosts})
   except Exception as e:
       logging.error(f"Unexpected error: {str(e)}")
       return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

async def create_sql_pool(ship_name):
   ship_creds = odp_sql_server_creds.get(ship_name, {})
   server = ship_creds.get('server')
   uid = ship_creds.get('uuid')
   password = ship_creds.get('password')
   if not all([server, uid, password]):
       logging.warning(f"Missing credentials for {ship_name}. Server: {server}, UID: {uid}.")
       return None, False
   logging.info(f"Creating SQL pool for {ship_name} with server {server} and uid {uid}.")
   try:
       pool = await aioodbc.create_pool(
           dsn=f"Driver={{SQL Server}};Server={server};UID={uid};PWD={password};",
           minsize=1,
           maxsize=5
       )
       logging.info(f"Successfully created pool for {ship_name}.")
       return pool, True
   except Exception as e:
       logging.error(f"Failed to create pool for {ship_name}: {e}")
       return None, False
   
async def get_fidelio_odp_data(ship_name, pool):
   async with pool.acquire() as conn:
       async with conn.cursor() as cursor:
           try:
               logging.info(f"Fetching data for ship: {ship_name}")
               sql_query = """
                   SELECT MAX([POS_MODDATE]) AS POS_MODDATE,
                          MAX([ETL_PROCESS_TS]) AS ETL_PROCESS_TS
                   FROM [LZ].[fidelio].[POS]
               """
               await cursor.execute(sql_query)
               result = await cursor.fetchone()
               if result:
                   return {'mod_date': result[0], 'etl_process_dt': result[1]}
               else:
                   logging.warning(f"No data found for ship: {ship_name}")
                   return {'mod_date':None, 'etl_process_dt':None}
           except Exception as e:
               logging.error(f"Error while fetching SQL data for {ship_name}: {e}")
               return {"error": f"Error fetching SQL data for {ship_name}: {e}"}
   return None
def format_date(date_str, current_format='%Y-%m-%dT%H:%M:%S', new_format='%Y-%m-%d %H:%M:%S'):
   try:
       return datetime.strptime(date_str, current_format).strftime(new_format)
   except (ValueError, TypeError):
       return date_str  # Return the original value if there's an issue
MAX_CONCURRENT_REQUESTS = 15
global_app_health = {}
@app.route('/striim/status-by-ship', methods=['POST', 'GET'])
async def health_stats_by_ship(appname=None):
   global global_app_health
   selected_ship = 'All' if request.method == 'GET' else (await request.get_json()).get('ship')
   app_health = {}
   semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)
   async def retrieve_ship_health_data(ship):
       async with semaphore:
           try:
               app_health[ship] = {}
               ship_creds = odp_sql_server_creds.get(ship, {})
               pool, sql_success = await create_sql_pool(ship)
               if pool is None:
                   app_health[ship]['sqlHealth'] = {"status": "unavailable", "message": "SQL pool not available"}
                   return
               logging.info(f"Connection pool successfully created for {ship}")
               async with httpx.AsyncClient(timeout=timeout) as client:
                   token_url = await build_url(ship, endpoint_type='token')
                   auth_token = await get_token(ship, token_url)
                   headers = {
                       "Authorization": f"STRIIM-TOKEN {auth_token}",
                       "Content-Type": "application/json"
                   }
                   if auth_token:
                       logging.info(f"Auth token retrieved for {ship}: {auth_token}")
                       health_path = f'health?token={auth_token}'
                       parsed_url = await build_url(ship, endpoint_type="applications")
                       await fetch_health_data(ship, parsed_url, headers, app_health, client, pool, sql_success)
                   else:
                       logging.warning(f"No auth token for {ship}, not updating health data.")
           except Exception as e:
               logging.error(f"Unexpected error retrieving health data for {ship}: {e}")
           finally:
               if pool:
                   await close_pool_connections(pool, ship)
   ships = [selected_ship] if selected_ship != 'All' else list(odp_sql_server_creds.keys())
   await asyncio.gather(*(retrieve_ship_health_data(ship) for ship in ships))
   global_app_health = app_health
   if not global_app_health:
       logging.error("No health data was collected.")
       return jsonify({"error": "No health data available"}), 500
   return jsonify(global_app_health)

async def close_pool_connections(pool, ship):
   if pool:  # Ensure the pool is not None before trying to acquire connections
       try:
           async with pool.acquire() as conn:
               if conn:
                   await conn.close()  # Close individual connection
                   logging.info(f"Closed an open connection for {ship}.")
       except Exception as e:
           logging.error(f"Error closing individual connection: {e}")
   else:
       logging.error("Attempted to close connections, but pool is None.")

async def fetch_health_data(ship, parsed_url, headers, app_health, client, pool, sql_success):
   try:
       logging.info(f"Fetching health data for {ship} from {parsed_url}")
       response = await client.get(parsed_url, headers=headers)
       if response.status_code != 200:
           logging.error(f"Failed to retrieve health stats for {ship}. Status Code: {response.status_code}")
           return
       ship_data = response.json()
       for record in ship_data:
           if 'name' in record:
               name_space = record.get("namespace")
               app_name = record.get("name")
               status = record.get("status")
               full_app_name = f"{name_space}.{app_name}"
               logging.info(f"Processing {full_app_name} with status {status} for ship {ship}")
               app_health[ship][full_app_name] = {'appName': full_app_name, 'status': status}
               details = {'appName': full_app_name}
               app_health_map = {}
               try:
                   await update_sql_health_data(full_app_name, details, app_health_map, ship, pool)
                   app_health[ship][full_app_name].update(app_health_map.get(full_app_name, {}))
               except Exception as e:
                   logging.error(f"Error updating SQL health data for {full_app_name} on {ship}: {str(e)}")
   except Exception as e:
       logging.error(f"Error fetching health data for {ship}: {str(e)}")

async def update_sql_health_data(app_name, details, app_health_map, ship, pool):
   if details.get("appName") in ['admin.cdc_fidelio_to_odp', 'esp.cdc_fidelio_to_odp']:
       logging.info(f"Fetching SQL health data for {ship} and {app_name}")
       try:
           sql_health_data = await get_fidelio_odp_data(ship, pool)
           app_health_map[app_name] = {
               'sqlHealth': {
                   "status": "available",
                   "data": sql_health_data if sql_health_data else {"error": "No data found"}
               }
           }
           logging.info(f"Successfully retrieved SQL health data for {app_name}.")
       except Exception as e:
           logging.error(f"Error retrieving SQL health data for {app_name}: {str(e)}")
           app_health_map[app_name] = {
               'sqlHealth': {
                   "status": "unavailable",
                   "message": f"Error retrieving SQL health data: {str(e)}"
               }
           }

# Route for showing the checkpoint information for a specific ship
@app.route('/ship-details/<ship_name>/<app_name>')
async def ship_details(ship_name, app_name):
   global global_app_health
   logging.info("Fetching health data for ship: %s, app: %s", ship_name, app_name)
   # Decode the ship name
   ship_name_decoded = urllib.parse.unquote(ship_name)
   # Check if the ship has any health records
   health_records = global_app_health.get(ship_name_decoded, {}).get('healthRecords', [])
   if not health_records:
       logging.error(f"No health records found for {ship_name_decoded}")
       return "No health data found", 404
   # Extract the first health record's appHealthMap
   app_health_map = health_records[0].get('appHealthMap', {})
   # Fetch the details for the specific application requested
   details = app_health_map.get(app_name)
   if not details:
       logging.error(f"No details found for app {app_name} on {ship_name_decoded}")
       return "No checkpoint data found for the specified app", 404
   # Retrieve checkpoint data specific to this app
   checkpoint_data = details.get('checkpointInformation', [])
   if not checkpoint_data:
       logging.error(f"No checkpoint information found for app {app_name} on {ship_name_decoded}")
       return "No checkpoint data found", 404
   # Render the template with checkpoint data
   logging.info(f"Rendering checkpoint data for {ship_name_decoded} and app {app_name}")
   return await render_template('ship_details.html',
                                 ship_name=ship_name_decoded,
                                 checkpoint_data=checkpoint_data)

async def url_builder(endpoint=None):
    command = None
    selected_ship = None
    app_name = None

    if request.is_json:
        data = await request.get_json()
        selected_ship = data.get('ship')
        command = data.get('command')
        app_name = data.get('appName')
    else:
        selected_ship = request.form.get('ship')
        command = request.form.get('command')
        app_name = request.form.get('appName')

    ship_url = SHIP_API_MAP.get('Discovery')

    if not ship_url:
        logging.error(f"Could not find {ship_url}")
        return jsonify(f"Could not find {ship_url}"), 400
    
    if endpoint:
        striim_ship_api_url = f"{ship_url}/{app_name}/{endpoint}"
        logging.info(f"Built following URL: {striim_ship_api_url}")
    else:
        striim_ship_api_url = ship_url

    return striim_ship_api_url, selected_ship, command, app_name

# Route to check the deployment status (GET)
@app.route('/application/status', methods=['GET'])
async def check_deployment_status():
    logging.info(f"Checking deployment status...")

    ship = request.args.get('ship')
    app_name = request.args.get('appName')

    # Retrieve auth token
    auth_token = get_token()

    # Build the URL and other necessary info
    striim_ship_api_url, selected_ship, command, app_name = await url_builder(endpoint='deployment')

    headers = {
        "Authorization": f"STRIIM-TOKEN {auth_token}",
        "Content-Type": "application/json"
    }
    try:
        # Make a GET request to check the current status of the application
        status_response = requests.get(f'{striim_ship_api_url}', headers=headers)

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
        logging.error(f"Error retrieving status: {str(e)}")
        return jsonify({"error": str(e)}), 500

   
@app.route('/application/deploy', methods=['POST'])
async def deploy_app():
   selected_ship, app_name, parsed_url, auth_token = await get_dropdown_values()

   striim_ship_api_url, selected_ship, command, app_name = await url_builder(endpoint='deployment')
   headers = {
       "Authorization": f"STRIIM-TOKEN {auth_token}",
       "Content-Type": "application/json"
   }
   logging.info(f"Starting deployment process for app: {app_name} on ship: {selected_ship}")
   try:
       async with httpx.AsyncClient(timeout=timeout) as client:
           logging.info(f"deploy striim_ship_api_url {striim_ship_api_url}") 
           logging.info(f"deploy header {headers}") 
           deploy_response = await client.post(f'{striim_ship_api_url}', headers=headers)
           logging.info("HOLA AFTER DEPLOY RESPONSE")
       if deploy_response.status_code == 200:
           logging.info(f"inside 200 {headers}") 
           deploy_data = deploy_response.json()
           logging.info(f"Deployment successful: {deploy_data}")
           return jsonify({"message": f"Successfully deployed {app_name} on {selected_ship}."}), 200
       else:
           logging.error(f"Failed to deploy {app_name} on {selected_ship}. Status code: {deploy_response.status_code}")
           logging.error(deploy_response)
           logging.info(f"FINAL URL {deploy_response.url}")
           return jsonify({"error": f"Failed to deploy {app_name} on {selected_ship}."}), deploy_response.status_code
   except httpx.RequestError as e:
       logging.error(f"Error during deployment: {str(e)}")
       return jsonify({"error": str(e)}), 500
    
@app.route('/application/undeploy', methods=['DELETE'])
async def undeploy_app():
   # Get necessary values asynchronously
   selected_ship, app_name, parsed_url, auth_token  = await get_dropdown_values()
   auth_token = await get_token(selected_ship, parsed_url)
   # Build the URL and other parameters
   striim_ship_api_url, selected_ship, command, app_name = await url_builder(endpoint='deployment')
   headers = {
       "Authorization": f"STRIIM-TOKEN {auth_token}",
       "Content-Type": "application/json"
   }
   try:
       logging.info(f"Trying to undeploy app: {app_name} on ship {selected_ship}")
       # Use httpx for async HTTP requests
       async with httpx.AsyncClient() as client:
           response = await client.delete(f'{striim_ship_api_url}', headers=headers)
       # Handle the response
       if response.status_code == 200:
           logging.info(f"{app_name} undeployed successfully!")
           status_data = response.json()
           return jsonify({"message": f"Successfully undeployed {app_name} on {selected_ship}"}), 200
       else:
           logging.error(f"Failed to undeploy {app_name} on {selected_ship}. Status code: {response.status_code}")
           return jsonify({"error": f"Failed to undeploy {app_name} on {selected_ship}"}), response.status_code
   except httpx.RequestError as e:
       logging.error("Error trying to undeploy application")
       return jsonify({"error": str(e)}), 500
    


@app.route('/striim/status-all', methods=['POST', 'GET'])   
async def check_status_by_ship():

    # striim_ship_api_url, selected_ship, command, app_name = url_builder(endpoint='deployment')


    try:
        if request.method == 'GET':           
            return await render_template('all_status.html', active_page='status')
        elif request.method == 'POST':
            data = await request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400
            
            selected_ship = data.get('ship')

            if selected_ship is None:
                return jsonify({"error":"selectedValue is required"}),400

            return jsonify({"selected_ship":selected_ship})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except requests.RequestException as re:
        return jsonify({"error": "Failed to fetch data from the external service"}), 502
    except Exception as e:
        return jsonify({"error": " An unexpected error occurred. Please try again later"}), 500


@app.route("/get_applications", methods=["POST"])
async def get_applications():

    try:
        # Check if the request is JSON
        if request.is_json:
            data = await request.get_json()  # Get JSON data
            # Ensure 'ship' and 'token_url' are provided
            if not data or 'ship' not in data:
                return jsonify({"error": "Invalid request data, 'ship' is required"}), 400
            selected_ship = data['ship']  # Extract selected ship
            # Build URL for the selected ship to get AUTH TOKEN
            parsed_url_token = await build_url(selected_ship, endpoint_type='token')
            # Call the get_token function with the required arguments
            auth_token = await get_token(selected_ship, parsed_url_token)
            if not auth_token:
                return jsonify({"error": "Authorization token is missing"}), 403
            applications = []
            headers = {
            "Authorization": f"STRIIM-TOKEN {auth_token}",
            "Content-Type": "application/json"
            }
            # Build URL for the selected ship to get application API URL
            parsed_url_applications = await build_url(selected_ship, endpoint_type='applications')
            # Use httpx for async HTTP requests and get the list of applications on the selected ship that was selected on the front end.
            async with httpx.AsyncClient() as client:
                response = await client.get(parsed_url_applications, headers=headers)
                resp = response.json()
                logging.info(f"Received2: {resp}")
                for record in resp:
                    if 'name' in record:
                        name_space = record.get("namespace")
                        app_name = record.get("name")
                        full_app_name = name_space + "." + app_name
                        applications.append(full_app_name)
            return jsonify({"applications": applications}), 200  # Return applications with 200 status code
        else:
            logging.error("Request body is not JSON: %s", request.get_data())
            return jsonify({"error": "Request must be JSON"}), 415
    except Exception as e:
        logging.error(f"Error in get_applications: {str(e)}")
        return jsonify({"error": str(e)}), 500

# @app.route('/striim/status', methods=['POST'])
# def check_status():

#     striim_ship_api_url, selected_ship, command, app_name= url_builder()

#     try:
#         response = requests.get(f'{ship_url}/server/status')
#         if response.status_code == 200:
#             status_data = response.json()
#             return jsonify({"message":f"{selected_ship} is {status_data.get('status')}"}), 200

#         else:
#             return jsonify({"error": f"Failed to send command(s) to {selected_ship}"}), response.status_code
#     except requests.RequestException as e:
#         return jsonify({"error": str(e)}), 500


@app.route('/striim/sendcommands', methods=['POST'])
async def send_commands_to_ship():
    print("HELLO")

    striim_ship_api_url, selected_ship, command, app_name = await url_builder(endpoint="deployment")
    print("HELLO2")

    ship_url = SHIP_API_MAP.get(selected_ship)
    print("HELLO3")

    print("COMMAND: ", command)
    print("SELECTED SHP: ", selected_ship)
    print("SHIP URL: ", ship_url)

    if not command or not selected_ship:
        print("HELLO4")
        return jsonify({"error": "Commands and ship(s) must be provided"}), 400

    if not ship_url:
        print("HELLO5")
        return jsonify({"error": f"Could not find {selected_ship}"}), 404
    
    if len(command) <= 5:
        return jsonify({"error": f"Please enter a longer command."}), 404
    
    payload = {
        "ship": selected_ship, 
        "command": command}
    
    print("PAYLOAD: ", payload)
        
    try:
        # response = requests.post(f'{ship_url}/server/restart', json=payload)
        # if response.status_code == 200:
        if payload:
            # return jsonify(response.json()), 200
            # print("SEND COMMAND: ", response.text)
            print("TRY PAYLOAD: ",payload)
            return jsonify({"message": f"Sent command(s) to {selected_ship}"}), 200
        else:
            return jsonify({"error": f"Failed to send command(s) to {selected_ship}"}), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/striim/stop', methods=['DELETE'])
async def stop_server():
   # Get necessary values asynchronously
   selected_ship, app_name, parsed_url, auth_token  = await get_dropdown_values()
   auth_token = await get_token(selected_ship, parsed_url)
   # Build the URL and other parameters
   striim_ship_api_url, selected_ship, command, app_name = await url_builder(endpoint='sprint')
   data, app_status = await health_stats(auth_token, app_name)
   headers = {
       "Authorization": f"STRIIM-TOKEN {auth_token}",
       "Content-Type": "application/json"
   }
   try:
       logging.info(f"Trying to stop app: {app_name} on ship {selected_ship}")
       # Use httpx for async HTTP requests
       async with httpx.AsyncClient() as client:
           response = await client.delete(f'{striim_ship_api_url}', headers=headers)
       try:
           resp = response.json()
           logging.info(f"Received: {resp}")
       except ValueError as json_error:
           return jsonify({"error": "Failed to parse response JSON", "details": str(json_error)}), 500
       logging.info(f"Checking to see if {app_name} is deployed")
       if resp.get('status') == 'DEPLOYED':
           logging.info(f"{app_name} is in deployed status. Will continue...")
           if response.status_code == 200:
               logging.info(f"{app_name} on {selected_ship} stopped successfully!")
               return jsonify({"message": f"{app_name} on {selected_ship} was stopped", "status": "stopped"}), 200
           elif response.status_code == 202:
               logging.info(f"{app_name} is trying to stop...")
               return jsonify({"message": f"{app_name} on {selected_ship} is stopping", "status": "stopping"}), 202
           else:
               logging.info(f"Failed to stop {app_name} on {selected_ship}. Please try again later.")
               return jsonify({"error": f"Failed to stop {app_name} on {selected_ship}. Please try again later."}), response.status_code
       else:
           logging.error(f"{app_name} on {selected_ship} is not deployed or started. Please deploy/start app before continuing.")
           logging.error(f"Current status: {app_name}: {app_status}")
           return jsonify({"error": f"{app_name} on {selected_ship} is not deployed or started. Please deploy/start app before continuing."}), 400
   except httpx.RequestError as e:
       logging.error(f"Error while trying to stop {app_name}: {str(e)}")
       return jsonify({"error": str(e)}), 500

        
@app.route('/striim/start', methods=['POST'])
async def start_server():
   # Get necessary values asynchronously
   selected_ship, app_name, parsed_url, auth_token  = await get_dropdown_values()
   auth_token = await get_token(selected_ship, parsed_url)
   # Build the URL and other parameters
   striim_ship_api_url, selected_ship, command, app_name = await url_builder(endpoint='sprint')
   data, app_status = await health_stats(auth_token, app_name)
   headers = {
       "Authorization": f"STRIIM-TOKEN {auth_token}",
       "Content-Type": "application/json"
   }
   try:
       logging.info(f"Trying to start app: {app_name} on ship {selected_ship}")
       # Use httpx for async HTTP requests
       async with httpx.AsyncClient() as client:
           response = await client.post(f'{striim_ship_api_url}', headers=headers)
       try:
           resp = response.json()
           logging.info(f"Received: {resp}")
       except ValueError as json_error:
           return jsonify({"error": "Failed to parse response JSON", "details": str(json_error)}), 500
       logging.info(f"Checking to see if {app_name} is deployed")
       if resp.get('status') == 'DEPLOYED':
           logging.info(f"{app_name} is in deployed status. Will continue...")
           if response.status_code == 200:
               logging.info(f"{app_name} on {selected_ship} started successfully!")
               return jsonify({"message": f"Successfully started {app_name} on {selected_ship}", "status": "running"}), 200
           elif response.status_code == 202:
               logging.info(f"{app_name} is trying to start...")
               return jsonify({"message": f"{app_name} on {selected_ship} is starting", "status": "pending"}), 202
           else:
               logging.error(f"Failed to start {app_name} on {selected_ship}. Response Code: {response.status_code}. Please try again later.")
               return jsonify({"error": f"Failed to start {app_name} on {selected_ship}. Please try again later."}), response.status_code
       else:
           logging.error(f"{app_name} on {selected_ship} is not deployed.")
           logging.error(f"Current status: {app_name}: {app_status}")
           return jsonify({"error": f"{app_name} on {selected_ship} is not deployed. {app_name}: {app_status}"}), 400
   except httpx.RequestError as e:
       logging.error(f"Error while trying to start {app_name}: {str(e)}")
       return jsonify({"error": str(e)}), 500


@app.after_request    
def add_header(response):
    response.headers['Cache-Control'] ='no-store, no-chache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)