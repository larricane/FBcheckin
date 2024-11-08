import os
import time
import random
import requests
from datetime import datetime, timedelta


class siteCheckin:
    def __init__(self):
        self.base_url = 'https://flyingbird.pro'
        self.site_name = 'FlyingBird'  # 添加站点名称
        self.max_retries = 7
        self.delay_min = 1
        self.delay_max = 5
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 添加环境变量检查
        if not os.getenv('FB_USERNAME') or not os.getenv('FB_PASSWORD'):
            self.log("错误：FB_USERNAME 或 FB_PASSWORD 未设置")
            raise ValueError("必要的环境变量未设置")
        
    def log(self, message):
        """使用北京时间记录日志"""
        beijing_time = datetime.utcnow() + timedelta(hours=8)
        print(f"[{beijing_time}] {message}")
        
    def notify(self, title, message, checkin_info=None):
        """
        发送通知
        :param title: 通知标题
        :param message: 通知内容
        :param checkin_info: 签到返回的详细信息字典
        """
        if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
            try:
                # 调整为北京时间
                beijing_time = datetime.utcnow() + timedelta(hours=8)
                current_time = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
                
                text_message = (
                    f"{self.site_name} {title}\n\n"
                    f"站点: {self.base_url}\n"
                    f"时间: {current_time} (北京时间)\n"
                    f"状态: {message}\n"
                )
                
                # 如果有签到信息，添加主要信息
                if checkin_info and isinstance(checkin_info, dict):
                    if 'traffic' in checkin_info:
                        text_message += f"流量信息: {checkin_info['traffic']}\n"
                    if 'days' in checkin_info:
                        text_message += f"累计签到: {checkin_info['days']}天"
                
                response = requests.post(
                    f'https://api.telegram.org/bot{os.getenv("TELEGRAM_BOT_TOKEN")}/sendMessage',
                    data={
                        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
                        'text': text_message
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log("Telegram 通知发送成功")
                    return True
                else:
                    self.log(f"Telegram 通知发送失败: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                self.log(f"Telegram 通知异常: {str(e)}")
                return False
    
    def login(self):
        """登录"""
        login_url = f'{self.base_url}/auth/login'
        data = {
            'email': os.getenv('FB_USERNAME'),
            'passwd': os.getenv('FB_PASSWORD')
        }
        
        try:
            response = self.session.post(login_url, data=data)
            if response.json().get('ret') == 1:
                self.log("登录成功")
                return True
            else:
                self.log("登录失败")
                return False
        except Exception as e:
            self.log(f"登录异常: {str(e)}")
            return False
            
    def checkin(self):
        """签到"""
        checkin_url = f'{self.base_url}/user/checkin'
        
        # 随机延时
        time.sleep(random.uniform(1, 5))
        
        try:
            response = self.session.post(checkin_url)
            result = response.json()
            
            if response.status_code == 200:
                message = result.get('msg', '未知结果')
                # 提取更多信息
                checkin_info = {}
                if 'traffic' in result:
                    checkin_info['traffic'] = result['traffic']
                if 'days' in result:
                    checkin_info['days'] = result['days']
                    
                self.log(f"签到结果: {message}")
                self.notify('签到成功', message, checkin_info)
                return True
            else:
                self.log(f"签到失败: {result}")
                self.notify('签到失败', str(result))
                return False
                
        except Exception as e:
            self.log(f"签到异常: {str(e)}")
            self.notify('签到异常', str(e))
            return False
            
    def run(self):
        """运行主流程"""
        retry_count = 0
        
        while retry_count < self.max_retries:
            if self.login() and self.checkin():
                break
            
            retry_count += 1
            if retry_count < self.max_retries:
                self.log(f"第 {retry_count} 次重试")
                time.sleep(random.uniform(self.delay_min, self.delay_max))
            else:
                self.notify('签到失败', f'重试{self.max_retries}次后失败')

if __name__ == '__main__':
    checkin = siteCheckin()
    checkin.run()