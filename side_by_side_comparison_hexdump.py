#!/bin/env python3

"""
   simulate binary comparison of 2 very similar hexdumps side-by-side to compare
      <OFFSET>: <Col1> | <Col2>  <Col1_ascii> | <Col2_ascii>

   inspired by GeoHot:  https://www.youtube.com/watch?v=GXy5eVwnL_Q

   usage:
      ./side_by_side_comparison_hexdump.py
      ./side_by_side_comparison_hexdump.py a b # this should yield an error
      ./side_by_side_comparison_hexdump.py random_binary_data_1.dat random_binary_data_2.dat
"""
import random
random.seed(1)
import copy
from termcolor import colored
import sys
import os

format_1ByteHex = lambda val: f"{val:{0}{2}x}" # f"{val:{fill}{width}hex}"

def sample_data(N_bytes):
   dat = [format_1ByteHex(random.randint(0,255)) for i in range(N_bytes)]
   print(dat)
   return dat #' '.join(dat)

def make_similar_data(dat1):
   dat2 = copy.deepcopy(dat1)
   assert(len(dat2)==len(dat1))
   N_diffs = int(len(dat1)/10) # roughly 10% of overall length will be different
   diff_indices = random.sample(range(len(dat1)), N_diffs)
   diff_indices = sorted(diff_indices)
   #print(diff_indices)
   #print([(idx,dat1[idx]) for idx in diff_indices])
   diff_vals = [format_1ByteHex((int(dat1[idx],16)+random.randint(0,255))%255) for idx in diff_indices]
   for i, idx in enumerate(diff_indices):
      dat2[idx] = diff_vals[i]
   #print(diff_vals)
   print("indices: ", diff_indices)
   print("before:  ", [dat1[idx] for idx in diff_indices])
   print("after :  ", [dat2[idx] for idx in diff_indices])
   return dat2

def is_valid_hex_char(c):
   return ('0'<=c<='9') or ('a'<=c<='f') or ('A'<=c<='F')

def is_alphanumeric(c):
   return ('a'<=c<='z') or ('A'<=c<='Z') or ('0'<=c<='9')

def is_printable_ascii_char(c):
   # 0x20 == SPACE, but choose not to print ' ' but also '.', i.e. 0x20<ord(c)...
   return (0x20<ord(c)<=0x7e)

def chars_from_dat(dat1,dat2,i,N_bytes_per_row,last_row=False):
   chars1,chars2 = [],[]
   
   if last_row:
      z = zip(dat1[-i:],dat2[-i:])
   else:
      z = zip(dat1[i-N_bytes_per_row:i],dat2[i-N_bytes_per_row:i])
   
   pred = is_printable_ascii_char # is_printable_ascii_char, is_alphanumeric
   for s1,s2 in z:
      if s1 == s2:
         c = chr(int(s1,16)) # ord('a')==97, chr(97)=='a'
         if pred(c):
            chars1.append(c)
            chars2.append(c)
         else:
            chars1.append('.')
            chars2.append('.')
      else:
         c1 = chr(int(s1,16))
         c2 = chr(int(s2,16))
         if pred(c1):
            chars1.append(c1)
         else:
            chars1.append('.')
         if pred(c2):
            chars2.append(c2)
         else:
            chars2.append('.')
   return chars1,chars2

