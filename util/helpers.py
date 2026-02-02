import logging
import uuid

def make_api_call(rest_connector, endpoint, api_link, method, session = True, force_refresh = None, body = None, headers = None):
    """
    This function is making the actual API call

    @param endpoint
      this parameter represent the actual endopoint(prism central or cluster) which to connect to
    @param api_link
      api_link is the actual path to the API
    @ method
      method can be GET, PUT, POST, DELETE, and it's different according to the operation type
    @ session
      session can be True(default) or False, and it's the indicator if to use or not to use session when making the API call
    @ body
      body contains the actual body needed for request. Some request types may have/need no body(GET)
    
    """

    task_id , result = None, None

    try:
        result = rest_connector.invoke_rest_call('https://' + endpoint , api_link, method, session, force_refresh, body, headers)
    except Exception as error_message:
        logging.error(f' while calling the API: {error_message}')
        raise error_message

    # save the request call so that we can show it at the end for failed tasks -> Failed tasks will have the request displayed on the screen for easier manual retry.
    request_content = {
      "endpoint": endpoint,
      "api_link": api_link,
      "method": method,
      "session": session,
      "force_refresh": force_refresh,
      "body": body
    }

    if 'status' in result and 'execution_context' in result['status']: # status is only available for operations like create/update/delete
        task_id = result['status']['execution_context']['task_uuid']
        print("... Status: Accepted. Task UUID: " + str(task_id))

    return task_id, result, request_content

def create_logger(module_name='main', level='INFO', prefix=''):
    level = logging.getLevelName(level)
    # create a new and unique logger
    logger = logging.getLogger(str(uuid.uuid1()))
    if prefix != '':
            prefix = f'{prefix} ' # add space to the right

    formatter = logging.Formatter(f'%(asctime)s {prefix}- %(levelname)s - %(message)s', datefmt = "%Y-%m-%d %H:%M:%S")
    # setup stream handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.set_name(module_name)
    logger.addHandler(console_handler)

    logger.setLevel(logging.DEBUG)

    return logger


def get_subnets(rest_connector, endpoint):

        _, result, _ = make_api_call(
            rest_connector          = rest_connector,
            endpoint                = f'{endpoint}:9440',
            api_link                = "/PrismGateway/services/rest/v2.0/networks/",
            method                  = "GET",
            session                 = True
        )

        return result


def create_subnet(rest_connector, endpoint, subnet, vswitch_name):

        _, result, _ = make_api_call(
            rest_connector          = rest_connector,
            endpoint                = f"{endpoint}:9440",
            api_link                = "/PrismGateway/services/rest/v2.0/networks/",
            method                  = "POST",
            session                 = True,
            body                    = __generate_vlan_body(subnet, vswitch_name)
        )

        return result


def __generate_vlan_body(subnet, vswitch_name):

        body = {
                "name": subnet['name'],
                "vlan_id": subnet['vlan_id'],
                "vswitch_name": vswitch_name
                }
        
        if "ip_config" in subnet and subnet["ip_config"]["ipam_enabled"] is True:
                body["ip_config"] = {}

                if "network_address" in subnet["ip_config"]:
                        body["ip_config"]["network_address"] = subnet["ip_config"]["network_address"]
                
                if "dhcp_server_address" in subnet["ip_config"]:
                  body["ip_config"]["dhcp_server_address"] = subnet["ip_config"]["dhcp_server_address"]
                
                if "prefix_length" in subnet["ip_config"]:
                  body["ip_config"]["prefix_length"] = subnet["ip_config"]["prefix_length"]

                if "default_gateway" in subnet["ip_config"]:
                  body["ip_config"]["default_gateway"] = subnet["ip_config"]["default_gateway"]

                if "dhcp_options" in subnet["ip_config"]:
                  body["ip_config"]["dhcp_options"] = subnet["ip_config"]["dhcp_options"]
                
                if "pool" in subnet["ip_config"]:
                  body["ip_config"]["pool"] = subnet["ip_config"]["pool"]

        return body