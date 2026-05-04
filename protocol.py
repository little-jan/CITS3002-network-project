"""
This file contains:

Data link layer ->
- frame creation
- MAC addressing
- forwarding behaviour
- delivery of data to upper layer

Network layer ->
- packet creation
- routing decisions
- forwarding between networks
- basic control mechanisms

Transport layer ->
- data segmentation
- construction of transport segments
- error detection
- simple reliable data transfer mechanism
"""


# header classes
class DataLinkFrame:
    def __init__(self, dest_mac, src_mac, payload):
        self.dest_mac = dest_mac
        self.src_mac = src_mac
        self.eth_type = 0x0800
        self.payload = payload  # layer 3 packet


class UDPSegment:
    def __init__(self, source_port, dest_port, segment_length, data_type, sequence_number, segment_data, checksum=None):
        self.source_port = source_port
        self.dest_port = dest_port
        self.segment_length = segment_length  # header + data length
        self.data_type = data_type  # 0=DATA, 1=ACK
        self.sequence_number = sequence_number  # 0 or 1
        self.segment_data = segment_data  # contains the application message, empty for ACK
        self.checksum = self._checksum()

    def _checksum(self):
        # TODO: checksum logic
        raise NotImplementedError


# layer classes
class DataLinkLayer:
    def __init__(self, my_mac, network_layer):
        self.my_mac = my_mac
        self.network_layer = network_layer

        self.mac_table = {}  # maps IP to MAC
        self.switch_table = {}  # maps MAC to interface

    def create_frame(self, dest_mac, src_mac, layer3_pkt):
        return DataLinkFrame(dest_mac, src_mac, layer3_pkt)

    def learn_mac(self, mac_address, interface):
        self.switch_table[mac_address] = interface

    def on_frame_received(self, interface, frame=DataLinkFrame):
        self.learn_mac(frame.src_mac, interface)

        if frame.dest_mac == self.my_mac:
            self.network_layer.receive_packet(frame.payload)
            print(f"Layer 2: Packet received from Network Layer")

        else:
            self.forward_frame(frame)

    def forward_frame(self, frame):
        if frame.dest_mac == self.my_mac:
            pass

        elif frame.dest_mac in self.switch_table:
            outgoing_interface = self.switch_table[frame.dest_mac]
            print(f"Layer 2: Forwarding frame to {frame.dest_mac} on interface {outgoing_interface}")

        else:
            print(f"Layer 2: Destination {frame.dest_mac} unknown, dropping frame.")


class TransportLayer:
    def __init__(self, my_port, application_layer):
        self.my_port = my_port
        self.application_layer = application_layer

    def create_segment(self, source_port, dest_port, segment_length, data_type, sequence_number, segment_data):
        return UDPSegment(source_port, dest_port, segment_length, data_type, sequence_number, segment_data)

    def on_segment_received(self, segment=UDPSegment):
        if segment.dest_port == self.my_port:
            self.application_layer.receive_packet(segment.segment_data)