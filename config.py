"""
Stores all fixed configuration parameters for the Mini Internet Protocol Stack Simulator.
This includes:
- IP addresses 
- MAC addresses 
- routing tables 
- MAC (ARP) tables
- protocol constants
"""

# IP Addresses
HOST_A_IP = "10.0.1.10"
ROUTER_R1_IF1_IP = "10.0.1.1"
ROUTER_R1_IF2_IP = "10.0.2.1"
HOST_B_IP = "10.0.2.20"

# MAC Addresses
HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
ROUTER_R1_IF1_MAC = "BB:BB:BB:BB:BB:BB"
ROUTER_R1_IF2_MAC = "CC:CC:CC:CC:CC:CC"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"

# Network Subnets
NETWORK_1 = "10.0.1.0"   # Subnet containing Host A and R1 Interface 1
NETWORK_2 = "10.0.2.0"   # Subnet containing Host B and R1 Interface 2
SUBNET_MASK = "255.255.255.0"  # /24 mask for both subnets


""" 
Routing tables :
Each entry maps 
-"next_hop": the IP of the next device to forward to
- "interface": the outgoing interface name
"""

# Host A: sits on Network 1, default route sends everything else to R1 Interface 1
HOST_A_ROUTING_TABLE = {
    "10.0.1.0/24": {"next_hop": None, "interface": "eth0"},  # local
    "0.0.0.0/0":   {"next_hop": "10.0.1.1", "interface": "eth0"}  # default
}

# Host B: sits on Network 2, default route sends everything else to R1 Interface 2
HOST_B_ROUTING_TABLE = {
    "10.0.2.0/24": {"next_hop": None, "interface": "eth0"},  
    "0.0.0.0/0":   {"next_hop": ROUTER_R1_IF2_IP, "interface": "eth0"}, #SHOULD THIS BE ROUTER_R1_IF2_IP OR 10.0.2.1
}
 
# Router R1: knows both directly connected networks
ROUTER_R1_ROUTING_TABLE = {
    "10.0.1.0/24": {"next_hop": None, "interface": "Interface 1"},  # directly connected
    "10.0.2.0/24": {"next_hop": None, "interface": "Interface 2"},  # directly connected
}
 


"""
ARP Tables (maps next-hop IP -> MAC address)
These are pre-populated (no ARP protocol needed in this simulation).
Each device only knows the MACs of its directly reachable neighbours.
"""

# Host A knows: the router's Interface 1 MAC
HOST_A_MAC_TABLE = {
    ROUTER_R1_IF1_IP: ROUTER_R1_IF1_MAC,
}
 
# Host B knows: the router's Interface 2 MAC
HOST_B_MAC_TABLE = {
    ROUTER_R1_IF2_IP: ROUTER_R1_IF2_MAC,
}
 
# Router R1 Interface 1 knows: Host A's MAC
ROUTER_R1_IF1_MAC_TABLE = {
    HOST_A_IP: HOST_A_MAC,
}
 
# Router R1 Interface 2 knows: Host B's MAC
ROUTER_R1_IF2_MAC_TABLE = {
    HOST_B_IP: HOST_B_MAC,
}


# Protocol Constants
 
DEFAULT_TTL         = 100    # Initial TTL value for all IP packets
ETH_TYPE_IPV4       = 0x0800 # Ethernet type field value indicating IPv4 payload
IP_PROTOCOL_UDP     = 17     # IP protocol field value indicating UDP payload
MAX_SEGMENT_SIZE    = 500    # Maximum application data (bytes) per UDP-like segment
 
# Transport layer segment types
SEGMENT_TYPE_DATA   = 0      # DATA segment
SEGMENT_TYPE_ACK    = 1      # ACK segment
 
# Well-known ports used in this simulation
SRC_PORT            = 5000   # Source port (Host A application)
DST_PORT            = 80     # Destination port (Host B application)
 
# Layer 4 header size in bytes 
UDP_HEADER_SIZE     = 8