# TODO: confirm these imports are needed
from config import *
from devices import *


# TODO (STILL UNFINISHED):
#   transport layer checksum implementation

# header classes
class UDPHeader:
    def __init__(self, source_port, dest_port, data_length, segment_type, sequence_number, payload, checksum=None):
        self.source_port = source_port
        self.dest_port = dest_port
        self.segment_length = 10 + data_length  # length of header + data
        self.segment_type = segment_type  # 0 = DATA, 1 = ACK
        self.sequence_number = sequence_number  # should alternate between 0 and 1
        self.payload = payload  # data getting sent

        if checksum is None:
            self.checksum =  self._generate_checksum()
        else:
            self.checksum = checksum

    def _generate_checksum(self):  # TODO: how to generate a checksum
        pass

class IPPacket:
    def __init__(self, source_ip, dest_ip, ttl, protocol, packet_length, payload):
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.ttl = ttl  # should start at 100 and decrement at each router
        self.protocol = protocol  # should be 17 (indicates UDP payload)
        self.packet_length = packet_length  # IP packer header + UDP segment from transport layer
        self.payload = payload  # UDP segment

class EthernetFrame:
    def __init__(self, dest_mac, source_mac, frame_type, payload):
        self.dest_mac = dest_mac
        self.source_mac = source_mac
        self.frame_type = frame_type
        self.payload = payload


# layer 4 (transport layer) classes
class RDTSender:
    def __init__(self, source_port=None, network_channel=None, host_name=None, dest_port=None, data_size=None, payload=None, dest_ip=None, source_ip=None):
        self.sequence_number = 0
        self.current_state = 0  # 0 = waiting for app data, 1 = waiting for ack from receiver
        self.last_packet_sent = None

        # init config
        self.source_port = source_port
        self.network_channel = network_channel
        self.host_name = host_name
        self.dest_port = dest_port
        self.data_size = data_size
        self.payload = payload
        self.dest_ip = dest_ip
        self.source_ip = source_ip

    def encapsulate(self, source_port, data, data_size, dest_port):
        segment_length = 500  # have to change this depending on how long we want the segment to be
        if data_size <= segment_length:
            current_segment = UDPHeader(source_port, dest_port, segment_length, 0, self.sequence_number, data)
            return current_segment
        else:
            return  # TODO: need to figure out how to segment data

    def rdt_sender(self, source_port, host_name, payload, data_size, dest_port, network_channel, dest_ip, source_ip):
        self.source_port = source_port
        self.host_name = host_name
        self.payload = payload
        self.data_size = data_size
        self.dest_port = dest_port
        self.network_channel = network_channel
        self.dest_ip = dest_ip
        self.source_ip = source_ip
        print(f"{self.host_name}: Layer 4: Data received from Application Layer. Data size={self.data_size}\n")
        current_segment = self.encapsulate(self.source_port, self.payload, self.data_size, self.dest_port)
        print(f"{self.host_name}: Layer 4: Checksum computed\n")
        print(f"{self.host_name}: Layer 4: Segment created by adding transport layer header (DATA, seq={current_segment.sequence_number}) (encapsulation)\n")

        self.current_state = 1
        self.last_packet_sent = current_segment

        self.send(current_segment, self.source_ip, self.dest_ip, self.host_name)

    def send(self, packet, source_ip, dest_ip, host_name):
        print(f"{host_name}: Layer 4: Segment sent to Network Layer\n")
        self.network_channel.layer_transmission(packet, dest_ip, source_ip, host_name)

    def receive(self, segment, sender_ip=None):
        print(f"{self.host_name}: Layer 4: Segment received from Network Layer")

        if self.checksum_verification(segment):
            print(f"{self.host_name}: Layer 4: Checksum verified")

            if segment.segment_type == 1:
                self.ack_verification(segment)

    def checksum_verification(self, segment):  # TODO: checksum
        pass

    def ack_verification(self, feedback_segment):
        print(f"{self.host_name}: Layer 4: ACK received: seq={feedback_segment.sequence_number}\n")

        if feedback_segment.sequence_number == self.sequence_number:
            self.current_state = 0
            self.sequence_number = 1 - self.sequence_number
        else:
            print(f"{self.host_name}: Layer 4: Duplicate/Invalid ACK. Retransmitting...")
            self.retransmission(self.last_packet_sent)

    def retransmission(self, packet):
        print(f"{self.host_name}: Layer 4: Retransmitting segment...")
        self.send(packet, self.source_ip, self.dest_ip, self.host_name)

