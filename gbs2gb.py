#!/usr/bin/python

GBS2GB_FILE = 'gbsplay_104u.bin'
GBS_FILE = 'picross.gbs'

OUTPUT_FILE = 'picross.gb'

from io import BytesIO
import math

# load gbs2gb and gbs
with open(GBS2GB_FILE, 'rb') as base:
	gbs2gb = base.read()

with open(GBS_FILE, 'rb') as gbs_f:
	gbs = gbs_f.read()

# get load address
load_addr = int.from_bytes(gbs[6:8], byteorder='little')

# patch up the GBSPlay binary
gbs2gb = BytesIO(gbs2gb)

# rst vectors
gbs2gb.seek(0x01); gbs2gb.write((load_addr + 0x00).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x09); gbs2gb.write((load_addr + 0x08).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x11); gbs2gb.write((load_addr + 0x10).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x19); gbs2gb.write((load_addr + 0x18).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x21); gbs2gb.write((load_addr + 0x20).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x29); gbs2gb.write((load_addr + 0x28).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x31); gbs2gb.write((load_addr + 0x30).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x39); gbs2gb.write((load_addr + 0x38).to_bytes(2, byteorder='little'))

# gbs metadata
header = load_addr - 0x70
gbs2gb.seek(0x0C); gbs2gb.write((header + 0x10).to_bytes(2, byteorder='little')) # title (line 1)
gbs2gb.seek(0x14); gbs2gb.write((header + 0x20).to_bytes(2, byteorder='little')) # title (line 2)
gbs2gb.seek(0x1C); gbs2gb.write((header + 0x30).to_bytes(2, byteorder='little')) # author (line 1)
gbs2gb.seek(0x24); gbs2gb.write((header + 0x40).to_bytes(2, byteorder='little')) # author (line 2)
gbs2gb.seek(0x2C); gbs2gb.write((header + 0x50).to_bytes(2, byteorder='little')) # copyright (line 1)
gbs2gb.seek(0x34); gbs2gb.write((header + 0x60).to_bytes(2, byteorder='little')) # copyright (line 2)

# handlers of some sort
gbs2gb.seek(0x41); gbs2gb.write((load_addr + 0x40).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x51); gbs2gb.write((load_addr + 0x48).to_bytes(2, byteorder='little'))

# GB cart type
gbs2gb.seek(0x147); # 0 = ROM only, 1 = ROM + MBC1 (multiple banks)
 
# Complement
cp = 0
gbs2gb.seek(0x134)
for i in gbs2gb.read(0x19):
	cp = cp - i - 1
csb = ((0xffff - cp) % 256).to_bytes(1, byteorder='big')
gbs2gb.seek(0x14D); gbs2gb.write(csb) # put header checksum

# Checksum
# gbs2gb.seek(0x14E);

# patch some more stuff
num_songs = load_addr - 0x6c
first_song = load_addr - 0x6b
init = load_addr - 0x68
play = load_addr - 0x66
stack = load_addr - 0x64
tma = load_addr - 0x62
tac = load_addr - 0x61

gbs2gb.seek(0x157); gbs2gb.write((stack).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x178); gbs2gb.write((num_songs).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x181); gbs2gb.write((tac).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x190); gbs2gb.write((tac).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x19b); gbs2gb.write((tma).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x1af); gbs2gb.write((first_song).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x1c9); gbs2gb.write((tac).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x1e9); gbs2gb.write((play).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x208); gbs2gb.write((num_songs).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x217); gbs2gb.write((num_songs).to_bytes(2, byteorder='little'))
gbs2gb.seek(0x254); gbs2gb.write((init).to_bytes(2, byteorder='little'))

# append the gbs
with open(OUTPUT_FILE, 'wb') as out:
	# write patched gbs2gb
	gbs2gb.seek(0)
	out.write(gbs2gb.read())
	
	# pad it out with (LOAD - GBS2GB size - GBS header size)
	out.write(b'\xFF'*(load_addr - 0x400 - 0x70))
	
	# append the gbs
	out.write(gbs)
	
	# if our final size isn't a multiple of 0x4000, pad it out to the
	# nearest multiple
	if out.tell() % 0x4000:
		out.write(b'\xFF'*((0x4000 * math.ceil(out.tell() / 0x4000)) - out.tell()))

# done
