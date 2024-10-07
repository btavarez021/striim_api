# import urllib.parse
# import requests
# from requests import RequestException
# import json
# import os
# import re

# username = os.getenv('striim_username')
# password = os.getenv('discovery_password')
# encoded_password = urllib.parse.quote(password)

# if password:
#     encoded_password = urllib.parse.quote(password)
# else:
#     print("Password not found in environmental variables.")

# striim_api_url = 'http://10.65.61.154:9080/'
# auth_path = 'security/authenticate'

# def get_token(username, password):
#         payload = {'username': username, 'password': password}

#         try:
#             url = striim_api_url + auth_path
#             resp = requests.post(url, data=payload)
#             if resp.status_code != 200:
#                 return "Likely: wrong username / password"
#             tokenjson = json.loads(resp.text)
#             print(tokenjson)
#             return tokenjson["token"]
#         except RequestException as ex:
#             print(ex)
#             raise ex
# def health_stats(authToken):
#     health_path = f'health?token={authToken}'
#     url = striim_api_url + health_path
#     resp = requests.get(url)
#     if resp == 200:
#         data = json.loads(resp.text)
#         print(f"Health: {data}")
#         return data
#     else:
#          print(f"Error: {resp.status_code} - {resp.text}")

# def deploy_app(auth_token, app_name ):

#     headers = {
#         "Authorization": f"STRIIM-TOKEN {auth_token}", 
#         "Content-Type": "application/json"
#     }
#     print(headers)
#     try:
#         response = requests.post(f'{striim_api_url}/api/v2/applications/{app_name}/deployment', headers=headers)
#         print(f"RESPONSE: {response}")
#         if response.status_code == 200:
#             status_data = response.json()
#             print(f"JSONNN: {status_data}")
#             # return jsonify({"message":f"{selected_ship} is {status_data.get('status')}"}), 200
#         else:
#             print(f"failed with statuscode {response.status_code}")
#             # return jsonify({"error": f"Failed to send command(s) to {selected_ship}"}), response.status_code
#     except requests.RequestException as e:
#         print(f'RequestException: {str(e)}')
#         # return jsonify({"error": str(e)}), 500

# data = {
#         'namespace': 'admin', 'name': 'benny_test', 'status': 'DEPLOYED', 
#         'links': 
#             [
#                 {'rel': 'self', 'allow': ['GET', 'DELETE'], 'href': '/api/v2/applications/admin.benny_test'}, 
#                 {'rel': 'deployment', 'allow': ['POST', 'DELETE'], 'href': '/api/v2/applications/admin.benny_test/deployment'}, 
#                 {'rel': 'sprint', 'allow': ['POST', 'DELETE'], 'href': '/api/v2/applications/admin.benny_test/sprint'}
#             ]
#         }
# # health_stats(auth_token)
# # deploy_app(auth_token, 'admin.benny_test')

# # print(data['links'][0]['href'])


# # auth_token = get_token(username, password)

# # headers = {
# #         "Authorization": f"STRIIM-TOKEN {auth_token}", 
# #         "Content-Type": "application/json"
# #     }

# # response = requests.post('http://10.65.61.154:9080/api/v2/applications/admin.benny_test/deployment', headers=headers)
# # print(response.json())
# # for url_list in response.json():   
# # response = response.json()
# # for url in response["links"]:
# #     if 'deployment' in url['href']:
# #         print(url['href'])

# # match = re.search(r'href":"([^"]+)"', response)
# # print(match)
# # print(url_list_decoded["links"])
# # if 'deployment' in url_list:
# #     print(url_list['href'])

