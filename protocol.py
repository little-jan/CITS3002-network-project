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

    def on_frame_received(self, interface, frame:DataLinkFrame):
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
    def __init__(self, my_port, application_layer, network_layer):
        self.my_port = my_port
        self.application_layer = application_layer
        self.network_layer = network_layer

        # rdt2.2 sender state logic
        self.sequence_num = 0  # alternates between 0 and 1
        self.last_sent_segment = None

        # rdt2.2 receiver state logic
        self.expected_sequence_num = 0
        self.last_sent_ack = 1  # initialise to hte opposite of the first expected

    def create_segment(self, source_port, dest_port, segment_length, data_type, sequence_number, segment_data):
        return UDPSegment(source_port, dest_port, segment_length, data_type, sequence_number, segment_data)

    def on_segment_received(self, segment:UDPSegment, source_ip):
        print("Layer4: Segment received from Network Layer")

        if not self.verify_checksum(segment):
            print(f"Layer 4: Segment discarded due to checksum error")

            if segment.data_type == 0:
                self._send_ack(source_ip, segment.source_port, self.last_sent_ack)

            else:
                print("Layer 4: Segment retransmitted due to incorrect ACK")
                self.network_layer.receive_segment(self.last_sent_segment, source_ip)

            return
        print("Layer 4: Checksum verified")

        if segment.data_type == 0:
            if segment.sequence_number == self.expected_sequence_num:
                print(f"Layer 4: DATA segment delivered to Application Layer. Data size = {len(segment.segment_data)}")
                self.application_layer.receive_packet(segment.segment_data)
                self._send_ack(source_ip, segment.source_port, segment.sequence_number)
                self.last_sent_ack = segment.sequence_number
                self.expected_sequence_num = 1 - self.expected_sequence_num

            else:
                self._send_ack(source_ip, segment.source_port, self.last_sent_ack)

        elif segment.data_type == 1:
            print(f"Layer 4: ACK received: seq={segment.sequence_number}")
            if segment.sequence_number == self.sequence_num:
                self.sequence_num = 1 - self.sequence_num

            else:
                print("Layer 4: Segment retransmitted due to incorrect ACK")
                self.network_layer.receive_segment(self.last_sent_segment, source_ip)

    def _send_ack(self, dest_ip, dest_port, ack_sequence_num):
        ack_segment = self.create_segment(self.my_port, dest_port, 8, 1, ack_sequence_num, "")
        print(f"Layer 4: Segment created by adding transport layer header (ACK, seq={ack_sequence_num})")
        print("Layer 4: Segment sent to Network Layer")
        self.network_layer.receive_segment(ack_segment, dest_ip)

    def send_segment(self, dest_ip, dest_port, data):
        segment_length = len(data) + 8  # assuming that there is an 8-byte header
        segment = self.create_segment(self.my_port, dest_port, segment_length, 0, self.sequence_num, data)
        self.last_sent_segment = segment
        print(f"Layer 4: Checksum computed")
        print(f"Layer 4: Segment created by adding transport layer header (DATA, seq={self.sequence_num})")
        print(f"Layer 4: Segment sent to Network Layer")
        self.network_layer.receive_segment(segment, dest_ip)