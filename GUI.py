# Copyright (C) 2019 Mika Thesephicloud on Lich| <https://github.com/TheSephiCloud>.
#
# This file is part of FFlogs-Viewer.
#
# FFlogs-Viewer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FFlogs-Viewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FFlogs-Viewer.  If not, see <https://www.gnu.org/licenses/>.

import ast
import os
import sys
import webbrowser
import time
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import configparser

from FFlogs_Processing import get_zones, process_name_and_paste, finalize_percentiles

wd = os.getcwd()

config_and_data = configparser.ConfigParser()
difficulty = 1
try:
    config_and_data.read(wd + r"/pics/data.ini")
    API_key = config_and_data['Settings']['API_key']
    data = ast.literal_eval(config_and_data['Data']['data_savage'])
except KeyError:
    print("KeyError, Key not found in the file")
    API_key = ""
    difficulty = 1
    data = []

link_codes = []
zones_main, ids_main, zone_names_main = get_zones(difficulty)  # 1 is Savage, 0 is Story
zones, ids, zone_names = list(zones_main), list(ids_main), list(zone_names_main)
class_sort = (("pld", "Paladin"), ("war", "Warrior"), ("drk", "Dark Knight"), ("gnb", "Gunbreaker"),
              ("nin", "Ninja"), ("drg", "Dragoon"), ("mnk", "Monk"), ("sam", "Samurai"),
              ("brd", "Bard"), ("mch", "Machinist"), ("dnc", "Dancer"),
              ("smn", "Summoner"), ("rdm", "Red Mage"), ("blm", "Black Mage"),
              ("ast", "Astrologian"), ("sch", "Scholar"), ("whm", "White Mage"))


def setup_table_interaction():
    for i in range(len(class_sort) + 1):
        for j in range(len(ids_main) + len(zones_main) + 1):
            temp = QTableWidgetItem()
            temp.setFlags(Qt.ItemIsEnabled)
            table.setItem(j, i, temp)


def setup_table_head():
    table.setColumnCount(len(class_sort) + 1)
    table.setRowCount(len(ids)+len(zones) + 1)
    for i, classes in enumerate(class_sort):
        try:
            path = wd + f"/pics/{classes[0]}.png"
            pic = QTableWidgetItem()
            pic.setIcon(QIcon(path))
            pic.setFlags(Qt.ItemIsEnabled)
        except Exception:
            pic = QTableWidgetItem("Pic not found")
            pic.setFlags(Qt.ItemIsEnabled)
        table.setItem(0, i + 1, pic)
        if i in range(4):
            table.item(0, i + 1).setBackground(QColor(0, 0, 100))
        elif i in range(8):
            table.item(0, i + 1).setBackground(QColor(110, 0, 0))
        elif i in range(11):
            table.item(0, i + 1).setBackground(QColor(120, 40, 0))
        elif i in range(14):
            table.item(0, i + 1).setBackground(QColor(100, 0, 100))
        elif i in range(17):
            table.item(0, i + 1).setBackground(QColor(0, 100, 0))


def setup_table_side():
    old = 0
    k = 0
    text_zones = []
    temp = []
    for i, zone in enumerate(zones):
        if not old == zone[0]:
            text_zones.append(temp)
            temp = [zone_names[k]]
            k += 1
        temp.append("          " + zone[2])
        if i == len(zones) - 1:
            text_zones.append(temp)
            temp = []
        old = zone[0]
    global zones_list
    zones_list = []
    for zone in reversed(text_zones):
        for encounter in zone:
            zones_list.append(encounter)
    for i, string in enumerate(zones_list):
        temp = QTableWidgetItem(string)
        temp.setFlags(Qt.ItemIsEnabled)
        table.setItem(i + 1, 0, temp)


def setup_table():
    table.clear()
    setup_table_interaction()
    setup_table_head()
    setup_table_side()
    table.resizeColumnsToContents()
    table.resizeRowsToContents()


