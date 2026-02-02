import sys
import os
import urllib3

from util.colors import green, nc
from util.arguments import get_args
from util.helpers import create_logger, get_subnets, create_subnet
from util.configuration import Configuration
from util.rest_api_connector import RestApiConnector

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------------------------------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
  # loading arguments
  arguments = get_args()

  # create logger
  log = create_logger(module_name="COPY_SUBNETS", level=arguments.log_level, prefix="COPY_SUBNETS")

  # loading Config
  config = Configuration(log, args=get_args())
  config.rest_connector = RestApiConnector(config.args.api_user, config.args.api_pass)

  log.debug(f"Running with: options= {str(config)} args={str(config.args)}")

  log.info("script is started")

  # get subnets from source and destination clusters
  src_subnets = get_subnets(config.rest_connector, config.args.source_cluster)
  dst_subnets = get_subnets(config.rest_connector, config.args.destination_cluster)

  src_entities = src_subnets.get('entities', [])
  dst_entities = dst_subnets.get('entities', [])

  # consider only subnets defined on the source bridge
  source_subnets = [s for s in src_entities if s.get('vswitch_name') == config.args.source_bridge]

  to_copy = []
  # prepare rows including whether already exists on destination
  rows = []
  for s in source_subnets:
    exists_on_dest = any(x.get('vswitch_name') == config.args.destination_bridge and x.get('vlan_id') == s.get('vlan_id') for x in dst_entities)
    if not exists_on_dest:
      to_copy.append(s)

    name = s.get('name', '')
    vlan = s.get('vlan_id', '')
    ip_conf = s.get('ip_config', {}) or {}
    dhcp_enabled = ip_conf.get('ipam_enabled', False)
    dhcp_server = ip_conf.get('dhcp_server_address', '')
    network = ip_conf.get('network_address', '')
    prefix = ip_conf.get('prefix_length')
    subnet_ip = f"{network}/{prefix}" if network and prefix is not None else network
    gateway = ip_conf.get('default_gateway', '')
    exists_str = "Yes" if exists_on_dest else "No"
    rows.append((name, vlan, exists_str, str(dhcp_enabled), dhcp_server, subnet_ip, gateway))

  if not rows:
    print(f"No VLANs found on bridge {config.args.source_bridge}")
  else:
    headers = ("Name", "VLAN", "Present on Destination", "DHCP", "DHCP Server", "Subnet", "Gateway")
    widths = [max(len(str(x)) for x in col) for col in zip(*(rows + [headers]))]

    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("  ".join('-' * w for w in widths))
    for r in rows:
      print("  ".join(str(cell).ljust(w) for cell, w in zip(r, widths)))

  # now create the subnet(s) on the destination cluster & bridge for those not present
  if not to_copy:
    print("No subnets to copy.")
  else:
    # ask user how to proceed
    while True:
      print("\nChoose copy mode: [A] Automatic, [Y] Manual confirmation per subnet, [N] Cancel")
      mode = input("Selection (A/Y/N): ").strip().upper()
      if mode in ("A", "Y", "N"):
        break
      print("Invalid selection. Please choose A, Y or N.")

    if mode == "N":
      print("Operation cancelled by user.")
    else:
      for subnet in to_copy:
        do_copy = True
        if mode == "Y":
          # per-subnet confirmation
          while True:
            resp = input(f"Copy VLAN {subnet.get('vlan_id')} ({subnet.get('name','')})? [Y/N]: ").strip().upper()
            if resp in ("Y", "N"):
              do_copy = (resp == "Y")
              break
            print("Please enter Y or N.")

        if not do_copy:
          print(f"Skipping VLAN {subnet.get('vlan_id')}")
          continue

        print(f"Copying the VLAN {subnet.get('vlan_id')}", end="")
        result = create_subnet(config.rest_connector, config.args.destination_cluster, subnet, config.args.destination_bridge)
        if "network_uuid" in result:
          print(f"...{green}Done{nc}. Network uuid: {result['network_uuid']}")