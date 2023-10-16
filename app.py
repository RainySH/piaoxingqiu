import config
from piaoxingqiu import Piaoxingqiu

res = Piaoxingqiu.get_sessions(config.show_id)

print(res)