def show_data(enc_data):
    global link_codes
    link_codes = []
    setup_table()
    for dat in enc_data:
        row, column = 0, 0
        for i, zo in enumerate(zones_list):
            if zo == "          " + dat[3]:
                row = i + 1
                break
        for i, cla in enumerate(class_sort):
            if cla[1] == dat[0]:
                column = i + 1
                break
        if not row == 0 and not column == 0:
            temp = QTableWidgetItem(str(dat[1]))
            temp = set_color(temp)
            temp.setToolTip(str(dat[5]))
            temp.setFlags(Qt.ItemIsEnabled)
            table.setItem(row, column, temp)
            link_codes.append((row, column, dat[4]))


def change_diff_expac(enabled):
    if enabled:
        delete_list_zones, delete_list_ids_zone_names = [], []
        global zones, ids, zone_names
        zones, ids, zone_names = list(zones_main), list(ids_main), list(zone_names_main)
        hwb, sbb, shbb = hw_button.isChecked(), sb_button.isChecked(), shb_button.isChecked()
        if hwb:
            for i, c_id in enumerate(ids):
                if not 1 <= c_id <= 13:
                    for j, zo in enumerate(zones):
                        if zo[0] == c_id:
                            delete_list_zones.append(j)
                    delete_list_ids_zone_names.append(i)
        elif sbb:
            for i, c_id in enumerate(ids):
                if not 14 <= c_id <= 25:
                    for j, zo in enumerate(zones):
                        if zo[0] == c_id:
                            delete_list_zones.append(j)
                    delete_list_ids_zone_names.append(i)
        elif shbb:
            for i, c_id in enumerate(ids):
                if not 26 <= c_id <= 75:
                    for j, zo in enumerate(zones):
                        if zo[0] == c_id:
                            delete_list_zones.append(j)
                    delete_list_ids_zone_names.append(i)
        extb, savb, ultb = extreme_button.isChecked(), savage_button.isChecked(), ultimate_button.isChecked()
        if extb:
            for i, name in enumerate(zone_names):
                if "Extreme" not in name:
                    delete_list_ids_zone_names.append(i)
                    for j, zo in enumerate(zones):
                        if zo[0] == ids[i]:
                            delete_list_zones.append(j)
        elif savb:
            for i, name in enumerate(zone_names):
                if "Savage" not in name:
                    delete_list_ids_zone_names.append(i)
                    for j, zo in enumerate(zones):
                        if zo[0] == ids[i]:
                            delete_list_zones.append(j)
        elif ultb:
            for i, name in enumerate(zone_names):
                if "Bahamut" not in name and "Refrain" not in name:
                    delete_list_ids_zone_names.append(i)
                    for j, zo in enumerate(zones):
                        if zo[0] == ids[i]:
                            delete_list_zones.append(j)
        delete_list_zones = list(dict.fromkeys(sorted(delete_list_zones)))
        for i in reversed(delete_list_zones):
            del zones[i]
        delete_list_ids_zone_names = list(dict.fromkeys(sorted(delete_list_ids_zone_names)))
        for i in reversed(delete_list_ids_zone_names):
            del ids[i]
            del zone_names[i]
        for dat in data:
            if dat[0] == current_player.text():
                show_data(dat[2])
                break


def set_color(item):
    val = eval(item.text())
    item.setTextAlignment(Qt.AlignCenter)
    if val >= 100:
        item.setForeground(QBrush(QColor(229, 204, 128)))
    elif val >= 95:
        item.setForeground(QBrush(QColor(255, 128, 0)))
    elif val >= 75:
        item.setForeground(QBrush(QColor(163, 53, 238)))
    elif val >= 50:
        item.setForeground(QBrush(QColor(0, 112, 255)))
    elif val >= 25:
        item.setForeground(QBrush(QColor(30, 255, 0)))
    elif val >= 0:
        item.setForeground(QBrush(QColor(102, 102, 102)))
    return item


