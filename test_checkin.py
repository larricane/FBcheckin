import os
from dotenv import load_dotenv
import unittest
from checkin import siteCheckin
from unittest.mock import patch

class TestCheckin(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 加载.env文件
        load_dotenv()
        self.checker = siteCheckin()
        
        # 验证环境变量
        if not os.getenv('FB_USERNAME') or not os.getenv('FB_PASSWORD'):
            self.skipTest("未在.env中设置登录凭据")
    
    def test_login(self):
        """测试登录功能"""
        print("\n测试登录功能...")
        result = self.checker.login()
        self.log_result("登录测试", result)
        
    def test_checkin(self):
        """测试签到功能"""
        print("\n测试签到功能...")
        # 先登录
        self.checker.login()
        result = self.checker.checkin()
        self.log_result("签到测试", result)
        
    def test_retry_mechanism(self):
        """测试重试机制"""
        print("\n测试重试机制...")
        # 故意使用错误的URL测试重试
        self.checker.base_url = "https://invalid-url.com"
        self.checker.max_retries = 3  # 减少重试次数加快试
        self.checker.run()
        
    def test_notification(self):
        """测试通知功能"""
        print("\n测试通知功能...")
        
        if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
            print("测试 Telegram 通知...")
            try:
                result = self.checker.notify(
                    "Telegram测试", 
                    "这是一条Telegram测试消息"
                )
                self.log_result("Telegram通知测试", result)
            except Exception as e:
                print(f"Telegram通知测试异常: {str(e)}")
                raise
            
    def test_notification_mock(self):
        """使用mock测试通知功能"""
        print("\n使用mock测试通知功能...")
        with patch('requests.post') as mock_post:
            # 模拟成功响应
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"ok": True}
            
            result = self.checker.notify("测试标题", "测试消息")
            self.assertTrue(result)
            self.log_result("Mock通知测试", result)
    
    def log_result(self, test_name, result):
        """输出测试结果"""
        status = "成功" if result else "失败"
        print(f"{test_name}: {status}")
        
    @patch('requests.Session.post')
    def test_mock_login(self, mock_post):
        """使用mock测试登录功能"""
        print("\n使用mock测试登录...")
        # 模拟登录成功的响应
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"ret": 1}
        
        result = self.checker.login()
        self.assertTrue(result)
        self.log_result("Mock登录测试", result)

def main():
    """主测试函数"""
    print("开始测试签到脚本...")
    print("=" * 50)
    
    # 检查环境变量
    required_vars = ['FB_USERNAME', 'FB_PASSWORD']
    optional_vars = ['PUSH_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    
    print("检查环境变量配置:")
    for var in required_vars:
        status = "✓" if os.getenv(var) else "✗"
        print(f"  {var}: {status}")
    
    print("\n可选配置:")
    for var in optional_vars:
        status = "✓" if os.getenv(var) else "-"
        print(f"  {var}: {status}")
    
    print("\n运行单元测试...")
    unittest.main(argv=[''], verbosity=2)

if __name__ == '__main__':
    main() 