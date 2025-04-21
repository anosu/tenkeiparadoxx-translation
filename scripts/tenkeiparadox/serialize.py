import lz4.block

import msgpack
from msgpack import ExtType


def deserialize(data_list: tuple[ExtType, bytes] | list[list] | bytes) -> list:
    if not data_list or len(data_list) == 0:
        return []
    unpacker = msgpack.Unpacker(strict_map_key=False, timestamp=1)
    if isinstance(data_list, bytes):
        unpacker.feed(data_list)
        data_list = unpacker.unpack()

    if not isinstance(data_list[0], ExtType):
        return data_list

    ext: ExtType = data_list[0]
    unpacker.feed(ext.data)
    decompressed_data = b''.join(
        lz4.block.decompress(data, size)
        for size, data in zip(unpacker, data_list[1:])
    )
    unpacker.feed(decompressed_data)
    return unpacker.unpack()


def deserialize_api(data: bytes):
    unpacker = msgpack.Unpacker(strict_map_key=False, timestamp=1)
    unpacker.feed(data)

    return {
        key: deserialize(unpacker.unpack())
        for key in ['errors', 'result', 'present', 'deleted', 'notifications']
    }
