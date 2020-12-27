#
# Preprocessing and verification before training
#

from pathlib import Path
from  processgti.herbariumgtiv import *

# Directory containing the original set of segmented images
source_dir = Path(Path().absolute().parent, "herbariumsheets","notUsedTHS")
# Directory containing the segments (rezised to 96DPI)
finished_dir = Path(Path().absolute().parent, "herbariumsheets","notUsedTHS", "modified")

visual_inspect_segments(source_dir, source_dir, finished_dir)
