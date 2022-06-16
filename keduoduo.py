import datetime
import os
import time
import random
import cv2
import numpy as np
import pytesseract
import pysjtu.ocr
from pysjtu import Session, Client, NNRecognizer
from pysjtu.exceptions import LoginException, SelectionNotAvailableException

sectors = []


def print_to_file(tag, note):
    with open(scriptName + '.txt', 'a', encoding='utf-8') as f:
        text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + '[ ' + tag + ' ]:   ' + note + '\n'
        f.write(text)


def find_class(sector, class_name):
    class_i_want_id = None
    for index in range(len(sectors[sector].classes)):
        if class_name in sectors[sector].classes[index].class_name:
            class_i_want_id = index
            break
    return [sector, class_i_want_id]


def select_class(class_list):
    sector = class_list[0]
    class_id = class_list[1]

    class_i_want = sectors[sector].classes[class_id]
    if class_i_want.is_registered():
        print("已选上 ", class_i_want.name)
        return True

    try:
        class_i_want.register()
        if class_i_want.is_registered():
            print("已选上 ", class_i_want.name)
        print_to_file('Select', '第 ' + str(n) + ' 次' + ' 已选上 ' + class_i_want.name)
        return True
    except:
        if class_i_want.students_registered >= class_i_want.students_planned:
            print(class_i_want.name, " 人满失败")
        else:
            print(class_i_want.name, " 其他原因失败")
        return False


def teacher_list_to_string(teacher_list):
    temp_string = ""
    for teacher in teacher_list:
        temp_string += (teacher[0] + ' ')
    return temp_string


def better_class(class_list):
    print()
    print("****************优选开始****************")
    for index in range(len(class_list)):
        tmp = sectors[class_list[index][0]].classes[class_list[index][1]]

        if tmp.is_registered():
            if index != 0:
                for j in range(index):
                    print_tmp = sectors[class_list[j]
                    [0]].classes[class_list[j][1]]
                    print("**  未能选择 ", print_tmp.teachers, print_tmp,
                          print_tmp.students_registered, "/", print_tmp.students_planned)
            else:
                print("**  已最优")
            print("---------------------------------")
            print("**  现在为 ", tmp.teachers, tmp,
                  tmp.students_registered, "/", tmp.students_planned)
            print("****************优选结束****************")
            print()
            return index

        else:
            if tmp.students_registered < tmp.students_planned:
                is_registered_one = False
                for j in range(len(class_list)):
                    if sectors[class_list[j][0]].classes[class_list[j][1]].is_registered():
                        class_i_dontwant = sectors[class_list[j]
                        [0]].classes[class_list[j][1]]
                        is_registered_one = True
                        break
                try:
                    if is_registered_one:
                        class_i_dontwant.deregister()
                    tmp.register()
                except:
                    print("！！！出错了！！！")
                if tmp.is_registered():
                    if is_registered_one:
                        print("**  已选上", tmp.teachers,
                              tmp, '\n', "**  已退课 ", class_i_dontwant.teachers, class_i_dontwant)

                        teacher_string = teacher_list_to_string(tmp.teachers)
                        class_i_dontwant_teacher_string = teacher_list_to_string(
                            class_i_dontwant.teachers)
                        print_to_file('Change', '第 ' + str(n) + ' 次' + ' 已选上 ' + teacher_string + tmp.name
                                      + " || 已退课 " + class_i_dontwant_teacher_string + class_i_dontwant.name)
                    else:
                        print("**  已选上", tmp.teachers, tmp)
                        teacher_string = teacher_list_to_string(tmp.teachers)
                        print_to_file('Change', '第 ' + str(n) + ' 次' +
                                      ' 已选上 ' + teacher_string + tmp.name)

                    print("****************优选结束****************")
                    print()
                return index

    print("未能选择", tmp.name)
    print("****************优选结束****************")
    return -1


class ForceRestrat(Exception):
    pass


class TesseractRecognizer(pysjtu.ocr.Recognizer):
    def recognize(self, img):
        nparr = np.frombuffer(img, np.uint8)
        im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        text = pytesseract.image_to_string(im)
        return text.strip()


if __name__ == '__main__':
    print("进入选课系统...")
    n = 0
    scriptName = os.path.basename(__file__)
    print_to_file('Welcome', '进入选课')
    while True:
        try:
            sess_file = open("session", mode="r+b")
        except FileNotFoundError:
            sess_file = None  # type: ignore

        sess = Session(ocr=NNRecognizer())

        try:
            # Step1: 填写Jaccount用户名密码
            with Session(session_file=sess_file) if sess_file else Session(username="username", password="password",
                                                                           ocr=TesseractRecognizer()) as sess:
                client = Client(session=sess)
                print(client.student_id)
                print(client.term_start_date)
                sectors = client.course_selection_sectors
                sector_name = []
                for i in range(len(sectors)):
                    sector_name.append(sectors[i].name)

                # Step2: 确认选课类型
                Zhu_Xiu = sector_name.index("主修课程")
                Tong_Shi = sector_name.index("公共选修课")
                # Tong_Xuan = sector_name.index("通选课")

                class_i_want_list = []
                '''
                对于不需要换选/优选的课程：
                class_i_want_list.append([find_class(Zhu_Xiu, "(2024-2025-2)-EE101-1")])
                
                对于有换选/优选需求的课程，建立一个优选列表，优先级从高到低排列。
                如果排在前面的课有余量，会先去退掉排在后面的课，然后再来选，直到选到最优的课
                class_i_want_list.append([
                    find_class(Tong_Shi, "(2024-2025-2)-EE101-1"),
                    find_class(Zhu_Xiu, "(2024-2025-2)-EE103-1"),
                    find_class(Tong_Shi, "(2024-2025-2)-MATH1203-1"),
                    ])
                '''

                # Step3: 填写选课列表，要求见上
                class_i_want_list.append([
                    find_class(Zhu_Xiu, "(2022-2023-1)-EE435-1"),
                    find_class(Zhu_Xiu, "(2022-2023-1)-EE436-1"),
                ])

                class_i_want_list.append([
                    find_class(Zhu_Xiu, "(2022-2023-1)-EE104-1"),
                ])

                # main

                while True:
                    n = n + 1
                    print("第", n, "次")
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                    for i in range(len(class_i_want_list)):
                        if len(class_i_want_list[i]) == 1:
                            select_class(class_i_want_list[i][0])
                        else:
                            better_class(class_i_want_list[i])

                    time.sleep(random.uniform(1, 3))
                    print()
                    if n % 10 == 0:
                        raise ForceRestrat('Force Restart!')
        except LoginException:
            print("登陆失败，请检查用户名密码！\n等待重启\n")
            time.sleep(1)
        except SelectionNotAvailableException:
            print("对不起，当前不属于选课阶段！\n等待重启\n")
            time.sleep(1)
        except ForceRestrat:
            print("强制重启\n")
        except Exception as e:
            print(e)
            print("其他错误！\n等待重启\n")
            time.sleep(1)
