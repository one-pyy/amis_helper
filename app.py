from amisHelper import startAmis
import fastapi as f
from typing import *

app=f.FastAPI()
startAmis(app,"/amis/set")
