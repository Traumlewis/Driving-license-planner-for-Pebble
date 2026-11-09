#!/usr/bin/env python3
"""LP5P experiment: selected text, BPE dictionary and Huffman book in one packet.

This is a desktop feasibility prototype, NOT a supported watch packet format.
It never changes a build, the live catalogue, existing codecs or app storage.
"""
import argparse
from collections import Counter
import heapq
import itertools
import json
from pathlib import Path
import struct
import zlib
import bz2

ROOT = Path(__file__).resolve().parents[2]
HEADER = struct.Struct('<4sIHHHHIIII')
PACKET_LIMIT = 2560
MANIFEST_BYTES = 16
APP_RESERVE = 1500
OLD_WATCH_QUOTA = 4096
STEPS = (0, 32, 64, 96, 128, 192, 256, 384, 512, 768, 1024)


def varint(value):
    out = bytearray()
    while value >= 128:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return out


def read_varint(raw, position):
    value = shift = 0
    while position < len(raw) and shift <= 21:
        byte = raw[position]
        position += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, position
        shift += 7
    raise ValueError('Invalid varint')


def canonical_codes(lengths):
    codes = {}
    code = previous = 0
    for length, token in sorted((n, i) for i, n in enumerate(lengths) if n):
        if length > 31:
            raise ValueError('Huffman code too deep')
        code <<= length-previous
        if code >= 1 << length:
            raise ValueError('Oversubscribed Huffman book')
        codes[token] = (code, length)
        code += 1
        previous = length
    if not codes:
        raise ValueError('Empty Huffman book')
    return codes


def huffman_lengths(sequences, alphabet):
    frequency = Counter(token for sequence in sequences for token in sequence)
    serial = itertools.count()
    queue = [(n, next(serial), token) for token, n in sorted(frequency.items())]
    heapq.heapify(queue)
    while len(queue) > 1:
        a = heapq.heappop(queue)
        b = heapq.heappop(queue)
        heapq.heappush(queue, (a[0]+b[0], next(serial), (a[2], b[2])))
    lengths = [0]*alphabet

    def visit(node, depth):
        if isinstance(node, int):
            lengths[node] = max(1, depth)
        else:
            visit(node[0], depth+1)
            visit(node[1], depth+1)

    visit(queue[0][2], 0)
    return lengths


def encode_book(lengths):
    # A byte stores a five-bit code length and a run of one to eight symbols.
    out = bytearray()
    for length, run in itertools.groupby(lengths):
        count = sum(1 for _ in run)
        while count:
            n = min(8, count)
            out.append((length << 3) | (n-1))
            count -= n
    return out


def encode(sequences, dictionary, *, schema_id=0, language=0, name='Test'):
    lengths = huffman_lengths(sequences, 256+len(dictionary))
    codes = canonical_codes(lengths)
    dictionary_bytes = bytearray()
    for left, right in dictionary:
        dictionary_bytes += varint(left)+varint(right)
    book = encode_book(lengths)
    directory = bytearray()
    payload = bytearray()
    pending = pending_bits = bit_count = 0
    for sequence in sequences:
        size = sum(codes[token][1] for token in sequence)
        if not size:
            raise ValueError('Empty text')
        directory += varint(size)
        bit_count += size
        for token in sequence:
            code, n = codes[token]
            pending = (pending << n) | code
            pending_bits += n
            while pending_bits >= 8:
                pending_bits -= 8
                payload.append((pending >> pending_bits) & 255)
        pending &= (1 << pending_bits)-1
    if pending_bits:
        payload.append(pending << (8-pending_bits))
    encoded_name = name.encode()
    body = encoded_name+dictionary_bytes+book+directory+payload
    header = HEADER.pack(b'LP5P', schema_id, len(sequences), len(dictionary),
                         len(encoded_name), language, HEADER.size+len(body),
                         bit_count, len(book), 0)
    crc = zlib.crc32(header+body)
    packet = header[:-4]+struct.pack('<I', crc)+body
    return packet, dict(headerBytes=HEADER.size, nameBytes=len(encoded_name),
                        dictionaryBytes=len(dictionary_bytes), bookBytes=len(book),
                        directoryBytes=len(directory), compressedTextBytes=len(payload),
                        dictionaryEntries=len(dictionary), packetBytes=len(packet))


