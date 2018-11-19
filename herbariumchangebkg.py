#
# Change Background on Instances
#

from pathlib import Path
from  processgti.herbariumgtiv import *

print("Recolour Instance Backgrounds")
size96_dir = Path(Path().absolute().parent, "herbariumsheets","sample05", "finalpass")
lightbkg_dir = Path(Path().absolute().parent, "herbariumsheets","sample05", "lightbkg")
change_instance_bkg(size96_dir, lightbkg_dir)