# health_data ={
#   "healthRecords" : [ {
#     "kafkaHealthMap" : { },
#     "waStoreHealthMap" : {
#       "admin.CDC_pyw_ENC_to_snf_ExceptionStore" : {
#         "fqWAStoreName" : "admin.CDC_pyw_ENC_to_snf_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       },
#       "System$Notification.notificationStore" : {
#         "fqWAStoreName" : "System$Notification.notificationStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 1727709991813
#       },
#       "esp.cdc_fidelio_to_odp_ExceptionStore" : {
#         "fqWAStoreName" : "esp.cdc_fidelio_to_odp_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       },
#       "admin.Initial_embarkd_to_snf_ExceptionStore" : {
#         "fqWAStoreName" : "admin.Initial_embarkd_to_snf_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       },
#       "admin.Initial_pyw_ENC_to_snf_ExceptionStore" : {
#         "fqWAStoreName" : "admin.Initial_pyw_ENC_to_snf_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       },
#       "admin.PYW_LAB_to_SNOWFLAKE_CDC_ExceptionStore" : {
#         "fqWAStoreName" : "admin.PYW_LAB_to_SNOWFLAKE_CDC_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       },
#       "admin.Initial_embarkd_form_poc_to_snf_ExceptionStore" : {
#         "fqWAStoreName" : "admin.Initial_embarkd_form_poc_to_snf_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 1725878106472
#       },
#       "System$Alerts.AlertingApp_ExceptionStore" : {
#         "fqWAStoreName" : "System$Alerts.AlertingApp_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       },
#       "admin.PYW_LAB_to_SNOWFLAKE_IL_ExceptionStore" : {
#         "fqWAStoreName" : "admin.PYW_LAB_to_SNOWFLAKE_IL_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       },
#       "admin.test_embarkd_ExceptionStore" : {
#         "fqWAStoreName" : "admin.test_embarkd_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       },
#       "admin.benny_test_ExceptionStore" : {
#         "fqWAStoreName" : "admin.benny_test_ExceptionStore",
#         "writeRate" : 0,
#         "lastWriteTime" : 0
#       }
#     },
#     "cacheHealthMap" : { },
#     "clusterSize" : 1,
#     "appHealthMap" : {
#       "admin.Initial_embarkd_form_poc_to_snf" : {
#         "lastModifiedTime" : 1725877042685,
#         "checkpointInformation" : "",
#         "rate" : 0.0,
#         "appId" : {
#           "stringRep" : "01ef6e94-61f1-6581-8112-005056a3d7b2"
#         },
#         "cpuRate" : 0.0,
#         "fqAppName" : "admin.Initial_embarkd_form_poc_to_snf",
#         "status" : "CREATED",
#         "loadLevel" : "NOT_AVAILABLE"
#       },
#       "admin.PYW_LAB_to_SNOWFLAKE_IL" : {
#         "lastModifiedTime" : 1700244564807,
#         "checkpointInformation" : "",
#         "rate" : 0.0,
#         "appId" : {
#           "stringRep" : "01ee8574-70ab-c571-8d28-005056a3d7b2"
#         },
#         "cpuRate" : 0.0,
#         "fqAppName" : "admin.PYW_LAB_to_SNOWFLAKE_IL",
#         "status" : "CREATED",
#         "loadLevel" : "NOT_AVAILABLE"
#       },
#       "esp.Fidelio_Test_Connection" : {
#         "lastModifiedTime" : 1714076695661,
#         "checkpointInformation" : "",
#         "rate" : 0.0,
#         "appId" : {
#           "stringRep" : "01edb2b5-753a-1981-ac56-005056a3d7b2"
#         },
#         "cpuRate" : 0.0,
#         "fqAppName" : "esp.Fidelio_Test_Connection",
#         "status" : "CREATED",
#         "loadLevel" : "NOT_AVAILABLE"
#       },
#       "admin.PYW_LAB_to_SNOWFLAKE_IL_SchemaMigration" : {
#         "lastModifiedTime" : 1700245491692,
#         "checkpointInformation" : [ {
#           "firstRecordedCheckpoint" : {
#             "checkpointDuration" : "N/A",
#             "checkpointType" : "N/A",
#             "checkpointTime" : "N/A"
#           }
#         }, {
#           "lastTwoRecordedCheckpoints" : [ {
#             "checkpointDuration" : "N/A",
#             "checkpointType" : "N/A",
#             "checkpointTime" : "N/A"
#           }, {
#             "checkpointDuration" : "N/A",
#             "checkpointType" : "N/A",
#             "checkpointTime" : "N/A"
#           } ]
#         } ],
#         "rate" : 0.0,
#         "appId" : {
#           "stringRep" : "01ee8576-9923-32c1-8d28-005056a3d7b2"
#         },
#         "cpuRate" : 0.0,
#         "fqAppName" : "admin.PYW_LAB_to_SNOWFLAKE_IL_SchemaMigration",
#         "status" : "CREATED",
#         "loadLevel" : "NOT_AVAILABLE"
#       },
#       "admin.PYW_LAB_to_SNOWFLAKE_CDC" : {
#         "lastModifiedTime" : 1700579827572,
#         "checkpointInformation" : "",
#         "rate" : 0.0,
#         "appId" : {
#           "stringRep" : "01ee8881-08d9-e341-8d28-005056a3d7b2"
#         },
#         "cpuRate" : 0.0,
#         "fqAppName" : "admin.PYW_LAB_to_SNOWFLAKE_CDC",
#         "status" : "CREATED",
#         "loadLevel" : "NOT_AVAILABLE"
#       }
#     },
#     "serverHealthMap" : {
#       "Global.S10_65_61_154" : {
#         "memory" : 910020256,
#         "cpu" : "5.8%",
#         "elasticsearchFree" : "23GB",
#         "uuid" : {
#           "stringRep" : "687b3b7a-f170-43ae-9686-a88365b45cb5"
#         },
#         "cpuRatePerCore" : 0.2175,
#         "fqServerName" : "Global.S10_65_61_154",
#         "diskFree" : "/: 53.67%"
#       }
#     },
#     "sourceHealthMap" : {
#       "admin.PYW_LAB_to_SNOWFLAKE_IL_DBSource" : {
#         "eventRate" : 0.0,
#         "lastEventTime" : 0,
#         "fqSourceName" : "admin.PYW_LAB_to_SNOWFLAKE_IL_DBSource"
#       },
#       "esp.Source_Fidelio" : {
#         "eventRate" : 0.0,
#         "lastEventTime" : 0,
#         "fqSourceName" : "esp.Source_Fidelio"
#       },
#       "admin.PYW_LAB_to_SNOWFLAKE_CDC_MysqlCDC" : {
#         "eventRate" : 0.0,
#         "lastEventTime" : 0,
#         "fqSourceName" : "admin.PYW_LAB_to_SNOWFLAKE_CDC_MysqlCDC"
#       },
#       "admin.source_embarkd_form_poc" : {
#         "eventRate" : 0.0,
#         "lastEventTime" : 0,
#         "fqSourceName" : "admin.source_embarkd_form_poc"
#       }
#     },
#     "elasticSearch" : "true",
#     "targetHealthMap" : {
#       "System$Alerts.SlackAlertSender" : {
#         "eventRate" : 0,
#         "lagEnd2End" : "",
#         "fqTargetName" : "System$Alerts.SlackAlertSender",
#         "lastWriteTime" : 0
#       },
#       "System$Alerts.TeamsAlertSender" : {
#         "eventRate" : 0,
#         "lagEnd2End" : "",
#         "fqTargetName" : "System$Alerts.TeamsAlertSender",
#         "lastWriteTime" : 0
#       },
#       "admin.Snowflake_PYW_LAB_to_SNOWFLAKE_IL_Target" : {
#         "eventRate" : 0,
#         "lagEnd2End" : "",
#         "fqTargetName" : "admin.Snowflake_PYW_LAB_to_SNOWFLAKE_IL_Target",
#         "lastWriteTime" : 0
#       },
#       "System$Alerts.WebAlertSender" : {
#         "eventRate" : 0,
#         "lagEnd2End" : "",
#         "fqTargetName" : "System$Alerts.WebAlertSender",
#         "lastWriteTime" : 1727709991813
#       },
#       "admin.Snowflake_PYW_LAB_to_SNOWFLAKE_CDC_Target" : {
#         "eventRate" : 0,
#         "lagEnd2End" : "",
#         "fqTargetName" : "admin.Snowflake_PYW_LAB_to_SNOWFLAKE_CDC_Target",
#         "lastWriteTime" : 0
#       },
#       "admin.target_initial_embarkd_to_snf" : {
#         "eventRate" : 0,
#         "lagEnd2End" : "",
#         "fqTargetName" : "admin.target_initial_embarkd_to_snf",
#         "lastWriteTime" : 0
#       },
#       "System$Alerts.InstantEmailSender" : {
#         "eventRate" : 0,
#         "lagEnd2End" : "",
#         "fqTargetName" : "System$Alerts.InstantEmailSender",
#         "lastWriteTime" : 1725878114665
#       }
#     },
#     "stateChangeList" : [ ],
#     "issuesList" : [ ],
#     "startTime" : 1727716461241,
#     "id" : "01ef7f4f-6ef4-1a91-8112-005056a3d7b2",
#     "endTime" : 1727716521276,
#     "derbyAlive" : "true",
#     "agentCount" : 0
#   } ],
#   "next" : "/healthRecords?size=1&from=1",
#   "prev" : "/healthRecords?size=1&from=0"
# }

