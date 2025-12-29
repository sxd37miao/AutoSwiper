import uiautomator2 as u2
import time
import random
from configparser import ConfigParser
from random_functions import *
import os

def load_config():
    """加载配置文件"""
    cp = ConfigParser()
    cp.read('config.ini', encoding='utf-8')
    
    # 读取应用列表
    app_list_str = cp.get('apps', 'app_list')
    # 解析应用列表，移除引号和空格
    app_list = [app.strip().strip("'\"") for app in app_list_str.strip("[]").split(',')]
    
    # 读取模式配置
    normal_mode = cp.getboolean('modes', 'normal_mode')
    emulation_mode = cp.getboolean('modes', 'emulation_mode')
    fast_mode = cp.getboolean('modes', 'fast_mode')
    
    # 读取其他配置参数
    config = {
        'min_sleep_time': cp.getfloat('config', 'min_sleep_time'),
        'max_sleep_time': cp.getfloat('config', 'max_sleep_time'),
        'min_swipe_time': cp.getfloat('config', 'min_swipe_time'),
        'max_swipe_time': cp.getfloat('config', 'max_swipe_time'),
        'min_swipe_long': cp.getfloat('config', 'min_swipe_long'),
        'max_swipe_long': cp.getfloat('config', 'max_swipe_long'),
        'pause_probability': cp.getint('config', 'pause_probability'),
        'like_probability': cp.getint('config', 'like_probability'),
        'max_loop_count': cp.getint('config', 'max_loop_count')
    }
    
    return app_list, normal_mode, emulation_mode, fast_mode, config

def connect_device():
    """连接设备"""
    try:
        # 自动连接设备
        d = u2.connect()
        print("设备连接成功！")
        return d
    except Exception as e:
        print(f"设备连接失败: {e}")
        print("请确保:")
        print("1. 手机已通过USB连接到电脑")
        print("2. 手机已开启USB调试模式")
        print("3. 电脑已正确安装ADB工具")
        return None

def open_app(d, app_name):
    """根据应用名称打开应用，这里使用应用包名映射"""
    # 应用名称到包名的映射
    app_package_map = {
        '拼多多': 'com.xunmeng.pinduoduo',
        '抖音极速版': 'com.ss.android.ugc.aweme.lite',
        '今日头条极速版': 'com.ss.android.article.lite',
        '爱奇艺极速版': 'com.qiyi.video.lite'
    }
    
    if app_name in app_package_map:
        package_name = app_package_map[app_name]
        print(f"正在打开 {app_name} (包名: {package_name})...")
        d.app_start(package_name)
        time.sleep(5)  # 等待应用启动
        return True
    else:
        print(f"未找到应用 {app_name} 的包名")
        return False

def swipe_video(d, config):
    """滑动视频"""
    # 获取屏幕尺寸
    width, height = d.info['displayWidth'], d.info['displayHeight']
    
    # 计算滑动距离和时间
    swipe_distance = random_swipe_long(config['min_swipe_long'], config['max_swipe_long'])
    swipe_time = random_swipe_time(config['min_swipe_time'], config['max_swipe_time'])
    
    # 从屏幕中央偏下的位置开始滑动
    start_x = width * 0.5
    start_y = height * 0.8
    end_y = height * (0.8 - swipe_distance)
    
    # 执行滑动操作
    d.swipe(start_x, start_y, start_x, end_y, swipe_time)
    
    # 等待视频播放时间
    sleep_time = random_sleep_time(config['min_sleep_time'], config['max_sleep_time'])
    time.sleep(sleep_time)

def random_pause_video(d, config):
    """随机暂停视频"""
    if random_pause(config['pause_probability']):
        print("随机暂停视频...")
        # 点击屏幕中央暂停视频
        width, height = d.info['displayWidth'], d.info['displayHeight']
        d.click(width * 0.5, height * 0.5)
        time.sleep(random.uniform(1, 3))
        # 再次点击继续播放
        d.click(width * 0.5, height * 0.5)

def random_like_video(d, config):
    """随机点赞视频"""
    if random_like(config['like_probability']):
        print("随机点赞视频...")
        # 点击屏幕右侧点赞（具体位置可能需要根据实际应用调整）
        width, height = d.info['displayWidth'], d.info['displayHeight']
        d.click(width * 0.85, height * 0.2)

def enter_swipe_mode(d, app_name, config, normal_mode, emulation_mode, fast_mode):
    """进入滑动模式"""
    print(f"开始在 {app_name} 中刷视频...")
    loop_count = 0
    
    while loop_count < config['max_loop_count']:
        # 滑动到下一个视频
        swipe_video(d, config)
        
        # 根据模式决定是否执行额外操作
        if normal_mode:
            # 正常模式：偶尔暂停
            random_pause_video(d, config)
        elif emulation_mode:
            # 仿真模式：偶尔暂停并随机点赞
            random_pause_video(d, config)
            random_like_video(d, config)
        elif fast_mode:
            # 快速模式：不执行额外操作，仅滑动
            pass
        
        loop_count += 1
        print(f"已循环 {loop_count} 次，目标 {config['max_loop_count']} 次")
    
    print(f"{app_name} 达到最大循环次数，准备切换应用...")

def main():
    print("=== Auto Swiper 启动 ===")
    
    # 加载配置
    app_list, normal_mode, emulation_mode, fast_mode, config = load_config()
    
    print("支持的应用列表:", app_list)
    if normal_mode:
        mode = "正常模式"
    elif emulation_mode:
        mode = "仿真模式"
    elif fast_mode:
        mode = "快速模式"
    else:
        mode = "未知模式"
    print(f"当前模式: {mode}")
    
    # 连接设备
    d = connect_device()
    if not d:
        return
    
    # 显示功能选项
    print("\n请选择功能:")
    for i, app in enumerate(app_list, 1):
        print(f"{i}. {app}")
    print(f"{len(app_list)+1}. 配置管理")
    
    try:
        choice = int(input("请输入您要打开的软件编号: "))
        
        if 1 <= choice <= len(app_list):
            app_name = app_list[choice - 1]
            print(f"您选择了: {app_name}")
            
            # 打开选定的应用
            if open_app(d, app_name):
                print("应用已打开，开始自动刷视频...")
                
                # 进入滑动模式
                enter_swipe_mode(d, app_name, config, normal_mode, emulation_mode, fast_mode)
                
                # 循环结束后自动切换到其他应用
                remaining_apps = [app for app in app_list if app != app_name]
                # 根据README，不随机到拼多多（如果当前不是拼多多的话）
                if app_name != '拼多多' and '拼多多' in remaining_apps:
                    remaining_apps.remove('拼多多')
                
                if remaining_apps:
                    next_app = random.choice(remaining_apps)
                    print(f"切换到下一个应用: {next_app}")
                    
                    # 关闭当前应用
                    app_package_map = {
                        '拼多多': 'com.xunmeng.pinduoduo',
                        '抖音极速版': 'com.ss.android.ugc.aweme.lite',
                        '今日头条极速版': 'com.ss.android.article.lite',
                        '爱奇艺极速版': 'com.qiyi.video.lite'
                    }
                    d.app_stop(app_package_map.get(app_name, app_name))
                    
                    # 打开下一个应用
                    if open_app(d, next_app):
                        enter_swipe_mode(d, next_app, config, normal_mode, emulation_mode, fast_mode)
        elif choice == len(app_list) + 1:
            # 配置管理 - 这里简化处理，直接调用配置管理函数
            import subprocess
            subprocess.run(["python", "config_manager.py"])
        else:
            print("无效的选择！")
    
    except ValueError:
        print("请输入有效的数字！")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()