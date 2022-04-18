import time
from selenium import webdriver
import os.path
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
import cv2
from PIL import Image
import re
import base64

'''
获取图片
'''


def getImage(fileName):
    img = Image.open(fileName)
    # 打印当前图片的模式以及格式
    # print('未转化前的: ', img.mode, img.format)
    # 使用系统默认工具打开图片
    # img.show()
    return img


'''
1) 将图片进行降噪处理, 通过二值化去掉后面的背景色并加深文字对比度
'''


def convert_Image(img, standard=127.5):
    '''
    【灰度转换】
    '''
    image = img.convert('L')

    '''
    【二值化】
    根据阈值 standard , 将所有像素都置为 0(黑色) 或 255(白色), 便于接下来的分割
    '''
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if pixels[x, y] > standard:
                pixels[x, y] = 255
            else:
                pixels[x, y] = 0
    return image


import pytesseract

'''
使用 pytesseract 库来识别图片中的字符
'''


def change_Image_to_text(img):
    '''
    如果出现找不到训练库的位置, 需要我们手动自动
    语法: tessdata_dir_config = '--tessdata-dir "<replace_with_your_tessdata_dir_path>"'
    '''
    testdata_dir_config = '--tessdata-dir "Tesseract-OCR\\tessdata"'
    textCode = pytesseract.image_to_string(img, lang='eng', config=testdata_dir_config)
    # 去掉非法字符，只保留字母数字
    textCode = re.sub("\W", "", textCode)
    return textCode


def main():
    img = convert_Image(getImage(fileName))
    # print('识别的结果：', change_Image_to_text(img))
    result = change_Image_to_text(img)
    return result


def get_tracks(distance):
    """
    v = v0+at
    x = v0t+1/2at**2
    """
    # 定义存放运动轨迹的列表
    tracks = []
    # 定义初速度
    v = 0
    # 定义单位时间
    t = 0.5
    # 定义匀加速运动和匀减速运动的分界线
    mid = distance * 4 / 5
    # 定义当前位移
    current = 0
    # 为了一直移动，定义循环
    while current < distance:
        if mid > current:
            a = 24
        else:
            a = -36
        v0 = v
        # 计算位移
        x = v0 * t + 1 / 2 * a * t ** 2
        # 计算滑块当前位移
        current += x
        # 计算末速度
        v = v0 + a * t
        tracks.append(round(x))
    return tracks


def identify_gap(bg, tp):
    '''
    bg: 背景图片
    tp: 缺口图片
    out:输出图片
    '''
    # 读取背景图片和缺口图片
    bg_img = cv2.imread(bg)  # 背景图片
    tp_img = cv2.imread(tp)  # 缺口图片

    # 识别图片边缘
    bg_edge = cv2.Canny(bg_img, 100, 200)
    tp_edge = cv2.Canny(tp_img, 100, 200)

    # 转换图片格式
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    # 缺口匹配
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配

    # 绘制方框
    th, tw = tp_pic.shape[:2]
    tl = max_loc  # 左上角点的坐标
    br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标

    # 返回缺口的X坐标
    return tl[0]


def get_image(driver):
    url1 = driver.find_element_by_xpath('//*[@id="layui-layer100001"]/div/div/div/div[1]/img[1]').get_attribute('src')
    group1 = re.search(r'data:image/png;base64,(.*)', url1)
    data1 = base64.b64decode(group1[1])

    url2 = driver.find_element_by_xpath('//*[@id="layui-layer100001"]/div/div/div/div[1]/img[2]').get_attribute('src')
    group2 = re.search(r'data:image/png;base64,(.*)', url2)
    data2 = base64.b64decode(group2[1])
    with open('background.png', 'wb') as fp:
        fp.write(data1)
    with open('target.png', 'wb') as fp:
        fp.write(data2)


def fill():
    driver.find_element_by_xpath('//*[@id="username"]').send_keys(a)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(b)
    c = driver.find_element_by_xpath('//*[@id="fm1"]/div[4]/img')
    c.screenshot('code.png')
    code = main()
    driver.find_element_by_xpath('//*[@id="authcode"]').send_keys(code)
    driver.find_element_by_xpath('//*[@id="passbutton"]').click()
    time.sleep(0.5)
    # 捕捉验证码识别错误
    try:
        driver.find_element_by_xpath('//*[@id="group-4"]/div[2]/div/div[2]/p[1]').click()
    except NoSuchElementException:
        driver.find_element_by_xpath('//*[@id="username"]').send_keys(a)
        driver.find_element_by_xpath('//*[@id="password"]').send_keys(b)
        c = driver.find_element_by_xpath('//*[@id="fm1"]/div[4]/img')
        c.screenshot('code.png')
        code = main()
        driver.find_element_by_xpath('//*[@id="authcode"]').send_keys(code)
        driver.find_element_by_xpath('//*[@id="passbutton"]').click()
        driver.find_element_by_xpath('//*[@id="group-4"]/div[2]/div/div[2]/p[1]').click()
    time.sleep(1)
    windows = driver.window_handles
    driver.switch_to.window(windows[1])
    tem = driver.find_element_by_xpath('//*[@id="form"]/div[18]/div[1]/div/div[2]/div/div/input')

    tem.clear()
    tem.send_keys('36')
    driver.find_element_by_xpath('//*[@id="post"]').click()
    time.sleep(2)
    i = 0
    while True:
        time.sleep(2)
        get_image(driver)
        distance = identify_gap('background.png', 'target.png')
        # tracks = get_tracks(distance+6.5)
        time.sleep(1)
        slider = driver.find_element_by_xpath('//*[@id="layui-layer100001"]/div/div/div/div[2]/div[2]/div[2]')
        ActionChains(driver).click_and_hold(slider).perform()
        # for x in tracks:
        # ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
        ActionChains(driver).move_by_offset(xoffset=distance + 10, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(driver).release().perform()
        i += 1
        time.sleep(1)
        try:
            refresh = driver.find_element_by_xpath('//*[@id="layui-layer100001"]/div/div/div/div[2]/div[3]')
        except NoSuchElementException:
            driver.quit()
            break
        if i % 4 == 0:
            refresh.click()


names = [['账号', '密码']]

if __name__ == "__main__":
    while names:
        url = 'https://web-vpn.sues.edu.cn'
        driver = webdriver.Chrome()
        driver.get(url)
        a = names[-1][0]
        b = names[-1][1]
        names.pop()
        fileName = 'code.png'
        fill()
    os.remove(r'code.png')
    os.remove(r'background.png')
    os.remove(r'target.png')
