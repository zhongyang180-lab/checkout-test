import pytest
import requests
import time
from threading import Thread
from checkout_service import app

class TestCheckoutSystem:
    """Checkout微服务系统测试类 - 精简版"""
    
    BASE_URL = "http://localhost:5000"
    
    @classmethod
    # 测试前准备
    def setup_class(cls):
        """启动测试服务器"""
        cls.server_thread = Thread(target=app.run, kwargs={
            'debug': False, 
            'host': '0.0.0.0', 
            'port': 5000,
            'use_reloader': False
        })
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)  # 等待服务器启动
    # 测试正常购物车结算
    def test_normal_checkout(self):
        """测试1: 正常购物车结算"""
        payload = {
            "items": [
                {"name": "商品A", "price": 100, "quantity": 2},
                {"name": "商品B", "price": 50, "quantity": 3}
            ]
        }
        
        response = requests.post(f"{self.BASE_URL}/checkout", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["total"] == 100*2 + 50*3  # 350
    # 测试空购物车错误处理
    def test_empty_cart(self):
        """测试2: 空购物车错误处理"""
        payload = {"items": []}
        
        response = requests.post(f"{self.BASE_URL}/checkout", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "empty cart"
    # 测试缺少items字段错误处理
    def test_missing_items_field(self):
        """测试3: 缺少items字段"""
        payload = {"other_field": "value"}
        
        response = requests.post(f"{self.BASE_URL}/checkout", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    # 测试小数价格计算
    def test_decimal_prices(self):
        """测试4: 小数价格计算"""
        payload = {
            "items": [
                {"name": "商品A", "price": 19.99, "quantity": 2},
                {"name": "商品B", "price": 7.50, "quantity": 1}
            ]
        }
        
        response = requests.post(f"{self.BASE_URL}/checkout", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        expected_total = 19.99*2 + 7.50*1
        assert abs(data["total"] - expected_total) < 0.01
    # 测试零价格商品处理
    def test_zero_price(self):
        """测试5: 零价格商品处理"""
        payload = {
            "items": [
                {"name": "免费商品", "price": 0, "quantity": 5}
            ]
        }
        
        response = requests.post(f"{self.BASE_URL}/checkout", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

if __name__ == "__main__":
    # 启动服务器
    server_thread = Thread(target=app.run, kwargs={
        'debug': False, 
        'host': '0.0.0.0', 
        'port': 5000,
        'use_reloader': False
    })
    server_thread.daemon = True
    server_thread.start()
    time.sleep(2)
    
    # 运行测试
    pytest.main([__file__, "-v"])