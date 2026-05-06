# header classes
class UDPHeader:
    def __init__(self, source_port, dest_port, segment_length, segment_type, sequence_number, payload, checksum=None):
        self.source_port = source_port
        self.dest_port = dest_port
        self.segment_length = segment_length  # length of header + data
        self.segment_type = segment_type  # 0 = DATA, 1 = ACK
        self.sequence_number = sequence_number  # should alternate between 0 and 1
        self.payload = payload  # data getting sent

        if checksum is None:
            self.checksum =  self._generate_checksum()
        else:
            self.checksum = checksum

    def _generate_checksum(self):
        pass

# layer 4 (transport layer) classes
class RDTSender:
    def __init__(self, source_port, network_channel=None, host_name=None, dest_port=None, data_size=None, payload=None):
        self.source_port = source_port
        self.sequence_number = 0
        self.current_state = 0  # 0 = waiting for app data, 1 = waiting for ack from receiver
        self.last_packet_sent = None

        # init config
        self.network_channel = None
        self.host_name = None
        self.dest_port = None
        self.data_size = None
        self.payload = None

    def encapsulate(self, data, data_size, dest_port):
        segment_length = 100  # have to change this depending on how long we want the segment to be
        if data_size <= segment_length:
            current_segment = UDPHeader(self.source_port, dest_port, segment_length, 0, self.sequence_number, data)
            return current_segment
        else:
            return  # need to figure out how to segment data

    def rdt_sender(self, host_name, payload, data_size, dest_port, network_channel):
        self.host_name = host_name
        self.payload = payload
        self.data_size = data_size
        self.dest_port = dest_port
        self.network_channel = network_channel
        print(f"{self.host_name}: Layer 4: Data received from Application Layer. Data size={self.data_size}\n")
        current_segment = self.encapsulate(self.payload, self.data_size, self.dest_port)
        print(f"{self.host_name}: Layer 4: Checksum computed\n")
        print(f"{self.host_name}: Layer 4: Segment created by adding transport layer header (DATA, seq={current_segment.sequence_number}) (encapsulation)\n")

        self.current_state = 1
        self.last_packet_sent = current_segment

        self.send(current_segment)

        return current_segment

    def send(self, packet):
        self.network_channel.transmit(packet, self.dest_port)
        print(f"{self.host_name}: Layer 4: Segment sent to Network Layer\n")

    def ack_verification(self, feedback):  # this should verify the ACK received from the receiver side
        pass

    def retransmission(self, packet):
        pass

class RDTReceiver:
    def __init__(self):
        pass

    def sequence_verification(self, packet):
        pass

    def checksum_verification(self, packet):
        pass

    def extract_data(self, packet):
        pass

    def generate_ack(self):
        pass