def pressed_send_button():
    try:
        name_entered = name_entry.text()
        server_entered = server_entry.text()
        paste_entered = paste_entry.text()
        name_entry.setText("")
        server_entry.setText("")
        paste_entry.setText("")
        if paste_entered:
            name_list = process_name_and_paste(paste_entered)
            for i, entry in enumerate(data):
                for n, name in enumerate(name_list):
                    if entry[0] == name[0]:
                        del data[i]
            for name_data in reversed(name_list):
                data.insert(0, (name_data[0], name_data[1], finalize_percentiles(name_data[0], zones_main, ids_main, region=name_data[1])))
                time.sleep(0.2)
        elif server_entered:
            name_data = process_name_and_paste(name_entered + "@" + server_entered)
            for i, entry in enumerate(data):
                for n, name in enumerate(name_data):
                    if entry[0] == name[0]:
                        del data[i]
            data.insert(0, (name_data[0][0], name_data[0][1], finalize_percentiles(name_data[0][0], zones_main, ids_main, region=name_data[0][1])))
        elif name_entered:
            name_data = process_name_and_paste(name_entered)
            for i, entry in enumerate(data):
                for n, name in enumerate(name_data):
                    if entry[0] == name[0]:
                        del data[i]
            data.insert(0, (name_data[0][0], name_data[0][1], finalize_percentiles(name_data[0][0], zones_main, ids_main, region=name_data[0][1])))
        show_data(data[0][2])
        current_player.setText(data[0][0])
        setup_player_list()
        data_list.resizeColumnsToContents()
    except Exception:
        print("Unrecognizable name entered (Or any other Error, really)")


def open_link(row, column):
    for lin_dat in link_codes:
        if lin_dat[0] == row and lin_dat[1] == column:
            code = lin_dat[2]
            link = f"https://www.fflogs.com/reports/{code}"
            webbrowser.open(link)
            break


def change_player(row, column):
    if column == 2:
        show_data(data[row][2])
        current_player.setText(data[row][0])
        setup_player_list()


def del_and_rel(row, column):
    if column == 1:
        data[row] = (data[row][0], data[row][1], finalize_percentiles(data[row][0], zones, ids, region=data[row][1]))
        show_data(data[row][2])
    elif column == 0:
        del data[row]
        setup_player_list()
        change_player(row, 2)


def setup_player_list():
    data_list.setRowCount(len(data))
    for i, dat in enumerate(data):
        temp = QTableWidgetItem(dat[0])
        temp.setFlags(Qt.ItemIsEnabled)
        data_list.setItem(i, 2, temp)
        try:
            del_path = wd + r"\pics\delete.png"
            rel_path = wd + r"\pics\reload.png"
            delete = QTableWidgetItem()
            delete.setIcon(QIcon(del_path))
            delete.setFlags(Qt.ItemIsEnabled)
            data_list.setItem(i, 0, delete)
            reload = QTableWidgetItem()
            reload.setIcon(QIcon(rel_path))
            reload.setFlags(Qt.ItemIsEnabled)
            data_list.setItem(i, 1, reload)
        except Exception:
            pass
    data_list.resizeColumnsToContents()
    data_list.resizeRowsToContents()


# noinspection PyArgumentList
def dark_fusion_mode(application):
    application.setStyle('Fusion')
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    application.setPalette(dark_palette)
    application.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


app = QApplication()
dark_fusion_mode(app)
app.setStyleSheet("QWidget { margin: 2px; }")

GUI = QWidget()
layout = QGridLayout()
first_bar, second_bar_1, second_bar_2, table_bar = QHBoxLayout(), QHBoxLayout(), QHBoxLayout(), QHBoxLayout()

first_bar.addWidget(QLabel("Name:"))
name_entry = QLineEdit()
name_entry.returnPressed.connect(pressed_send_button)
first_bar.addWidget(name_entry)

