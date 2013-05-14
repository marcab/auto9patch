#!/usr/bin/env python

from PIL import Image

_BLACK = (0, 0, 0, 255)

def auto9patch(inpath, outpath):

  # image data
  im = Image.open(inpath)
  pix = im.load();
  width, height = im.size

  # Find duplicate columns
  col_seq_start = None
  max_col_seq_start = None
  max_col_seq_end = None
  for x in range(1, width):
    for y in range(1, height):
      if pix[x-1,y] != pix[x,y]:
        if col_seq_start != None:
          if (max_col_seq_start == None) or (
              (max_col_seq_end - max_col_seq_start) <
              (x+1 - col_seq_start)):
            max_col_seq_start = col_seq_start
            max_col_seq_end = x+1
          col_seq_start = None
        break
    else:
      if col_seq_start is None:
        col_seq_start = x

  # Make the narrow image
  end_length = width - max_col_seq_end
  tmp_copy = im.crop((0, 0, max_col_seq_start + end_length, height))
  tmp_pix = tmp_copy.load()
  for y in range(0, height):
    for i in range(0, end_length):
      tmp_pix[max_col_seq_start + i, y] = pix[max_col_seq_end + i, y]

  # Refresh image info
  im = tmp_copy
  pix = im.load();
  width, height = im.size

  # Find duplicate rows
  row_seq_start = None
  max_row_seq_start = None
  max_row_seq_end = None
  for y in range(1, height):
    for x in range(1, width):
      if pix[x,y-1] != pix[x,y]:
        if row_seq_start != None:
          if (max_row_seq_start == None) or (
              (max_row_seq_end - max_row_seq_start) <
              (y+1 - row_seq_start)):
            max_row_seq_start = row_seq_start
            max_row_seq_end = y+1
          row_seq_start = None
        break
    else:
      if row_seq_start is None:
        row_seq_start = y

  # Create minimal image
  end_length = height - max_row_seq_end
  tmp_copy = im.crop((0, 0, width, max_row_seq_start + end_length))
  tmp_pix = tmp_copy.load()
  for x in range(0, width):
    for i in range(0, end_length):
      tmp_pix[x, max_row_seq_start + i] = pix[x, max_row_seq_end + i]

  # Refresh image info
  im = tmp_copy
  pix = im.load();
  width, height = im.size

  # Crawl for content top
  content_top = max_row_seq_start-1
  try:
    while pix[max_col_seq_start-1, content_top-1][3] == 255:
      content_top-=1
  except IndexError:
    pass

  # Crawl for content bottom
  content_bottom = max_row_seq_start-1
  try:
    while pix[max_col_seq_start-1, content_bottom+1][3] == 255:
      content_bottom+=1
  except IndexError:
    pass
  
  # Crawl for content left
  content_left = max_col_seq_start-1
  try:
    while pix[content_left-1, max_row_seq_start-1][3] == 255:
      content_left-=1
  except IndexError:
    pass

  # Crawl for content right
  content_right = max_col_seq_start-1
  try:
    while pix[content_right+1, max_row_seq_start-1][3] == 255:
      content_right+=1
  except IndexError:
    pass

  # Create nine-patch
  final_im = Image.new('RGBA', (width + 2, height + 2), (0, 0, 0, 0))
  final_pix = final_im.load()

  # Draw patches 
  final_pix[max_col_seq_start, 0] = _BLACK
  final_pix[0, max_row_seq_start] = _BLACK
  for x in range(0, width):
    for y in range(0, height):
      final_pix[x+1, y+1] = pix[x, y]

  # Get final image dimensions
  width, height = final_im.size

  # Draw horizontal content
  for x in range(content_left+1, content_right+2):
    final_pix[x, height-1] = _BLACK
    
  # Draw vertical content
  for y in range(content_top+1, content_bottom+2):
    final_pix[width-1, y] = _BLACK
  
  final_im.save(outpath)

if __name__ == "__main__":

  import sys
  import os

  if len(sys.argv) < 2:
    sys.stderr.write("Usage: %s [png_paths...]\n" % sys.argv[0])
    sys.exit(1)
  
  for inpath in sys.argv[1:]:
    base, extension = os.path.splitext(inpath)
    if extension != ".png":
      sys.stderr.write("Error: %s does not have png extension." % inpath)
      sys.exit(1)
    outpath = base + ".9.png"
    print "Making %s..." % outpath,
    auto9patch(inpath, outpath)
    print " done!"
