"""Desktop proof for the experimental self-contained decoder, not watch integration."""
import struct
import unittest
from unittest.mock import patch
import zlib

from self_contained_languages import HEADER, canonical_codes, candidates, decode, encode


def repair_crc(packet):
    raw = bytearray(packet)
    raw[HEADER.size-4:HEADER.size] = bytes(4)
    raw[HEADER.size-4:HEADER.size] = struct.pack('<I', zlib.crc32(raw))
    return bytes(raw)


class SelfContainedDecoderTests(unittest.TestCase):
    def test_unknown_language_decodes_without_any_external_dictionary(self):
        texts = ['Nouvelle langue : œ, é, ç', 'Polski: żółć', '日本語のテスト']
        packet, _ = min(candidates(texts, language=17, name='Essai'), key=lambda item: len(item[0]))
        with patch('pathlib.Path.read_text', side_effect=AssertionError('External dictionary accessed')):
            decoded = decode(packet)
        self.assertEqual(decoded['strings'], texts)
        self.assertEqual(decoded['language'], 17)

    def test_crc_covers_header_and_all_packet_data(self):
        packet, _ = encode([list(b'abcabcabc')], [])
        for position in range(len(packet)):
            bad = bytearray(packet)
            bad[position] ^= 1
            with self.assertRaises((ValueError, UnicodeError)):
                decode(bytes(bad))

    def test_repaired_crc_does_not_allow_forward_dictionary_references(self):
        packet, _ = encode([[256]], [(97, 97)], name='X')
        bad = bytearray(packet)
        # First dictionary token becomes 256; token 256 cannot refer to itself.
        bad[HEADER.size+1:HEADER.size+3] = b'\x80\x02'
        with self.assertRaisesRegex(ValueError, 'dictionary reference'):
            decode(repair_crc(bad))

    def test_oversubscribed_codebook_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Oversubscribed'):
            canonical_codes([1, 1, 1])

    def test_expansion_and_utf8_limits(self):
        for text in [b'x'*2048, b'bad\0text', b'bad\xfftext']:
            packet, _ = encode([list(text)], [])
            with self.assertRaises((ValueError, UnicodeError)):
                decode(packet)


if __name__ == '__main__':
    unittest.main()
