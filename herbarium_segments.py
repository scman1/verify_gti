#
# Preprocessing and verification before training
#

from pathlib import Path
from  processgti.herbariumgtiv import *

# Directory containing the original set of segmented images
source_dir = Path(Path().absolute().parent, "herbariumsheets","sample05b")
# Directory containing the segments (rezised to 96DPI)
finished_dir = Path(Path().absolute().parent, "herbariumsheets","sample05b", "finalpass")

extract_segments_from_files(finished_dir, source_dir)
