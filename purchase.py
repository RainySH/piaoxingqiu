import yaml
from piaoxingqiu import Piaoxingqiu

class Purchase:
    def __init__(self) -> None:
        """Initialize Piaoxingqiu module and load requirement from requirement.yaml.
        """
        ## Initialize Piaoxingqiu #############################################
        self.Piaoxingqiu = Piaoxingqiu()
        #######################################################################

        ## Load Requirement Info ##############################################
        with open('requirement.yaml', 'r', encoding='utf-8') as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)

        # Performance info
        self.show = {
            'show_id' : config['Show']['show_id'],
            'session_id' : config['Show']['session_id'],
            'session_id_exclude' : [],
            'seat_plan_id' : config['Show']['seat_plan_id'],
            'price' : 0
        }
        # Bill info
        self.bill = {
            'buy_count' : config['Bill']['buy_count'],
            'deliver_method' : config['Bill']['deliver_method']
        }
        # Audience info
        self.audiences = [audience for audience in config['Audience']]
        #######################################################################
    
    def pre_purchase(self, token) -> None:
        """Load neccessary info and initialize audiences before purchase.
        """
        ## Initilize and Load Audiences ################################################
        # Initialize audiences
        self.Piaoxingqiu.initialize_audience(token, self.audiences)

        # Load audiences
        self.audiences = self.Piaoxingqiu.get_audiences(token)
        if self.bill['buy_count'] > len(self.audiences):
            raise Exception("购票数量大于观演人数量，请检查配置文件")
        self.bill['audience_ids'] = [audience["id"] for audience in self.audiences]
        #######################################################################

        ## Load Seat Info ####################################################
        # Load seat plan if session_id is specified
        if self.show['session_id']:
            self.seat_plans = self.Piaoxingqiu.get_seat_plans(self.show['show_id'], self.show['session_id'])

        # Load seat price is seat_plan_id is specified
        if self.show['seat_plan_id']:
            for seat in self.seat_plans:
                if seat["seatPlanId"] == self.show['seat_plan_id']:
                    self.show['price'] = seat["originalPrice"]
                    break
        #######################################################################     

    def purchase(self, token) -> bool:
        """Purchase ticket.
        """
        ## Select Available Session ####################################################
        # Select available session if session_id is not specified
        if not self.show['session_id']:
            while True:
                sessions = self.Piaoxingqiu.get_sessions(self.show['show_id'])
                if sessions:
                    for session_candidate in sessions:
                        if session_candidate["sessionStatus"] == 'ON_SALE' and session_candidate["bizShowSessionId"] not in self.show['session_id_exclude']:
                            self.show['session_id'] = session_candidate["bizShowSessionId"]
                            print("session_id:" + self.show['session_id'])
                            break
                    if self.show['session_id']:
                        break
                    else:
                        print("未获取到在售状态且符合购票数量需求的session")
                        self.show['session_id_exclude'] = []  # Reset session_id_exclude to null for another chance
        #######################################################################

        ## Select Available Seat ##############################################
        # Select available seat if seat_plan_id is not specified
        if not self.show['seat_plan_id']:
            while True:
                self.seat_plans = self.Piaoxingqiu.get_seat_plans(self.show['show_id'], self.show['session_id'])
                self.seat_count = self.Piaoxingqiu.get_seat_count(self.show['show_id'], self.show['session_id'])

                for seat_candidate in self.seat_count:
                    if seat_candidate["canBuyCount"] >= self.bill['buy_count']:
                        self.show['seat_plan_id'] = seat_candidate["seatPlanId"]
                        for seat in self.seat_plans:
                            if seat["seatPlanId"] == self.show['seat_plan_id']:
                                self.show['price'] = seat["originalPrice"]  # Seat price
                                break
                        break
                
                if self.show['seat_plan_id']:
                    print("seat_id:" + self.show['seat_plan_id'])
                    break
                else:
                    print("未获取到在售状态且符合购票数量需求的seat")
        #######################################################################

        ## Load Deliver Method ################################################
        # Load deliver method if not specified
        if not self.bill['deliver_method']:
            self.bill['deliver_method'] = self.Piaoxingqiu.get_deliver_method(token, self.show['show_id'], self.show['session_id'], self.show['seat_plan_id'], self.show['price'], self.bill['buy_count'])
            print("deliver_method:" + self.bill['deliver_method'])
        #######################################################################

        ## Create Order #######################################################
        # Deliver method : VENUE_E
        if self.bill['deliver_method'] == "VENUE_E":
            order_status = self.Piaoxingqiu.create_order(token, self.show['show_id'], self.show['session_id'], self.show['seat_plan_id'], self.show['price'], self.bill['buy_count'], self.bill['deliver_method'], 0, None,
                         None, None, None, None, [])
        else:
            # Deliver method : EXPRESS
            if self.bill['deliver_method'] == "EXPRESS":
                # Load address
                address = self.Piaoxingqiu.get_address(token)
                address_id = address["addressId"] 
                location_city_id = address["locationId"] 
                receiver = address["username"]  
                cellphone = address["cellphone"] 
                detail_address = address["detailAddress"]

                # Load express fee
                express_fee = self.Piaoxingqiu.get_express_fee(token, self.show['show_id'], self.show['session_id'], self.show['seat_plan_id'], self.show['price'], self.bill['buy_count'],
                                                            location_city_id)

                # Create order
                order_status = self.Piaoxingqiu.create_order(token, self.show['show_id'], self.show['session_id'], self.show['seat_plan_id'], self.show['price'], self.bill['buy_count'], self.bill['deliver_method'],
                                    express_fee["priceItemVal"], receiver,
                                    cellphone, address_id, detail_address, location_city_id, self.bill['audience_ids'])
            elif self.bill['deliver_method'] in ["E_TICKET", "ID_CARD", "VENUE"]:
                order_status = self.Piaoxingqiu.create_order(token, self.show['show_id'], self.show['session_id'], self.show['seat_plan_id'], self.show['price'], self.bill['buy_count'], self.bill['deliver_method'], 0, None,
                                    None, None, None, None, self.bill['audience_ids'])
            else:
                print("不支持的deliver_method：" + self.bill['deliver_method'])
                order_status = False
        #######################################################################
        
        return order_status
    

if __name__ == '__main__':
    with open('account.yaml', 'r', encoding='utf-8') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    
    accounts = [{'token': account['token']} for account in config['Account']]
    
    instance = Purchase()
    
    instance.pre_purchase(accounts[0]['token'])

    while True:
        try:
            if instance.purchase(accounts[0]['token']):
                break
        except Exception as e:
            print(e)
            break
