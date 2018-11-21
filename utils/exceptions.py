class PricePolicyNotExist(Exception):
    def __int__(self, msg):
        self.msg = msg
