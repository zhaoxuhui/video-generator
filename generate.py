import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os


def findAllFiles(root_dir, filter):
    """
    在指定目录查找指定类型文件

    :param root_dir: 查找目录
    :param filter: 文件类型
    :return: 路径、名称、文件全路径

    """

    print("Finding files ends with \'" + filter + "\' ...")
    separator = os.path.sep
    paths = []
    names = []
    files = []
    for parent, dirname, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(filter):
                paths.append(parent + separator)
                names.append(filename)
    for i in range(paths.__len__()):
        files.append(paths[i] + names[i])
    print(names.__len__().__str__() + " files have been found.")
    paths.sort()
    names.sort()
    files.sort()
    return paths, names, files


def isDirExist(path='output'):
    """
    判断指定目录是否存在，如果存在返回True，否则返回False并新建目录

    :param path: 指定目录
    :return: 判断结果

    """

    if not os.path.exists(path):
        os.mkdir(path)
        return False
    else:
        return True


def readData(file_path):
    """
    输入、读取排名数据文件，数据文件包含英文名、排名、免签国数量、护照图片、中文名，各项之间以英文逗号隔开

    :param file_path:数据文件路径
    :return:数据list
    """
    data = []
    f = open(file_path, "r", encoding='utf-8')
    line = f.readline()
    while line:
        parts = line.split(',')
        data.append([parts[0], parts[1], parts[2], parts[3], parts[4]])
        line = f.readline()
    return data


def createItems(data_list, width=270, height=660, outputdir="items\\", passport_base="passports\\",
                font_path='HWXH.ttf'):
    """
    根据数据创建每个项目，并将项目保存成图片文件，以便后续调用

    :param data_list: 数据列表
    :param width: 每个item的宽度
    :param height: 每个item的高度
    :param outputdir: item图片的输出文件夹
    :param passport_base: 护照图片所在的文件夹
    :param font_path: 字体文件路径
    :return: None
    """
    isDirExist(outputdir)
    for i in range(len(data_list)):
        # 数据文件中$表示换行
        eng_name = data_list[i][0]
        eng_name = eng_name.replace("$", "\n")
        rank = data_list[i][1]
        visa_free = data_list[i][2]
        passport_img = data_list[i][3]
        chn_name = data_list[i][4]
        chn_name = chn_name.replace("$", "\n")

        # 背景色相关设置
        blank_bk = np.zeros((height, width, 3), np.uint8)
        blank_bk[:160, :] = 230
        blank_bk[160:540, :] = 240
        blank_bk[540:, :] = 230
        blank_bk[160:161, :] = 0
        blank_bk[:, :1] = 0
        blank_bk[:, width - 1:] = 0
        blank_bk[540:541, :] = 0

        info = Image.fromarray(blank_bk)
        draw = ImageDraw.Draw(info)

        # 向图片中写入内容
        print(eng_name, passport_img)
        passport_img = cv2.imread(passport_base + passport_img)
        font = ImageFont.truetype(font_path, 30)
        draw.text((20, 0), eng_name, (0, 0, 0), font=font)
        draw.text((20, 75), chn_name, (0, 0, 0), font=font)
        draw.text((20, 550), "排名：" + rank, (0, 0, 0), font=font)
        draw.text((20, 600), "免签：" + visa_free, (0, 0, 0), font=font)
        background = np.array(info)

        # 评价内容并输出图片
        passport_start_x = 10
        passport_start_y = 170
        passport_height = 357
        passport_width = 250
        resize_passport = cv2.resize(passport_img, (passport_width, passport_height), interpolation=cv2.INTER_AREA)
        background[passport_start_y:passport_start_y + passport_height,
        passport_start_x:passport_start_x + passport_width,
        :] = resize_passport
        cv2.imwrite(outputdir + (i + 1).__str__().zfill(3) + ".png", background)


def joinItems(input_dir="items\\"):
    """
    拼接所有item为一个图片

    :param input_dir: item所在的文件夹
    :return: 拼接好的图片
    """
    _, _, item_list = findAllFiles(input_dir, ".png")
    join_img = cv2.imread(item_list[0])
    for i in range(1, len(item_list)):
        join_img = np.hstack((join_img, cv2.imread(item_list[i])))
    return join_img


