# Local imports
from Logic.DB_connection import make_connection
from Logic.Creater_image import Creater_image
from Logic.Executer import Executer
from Logic.Make_folder import make_folder

conn, cur = make_connection()

deltaDays = 0

make_folder(deltaDays, True)
make_folder(deltaDays)
Creater_im = Creater_image(cur, conn, Executer, deltaDays)
flag = Creater_im.Save_Full()

