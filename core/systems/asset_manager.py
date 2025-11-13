"""
资产管理系统
"""

class AssetManager:
    def __init__(self):
        self.assets = {
            'cash': 80000,
            'investments': [],
            'properties': [],
            'businesses': []
        }
    
    def get_total_assets(self):
        """计算总资产"""
        total = self.assets['cash']
        
        for inv in self.assets['investments']:
            total += inv['current_value']
        
        for prop in self.assets['properties']:
            total += prop['value']
        
        for biz in self.assets['businesses']:
            total += biz['value']
        
        return total
    
    def can_afford(self, amount):
        """检查是否有足够现金"""
        return self.assets['cash'] >= amount
    
    def deduct_cash(self, amount):
        """扣除现金"""
        if self.can_afford(amount):
            self.assets['cash'] -= amount
            return True
        return False
    
    def add_investment(self, name, amount, term, expected_return):
        """添加投资"""
        investment = {
            'name': name,
            'amount': amount,
            'current_value': amount,
            'term': term,
            'expected_return': expected_return,
            'months_held': 0
        }
        self.assets['investments'].append(investment)
        return investment
    
    def add_property(self, name, price, monthly_rent):
        """添加房产"""
        property_item = {
            'name': name,
            'value': price,
            'monthly_rent': monthly_rent
        }
        self.assets['properties'].append(property_item)
        return property_item
    
    def add_business(self, name, investment, monthly_income):
        """添加生意"""
        business = {
            'name': name,
            'value': investment,
            'monthly_income': monthly_income
        }
        self.assets['businesses'].append(business)
        return business
    
    def update_monthly(self):
        """每月更新资产"""
        # 投资收益
        for inv in self.assets['investments']:
            inv['months_held'] += 1
            monthly_return = inv['amount'] * inv['expected_return'] / 12
            inv['current_value'] += monthly_return
        
        # 房租收入
        for prop in self.assets['properties']:
            self.assets['cash'] += prop['monthly_rent']
        
        # 生意收入
        for biz in self.assets['businesses']:
            self.assets['cash'] += biz['monthly_income']
    
    def get_monthly_income(self):
        """计算月收入"""
        income = 0
        
        for inv in self.assets['investments']:
            income += inv['amount'] * inv['expected_return'] / 12
        
        for prop in self.assets['properties']:
            income += prop['monthly_rent']
        
        for biz in self.assets['businesses']:
            income += biz['monthly_income']
        
        return income
