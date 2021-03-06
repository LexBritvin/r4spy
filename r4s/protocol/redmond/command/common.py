from r4s.protocol import int_to_arr
from r4s.protocol.redmond.response.common import SuccessResponse, ErrorResponse, VersionResponse
from r4s.protocol.redmond.response.kettle import KettleResponse

_DATA_BEGIN_BYTE = 0x55
_DATA_END_BYTE = 0xaa


class RedmondCommand:
    CODE = NotImplemented
    resp_cls = NotImplemented

    @classmethod
    def wrap(cls, counter, cmd, data):
        return bytes([_DATA_BEGIN_BYTE, counter, cmd, *data, _DATA_END_BYTE])

    @staticmethod
    def unwrap(byte_arr):
        int_array = [x for x in byte_arr]
        start, i, cmd = int_array[:3]
        return i, cmd, int_array[3:-1]

    def wrapped(self, counter):
        return self.wrap(counter, self.CODE, self.to_arr())

    def to_arr(self):
        return []

    def parse_resp(self, resp):
        return self.resp_cls.from_bytes(resp)


class CmdFw(RedmondCommand):
    CODE = 1
    resp_cls = VersionResponse


class Cmd3On(RedmondCommand):
    CODE = 3
    resp_cls = SuccessResponse


class Cmd4Off(RedmondCommand):
    CODE = 4
    resp_cls = SuccessResponse


class FullProgram:

    def to_arr(self):
        raise NotImplemented


class Cmd5SetProgram(RedmondCommand):
    CODE = 5
    resp_cls = SuccessResponse

    def __init__(self, program: FullProgram):
        self.program = program

    def to_arr(self):
        return self.program.to_arr()


class Cmd6Status(RedmondCommand):
    CODE = 6

    def __init__(self, resp_cls):
        self.resp_cls = resp_cls

    def parse_resp(self, resp):
        return self.resp_cls.from_bytes(resp)


class Cmd62SwitchSound(RedmondCommand):
    CODE = 60
    resp_cls = SuccessResponse

    def __init__(self, state):
        self.state = state

    def to_arr(self):
        return [int(self.state)]


class Cmd62SwitchLock(RedmondCommand):
    CODE = 62
    resp_cls = SuccessResponse

    def __init__(self, state):
        self.state = state

    def to_arr(self):
        return [int(self.state)]


class CmdSync(RedmondCommand):
    CODE = 110
    resp_cls = ErrorResponse

    def __init__(self, timezone=4):
        # TODO: Get real timezone.
        from datetime import datetime
        self.now = int(datetime.now().timestamp())
        self.tmz = timezone * 3600

    def to_arr(self):
        return [*int_to_arr(self.now, 4), *int_to_arr(self.tmz, 4)]


class CmdAuth(RedmondCommand):
    CODE = 255
    resp_cls = SuccessResponse

    def __init__(self, key):
        self.key = key

    def to_arr(self):
        return self.key
