import config
from piaoxingqiu import Piaoxingqiu

class Purchase:
    def __init__(self) -> None:
        self.account = {'token': config.token}
        self.requirement = {
            'show_id' : config.show_id,
            'session_id' : config.session_id,
            'buy_count' : config.buy_count,
            'audience_idx' : config.audience_idx,
            'deliver_method' : config.deliver_method,
            'seat_plan_id' : config.seat_plan_id,
            'price' : 0
        }

    def pre_purchase(self) -> None:
        # 获取观演人信息
        audiences = Piaoxingqiu.get_audiences(self.account['token'])
        if len(self.requirement['audience_idx']) == 0:
            self.requirement['audience_idx'] = range(self.requirement['buy_count'])
        self.requirement['audience_ids'] = [audiences[i]["id"] for i in self.requirement['audience_idx']]
        
        # 获取座位信息
        self.seat_plans = Piaoxingqiu.get_seat_plans(self.requirement['show_id'], self.requirement['session_id'])
        print(self.seat_plans)

        if self.requirement['seat_plan_id']:
            for seat in self.seat_plans:
                if seat["seatPlanId"] == self.requirement['seat_plan_id']:
                    self.requirement['price'] = seat["originalPrice"]
                    break       

    def purchase_without_seat(self) -> None:
        while True:
            try:
                seat_count = Piaoxingqiu.get_seat_count(self.requirement['show_id'], self.requirement['session_id'])

                for seat_candidate in seat_count:
                    if seat_candidate["canBuyCount"] >= self.requirement['buy_count']:
                        self.requirement['seat_plan_id'] = seat_candidate["seatPlanId"]
                        for seat in self.seat_plans:
                            if seat["seatPlanId"] == self.requirement['seat_plan_id']:
                                self.requirement['price'] = seat["originalPrice"]  # 门票单价
                                break
                        break
                
                if not self.requirement['deliver_method']:
                    self.requirement['deliver_method'] = Piaoxingqiu.get_deliver_method(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'])
                    print("deliver_method:" + self.requirement['deliver_method'])

                if self.requirement['deliver_method'] == "VENUE_E":
                    Piaoxingqiu.create_order(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'], self.requirement['deliver_method'], 0, None,
                                 None, None, None, None, [])
                else:
                    if self.requirement['deliver_method'] == "EXPRESS":
                        # 获取默认收货地址
                        address = Piaoxingqiu.get_address(self.account['token'])
                        address_id = address["addressId"]  # 地址id
                        location_city_id = address["locationId"]  # 460102
                        receiver = address["username"]  # 收件人
                        cellphone = address["cellphone"]  # 电话
                        detail_address = address["detailAddress"]  # 详细地址

                        # 获取快递费用
                        express_fee = Piaoxingqiu.get_express_fee(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'],
                                                            location_city_id)

                        # 下单
                        Piaoxingqiu.create_order(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'], self.requirement['deliver_method'],
                                            express_fee["priceItemVal"], receiver,
                                            cellphone, address_id, detail_address, location_city_id, self.requirement['audience_ids'])
                    elif self.requirement['deliver_method'] in ["E_TICKET", "ID_CARD", "VENUE"]:
                        Piaoxingqiu.create_order(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'], self.requirement['deliver_method'], 0, None,
                                            None, None, None, None, self.requirement['audience_ids'])
                    else:
                        print("不支持的deliver_method:" + self.requirement['deliver_method'])
                    
                    break

            except Exception as e:
                print(e)
    
    def purchase_with_seat(self) -> None:
        while True:
            try:
                if self.requirement['deliver_method'] == "VENUE_E":
                    Piaoxingqiu.create_order(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'], self.requirement['deliver_method'], 0, None,
                                 None, None, None, None, [])
                else:
                    if self.requirement['deliver_method'] == "EXPRESS":
                        # 获取默认收货地址
                        address = Piaoxingqiu.get_address(self.account['token'])
                        address_id = address["addressId"]  # 地址id
                        location_city_id = address["locationId"]  # 460102
                        receiver = address["username"]  # 收件人
                        cellphone = address["cellphone"]  # 电话
                        detail_address = address["detailAddress"]  # 详细地址

                        # 获取快递费用
                        express_fee = Piaoxingqiu.get_express_fee(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'],
                                                            location_city_id)

                        # 下单
                        Piaoxingqiu.create_order(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'], self.requirement['deliver_method'],
                                            express_fee["priceItemVal"], receiver,
                                            cellphone, address_id, detail_address, location_city_id, self.requirement['audience_ids'])
                    elif self.requirement['deliver_method'] in ["E_TICKET", "ID_CARD", "VENUE"]:
                        Piaoxingqiu.create_order(self.account['token'], self.requirement['show_id'], self.requirement['session_id'], self.requirement['seat_plan_id'], self.requirement['price'], self.requirement['buy_count'], self.requirement['deliver_method'], 0, None,
                                            None, None, None, None, self.requirement['audience_ids'])
                    else:
                        print("不支持的deliver_method:" + self.requirement['deliver_method'])
                    
                    break

            except Exception as e:
                print(e)

if __name__ == '__main__':
    instance = Purchase()
    instance.pre_purchase()
    instance.purchase_with_seat()