def mk_hexdump_compare(dat1, dat2):
   N_bytes_per_row = 8
   color = "yellow"
   dump = ""
   dump += f"{0:#{0}{8+2}x}: "
   right = ""
   #dump = []
   #dump.append(f"{0:#{0}{8+2}x}: ")
   #right = []

   for i,b in enumerate(dat1):
      if i%N_bytes_per_row==0 and i!=0:
         chars1,chars2 = chars_from_dat(dat1,dat2,i,N_bytes_per_row)
         dump += "| " + right #+ ' '.join([f"{b:{0}{'>'}{2}} "  ])
         dump += "  " + ''.join(chars1) + " | " + ''.join(chars2)
         dump += f"\n{i:#{0}{8+2}x}: "
         right = ""
         #dump.append("| " + ''.join(right))
         #dump.append(f"\n{i:#{0}{8+2}x}: ")
         #right = []
      if dat1[i]==dat2[i]:
         dump += f"{b:{0}{'>'}{2}} " #dump += f"{b:>2} "
         right += f"{dat2[i]:{0}{'>'}{2}} "
         #dump.append(f"{b:{0}{'>'}{2}} ")
         #right.append(f"{dat2[i]:{0}{'>'}{2}} ")
      else:
         dump += colored(f"{b:{0}{'>'}{2}} ", color)
         right += colored(f"{dat2[i]:{0}{'>'}{2}} ", color)
         #dump.append(colored(f"{b:{0}{'>'}{2}} ", color))
         #right.append(colored(f"{dat2[i]:{0}{'>'}{2}} ", color))
   
   # last line
   N_remaining_chars = len(dat1)%N_bytes_per_row
   print(f"N_remaining_chars: {N_remaining_chars} –– {[right]}")
   #N_bytes_last_line = len(right.split())
   N_pad = N_bytes_per_row - N_remaining_chars
   if N_remaining_chars:
      dump  += "   "*N_pad
      right += "   "*N_pad
      chars1,chars2 = chars_from_dat(dat1,dat2,N_remaining_chars,N_bytes_per_row,last_row=True)
      chars1  += ' '*N_pad
      chars2  += ' '*N_pad
   else:
      chars1,chars2 = chars_from_dat(dat1,dat2,len(dat1),N_bytes_per_row,last_row=False)
   dump += "| " + right
   dump += "  " + ''.join(chars1) + " | " + ''.join(chars2)
   #dump.append("| " + ''.join(right))
   
   col_width = dump.find('\n') # len(dump.splitlines()[0])
   #col_width = len(dump[0])
   print('—'*col_width)
   print(dump)
   #print(''.join(dump))
   print('—'*col_width)
   """dump = "—"*col_width + "\n" + dump + "\n" + "—"*col_width
   return dump"""

def make_similar_binary_files():
   fname_blob_1 = "random_binary_data_1.dat"
   fname_blob_2 = "random_binary_data_2.dat"
   N_bytes = 1020 #1024
   N_diffs = int(N_bytes/10) # roughly 10% of overall length will be different
   if (os.path.exists(fname_blob_1)):
      print(f"'{fname_blob_1}' already exists! Not creating it.")
   else:
      print(f"Creating '{fname_blob_1}' and '{fname_blob_2}'")
      rand_ints = [random.randint(0,255) for i in range(N_bytes)]
      ba1 = bytearray(rand_ints)
      ba2 = copy.deepcopy(ba1)
      diff_indices = random.sample(range(len(ba1)), N_diffs)
      diff_vals = [(ba1[idx]+random.randint(0,255))%255 for idx in diff_indices]
      for i, idx in enumerate(diff_indices):
         ba2[idx] = diff_vals[i]
      with open(fname_blob_1, "wb") as f1, open(fname_blob_2, "wb") as f2:
         f1.write(ba1)
         f2.write(ba2)

def tests():
   print("--- using simulated data ---")
   for offset in [-3,-2,-1,0,1,2,3]:
      print(f"offset = {offset}")
      dat1 = sample_data(N_bytes=128+offset)
      dat2 = make_similar_data(dat1)
      mk_hexdump_compare(dat1, dat2)

if __name__ == "__main__":
   # generate binary file
   make_similar_binary_files()
   # run tests
   #tests()

   print(f"sys.argv: {sys.argv}")
   if len(sys.argv)==1:
      # use simulated dataprint(sys.argv)
      print("--- using simulated data ---")
      dat1 = sample_data(N_bytes=128+0)
      dat2 = make_similar_data(dat1)
      mk_hexdump_compare(dat1, dat2)
   else:
      if len(sys.argv)!=3:
         print("ERROR: have to pass in exactly 2 files/blobs to compare")
         exit(-1)

      if (not os.path.exists(sys.argv[1]) or not os.path.exists(sys.argv[2])):
         print("One or both files don't exist!")
         exit(-1)

      print("--- using real binary data ---")
      print(f"opening the following files/blobs: '{sys.argv[1]}' and '{sys.argv[2]}'")
      with open(sys.argv[1], "rb") as f1, open(sys.argv[2], "rb") as f2:
         #f1_byte, f2_byte = f1.read(1), f2.read(1)
         ba1, ba2 = f1.read(), f2.read()
         dat1 = [f"{ba1[i]:x}" for i in range(len(ba1))]
         dat2 = [f"{ba2[i]:x}" for i in range(len(ba2))]
         mk_hexdump_compare(dat1, dat2)
