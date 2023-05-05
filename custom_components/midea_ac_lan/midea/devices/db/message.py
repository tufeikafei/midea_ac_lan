from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageDBBase(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xDB,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageDBBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query,
            body_type=0x03)

    @property
    def _body(self):
        return bytearray([])


class MessagePower(MessageDBBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x02)
        self.power = False

    @property
    def _body(self):
        power = 0x01 if self.power else 0x00
        return bytearray([
            power,
            0xFF, 0xFF, 0xFF, 0xFF,
            0xFF, 0xFF, 0xFF, 0xFF,
            0xFF, 0xFF, 0xFF, 0xFF,
            0xFF, 0xFF, 0xFF, 0xFF,
            0xFF, 0xFF, 0xFF, 0xFF
        ])


class MessageStart(MessageDBBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x02)
        self.start = False
        self.washing_data = bytearray([0x00,0x09,0xFF,0x00,0x01,0x02,0xFF,0xFF,0xFF,0xFF,0x00,0xFF,0xFF])

    @property
    def _body(self):
        if self.start: # Pause
            return bytearray([
                0xFF, 0x01
            ]) + self.washing_data
        else:
            # Pause
            return bytearray([
                0xFF, 0x00
            ])

class MessageDehytration(MessageDBBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.set,
            body_type=0x02)
        self.dehytration = False
        self.washing_data = bytearray([0x00,0x09,0xFF,0x00,0x01,0x02,0xFF,0xFF,0xFF,0xFF,0x00,0xFF,0xFF])

    @property
    def _body(self):
        if self.dehytration: # Pause
            return bytearray([
                0xFF, 0x01
            ]) + self.washing_data
        else:
            # Pause
            return bytearray([
                0xFF, 0x00
            ])



class DBGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = body[1] > 0
        self.start = True if body[2] in [2, 6] else False
        
        self.dehytration = True if body[2] in [2, 6] else False

        # self.washing_data = body[3:16]
        print("body start:")

        print(body)
        print("body end:")

        # self.washing_data=bytearray([0x00,0x09,0xFF,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00])
        # body[3:16]=bytearray([0x00,0x09,0xFF,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00])
        self.progress = 0
        for i in range(0, 7):
            if (body[16] & (1 << i)) > 0:
                self.progress = i + 1
                break
        if self.power:
            self.time_remaining = body[17] + (body[18] << 8)
        else:
            self.time_remaining = None


class MessageDBResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.query, MessageType.set] or \
                (self._message_type == MessageType.notify1 and self._body_type == 0x04):
            self._body = DBGeneralMessageBody(body)
        self.set_attr()