def animateImg(join_img, video_width=1080, pixel_interval=50, output_dir="frames/", start_end_frames=60):
    """
    生成视频的帧影像

    :param join_img: 拼接好的影像
    :param video_width: 视频的宽度
    :param pixel_interval: 帧间移动的步长
    :param output_dir: 视频帧的输出文件夹
    :param start_end_frames: 开头和结尾静止帧的个数
    :return: None
    """
    isDirExist(output_dir)
    width = join_img.shape[1]
    for i in range(start_end_frames):
        cv2.imwrite(output_dir + "00000_" + i.__str__().zfill(2) + ".jpg", join_img[:, :video_width])
    counter = 0
    total = int((width - video_width) / pixel_interval)
    for i in range(0, width - video_width, pixel_interval):
        counter = i
        if i % 100 == 0:
            print("generating", int(i / pixel_interval), "/", total, "frames",
                  round(100 * (i / pixel_interval) / total, 2), "%", "range:", i, i + video_width)
        frame = join_img[:, i:i + video_width]
        cv2.imwrite(output_dir + (i + 1).__str__().zfill(5) + ".jpg", frame)
    for i in range(start_end_frames):
        cv2.imwrite(output_dir + (counter + 1).__str__().zfill(5) + "_" + i.__str__().zfill(2) + ".jpg",
                    join_img[:, width - video_width:])


def generateVideo(input_dir="frames\\", output_path="output.avi", fps=60):
    """
    根据帧内容组成一个视频

    :param input_dir: 视频帧所在文件夹
    :param output_path: 输出视频路径
    :param fps: 视频的FPS
    :return: None
    """
    _, _, frames = findAllFiles(input_dir, ".jpg")
    frame0 = cv2.imread(frames[0])
    # 获取原始视频帧大小及fps信息，注意宽高需要强制类型转换成int，否则VideoWriter会报错
    width = int(frame0.shape[1])
    height = int(frame0.shape[0])

    # 指定FourCC编码是XVID
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    for i in range(len(frames)):
        if i % 100 == 0:
            print("rendering", i, "/", len(frames), "frames", round(100 * (i) / len(frames), 2), "%")
        # 在获取每一帧并进行处理后，进行输出
        frame = cv2.imread(frames[i])
        out.write(frame)
    out.release()


if __name__ == '__main__':
    # # 第一步，读取数据文件
    # print("\n=>reading data...")
    # data = readData(file_path="rank.txt")

    # # 第二步，结合数据文件和护照图片生成Item并输出
    # print("\n=>creating items...")
    # createItems(data, width=270, height=660, outputdir="items\\", passport_base="passports\\", font_path='msyh.ttc')

    # 第三步，将所有Item拼接为一个图片并输出
    print("\n=>joining items...")
    img = joinItems(input_dir="items\\")
    cv2.imwrite("join.jpg", img)

    # 第四步，根据全图生成视频帧图片并输出
    print("\n=>creating video frames...")
    animateImg(img, output_dir="F:\\frames\\", video_width=1080, pixel_interval=1, start_end_frames=60)

    # 第五步，根据视频帧生成视频
    print("\n=>generating video...")
    generateVideo(input_dir="F:\\frames\\", output_path="F:\\output.avi", fps=40)

    print(""" __                    __    __                                   __ 
/  |                  /  |  /  |                                 /  |
$$ |        ______   _$$ |_ $$/_______         ______    ______  $$ |
$$ |       /      \ / $$   |$//       |       /      \  /      \ $$ |
$$ |      /$$$$$$  |$$$$$$/  /$$$$$$$/       /$$$$$$  |/$$$$$$  |$$ |
$$ |      $$    $$ |  $$ | __$$      \       $$ |  $$ |$$ |  $$ |$$/ 
$$ |_____ $$$$$$$$/   $$ |/  |$$$$$$  |      $$ \__$$ |$$ \__$$ | __ 
$$       |$$       |  $$  $$//     $$/       $$    $$ |$$    $$/ /  |
$$$$$$$$/  $$$$$$$/    $$$$/ $$$$$$$/         $$$$$$$ | $$$$$$/  $$/ 
                                             /  \__$$ |              
                                             $$    $$/               
                                              $$$$$$/                """)