class RDTReceiver:
    def __init__(self, host_name, network_layer, source_ip=None):
        self.host_name = host_name
        self.network_layer = network_layer
        self.source_ip = source_ip
        self.expected_sequence_number = 0

    def receive(self, segment, sender_ip):
        print(f"{self.host_name}: Layer 4: Segment received from Network Layer")

        if self.checksum_verification(segment):
            print(f"{self.host_name}: Layer 4: Checksum verified")

            if segment.segment_type == 0:
                if self.sequence_verification(segment):
                    app_data = self.decapsulation(segment)
                    data_size = segment.segment_length - 10
                    print(f"{self.host_name}: Layer 4: DATA segment delivered to Application Layer. Data size={data_size}")
                    self.expected_sequence_number = 1 - self.expected_sequence_number
                else:
                    print(f"{self.host_name}: Layer 4: Duplicate packet (seq={segment.sequence_number}). Dropping data.")
                self.extract_data(segment)
                self.generate_ack(segment, sender_ip)

                self.generate_ack(segment, sender_ip)

    def sequence_verification(self, segment):
        if segment.sequence_number == self.expected_sequence_number:
            return True
        else:
            return False

    def decapsulation(self, segment):
        return segment.payload

    def checksum_verification(self, packet):  # TODO: verify checksum
        pass

    def extract_data(self, segment):
        data_size = segment.segment_length - 10
        print(f"{self.host_name}: Layer 4: DATA segment delivered to Application Layer. Data size={data_size}")
        return segment.payload

    def generate_ack(self, received_segment, dest_ip):
        print(
            f"{self.host_name}: Layer 4: Segment created by adding transport layer header (ACK, seq={received_segment.sequence_number})")
        print(f"{self.host_name}: Layer 4: Segment sent to Network Layer\n")

        ack_segment = UDPHeader(
            source_port=received_segment.dest_port,
            dest_port=received_segment.source_port,
            data_length=0,
            segment_type=1,
            sequence_number=received_segment.sequence_number,
            payload=None
        )

        if self.network_layer:
            self.network_layer.layer_transmission(ack_segment, dest_ip, self.source_ip, self.host_name)

# layer 3 (network layer) class(es)
class NetworkLayer:
    def __init__(self, source_ip=None, host_name=None, dest_ip=None, payload=None, routing_table_data=None):
        self.source_ip = source_ip
        self.host_name = host_name
        self.dest_ip = dest_ip
        self.payload = payload
        self.ttl_value = None
        self.routing_table_data = routing_table_data
        self.data_link_layer = None  # TODO: implement this in devices.py
        self.transport_layer = None

    def layer_transmission(self, udp_segment, dest_ip, source_ip, host_name):
        # convert transport layer segment to something that can be sent on network layer
        self.ttl_value = 100
        self.host_name = host_name
        print(f"{host_name}: Layer 3: Segment received from Transport Layer: SRC_IP={source_ip}, DST_IP={dest_ip}, TTL={self.ttl_value}\n")
        current_packet = self.encapsulate(udp_segment, dest_ip, source_ip)
        route_next_hop, interface = self.routing_table(dest_ip)
        actual_next_hop = self.next_hop_determination(dest_ip, route_next_hop)
        print(f"{host_name}: Layer 3: Next-hop IP determined: {actual_next_hop}\n")
        print(f"{host_name}: Layer 3: Outgoing interface selected")
        self.transmit(current_packet, actual_next_hop, interface)

    # network layer sender
    def encapsulate(self, udp_segment, dest_ip, source_ip):
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        print(f"{self.host_name}: Layer 3: Destination IP read: {self.dest_ip}\n")
        protocol = 17
        packet_length = 12 + udp_segment.segment_length  # need to double-check the size of IP packet header, whether it's 12 or 20
        self.payload = udp_segment

        current_packet = IPPacket(source_ip, dest_ip, self.ttl_value, protocol, packet_length, self.payload)

        return current_packet

    def routing_table(self, dest_ip):  # checks routing table to see which network the destination IP belongs to
        print(f"{self.host_name}: Layer 3: Routing table lookup performed\n")
        if dest_ip in self.routing_table_data:
            route = self.routing_table_data[dest_ip]
        else:
            route = self.routing_table_data.get("0.0.0.0/0")  # default route (TODO: do we need to change this?)
        return route['next_hop'], route['interface']  # TODO: also need to check whether this syntax is correct

    def next_hop_determination(self, dest_ip, route_next_hop):  # identifies specific IP address of next device in the path as well as which interface to use to send the packet out
        if route_next_hop is None:
            return dest_ip
        else:
            return route_next_hop

    def ttl(self, packet):  # time to live
        old_ttl = packet.ttl
        packet.ttl -= 1
        print(f"{self.host_name}: Layer 3: TTL decremented: {old_ttl} -> {packet.ttl}\n")

        if packet.ttl <= 0:
            print(f"{self.host_name}: Layer 3: Packet dropped (TTL reached 0)\n")
            return False
        return True

    def transmit(self, packet, next_hop_ip, interface):
        # transmits IP packet into data link layer
        self.data_link_layer.layer_transmission(packet, next_hop_ip, interface)

    # network layer receiver
    def receive(self, packet):  # verifies destination IP
        # received IP packet from data link layer
        # if destination IP matches device's own IP, identify packet as local delivery
        # else transmit()
        # check TTL: if ttl reached 0 at a router, packet is dropped
        print(f"{self.host_name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.source_ip}, DST_IP={packet.dest_ip}, TTL={packet.ttl}")
        print(f"{self.host_name}: Layer 3: Destination IP read: {packet.dest_ip}")

        if "Router" in self.host_name:
            if self.ttl(packet):
                route_next_hop, interface = self.routing_table(packet.dest_ip)
                actual_next_hop = self.next_hop_determination(packet.dest_ip, route_next_hop)

                print(f"{self.host_name}: Layer 3: Next-hop IP determined: {actual_next_hop}")
                print(f"{self.host_name}: Layer 3: Outgoing interface selected (Interface {interface})")
                print(f"{self.host_name}: Layer 3: Packet forwarded to Data Link Layer")

                self.transmit(packet, actual_next_hop, interface)
        elif packet.dest_ip == self.source_ip:
            print(f"{self.host_name}: Layer 3: Packet identified as local delivery")
            print(f"{self.host_name}: Layer 3: Segment delivered to Transport Layer")

            if self.transport_layer:
                self.transport_layer.receive(packet.payload, packet.source_ip)
            else:
                print(f"{self.host_name}: Layer 3: ERROR - No Transport Layer connected.")
        else:
            print(f"{self.host_name}: Layer 3: Packet dropped. Not a router and destination IP does not match.")

