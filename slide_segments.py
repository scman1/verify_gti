#
# Preprocessing and verification before training
#

from pathlib import Path
from  processgti.microscopygtiv import *

# Directory containing the original set of segmented images
source_dir = Path(Path().absolute().parent, "slides","sample05c","renamed")
# Directory containing the segments (rezised to 96DPI)
finished_dir = Path(Path().absolute().parent, "slides","sample05c", "gt_segments")

extract_segments_from_files(finished_dir, source_dir)
 
