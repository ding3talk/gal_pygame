import pygame#引入游戏引擎
import sys#引入系统库
import os#引入系统库
import math#引入数学库
import time#引入时间库
import shutil#引入文件库
import _thread#引入多线程
import cv2#引入图片处理库
import traceback#引入错误处理库
from PIL import Image, ImageFilter#引入图片处理库
from pygame.locals import *#引入pygame顶级函数
import win32gui, win32ui, win32con, win32api#引入windowsapi

try:#捕捉所有错误（如果被弹出）
    class ImageButtonAni:#图片按钮动画
        global time_passed, mouse_rect
        def __init__(self, Surface_list, button_xy):
            self.Surface_list = Surface_list
            self.button_xy = button_xy
            self.frame = len(Surface_list) - 1
            self.button = Surface_list[0]
            self.collide_button = False
            self.button_time_all = 0
            self.collide_warring = False
            self.button_rect = pygame.Rect(
                self.button_xy, (self.button.get_width(), self.button.get_height()))#创建按钮判定矩形

        def button_ani(self, time, type_mouse_xy):
            self.button_rect = pygame.Rect(
                self.button_xy, (self.button.get_width(), self.button.get_height()))#创建新的按钮判定矩形

            self.button_time_all += time_passed#加上上一帧所用的时间，得到总绘制时间
            self.spend = self.frame / time

            if self.button_time_all >= time:#判定绘制时间是否超时
                self.button_time_all = 0
                self.collide_button = True
                #超时则归零，并声明明绘制完成

            if self.button_rect.colliderect(mouse_rect) and not self.collide_button:
                #判定鼠标是否接触按钮并还未绘制按钮动画
                self.button = self.Surface_list[math.floor(self.button_time_all * self.spend)]#根据时间引入按钮动画的不同帧
                return self.button

            if self.button_rect.colliderect(mouse_rect) and self.collide_button:
                #判定鼠标是否接触按钮并还已绘制按钮动画（停留）
                self.button = self.Surface_list[self.frame]#保持最后一帧
                return self.button

            if not self.button_rect.colliderect(mouse_rect) and not self.collide_button:
                # 判定鼠标是否未接触按钮并还未绘制按钮动画（未接触）
                self.button_time_all = 0#时间退回
                self.collide_button = False#声明状态退回
                self.button = self.Surface_list[0]#回到第一帧
                return self.button

            if not self.button_rect.colliderect(mouse_rect) and self.collide_button:
                #判定鼠标是否未接触按钮并还已绘制按钮动画（离开）
                self.button_time_all = 0#时间退回
                self.collide_button = False#声明状态退回
                self.button = self.Surface_list[0]#复原退出按钮
                return self.button

        def get_button_collide(self, type_mouse_xy):
            if self.button_rect.collidepoint(type_mouse_xy):#判定鼠标是否点击按钮
                print('nb')
                return True#声明开始绘制提示

    class WordButtonAni:#文字按钮动画
        global time_passed, mouse_rect

        def __init__(self, word, re_word, button_xy):
            self.word = word
            self.re_word = re_word
            self.button_xy = button_xy
            self.button_time_all = 0
            self.collide_button = False

        def button_ani(self, time):
            self.button_rect = pygame.Rect(
                self.button_xy, (self.word.get_width(), self.word.get_height()))#创建按钮判定矩形

            self.button_time_all += time_passed#加上上一帧所用的时间，得到总绘制时间
            self.spend = self.button_rect.width / time#V=s/t

            if self.button_time_all >= time:#判定绘制时间是否超时
                self.button_time_all = 0
                self.collide_button = True#超时则归零，并声明明绘制完成

            if self.button_rect.colliderect(mouse_rect) and not self.collide_button:
                #判定鼠标是否接触退出按钮并还未绘制退出按钮动画
                self.word_cut = self.re_word.subsurface((0, 0, self.button_time_all * self.spend, self.button_rect.height))
                #逐次截取文字
                return self.word_cut#返回绘制对象

            if self.button_rect.colliderect(mouse_rect) and self.collide_button:
                #判定鼠标是否接触退出按钮并还已绘制退出按钮动画（停留）
                return self.re_word#返回停留文字

            if not self.button_rect.colliderect(mouse_rect) and not self.collide_button:
                #判定鼠标是否未接触退出按钮并还未绘制退出按钮动画（未接触）
                self.button_time_all = 0
                self.collide_button = False#声明状态退回
                return self.word#退回原文字

            if not self.button_rect.colliderect(mouse_rect) and self.collide_button:
                #判定鼠标是否未接触退出按钮并还已绘制退出按钮动画（离开）
                self.button_time_all = 0
                self.collide_button = False#声明状态退回
                return self.word#退回原文字

    class DrawCenter:#定义在屏幕中间绘制的类
        def draw_rect(self, Surface, color, size, width = 0, horn = 90):
            global w_face, h_face#声明全局变量
            rect_xy = ((w_face - size[0]) // 2, (h_face - size[1]) // 2)#根据大小判定绘制位置，使矩形在屏幕中间
            pygame.draw.rect(Surface, color, (rect_xy, size), width, horn)#绘制矩形
            self.draw_xy = rect_xy#输出绘制位置

        def make_rect(self, size):
            global w_face, h_face
            rect_xy = ((w_face - size[0]) // 2, (h_face - size[1]) // 2)
            self.warring_xy = rect_xy#输出绘制位置

            return pygame.Rect(rect_xy, size)

    class ImageHandle:
        def __init__(self, file_image_name, re_image_name, type):#类构造函数
            self.img = Image.open(file_image_name)#读取文件
            self.re_image_name = re_image_name#读取转换后文件名
            self.type = type#读取保存格式

        def resize_image(self, re_w, re_h):#用Image库改变图像大小
            self.re_img = self.img.resize((re_w, re_h),Image.ANTIALIAS)#改变图像大小
            self.re_img.save(self.re_image_name, self.type)#保存

        def gaussian_blur(self, fuzzy_kernel):
            self.dst = self.img.filter(ImageFilter.GaussianBlur(radius=fuzzy_kernel))#做高斯模糊处理
            self.dst.save(self.re_image_name, self.type)#保存图片

    def warring_frame(home, warring_image, return_xy=False, return_size=False):#创建提示框架
        draw_rect = DrawCenter()

        warring_region = draw_rect.make_rect((w_face // 2, h_face // 2))#创建提示窗口框架矩形范围

        warring = home.subsurface(warring_region)
        pygame.image.save(warring, warring_image)#以提示窗口框架矩形范围在屏幕上截取并保存

        warring_handle = ImageHandle(warring_image, warring_image, warring_image.split('.')[1])
        warring_handle.gaussian_blur(99)#把刚刚的图片更高级高斯模糊
        warring = pygame.image.load(warring_image).convert()#加载成surface

        pygame.draw.rect(warring, (255, 255, 255), ((0, 0), warring_region.size), h_face // 200)#画边框

        if return_xy:
            return (warring, draw_rect.warring_xy)

        if return_size:
            return (warring, warring_region.size)

        if return_xy and return_size:
            return (warring, draw_rect.warring_xy, warring_region.size)

        return warring#返回绘制好的Surface

    def exit_clean():#退出，并清除缓存文件
        shutil.rmtree('cache')
        os.mkdir('cache')
        sys.exit()

    def windows_home_cut():#截取当前桌面
        windows_home_image = 'cache/screen.bmp'#设置缓存的桌面截图图片路径

        hdesktop = win32gui.GetDesktopWindow()
        # 分辨率适应
        width_home = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height_home = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left_home = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top_home = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        # 创建设备描述表
        desktop_dc = win32gui.GetWindowDC(hdesktop)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        # 创建一个内存设备描述表
        mem_dc = img_dc.CreateCompatibleDC()
        # 创建位图对象
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width_home, height_home)
        mem_dc.SelectObject(screenshot)
        # 截图至内存设备描述表
        mem_dc.BitBlt((0, 0), (width_home, height_home), img_dc, (0, 0), win32con.SRCCOPY)
        # 将截图保存到文件中
        screenshot.SaveBitmapFile(mem_dc, windows_home_image)
        # 内存释放
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())
        '''
        我也不知道这是什么，总之这是利用Windowsapi截图
        '''

        img_deal = cv2.imread(windows_home_image)#cv获取截取图片
        dst_deal = cv2.GaussianBlur(img_deal, (55, 55), 0)#做高斯模糊处理
        cv2.imwrite(windows_home_image, dst_deal, [cv2.IMWRITE_PNG_COMPRESSION, 0])#保存图片
        return windows_home_image

    windows_home_image = windows_home_cut()#截取当前桌面，并设置路径

    pygame.init()#初始化

    pygame.mouse.set_visible(False)#消除系统光标

    clock = pygame.time.Clock()
    #初始化时钟

    home_exit_warring_image = 'cache/home_exit_warring_image.png'#设置缓存图片路径

    mouse_image = 'cache/mouse'#设置保存的鼠标图片名称
    micro_exit_image = 'cache/exit'#设置保存的退出按钮图片路径

    yinghua_image = 'image/yinghua'#获取樱花素材图片路径
    exit_image = 'image/exit'#获取退出按钮素材图片路径

    siyuanheitiC_font = 'font/思源黑体C.ttf'
    siyuanheitiE_font = 'font/思源黑体E.ttf'#获取字体路径

    sur = pygame.display.Info()
    w_face, h_face = (sur.current_w,sur.current_h)#获取分辨率

    home = pygame.display.set_mode((w_face,h_face), pygame.FULLSCREEN | pygame.DOUBLEBUF, depth = 32)
    #设置全屏，双缓冲窗口
    pygame.display.set_caption('樱花如此纯洁')#窗口名称

    try:#尝试导入素材文件
        yinghua_image_handle = ImageHandle(yinghua_image, mouse_image, 'png')
        yinghua_image_handle.resize_image(42, 40)#更改原樱花素材分辨率

        micro_exit_image_list = []
        for i in range(0, 25):#更改原退出按钮素材分辨率
            micro_exit_image_list.append('%s_ani_%s' % (micro_exit_image, i))#创建从小到大的退出图片标号
            exit_image_handle = ImageHandle(exit_image, micro_exit_image_list[i], 'png')
            exit_image_handle.resize_image(
                         w_face // 33 + i, w_face // 33 + i)#创建从小到大的退出图片序列，动画用

        game_home_font = pygame.font.Font(siyuanheitiE_font, 32)#引入按钮字体
        game_home_title_font = pygame.font.Font(siyuanheitiC_font, 92)#引入标题字体

        windows_home = pygame.image.load(windows_home_image).convert_alpha()#导入缓存图片
        home_exit = pygame.image.load(micro_exit_image_list[0]).convert_alpha()
        mouse = pygame.image.load(mouse_image).convert_alpha()#导入素材图片

        home_word_file = open('word/home.txt', mode='r', encoding='utf-8')

    except FileNotFoundError as error:
        pygame.mouse.set_visible(False)#恢复系统光标

        str_error = ''
        for i in str(error).strip('.'):
            str_error = str_error + str((ord(i)))#使用字符串方式把错误的ascii字符连接起来

        str_error = str(hex(int(str_error)))#转化为16进制字符串

        win32api.MessageBox(0, str_error + ':\n没有找到游戏文件', '文件路径错误',
                            win32con.MB_ICONWARNING)
        exit_clean()#退出
        #用Windowsapi弹出错误提示

    else:
        mouse_rect = pygame.Rect(
            w_face, h_face, mouse.get_width(), mouse.get_height())#初始化鼠标判定矩形在右下角

        micro_exit_list =[]
        for i in range(0, 25):
            micro_exit_list.append(pygame.image.load(micro_exit_image_list[i]).convert_alpha())#创建从小到大的退出图片对象

        beta_siyuanheitiE_font_word = game_home_font.render(' ', True, (0,0,0))#hack，制作一个标准主页按钮字体
        home_font_h = beta_siyuanheitiE_font_word.get_height()#得到它的高

        beta_siyuanheitiC_font_word = game_home_title_font.render(' ', True, (0,0,0))#hack，制作一个标准主页标题字体
        home_title_font_h = beta_siyuanheitiC_font_word.get_height()#得到它的高

        home_word_1_xy = (w_face // 10 * 9, h_face // 3 * 2)
        home_word_2_xy = (w_face // 10 * 9, h_face // 3 * 2 + home_font_h * 3)
        home_word_3_xy = (w_face // 10 * 9, h_face // 3 * 2 + home_font_h * 6)#定义文字按钮显示位置

        home_word_title_xy = (w_face // 30 * 1, home_word_1_xy[1] - home_title_font_h)#定义标题显示位置

        home_exit_xy = (7, 7)#定义退出按钮显示位置

        home_word_list = []#主页文字的列表
        for i in home_word_file.readlines():
            home_word_list.append(i.strip())
            #将行添加到列表中

        home_word_1 = game_home_font.render(home_word_list[1], True, (255,255,255))
        home_word_2 = game_home_font.render(home_word_list[2], True, (255,255,255))
        home_word_3 = game_home_font.render(home_word_list[3], True, (255,255,255))#创建主页按钮文字对象

        home_word_1_black = game_home_font.render(home_word_list[1], True, (255, 255, 255), (0, 0, 0))
        home_word_2_black = game_home_font.render(home_word_list[2], True, (255, 255, 255), (0, 0, 0))
        home_word_3_black = game_home_font.render(home_word_list[3], True, (255, 255, 255), (0, 0, 0))
        #创建主页按钮黑底文字对象

        home_word_title = game_home_title_font.render(home_word_list[0], True, (255,255,255))#创建主页标题文字对象

        home_word_surface_list = []
        for i in range(5, 5):
            home_word_surface_list.append(game_home_font.render(home_word_list[i], True, (255,255,255)))#创建主页提示文字列表

        home_word_1_example = WordButtonAni(home_word_1, home_word_1_black, home_word_1_xy)
        home_word_2_example = WordButtonAni(home_word_2, home_word_2_black, home_word_2_xy)
        home_word_3_example = WordButtonAni(home_word_3, home_word_3_black, home_word_3_xy)
        #创建主页文字按钮动画实例

        home_exit_example = ImageButtonAni(micro_exit_list, home_exit_xy)#创建图片按钮动画实例

        warring_frame_draw = False
        #初始化变量

        while True:#主循环
            type_mouse_xy = w_face, h_face#设置默认点击鼠标位置为右下角

            time_passed = clock.tick_busy_loop() / 1000#获得上一帧绘制经过的时间

            for event in pygame.event.get():#读取事件
                if event.type == pygame.QUIT:#退出键按下
                    exit_clean()#退出事件

                if event.type == pygame.KEYDOWN:#键盘按下
                    if event.key == pygame.K_ESCAPE:
                        exit_clean()#退出事件

                if event.type == pygame.MOUSEBUTTONDOWN:#鼠标按下
                    type_mouse_xy = pygame.mouse.get_pos()#获取点击鼠标位置

                if event.type == pygame.ACTIVEEVENT:
                    windows_home = pygame.image.load(windows_home_image).convert_alpha()

            home.blit(windows_home, (0, 0))#使用桌面填充，制作透明效果

            home.blit(home_word_title, home_word_title_xy)#绘制主页标题字体

            home.blit(home_word_1, home_word_1_xy)
            home.blit(home_word_2, home_word_2_xy)
            home.blit(home_word_3, home_word_3_xy)#绘制主页文字按钮

            home.blit(home_exit, home_exit_xy)#绘制主页退出按钮

            if home_exit_example.get_button_collide(type_mouse_xy):#判定是否开始绘制提示
                warring_frame_draw = True#指示开始绘制
                print('nb')

            if warring_frame_draw:#提示信息是否开始绘制
                warring_frame_if = False
                if not warring_frame_if:#框架是否被生成
                    home_exit_warring, home_exit_warring_xy , home_exit_warring_size = warring_frame(
                        windows_home, home_exit_warring_image, return_xy=True, return_size=True)#创建提示框架
                    warring_frame_if = True#确保只生成一次模糊框架

                home_exit_warring.blit(home_word_surface_list[0], (0, 0))
                '''
                warring_frame_draw = False#指示结束绘制
                '''

            x_mouse, y_mouse = pygame.mouse.get_pos()#获得鼠标位置
            x_mouse_rect = x_mouse - mouse.get_width() // 2
            y_mouse_rect = y_mouse - mouse.get_height() // 2#获得鼠标图片位置

            mouse_rect = pygame.Rect(
                x_mouse_rect, y_mouse_rect, mouse.get_width(), mouse.get_height())#获得鼠标判定矩形

            home.blit(mouse, (x_mouse_rect, y_mouse_rect))#把鼠标图片绘制上去

            home_word_1 = home_word_1_example.button_ani(0.15)
            home_word_2 = home_word_2_example.button_ani(0.15)
            home_word_3 = home_word_3_example.button_ani(0.15)

            home_exit = home_exit_example.button_ani(0.075, type_mouse_xy)

            pygame.display.flip()#刷新
            '''
            没做完
            '''

    finally:
        home_word_file.close()#清理文件

except:
    log_error = open('log/error_log.txt', mode='a', encoding='utf-8')#日志读写对象
    traceback.print_exc(file=log_error)#写入错误
    '''
    没做完
    '''

finally:
    log_error.close()#清理文件