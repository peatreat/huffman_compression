from functools import reduce
from math import ceil

class HuffmanTree:
    def __init__(self, freq: int, key: chr):
        self.map = {}
        self.freq = freq
        self.val = key
        self.left = None
        self.right = None

    def combine(left_tree, right_tree):
        tree = HuffmanTree(left_tree.freq + right_tree.freq, None)
        tree.left = left_tree
        tree.right = right_tree
        return tree

    def generate_map(self, bits=""):
        if self.left == None and self.right == None:
            self.map[self.val] = bits
            return

        if self.left != None:
            self.left.generate_map(bits + "0")
            self.map = {**self.map, **self.left.map}

        if self.right != None:
            self.right.generate_map(bits + "1")
            self.map = {**self.map, **self.right.map}


def sorted_insert(array: [HuffmanTree], tree: HuffmanTree):
    left = 0
    right = len(array) - 1

    mid_i = 0
    found = False

    while left <= right:
        mid_i = int((left + right) / 2)

        if array[mid_i].freq == tree.freq:
            found = True
            break
        elif array[mid_i].freq < tree.freq:
            left += 1
        else:
            right -= 1

    array.insert(mid_i if left < len(array) else len(array), tree)


def create_huffman_tree(array: [HuffmanTree]):
    while len(array) > 1:
        trees = array[:2]
        new_tree = HuffmanTree.combine(trees[0], trees[1])
        array = array[2:]
        sorted_insert(array, new_tree)

    return array


def bits_to_bytes(bits: str) -> (bytearray, str):
    out = bytearray()

    def extract(out: bytearray, bits: str, bit_size: int):
        j = int(len(bits) / bit_size)
        byte_sz = int(bit_size / 8)

        if j > 0:
            for i in range(j):
                val = int("".join(bits[i * bit_size : i * bit_size + bit_size]), 2)
                out.extend(val.to_bytes(byte_sz, "little"))

            bits = bits[j * bit_size :]

        return bits

    bits = extract(out, bits, 64)
    bits = extract(out, bits, 32)
    bits = extract(out, bits, 16)
    bits = extract(out, bits, 8)

    return (out, bits)

def get_bits_required(n: int, freqs, huffman_map) -> int:
    ratio = 0
    
    for k,v in huffman_map.items():
        ratio += (freqs[k] / n) * len(v)
        
    return ceil(n * ratio)

def get_total_bits_for_window(content, window_sz) -> int:
    freq_map = {}

    for i in range(0, len(content), window_sz):
        b = int.from_bytes(content[i:i+window_sz], "little")
        
        if b in freq_map:
            freq_map[b] += 1
        else:
            freq_map[b] = 1
            
    huffman_tree = create_huffman_tree([
            HuffmanTree(v, k)
            for k, v in sorted(freq_map.items(), key=lambda item: item[1])
    ])[0]
    
    huffman_tree.generate_map()
    
    return get_bits_required(int(ceil(len(content) / window_sz)), freq_map, huffman_tree.map)

def encode(filename) -> bytearray:
    compressed = bytearray()
    
    with open(filename, "rb") as file:
        content = file.read()
        freq_map = {}

        for b in content:
            if b in freq_map:
                freq_map[b] += 1
            else:
                freq_map[b] = 1
        
        freq_map = [
            HuffmanTree(v, k)
            for k, v in sorted(freq_map.items(), key=lambda item: item[1])
        ]

        huffman_tree = create_huffman_tree(freq_map)[0]
        huffman_tree.generate_map()

        remainder = ""

        for b in content:
            ba, extra = bits_to_bytes(remainder + huffman_tree.map[b])
            compressed.extend(ba)
            remainder = extra
        
        if len(remainder) > 0:
            remainder += "0" * (8 - len(remainder))
            compressed.extend(int(remainder, 2).to_bytes(1, "little"))
            
    return compressed


compressed = encode("input.bin")

with open("compressed.bin", "wb") as output:
    output.write(compressed)