def decode(packet):
    """Decode using ONLY the packet; no shared dictionary or translation files."""
    if len(packet) < HEADER.size:
        raise ValueError('Truncated header')
    magic, schema, count, merges, name_size, language, size, bits, book_size, crc = HEADER.unpack_from(packet)
    if magic != b'LP5P' or size != len(packet) or not 0 < count <= 296 or merges > 1024 or not 0 < name_size <= 23 or language > 63:
        raise ValueError('Invalid header')
    if zlib.crc32(packet[:HEADER.size-4]+bytes(4)+packet[HEADER.size:]) != crc:
        raise ValueError('CRC mismatch')
    cursor = HEADER.size
    name = packet[cursor:cursor+name_size].decode('utf-8')
    if '\0' in name:
        raise ValueError('Invalid name')
    cursor += name_size
    dictionary = []
    for i in range(merges):
        left, cursor = read_varint(packet, cursor)
        right, cursor = read_varint(packet, cursor)
        if left >= 256+i or right >= 256+i:
            raise ValueError('Cyclic or forward dictionary reference')
        dictionary.append((left, right))
    lengths = []
    if cursor+book_size > len(packet):
        raise ValueError('Truncated codebook')
    for byte in packet[cursor:cursor+book_size]:
        lengths.extend([byte >> 3]*((byte & 7)+1))
    cursor += book_size
    if len(lengths) != 256+merges:
        raise ValueError('Invalid codebook length')
    codes = canonical_codes(lengths)
    symbols = {(n, code): token for token, (code, n) in codes.items()}
    sizes = []
    for _ in range(count):
        length, cursor = read_varint(packet, cursor)
        if not length:
            raise ValueError('Empty text')
        sizes.append(length)
    if sum(sizes) != bits or cursor+(bits+7)//8 != len(packet):
        raise ValueError('Invalid payload size')
    result = []
    bit = 0
    for size in sizes:
        end = bit+size
        text = bytearray()
        while bit < end:
            code = token = 0
            for n in range(1, 32):
                if bit >= end:
                    raise ValueError('Truncated Huffman symbol')
                code = (code << 1) | ((packet[cursor+bit//8] >> (7-bit % 8)) & 1)
                bit += 1
                token = symbols.get((n, code))
                if token is not None:
                    break
            else:
                raise ValueError('Invalid Huffman symbol')
            pending = [token]
            while pending:
                token = pending.pop()
                if token < 256:
                    if token == 0 or len(text) >= 2047:
                        raise ValueError('Invalid expanded text')
                    text.append(token)
                else:
                    left, right = dictionary[token-256]
                    pending.extend((right, left))
                    if len(pending) > 64:
                        raise ValueError('Dictionary nesting too deep')
        result.append(text.decode('utf-8'))
    return dict(name=name, language=language, schemaId=schema, strings=result)


def candidates(texts, **metadata):
    sequences = [list(text.encode()) for text in texts]
    dictionary = []
    yield encode(sequences, dictionary, **metadata)
    for i in range(max(STEPS)):
        frequency = Counter(pair for sequence in sequences for pair in zip(sequence, sequence[1:]))
        if not frequency:
            return
        pair, count = min(frequency.items(), key=lambda item: (-item[1], item[0]))
        if count < 2:
            return
        dictionary.append(pair)
        for k, sequence in enumerate(sequences):
            out = []
            j = 0
            while j < len(sequence):
                if j+1 < len(sequence) and (sequence[j], sequence[j+1]) == pair:
                    out.append(256+i)
                    j += 2
                else:
                    out.append(sequence[j])
                    j += 1
            sequences[k] = out
        if len(dictionary) in STEPS:
            yield encode(sequences, dictionary, **metadata)


def experiment(output):
    output.mkdir(parents=True, exist_ok=True)
    schema = json.loads((ROOT/'tools/watch-schema.json').read_text())
    # Same language-independent key schema used by the live app.
    schema_id = zlib.crc32(json.dumps([(r['de'], r['maxBytes'], r['signature']) for r in schema], ensure_ascii=False, separators=(',', ':')).encode())
    report = dict(experimentalFormat='LP5P/self-contained-bpe-huffman',
                  productionVersionUnchanged='3.8.49', oldWatchQuota=OLD_WATCH_QUOTA,
                  reservedAppBytes=APP_RESERVE, currentPacketLimit=PACKET_LIMIT,
                  manifestBytes=MANIFEST_BYTES, results=[], shipped=False)
    for path in sorted((ROOT/'Packs/App/Languages').glob('*/watch-source.json')):
        source = json.loads(path.read_text())
        texts = [source['strings'][row['de']] for row in schema]
        trials = list(candidates(texts, schema_id=schema_id, language=source['language'], name=source['name']))
        for packet, _ in trials:
            decoded = decode(packet)
            assert decoded['strings'] == texts and decoded['language'] == source['language']
        packet, stats = min(trials, key=lambda item: len(item[0]))
        # Corruption/truncation must fail rather than produce changed text.
        for broken in (packet[:-1], bytes([packet[0] ^ 1])+packet[1:], packet[:-1]+bytes([packet[-1] ^ 1])):
            try:
                decode(broken)
            except (ValueError, UnicodeError, IndexError):
                pass
            else:
                raise AssertionError('Corrupted packet accepted')
        raw = b'\0'.join(text.encode() for text in texts)+b'\0'
        deflate = {}
        for window in (9, 10, 11, 12, 13, 15):
            encoder = zlib.compressobj(9, zlib.DEFLATED, -window)
            packed = encoder.compress(raw)+encoder.flush()
            assert zlib.decompress(packed, -window) == raw
            deflate[str(1 << window)] = len(packed)
        stored = len(packet)+MANIFEST_BYTES
        row = dict(locale=source['locale'], name=source['name'], textCount=len(texts),
                   rawBytes=len(raw), **stats, storedBytes=stored,
                   combinedWithAppReserve=stored+APP_RESERVE,
                   exceedsCurrentPacketBy=max(0, len(packet)-PACKET_LIMIT),
                   exceedsOldQuotaBy=max(0, stored+APP_RESERVE-OLD_WATCH_QUOTA),
                   fitsCurrentReceiver=len(packet) <= PACKET_LIMIT,
                   fitsOldStorage=stored+APP_RESERVE <= OLD_WATCH_QUOTA,
                   roundtripAllTexts=True, corruptAndTruncatedRejected=True,
                   deflateRawByWindow=deflate, bzip2Bytes=len(bz2.compress(raw, 9)),
                   candidateSizes=[dict(dictionaryEntries=s['dictionaryEntries'], packetBytes=len(p)) for p, s in trials])
        report['results'].append(row)
        (output/(source['locale']+'.experimental-lp5p')).write_bytes(packet)
        print(source['locale'], 'best', len(packet), 'packet bytes;', stored+APP_RESERVE,
              '/', OLD_WATCH_QUOTA, 'with app reserve', flush=True)
    report['allLanguagesFitOldStorage'] = all(row['fitsOldStorage'] for row in report['results'])
    report['decision'] = ('eligible-for-native-prototype' if report['allLanguagesFitOldStorage'] else 'do-not-migrate-storage-budget-exceeded')
    (output/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Separate experimental artifacts, never a live catalogue folder')
    args = parser.parse_args()
    if (ROOT/'Packs') == args.output.resolve() or ROOT/'Packs' in args.output.resolve().parents:
        parser.error('Experimental artifacts must not be published as live language packets')
    experiment(args.output)