# # for key, value in health_data.items():
# #     for k in value:
# #         print(k)

# # print(health_data["healthRecords"][0]["waStoreHealthMap"])

# # for key , value in health_data.items():
# #     if key == 'healthRecords':
# #         for inner_key, inner_value in value[0].items():
# #             if inner_key =='appHealthMap':
# #                 for inner_inner_key, inner_inner_value in inner_value.items():
# #                     print(inner_inner_value['fqAppName'])
# #                     print(inner_inner_value['status'])
# SHIP_API_MAP = {"Discovery":"http://10.65.61.154:9080/api/v2/applications", 
#                 "Ship 1":"http://localhost:5001/api/v1", "Ship 2":"http://localhost:5001/api/v1", 
#                 "Ship 3":"http://localhost:5001/api/v1", "Ship 4":"http://localhost:5001/api/v1",
#                 "Ship 5":"http://localhost:5001/api/v1"
#                 }

# import requests

# def url_builder():
#     command = None
#     selected_ship = None

#     auth_token = get_token()

#     headers = {
#         "Authorization": f"STRIIM-TOKEN {auth_token}",
#         "Content-Type": "application/json"
#     }

#     print("GETAPIURL")


#     if request.is_json:
#         print("IS JSON")
#         data = request.get_json()
#         print("Benn2: ", data)
#         selected_ship = data.get('ship')
#         print("benny data: ", selected_ship)
#         command = data.get('command')
#         app_name = data.get('appName')
#         print("app_name: ", app_name)
#     else:
#         selected_ship = request.form.get('ship')
#         command = request.form.get('command')
#         app_name = request.form.get('appName')
#         print("app_name: ", app_name)

#         print("NOT JSON")
#         print("Selected ship" ,selected_ship)

#     if not selected_ship:
#         print("NO SHIP SELECTED?")
#         return jsonify({"error": "No ship selected"}), 400

#     print(f"Selected Ship: {selected_ship}")
#     ship_url = SHIP_API_MAP.get(selected_ship)
#     print(f"SHIP URL: {ship_url}")

#     if not ship_url:
#         return jsonify(f"Could not find {ship_url}"), 400

#     return ship_url, selected_ship, command, app_name

# url_builder()

# full_url = "http://dawstriim01v.dawn.ncl.com:9080/api/v2/applications"

# parts = full_url.split("/")

# segment_to_keep = [0,1,2]
# new_parts = [part for idx, part in enumerate(parts) if idx in segment_to_keep]
# print("KEEP", "/".join(new_parts))
    
# from creds import username, password

# print(username.get('username'), password.get('Discovery'))


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


for url in SHIP_API_MAP.items():
    print(url)