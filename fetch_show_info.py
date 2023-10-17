import yaml
import requests
from piaoxingqiu import Piaoxingqiu

class Fetch_Show_Info:
    def __init__(self) -> None:
        with open('requirement.yaml', 'r', encoding='utf-8') as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
        
        self.show_id = config['Show']['show_id']

        self.Piaoxingqiu = Piaoxingqiu()

    def fetch(self) -> dict:
        show_info = self.Piaoxingqiu.get_show(self.show_id)
        
        with open('show_info.yaml', 'w', encoding='utf-8') as show_info_file:
            yaml.dump(show_info, show_info_file)
        
        return show_info



if __name__ == "__main__":
    instance = Fetch_Show_Info()
    res = instance.fetch()
    print(res)