import sys
import copy
import os
import subprocess
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QFileSystemWatcher, pyqtSlot
import xml.etree.ElementTree as ET
from PyQt5 import uic
from collections import OrderedDict

# 파일명에서 뒤 네 자리 숫자 추출하는 함수
def extract_file_number(file_name):
    try:
        file_number = int(file_name[-4:])
        return file_number
    except ValueError:
        return None


class Tab2Widget(QWidget):
    def __init__(self):
        super().__init__()

        # Variable to store the previously selected file path
        self.previous_selected_file = ""

        # 현재 선택된 큐보이드 ID, 시작 인덱스, 끝 인덱스를 저장할 변수
        self.current_cuboid_id = 0
        self.current_start_index = 1
        self.current_end_index = 1
        self.current_selected_index = 1
        # 현재 선택된 큐보이드 object 정보를 저장할 변수
        self.current_object_info = {}
        # 현재 선택된 파일 경로들을 저장할 변수
        self.current_file_paths = []

        # Variable to store the available cuboid_id values in the selected files
        self.available_cuboid_ids = set()

        # 탭2 UI 초기화
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # 상태창 UI
        self.label_files_tab2 = QLabel(self)
        self.label_files_tab2.setText("Selected Files: ")
        main_layout.addWidget(self.label_files_tab2)

        self.label_file_info_tab2 = QLabel(self)
        self.label_file_info_tab2.setText(
            "File Count: 0, Selected Count: 0, File Range: N/A")
        main_layout.addWidget(self.label_file_info_tab2)

        # 큐보이드 ID 선택 바 UI
        self.label_cuboid_id_tab2 = QLabel("Cuboid ID: ", self)
        main_layout.addWidget(self.label_cuboid_id_tab2)

        self.slider_cuboid_id_tab2 = QSlider(Qt.Horizontal, self)
        self.slider_cuboid_id_tab2.setFocusPolicy(Qt.NoFocus)
        self.slider_cuboid_id_tab2.setTickInterval(1)
        self.slider_cuboid_id_tab2.setSingleStep(1)
        self.slider_cuboid_id_tab2.valueChanged.connect(
            self.update_cuboid_id_tab2)
        main_layout.addWidget(self.slider_cuboid_id_tab2)

        # 시작 인덱스 선택 바 UI
        self.label_start_index_tab2 = QLabel("Start Index: 1", self)
        main_layout.addWidget(self.label_start_index_tab2)

        self.slider_start_index_tab2 = QSlider(Qt.Horizontal, self)
        self.slider_start_index_tab2.setFocusPolicy(Qt.NoFocus)
        self.slider_start_index_tab2.setTickInterval(1)
        self.slider_start_index_tab2.setSingleStep(1)
        self.slider_start_index_tab2.valueChanged.connect(
            self.update_start_index_tab2)
        main_layout.addWidget(self.slider_start_index_tab2)

        # 끝 인덱스 선택 바 UI
        self.label_end_index_tab2 = QLabel("End Index: 1", self)
        main_layout.addWidget(self.label_end_index_tab2)

        self.slider_end_index_tab2 = QSlider(Qt.Horizontal, self)
        self.slider_end_index_tab2.setFocusPolicy(Qt.NoFocus)
        self.slider_end_index_tab2.setTickInterval(1)
        self.slider_end_index_tab2.setSingleStep(1)
        self.slider_end_index_tab2.valueChanged.connect(
            self.update_end_index_tab2)
        main_layout.addWidget(self.slider_end_index_tab2)

        # 선택 인덱스 선택 바 UI
        self.label_selected_index_tab2 = QLabel("Selected Index: 1", self)
        main_layout.addWidget(self.label_selected_index_tab2)

        self.slider_selected_index_tab2 = QSlider(Qt.Horizontal, self)
        self.slider_selected_index_tab2.setFocusPolicy(Qt.NoFocus)
        self.slider_selected_index_tab2.setTickInterval(1)
        self.slider_selected_index_tab2.setSingleStep(1)
        self.slider_selected_index_tab2.valueChanged.connect(
            self.update_selected_index_tab2)
        main_layout.addWidget(self.slider_selected_index_tab2)

        # Group box for displaying object information
        self.group_box_object_info = QGroupBox("Object Information", self)

        grid_layout = QGridLayout()

        self.label_dimension = QLabel("Dimension:", self.group_box_object_info)
        self.label_location = QLabel("Location:", self.group_box_object_info)
        self.label_box = QLabel("Box:", self.group_box_object_info)
        self.label_alpha = QLabel("Alpha:", self.group_box_object_info)
        self.label_distance = QLabel("Distance:", self.group_box_object_info)
        self.label_yaw = QLabel("Yaw:", self.group_box_object_info)
        self.label_pitch = QLabel("Pitch:", self.group_box_object_info)
        self.label_roll = QLabel("Roll:", self.group_box_object_info)

        grid_layout.addWidget(self.label_dimension, 0, 0)
        grid_layout.addWidget(self.label_location, 1, 0)
        grid_layout.addWidget(self.label_box, 2, 0)
        grid_layout.addWidget(self.label_alpha, 3, 0)
        grid_layout.addWidget(self.label_distance, 4, 0)
        grid_layout.addWidget(self.label_yaw, 5, 0)
        grid_layout.addWidget(self.label_pitch, 6, 0)
        grid_layout.addWidget(self.label_roll, 7, 0)

        self.label_attribute_value = QLabel(self.group_box_object_info)
        grid_layout.addWidget(self.label_attribute_value, 0, 1, 8, 1)

        self.group_box_object_info.setLayout(grid_layout)
        main_layout.addWidget(self.group_box_object_info)

        # Select files button
        self.select_files_button = QPushButton("Select XML Files", self)
        self.select_files_button.clicked.connect(self.select_files_tab2)
        main_layout.addWidget(self.select_files_button)

        # Copy button
        self.copy_button = QPushButton("Copy", self)
        self.copy_button.clicked.connect(
            self.on_copy_button_clicked)  # Connect to a new handler
        main_layout.addWidget(self.copy_button)

        self.setLayout(main_layout)

        # 윈도우 크기 제한 설정
        self.setMinimumSize(450, 750)
        self.setMaximumSize(
            QApplication.desktop().availableGeometry(self).size())

    def center_on_screen(self):
        # 창을 화면 중앙으로 이동하는 메서드
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        qr.moveTop(10)  # 창을 위로 고정시키기 위해 y 좌표를 100으로 설정
        self.move(qr.topLeft())  # 변경된 부분

    def update_selected_index_tab2(self, value):
        self.current_selected_index = value
        selected_file_name = ""

        # Check if the current_selected_index is within the valid range
        if 1 <= self.current_selected_index <= len(self.current_file_paths):
            selected_file_path = self.current_file_paths[self.current_selected_index - 1]
            selected_file_name = os.path.basename(selected_file_path)
            # Remove the file extension
            selected_file_name = selected_file_name[:-4]
            # Get the last four characters
            selected_file_name = selected_file_name[-4:]

        self.label_selected_index_tab2.setText(
            f"Selected Index: {self.current_selected_index} ({selected_file_name})")
        self.update_object_info()

        # Update the object information only when the selected file changes
        if self.current_selected_index <= len(self.current_file_paths):
            selected_file_path = self.current_file_paths[self.current_selected_index - 1]
            if selected_file_path != self.previous_selected_file:
                self.previous_selected_file = selected_file_path
                self.update_object_info()

        # Update the object information only when the selected file changes
        if self.current_selected_index <= len(self.current_file_paths):
            selected_file_path = self.current_file_paths[self.current_selected_index - 1]
            if selected_file_path != self.previous_selected_file:
                self.previous_selected_file = selected_file_path
                self.update_object_info()

    def update_cuboid_id_tab2(self, value):
        self.current_cuboid_id = value
        self.label_cuboid_id_tab2.setText(
            f"Cuboid ID: {self.current_cuboid_id}")
        self.update_file_info()

        # 선택된 파일이 있을 때에만 object 정보 업데이트 수행
        if self.current_file_paths:
            self.update_object_info()

    def update_start_index_tab2(self, value):
        self.current_start_index = value
        selected_file_name = self.get_selected_file_name(
            self.current_start_index)
        self.label_start_index_tab2.setText(
            f"Start Index: {self.current_start_index} ({selected_file_name})")
        self.update_file_info()

    def load_files(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Load Files", "", "XML Files (*.xml);;All Files (*)", options=options)
        if file_paths:
            self.current_file_paths = sorted(file_paths)  # 파일 이름으로 정렬
            self.current_selected_index = 0
            self.update_object_info_table()

    def update_object_info_table(self):
        # Get the total number of rows and columns in the object_info_table
        num_rows = len(self.current_object_info)
        num_cols = self.object_info_table.columnCount()

        # Set the number of rows in the table based on the current_object_info length
        self.object_info_table.setRowCount(num_rows)

        # Loop through each row and populate the table with the object_info data
        for row in range(num_rows):
            object_info = self.current_object_info[row]

            for col in range(num_cols):
                # Get the value for each cell and convert to a display value
                value = object_info.get(self.object_info_headers[col], "")
                display_value = self.get_display_value(value)

                # Create a QTableWidgetItem and set it to the cell
                item = QTableWidgetItem(display_value)
                item.setFlags(Qt.ItemIsEnabled)
                self.object_info_table.setItem(row, col, item)

            # Add the file name's last four characters to the table
            item = QTableWidgetItem(self.current_file_names[row][-4:])
            item.setFlags(Qt.ItemIsEnabled)
            self.object_info_table.setItem(row, num_cols, item)

    def update_end_index_tab2(self, value):
        self.current_end_index = value
        selected_file_name = self.get_selected_file_name(
            self.current_end_index)
        self.label_end_index_tab2.setText(
            f"End Index: {self.current_end_index} ({selected_file_name})")
        self.update_file_info()

    def get_selected_file_name(self, index):
        if 1 <= index <= len(self.current_file_paths):
            file_name = self.current_file_paths[index - 1]
            # 파일 이름에서 뒤에서 숫자 네글자 추출
            numeric_suffix = file_name[-8:-4]
            return numeric_suffix if numeric_suffix.isdigit() else "N/A"
        return "N/A"

    def select_files_tab2(self):
        xml_files_tab2, _ = QFileDialog.getOpenFileNames(
            self, "Select XML Files", "", "XML Files (*.xml);;All Files (*)"
        )
        if not xml_files_tab2:
            return

        cuboid_ids = set()
        total_xml_files = len(xml_files_tab2)

        for xml_file in xml_files_tab2:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for obj in root.findall("object"):
                cuboid_id_elem = obj.find("cuboid_id")
                if cuboid_id_elem is not None:
                    cuboid_id = int(cuboid_id_elem.text)
                    cuboid_ids.add(cuboid_id)

        if not cuboid_ids:
            QMessageBox.warning(
                self, "Error", "Selected XML files do not have cuboid_id information."
            )
            return

        # 파일 이름으로 정렬
        self.current_file_paths = sorted(xml_files_tab2)
        self.label_files_tab2.setText(
            f"Selected Files: {', '.join(self.current_file_paths)}")
        self.label_cuboid_id_tab2.setText(
            f"Cuboid IDs: {', '.join(str(cuboid_id) for cuboid_id in cuboid_ids)}"
        )

        # Reset the selected index slider
        self.slider_selected_index_tab2.setRange(1, total_xml_files)
        self.slider_selected_index_tab2.setValue(1)
        self.current_selected_index = 1

        # Reset other sliders and labels
        self.slider_cuboid_id_tab2.setRange(min(cuboid_ids), max(cuboid_ids))
        self.slider_cuboid_id_tab2.setValue(min(cuboid_ids))
        self.slider_start_index_tab2.setRange(1, total_xml_files)
        self.slider_start_index_tab2.setValue(1)
        self.slider_end_index_tab2.setRange(1, total_xml_files)
        self.slider_end_index_tab2.setValue(total_xml_files)

        self.current_cuboid_id = min(cuboid_ids)
        self.current_start_index = 1
        self.current_end_index = total_xml_files

        self.update_file_info()  # 추가: Selected Index 설정을 초기화
        self.update_object_info()

    def on_copy_button_clicked(self):
        # Fetch the values from the sliders
        cuboid_id = self.slider_cuboid_id_tab2.value()
        selected_index = self.slider_selected_index_tab2.value()
        start_index = self.slider_start_index_tab2.value()
        end_index = self.slider_end_index_tab2.value()

        # Call the copy_object_info method with the fetched values
        self.copy_object_info(cuboid_id, selected_index,
                              start_index, end_index)

    def update_file_info(self):
        total_xml_files = len(self.current_file_paths)
        selected_count = min(self.current_end_index,
                             total_xml_files) - self.current_start_index + 1
        self.label_file_info_tab2.setText(
            f"File Count: {total_xml_files}, Selected Count: {selected_count}, File Range: {self.current_start_index}-{min(self.current_end_index, total_xml_files)}")
        self.current_selected_index = 1

    def update_object_info(self):
        # Check if the current_selected_index is within the valid range
        if 1 <= self.current_selected_index <= len(self.current_file_paths):
            selected_file_path = self.current_file_paths[self.current_selected_index - 1]
            tree = ET.parse(selected_file_path)
            root = tree.getroot()
            object_info = OrderedDict([
                ("height", "N/A"),
                ("width", "N/A"),
                ("length", "N/A"),
                ("x3d", "N/A"),
                ("y3d", "N/A"),
                ("z3d", "N/A"),
                ("yaw", "N/A"),
                ("pitch", "N/A"),
                ("roll", "N/A"),
                ("min_x", "N/A"),
                ("min_y", "N/A"),
                ("max_x", "N/A"),
                ("max_y", "N/A"),
                ("alpha", "N/A"),
                ("distance", "N/A"),
            ])

            for obj in root.findall("object"):
                cuboid_id_elem = obj.find("cuboid_id")
                if cuboid_id_elem is not None:
                    cuboid_id = int(cuboid_id_elem.text)
                    if cuboid_id == self.current_cuboid_id:
                        dimension_elem = obj.find("dimension")
                        location_elem = obj.find("location")
                        box_elem = obj.find("box")
                        alpha_elem = obj.find("alpha")
                        distance_elem = obj.find("distance")
                        yaw_elem = obj.find("yaw")
                        pitch_elem = obj.find("pitch")
                        roll_elem = obj.find("roll")

                        if dimension_elem is not None:
                            height_elem = dimension_elem.find("height")
                            width_elem = dimension_elem.find("width")
                            length_elem = dimension_elem.find("length")
                            if height_elem is not None and width_elem is not None and length_elem is not None:
                                object_info["height"] = height_elem.text or "0"
                                object_info["width"] = width_elem.text or "0"
                                object_info["length"] = length_elem.text or "0"

                        if location_elem is not None:
                            x3d_elem = location_elem.find("x3d")
                            y3d_elem = location_elem.find("y3d")
                            z3d_elem = location_elem.find("z3d")
                            if x3d_elem is not None and y3d_elem is not None and z3d_elem is not None:
                                object_info["x3d"] = x3d_elem.text or "0"
                                object_info["y3d"] = y3d_elem.text or "0"
                                object_info["z3d"] = z3d_elem.text or "0"

                        if yaw_elem is not None:
                            object_info["yaw"] = yaw_elem.text or "0"
                        if pitch_elem is not None:
                            object_info["pitch"] = pitch_elem.text or "0"
                        if roll_elem is not None:
                            object_info["roll"] = roll_elem.text or "0"

                        if box_elem is not None:
                            min_x_elem = box_elem.find("min_x")
                            min_y_elem = box_elem.find("min_y")
                            max_x_elem = box_elem.find("max_x")
                            max_y_elem = box_elem.find("max_y")
                            if min_x_elem is not None and min_y_elem is not None and max_x_elem is not None and max_y_elem is not None:
                                object_info["min_x"] = min_x_elem.text or "0"
                                object_info["min_y"] = min_y_elem.text or "0"
                                object_info["max_x"] = max_x_elem.text or "0"
                                object_info["max_y"] = max_y_elem.text or "0"

                        if alpha_elem is not None:
                            object_info["alpha"] = alpha_elem.text or "0"

                        if distance_elem is not None:
                            object_info["distance"] = distance_elem.text or "0"

                        # Update the GUI with the new object info
                        self.update_object_info_display(object_info)
                        return

            # If the current_cuboid_id is not found in any object, clear the GUI
            self.clear_object_info_display()

    def update_object_info_display(self, object_info):
        display_info = {
            "height": object_info.get("height", "N/A"),
            "width": object_info.get("width", "N/A"),
            "length": object_info.get("length", "N/A"),
            "x3d": object_info.get("x3d", "N/A"),
            "y3d": object_info.get("y3d", "N/A"),
            "z3d": object_info.get("z3d", "N/A"),
            "yaw": object_info.get("yaw", "N/A"),
            "pitch": object_info.get("pitch", "N/A"),
            "roll": object_info.get("roll", "N/A"),
            "min_x": object_info.get("min_x", "N/A"),
            "min_y": object_info.get("min_y", "N/A"),
            "max_x": object_info.get("max_x", "N/A"),
            "max_y": object_info.get("max_y", "N/A"),
            "alpha": object_info.get("alpha", "N/A"),
            "distance": object_info.get("distance", "N/A"),
        }

        dimension_text = f"Height: {display_info['height']}\n" \
                        f"Width: {display_info['width']}\n" \
                        f"Length: {display_info['length']}\n"

        location_text = f"x3d: {display_info['x3d']}\n" \
                        f"y3d: {display_info['y3d']}\n" \
                        f"z3d: {display_info['z3d']}\n"

        yaw_text = f"Yaw: {display_info['yaw']}"
        pitch_text = f"Pitch: {display_info['pitch']}"
        roll_text = f"Roll: {display_info['roll']}"

        box_text = f"Min X: {display_info['min_x']}\n" \
                f"Min Y: {display_info['min_y']}\n" \
                f"Max X: {display_info['max_x']}\n" \
                f"Max Y: {display_info['max_y']}\n"

        alpha_text = f"Alpha: {display_info['alpha']}\n"
        distance_text = f"Distance: {display_info['distance']}\n"

        # Change the order of how the labels are updated
        self.label_dimension.setText(dimension_text)
        self.label_box.setText(box_text)
        self.label_location.setText(location_text)
        self.label_distance.setText(distance_text)
        self.label_alpha.setText(alpha_text)
        self.label_yaw.setText(yaw_text)
        self.label_pitch.setText(pitch_text)
        self.label_roll.setText(roll_text)
        
    def clear_object_info_display(self):
        # Clear all labels in the GUI
        self.label_dimension.setText("")
        self.label_location.setText("")
        self.label_yaw.setText("")
        self.label_pitch.setText("")
        self.label_roll.setText("")
        self.label_box.setText("")
        self.label_alpha.setText("")
        self.label_distance.setText("")

    def copy_object_info(self, cuboid_id, selected_index, start_index, end_index):
        # Check if the current_selected_index is within the valid range
        if 1 <= selected_index <= len(self.current_file_paths):
            # Get the selected file path and parse the XML tree
            selected_file_path = self.current_file_paths[selected_index - 1]
            selected_tree = ET.parse(selected_file_path)
            selected_root = selected_tree.getroot()

            # Extract the selected cuboid's information from the selected file
            selected_cuboid_info = None
            for obj in selected_root.findall("object"):
                cuboid_id_elem = obj.find("cuboid_id")
                if cuboid_id_elem is not None and int(cuboid_id_elem.text) == cuboid_id:
                    selected_cuboid_info = copy.deepcopy(obj)
                    break

            # If the selected cuboid's information is not found, return without making any changes
            if selected_cuboid_info is None:
                print("선택한 큐보이드의 정보가 올바르지 않습니다.")
                return

            # List to store modified file paths
            modified_files = []

            # Loop through the files in the specified range (start_index to end_index)
            for idx in range(start_index - 1, min(end_index, len(self.current_file_paths))):
                if idx != selected_index - 1:
                    # Get the file path and parse the XML tree
                    current_file_path = self.current_file_paths[idx]
                    current_tree = ET.parse(current_file_path)
                    current_root = current_tree.getroot()

                    # Append the selected cuboid's information to the current file
                    current_root.append(copy.deepcopy(selected_cuboid_info))

                    # Save the modified tree back to the file
                    current_tree.write(current_file_path)
                    modified_files.append(current_file_path)

            # Print the list of modified files
            if modified_files:
                print("다음 파일들에 선택한 큐보이드 정보가 성공적으로 추가되었습니다:")
                for file_path in modified_files:
                    print(file_path)
            else:
                print("선택된 범위에 해당하는 파일이 없습니다.")

    def check_location_info(self):
        # Check if location information is missing or contains only "N/A" values
        for idx in range(self.current_selected_index - 1, min(self.current_end_index, len(self.current_file_paths))):
            object_info = self.current_object_info.get(idx, {})
            location_values = [object_info.get(
                "x3d", "N/A"), object_info.get("y3d", "N/A"), object_info.get("z3d", "N/A")]

            # Check if there is at least one valid location value
            if any(value != "N/A" for value in location_values):
                return True

        # If no valid location value is found, show the confirmation dialog
        message_box = QMessageBox(self)
        message_box.setWindowTitle("경고")
        message_box.setText("위치값 정보가 없습니다. 수정하시겠습니까?")
        message_box.setIcon(QMessageBox.Warning)
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button_yes = message_box.button(QMessageBox.Yes)
        button_no = message_box.button(QMessageBox.No)
        button_yes.setText("예")
        button_no.setText("아니오")
        result = message_box.exec_()
        return result == QMessageBox.Yes

    def get_display_value(self, value):
        try:
            num = float(value)
            return str(int(num)) if num.is_integer() else str(num)
        except (ValueError, TypeError):
            return "N/A"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # UI 파일 경로와 Python 파일 경로
        self.UI_FILE_PATH = r"C:\Users\alchera\Desktop\refile\ui_file.ui"
        self.PY_FILE_PATH = r"C:\Users\alchera\Desktop\refile\xml_editorV4.21.py"
        self.PYUIC_PATH = r"C:\Users\alchera\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\pyuic5.exe"

        # 이전에 선택한 파일들을 로드
        self.load_last_selected_files()

        # 현재 선택된 Class와 Subclass 저장 변수
        self.current_class = None
        self.current_subclass = None

        # 이전에 선택한 파일들을 저장할 변수 추가
        self.last_selected_files = []

        # XML 파일과 객체 정보 저장 변수
        self.xml_files = []
        self.object_data = []
        self.cuboid_ids = set()

        # UI 초기화
        self.setup_ui()
        self.setup_tabs()   # 탭 위젯을 설정하는 함수 호출
        self.setup_progress_bar()  # 진행 표시줄을 생성하는 함수 호출
        # 파일 시스템 감시기 초기화
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.handle_file_changed)

        # 파일 시스템 감시기 초기화
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.handle_file_changed)

        # 선택한 파일들을 감시하도록 설정
        if self.last_selected_files:
            self.setup_file_watching(self.last_selected_files)

        # 윈도우 타이틀 및 크기 설정
        self.setWindowTitle("Annotation Modifier")
        self.setGeometry(200, 200, 400, 700)

    def setup_tabs(self):
        self.tab_widget = QTabWidget(self)  # 탭 위젯 생성
        self.tab_widget.setGeometry(0, 0, 450, 700)

        self.tab1 = QWidget()  # 탭1 위젯 생성
        self.tab2 = Tab2Widget()  # 탭2 위젯 생성

        self.tab_widget.addTab(self.tab1, "Active")  # 탭1 추가
        self.tab_widget.addTab(self.tab2, "Lotation")  # 탭2 추가

        self.setCentralWidget(self.tab_widget)

        # 탭1 UI 구성
        self.label_files_tab1 = QLabel("Selected Files: ", self.tab1)
        self.label_files_tab1.setGeometry(20, 30, 360, 30)

        # Truncation 슬라이더 및 레이블 생성
        self.label_truncation = QLabel("Truncation Value: 0.00", self.tab1)
        self.label_truncation.setGeometry(20, 70, 200, 30)

        self.slider_truncation = QSlider(Qt.Orientation.Horizontal, self.tab1)
        self.slider_truncation.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_truncation.setGeometry(20, 110, 360, 30)
        self.slider_truncation.setRange(0, 99)
        self.slider_truncation.setTickInterval(1)
        self.slider_truncation.setSingleStep(1)
        self.slider_truncation.valueChanged.connect(self.update_truncation)

        # Occlusion 슬라이더 및 레이블 생성
        self.label_occlusion = QLabel("Occlusion Value: 0", self.tab1)
        self.label_occlusion.setGeometry(20, 150, 200, 30)

        self.slider_occlusion = QSlider(Qt.Orientation.Horizontal, self.tab1)
        self.slider_occlusion.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_occlusion.setGeometry(20, 190, 360, 30)
        self.slider_occlusion.setRange(0, 4)
        self.slider_occlusion.setTickInterval(1)
        self.slider_occlusion.setSingleStep(1)
        self.slider_occlusion.valueChanged.connect(self.update_occlusion)

        # Cuboid ID 슬라이더 및 레이블 생성
        self.label_cuboid_id = QLabel("Cuboid ID: ", self.tab1)
        self.label_cuboid_id.setGeometry(20, 230, 100, 30)

        self.line_edit_cuboid_id = QLineEdit(
            self.tab1)  # 추가: Cuboid ID를 입력받는 QLineEdit
        self.line_edit_cuboid_id.setGeometry(130, 230, 70, 30)
        self.line_edit_cuboid_id.setPlaceholderText(
            "Modify ID")  # 미리 보이는 힌트 텍스트

        self.slider_cuboid_id = QSlider(Qt.Orientation.Horizontal, self.tab1)
        self.slider_cuboid_id.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_cuboid_id.setGeometry(20, 270, 360, 30)
        self.slider_cuboid_id.setTickInterval(1)
        self.slider_cuboid_id.setSingleStep(1)
        self.slider_cuboid_id.valueChanged.connect(self.update_cuboid_id)

        # Start Index 슬라이더 및 레이블 생성
        self.label_start_index = QLabel("Start Index: 1", self.tab1)
        self.label_start_index.setGeometry(20, 310, 100, 30)

        self.slider_start_index = QSlider(Qt.Orientation.Horizontal, self.tab1)
        self.slider_start_index.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_start_index.setGeometry(130, 310, 250, 30)
        self.slider_start_index.setTickInterval(1)
        self.slider_start_index.setSingleStep(1)
        self.slider_start_index.valueChanged.connect(self.update_start_index)

        # End Index 슬라이더 및 레이블 생성
        self.label_end_index = QLabel("End Index: 1", self.tab1)
        self.label_end_index.setGeometry(20, 350, 100, 30)

        self.slider_end_index = QSlider(Qt.Orientation.Horizontal, self.tab1)
        self.slider_end_index.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_end_index.setGeometry(130, 350, 250, 30)
        self.slider_end_index.setTickInterval(1)
        self.slider_end_index.setSingleStep(1)
        self.slider_end_index.valueChanged.connect(self.update_end_index)

        # Start Index와 End Index를 조작하는 버튼 생성
        self.button_start_index_plus = QPushButton("+", self.tab1)
        self.button_start_index_plus.setGeometry(420, 310, 30, 30)
        self.button_start_index_plus.clicked.connect(
            self.increment_start_index)

        self.button_start_index_minus = QPushButton("-", self.tab1)
        self.button_start_index_minus.setGeometry(390, 310, 30, 30)
        self.button_start_index_minus.clicked.connect(
            self.decrement_start_index)

        self.button_end_index_plus = QPushButton("+", self.tab1)
        self.button_end_index_plus.setGeometry(420, 350, 30, 30)
        self.button_end_index_plus.clicked.connect(self.increment_end_index)

        self.button_end_index_minus = QPushButton("-", self.tab1)
        self.button_end_index_minus.setGeometry(390, 350, 30, 30)
        self.button_end_index_minus.clicked.connect(self.decrement_end_index)

        # Class와 Subclass 선택을 활성화하는 체크박스 생성
        self.checkbox_enable_class_subclass = QCheckBox(
            "Enable Class and Subclass Selection", self.tab1
        )
        self.checkbox_enable_class_subclass.setGeometry(20, 550, 350, 30)
        self.checkbox_enable_class_subclass.setChecked(
            False)  # 초기 상태를 비활성화로 설정
        self.checkbox_enable_class_subclass.stateChanged.connect(
            self.toggle_class_subclass_selection
        )

        # Class와 Subclass 선택 콤보 박스 생성
        self.label_class = QLabel("Class: ", self.tab1)
        self.label_class.setGeometry(20, 390, 100, 30)

        self.combo_class = QComboBox(self.tab1)
        self.combo_class.setGeometry(130, 390, 250, 30)
        self.combo_class.addItems(
            [
                "Car",
                "Bus",
                "Truck",
                "HeavyEquipment",
                "PersonalMobility",
                "Misc",
                "Cyclist",
                "Motorcycle",
            ]
        )
        self.combo_class.currentTextChanged.connect(self.update_subclass)

        self.label_subclass = QLabel("Subclass: ", self.tab1)
        self.label_subclass.setGeometry(20, 430, 100, 30)

        self.combo_subclass = QComboBox(self.tab1)
        self.combo_subclass.setGeometry(130, 430, 250, 30)
        self.combo_subclass.addItems(
            ["Normal", "Emergency", "SchoolBus", "None", "noRider", "Rider"]
        )

        # 파일 선택 버튼 생성
        self.button_select_files = QPushButton("Select XML Files", self.tab1)
        self.button_select_files.setGeometry(20, 470, 120, 30)
        self.button_select_files.clicked.connect(self.select_files)

        # XML 수정 버튼 생성
        self.button_modify = QPushButton("Modify XML", self.tab1)
        self.button_modify.setGeometry(150, 470, 120, 30)
        self.button_modify.clicked.connect(self.modify_xml)
        self.button_modify.setEnabled(False)

        # 객체 삭제 버튼 생성
        self.button_delete_object = QPushButton("Delete Object", self.tab1)
        self.button_delete_object.setGeometry(280, 470, 100, 30)
        self.button_delete_object.clicked.connect(self.delete_object)
        self.button_delete_object.setEnabled(False)

        # 파일 정보 텍스트 레이블 생성
        self.label_file_info = QLabel(
            "File Count: 0, Selected Count: 0, File Range: N/A", self.tab1
        )
        self.label_file_info.setGeometry(20, 510, 360, 30)

        # Copyrigh 텍스트 레이블 생성
        self.label_copyright = QLabel(
            "Copyright 2023.oddhyeon. All rights reserved.", self.tab1)
        self.label_copyright.setGeometry(20, 620, 360, 100)

    def setup_ui(self):
        self.setWindowTitle("XML Editor")
        self.setGeometry(100, 100, 500, 400)

    def setup_progress_bar(self):
        # 진행 표시줄 생성
        self.progress_bar = QProgressBar(self.tab1)
        self.progress_bar.setGeometry(20, 620, 360, 30)
        self.progress_bar.setValue(0)

    def increment_start_index(self):
        start_index = self.slider_start_index.value()
        if start_index < self.slider_start_index.maximum():
            self.slider_start_index.setValue(start_index + 1)

    def decrement_start_index(self):
        start_index = self.slider_start_index.value()
        if start_index > self.slider_start_index.minimum():
            self.slider_start_index.setValue(start_index - 1)

    def increment_end_index(self):
        end_index = self.slider_end_index.value()
        if end_index < self.slider_end_index.maximum():
            self.slider_end_index.setValue(end_index + 1)

    def decrement_end_index(self):
        end_index = self.slider_end_index.value()
        if end_index > self.slider_end_index.minimum():
            self.slider_end_index.setValue(end_index - 1)

    def setup_file_watching(self, files):
        # 감시할 XML 파일들을 추가
        for file in files:
            self.watcher.addPath(file)

    @pyqtSlot(str)
    def handle_file_changed(self, path):
        # Handle the file change event here
        # For example, you can reload the modified XML file and update the program
        print(f"File changed: {path}")
        # Reload and update the XML data here

    def delete_object_by_cuboid_id(self):
        # 슬라이더에서 선택된 큐보이드 ID를 가져옵니다.
        cuboid_id = self.slider_cuboid_id.value()

        # 큐보이드 ID와 연결된 XML 파일들을 저장할 리스트를 생성합니다.
        files_with_cuboid_id = []

        for xml_file in self.xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                objects_to_delete = []
                for obj in root.iter("object"):
                    obj_cuboid_id = int(obj.find("cuboid_id").text)
                    if obj_cuboid_id == cuboid_id:
                        objects_to_delete.append(obj)

                # 큐보이드 ID와 연결된 객체들을 삭제합니다.
                for obj in objects_to_delete:
                    root.remove(obj)

                tree.write(xml_file)
                if objects_to_delete:
                    files_with_cuboid_id.append(xml_file)
            except ET.ParseError as e:
                print(f"XML 파일 '{xml_file}' 파싱 중 오류가 발생하였습니다:", str(e))
            except FileNotFoundError:
                print(f"XML 파일 '{xml_file}'이 존재하지 않습니다.")

        if files_with_cuboid_id:
            print(
                f"ID {cuboid_id}에 연결된 객체가 {len(files_with_cuboid_id)}개의 파일에서 삭제되었습니다.")
        else:
            print(f"ID {cuboid_id}에 연결된 객체가 없습니다.")

    def toggle_class_subclass_selection(self, state):
        # Save the selected states of Class and Subclass combo boxes
        if state == Qt.CheckState.Checked:
            self.is_class_enabled = True
            self.is_subclass_enabled = True
        else:
            self.is_class_enabled = False
            self.is_subclass_enabled = False

        # Enable/disable Class and Subclass selection combo boxes based on the checkbox state
        self.combo_class.setEnabled(self.is_class_enabled)
        self.combo_subclass.setEnabled(self.is_subclass_enabled)

        # Update Class and Subclass combo boxes based on the checkbox state
        if self.is_class_enabled:
            self.update_subclass(self.combo_class.currentText())
        else:
            self.combo_subclass.clear()
            self.combo_subclass.setEnabled(False)

    def update_object_subtype(self, class_name):
        if class_name == "Car" or class_name == "Bus" or class_name == "Truck":
            self.combo_subtype.clear()
            self.combo_subtype.addItems(["Normal", "Emergency", "SchoolBus"])
        elif (
            class_name == "HeavyEquipment"
            or class_name == "PersonalMobility"
            or class_name == "Misc"
        ):
            self.combo_subtype.clear()
            self.combo_subtype.addItem("None")
        elif class_name == "Cyclist" or class_name == "Motorcycle":
            self.combo_subtype.clear()
            self.combo_subtype.addItems(["noRider", "Rider"])

    def toggle_class_selection(self, state):
        self.combo_class.setEnabled(state == Qt.CheckState.Checked)

    def toggle_subclass_selection(self, state):
        self.combo_subclass.setEnabled(state == Qt.CheckState.Checked)

    def update_truncation(self, value):
        truncation_value = value / 100.0
        self.label_truncation.setText(
            f"Truncation Value: {truncation_value:.2f}")

    def update_occlusion(self, value):
        occlusion_value = value
        self.label_occlusion.setText(f"Occlusion Value: {occlusion_value}")

    def update_cuboid_id(self, value):
        cuboid_id = value
        self.label_cuboid_id.setText(f"Cuboid ID: {cuboid_id}")

    def update_start_index(self, value):
        start_index = value
        self.label_start_index.setText(f"Start Index: {start_index}")
        self.update_file_info()

    def update_end_index(self, value):
        end_index = value
        self.label_end_index.setText(f"End Index: {end_index}")
        self.update_file_info()

    def update_file_info(self):
        file_count = len(self.xml_files)
        start_index = self.slider_start_index.value()
        end_index = self.slider_end_index.value()

        if self.xml_files:
            start_range = self.xml_files[start_index - 1][-8:-4]
            end_range = self.xml_files[end_index - 1][-8:-4]
            file_info = (
                f"File Count: {file_count},\t Selected Count: {end_index - start_index + 1},\t \nFile Range: {start_range} to {end_range}"
            )
        else:
            file_info = "File Count: 0,\t  Selected Count: 0 \n File Range: N/A"

        self.label_file_info.setText(file_info)

    def select_files(self):
        file_dialog = QFileDialog()
        options = file_dialog.options()
        xml_files, _ = file_dialog.getOpenFileNames(
            self, "Select XML Files", "", "XML Files (*.xml)", options=options
        )

        if xml_files:
            self.xml_files = xml_files
            self.last_selected_files = xml_files
            self.save_last_selected_files()
            self.xml_files.sort()

            self.label_files_tab1.setText(
                f"Selected Files: {', '.join(self.xml_files)}")
            self.button_modify.setEnabled(True)
            self.button_delete_object.setEnabled(True)
            self.cuboid_ids = self.extract_cuboid_ids(self.xml_files)
            max_cuboid_id = max(self.cuboid_ids) if self.cuboid_ids else 1
            self.slider_cuboid_id.setRange(1, max_cuboid_id)
            self.slider_cuboid_id.setValue(1)
            self.slider_start_index.setRange(1, len(self.xml_files))
            self.slider_start_index.setValue(1)
            self.slider_end_index.setRange(1, len(self.xml_files))
            self.slider_end_index.setValue(1)
            self.update_file_info()
        else:
            self.xml_files = self.last_selected_files
            self.update_file_info()
            self.button_modify.setEnabled(True)
            self.button_delete_object.setEnabled(True)

    def save_last_selected_files(self):
        with open("last_selected_files.pkl", "wb") as f:
            pickle.dump(self.last_selected_files, f)

    def load_last_selected_files(self):
        try:
            with open("last_selected_files.pkl", "rb") as f:
                self.last_selected_files = pickle.load(f)
        except FileNotFoundError:
            pass

    def extract_cuboid_ids(self, xml_files):
        cuboid_ids = set()

        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                for obj in root.iter("object"):
                    cuboid_id = int(obj.find("cuboid_id").text)
                    cuboid_ids.add(cuboid_id)

            except ET.ParseError as e:
                print(f"XML 파일 '{xml_file}' 파싱 중 오류가 발생하였습니다:", str(e))
            except FileNotFoundError:
                print(f"XML 파일 '{xml_file}'이 존재하지 않습니다.")

        return cuboid_ids

    def modify_xml(self):
        def is_duplicate_cuboid_id(existing_cuboid_ids, new_cuboid_id):
            return new_cuboid_id in existing_cuboid_ids

        if self.last_selected_files:
            total_files = len(self.last_selected_files)
            processed_files = 0

            selected_files = self.last_selected_files
            start_index = self.slider_start_index.value()
            end_index = self.slider_end_index.value()
            selected_files = selected_files[start_index - 1:end_index]

            cuboid_id_text = self.line_edit_cuboid_id.text().strip()
            if cuboid_id_text:
                new_cuboid_id = int(cuboid_id_text)
                if is_duplicate_cuboid_id(self.cuboid_ids, new_cuboid_id):
                    reply = QMessageBox.warning(self, "경고", "입력한 ID 값이 이미 존재합니다. 수정하시겠습니까?",
                                                QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.No:
                        return
            else:
                new_cuboid_id = None
            cuboid_id = self.slider_cuboid_id.value()
            truncation = self.slider_truncation.value() / 100.0
            occlusion = self.slider_occlusion.value()

            self.progress_bar.setValue(0)  # 진행 표시줄 초기화

            for idx, xml_file in enumerate(selected_files, 1):
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    for obj in root.iter("object"):
                        obj_cuboid_id = int(obj.find("cuboid_id").text)
                        if obj_cuboid_id == cuboid_id:
                            if cuboid_id_text:
                                obj.find("cuboid_id").text = str(
                                    cuboid_id_text)

                            obj.find("truncation").text = str(truncation)
                            obj.find("occlusion").text = str(occlusion)

                            if self.checkbox_enable_class_subclass.isChecked():
                                obj.find(
                                    "class").text = self.combo_class.currentText()
                                obj.find(
                                    "subclass").text = self.combo_subclass.currentText()

                    tree.write(xml_file)
                    processed_files += 1
                    progress = int((processed_files / total_files) * 100)
                    self.progress_bar.setValue(progress)

                    print(f"XML 파일 '{xml_file}'이 성공적으로 수정되었습니다.")
                except ET.ParseError as e:
                    print(f"XML 파일 '{xml_file}' 파싱 중 오류가 발생하였습니다:", str(e))
                except FileNotFoundError:
                    print(f"XML 파일 '{xml_file}'이 존재하지 않습니다.")

            self.progress_bar.setValue(100)  # 작업 완료 후 100%로 설정

    def delete_object(self):
        # 현재 선택된 클래스와 서브클래스를 가져옵니다.
        class_name = self.combo_class.currentText()
        subclass_name = self.combo_subclass.currentText()
        cuboid_id = self.slider_cuboid_id.value()

        # 메시지 박스를 통해 사용자의 확인을 받습니다.
        reply = QMessageBox.question(
            self,
            "Delete Object",
            f"정말 삭제하시겠습니까?\nCuboid ID: {cuboid_id}\n클래스: {class_name}\n서브클래스: {subclass_name}",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if self.xml_files:
                start_index = self.slider_start_index.value()
                end_index = self.slider_end_index.value()
                selected_files = self.xml_files[start_index - 1: end_index]

                for xml_file in selected_files:
                    try:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        objects = root.findall("object")

                        for obj in objects:
                            obj_class = obj.find("class").text
                            obj_subclass = obj.find("subclass").text
                            obj_cuboid_id = int(obj.find("cuboid_id").text)

                            if (
                                obj_cuboid_id == cuboid_id
                                and obj_class == class_name
                                and obj_subclass == subclass_name
                            ):
                                root.remove(obj)

                        tree.write(xml_file)
                        print(
                            f"XML 파일 '{xml_file}'에서 Cuboid ID '{cuboid_id}', 클래스 '{class_name}', 서브클래스 '{subclass_name}'인 객체가 삭제되었습니다."
                        )
                    except ET.ParseError as e:
                        print(f"XML 파일 '{xml_file}' 파싱 중 오류가 발생하였습니다:", str(e))
                    except FileNotFoundError:
                        print(f"XML 파일 '{xml_file}'이 존재하지 않습니다.")

    def update_subclass(self, class_name):
        if class_name == "Car" or class_name == "Bus" or class_name == "Truck":
            self.combo_subclass.clear()
            self.combo_subclass.addItems(["Normal", "Emergency", "SchoolBus"])
        elif (
            class_name == "HeavyEquipment"
            or class_name == "PersonalMobility"
            or class_name == "Misc"
        ):
            self.combo_subclass.clear()
            self.combo_subclass.addItem("None")
        elif class_name == "Cyclist" or class_name == "Motorcycle":
            self.combo_subclass.clear()
            self.combo_subclass.addItems(["noRider", "Rider"])

    def update_file_count(self):
        file_count = len(self.xml_files)
        self.label_file_count.setText(f"File Count: {file_count}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())