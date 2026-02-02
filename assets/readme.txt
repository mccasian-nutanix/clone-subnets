This script can copy all VLANs, including the DNS and DHCP settings, and also the DHCP Pool Ranges from a cluster to another cluster, or to the same cluster but other vswitch.

Use cases:
1. when cloning the subnets from br0 to br1 in the same cluster
2. when setting up a new cluster identical with an existing one(although that means same DHCP ranges on the new cluster)

# prepare
python3 -m pip install -r requirements.txt

# execution
python3 clone_subnets.py

# example
python3 clone_subnets.py --source-cluster=earth.spacex.nasa.com --destination-cluster=mars.spacex.nasa.com --source-bridge=br0 --destination-bridge=br1 --api-user=alien --api-pass=reborn2040 --log-level=INFO