# layer 2 (data link layer) class(es)
class DataLinkLayer:
    def __init__(self, mac_address, host_name, arp_table=None):
        self.mac_address = mac_address
        self.host_name = host_name
        self.arp_table = arp_table if arp_table is not None else {}
        self.network_layer = None
        self.mac_learning_table = {}
        self.connected_devices = {}

    def layer_transmission(self, packet, next_hop_ip, interface):
        print(f"{self.host_name}: Layer 2: Packet received from Network Layer")

        dest_mac = self.mac_addressing(next_hop_ip)
        print(f"{self.host_name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dest_mac}")

        frame_type = "0x0800"
        current_frame = self.encapsulation(dest_mac, self.mac_address, frame_type, packet)
        print(f"{self.host_name}: Layer 2: Frame created: SRC_MAC={self.mac_address}, DST_MAC={dest_mac}")

        if "Router" in self.host_name:
            print(f"{self.host_name}: Layer 2: Frame forwarded on Interface {interface}")
        else:
            print(f"{self.host_name}: Layer 2: Frame sent")

        if interface in self.connected_devices:
            next_device_layer2 = self.connected_devices[interface]
            next_device_layer2.receive_from_physical(current_frame, interface)
        else:
            print(f"{self.host_name}: Layer 2: DROP - Nothing connected to Interface {interface}")


    def mac_addressing(self, next_hop_ip):
        return self.arp_table.get(next_hop_ip, "FF:FF:FF:FF:FF:FF")

    def encapsulation(self, dest_mac, source_mac, frame_type, payload):
        return EthernetFrame(dest_mac, source_mac, frame_type, payload)

    def receive_from_physical(self, frame, interface=None):
        if interface and "Router" in self.host_name:
            print(f"{self.host_name}: Layer 2: Frame received on Interface {interface}")
            print(f"{self.host_name}: Layer 2: Source MAC learned: {frame.source_mac} on Interface {interface}")
        else:
            print(f"{self.host_name}: Layer 2: Frame received")
            print(f"{self.host_name}: Layer 2: Source MAC learned: {frame.source_mac}")
        self.mac_learning_table[frame.source_mac] = interface
        print(f"{self.host_name}: Layer 2: Packet delivered to Network Layer")
        if self.network_layer:
            self.network_layer.receive(frame.payload)