first_bar.addWidget(QLabel("Server:"))
server_entry = QLineEdit()
server_entry.returnPressed.connect(pressed_send_button)
first_bar.addWidget(server_entry)

first_bar.addWidget(QLabel("Copy Paste:"))
paste_entry = QLineEdit()
paste_entry.returnPressed.connect(pressed_send_button)
first_bar.addWidget(paste_entry)

first_bar.addWidget(QPushButton('Send', clicked=pressed_send_button, minimumWidth=125, minimumHeight=23))

layout.addLayout(first_bar, 0, 0, 1, 13)

cur_pl_font = QFont()
cur_pl_font.setPointSize(12)
cur_pl_font.setBold(True)
current_player = QLabel()
current_player.setFont(cur_pl_font)
layout.addWidget(current_player, 1, 0, 1, 8)

expansion_group = QButtonGroup(GUI)
all_expac_button = QRadioButton("All Expansions")
hw_button = QRadioButton("Heavensward")
sb_button = QRadioButton("Stormblood")
shb_button = QRadioButton("Shadowbringers")
all_expac_button.toggled.connect(change_diff_expac)
hw_button.toggled.connect(change_diff_expac)
sb_button.toggled.connect(change_diff_expac)
shb_button.toggled.connect(change_diff_expac)
expansion_group.addButton(all_expac_button)
expansion_group.addButton(hw_button)
expansion_group.addButton(sb_button)
expansion_group.addButton(shb_button)
second_bar_1.addWidget(all_expac_button)
second_bar_1.addWidget(hw_button)
second_bar_1.addWidget(sb_button)
second_bar_1.addWidget(shb_button)
layout.addLayout(second_bar_1, 1, 8)

difficulty_group = QButtonGroup(GUI)
all_diff_button = QRadioButton("All Difficulties")
extreme_button = QRadioButton("Extreme")
savage_button = QRadioButton("Savage")
ultimate_button = QRadioButton("Ultimate")
all_diff_button.toggled.connect(change_diff_expac)
extreme_button.toggled.connect(change_diff_expac)
savage_button.toggled.connect(change_diff_expac)
ultimate_button.toggled.connect(change_diff_expac)
difficulty_group.addButton(all_diff_button)
difficulty_group.addButton(extreme_button)
difficulty_group.addButton(savage_button)
difficulty_group.addButton(ultimate_button)
second_bar_2.addWidget(all_diff_button)
second_bar_2.addWidget(extreme_button)
second_bar_2.addWidget(savage_button)
second_bar_2.addWidget(ultimate_button)
layout.addLayout(second_bar_2, 1, 12)

all_expac_button.setChecked(True)
all_diff_button.setChecked(True)

table = QTableWidget()
table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
table.horizontalHeader().setVisible(False)
table.verticalHeader().setVisible(False)
table.setIconSize(QSize(100, 100))
table.cellDoubleClicked.connect(open_link)
table_bar.addWidget(table)

data_list = QTableWidget()
data_list.setIconSize(QSize(100, 100))
data_list.horizontalHeader().setStretchLastSection(True)
data_list.horizontalHeader().setVisible(False)
data_list.verticalHeader().setVisible(False)
data_list.setColumnCount(3)
data_list.cellClicked.connect(change_player)
data_list.cellDoubleClicked.connect(del_and_rel)
table_bar.addWidget(data_list)
layout.addLayout(table_bar, 2, 0, 15, 13)

GUI.setLayout(layout)

setup_table()
setup_player_list()
if not data == []:
    change_player(0, 2)

# noinspection PyArgumentList
GUI.resize(1200, 900)
GUI.show()

ret = app.exec_()

if config_and_data:
    if difficulty:
        config_and_data['Data']['data_savage'] = str(data)
    else:
        config_and_data['Data']['data_story'] = str(data)
    with open(wd + r"/pics/data.ini", 'w') as configfile:
        config_and_data.write(configfile)

sys.exit(ret)
