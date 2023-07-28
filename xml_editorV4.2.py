import sys
import os
import subprocess
import pickle
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QSlider,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QCheckBox,
    QLineEdit,
    QProgressBar,  # 진행 표시줄을 위한 클래스 추가
)
from PyQt5.QtCore import Qt, QFileSystemWatcher, pyqtSlot
import xml.etree.ElementTree as ET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.load_last_selected_files()  # 이전에 선택한 파일들을 로드

        self.current_class = None  # 현재 선택된 Class를 저장할 변수
        self.current_subclass = None  # 현재 선택된 Subclass를 저장할 변수
        self.last_selected_files = []  # 이전에 선택한 파일들을 저장할 변수 추가
        
        self.xml_files = []
        self.object_data = []  # List to store object information
        self.cuboid_ids = set()  # Set to store unique cuboid_id values in the XML files

        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.handle_file_changed)

        # Initial setup to monitor the XML files
        if self.last_selected_files:
            self.setup_file_watching(self.last_selected_files)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(20, 590, 380, 30)
        self.progress_bar.setValue(0)

        self.setWindowTitle("Annotation Modifier")
        self.setGeometry(200, 200, 400, 700)

        self.label_copyright = QLabel("Copyright 2023.oddhyeon.All right reserved. ", self)
        self.label_copyright.setGeometry(20, 620, 360, 30)

        self.label_files = QLabel("Selected Files: ", self)
        self.label_files.setGeometry(20, 30, 360, 30)

        self.label_truncation = QLabel("Truncation Value: 0.00", self)
        self.label_truncation.setGeometry(20, 70, 200, 30)

        self.slider_truncation = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_truncation.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_truncation.setGeometry(20, 110, 360, 30)
        self.slider_truncation.setRange(0, 99)
        self.slider_truncation.setTickInterval(1)
        self.slider_truncation.setSingleStep(1)
        self.slider_truncation.valueChanged.connect(self.update_truncation)

        self.label_occlusion = QLabel("Occlusion Value: 0", self)
        self.label_occlusion.setGeometry(20, 150, 200, 30)

        self.slider_occlusion = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_occlusion.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_occlusion.setGeometry(20, 190, 360, 30)
        self.slider_occlusion.setRange(0, 4)
        self.slider_occlusion.setTickInterval(1)
        self.slider_occlusion.setSingleStep(1)
        self.slider_occlusion.valueChanged.connect(self.update_occlusion)

        self.label_cuboid_id = QLabel("Cuboid ID: ", self)
        self.label_cuboid_id.setGeometry(20, 230, 100, 30)

        self.line_edit_cuboid_id = QLineEdit(self)  # 추가: Cuboid ID를 입력받는 QLineEdit
        self.line_edit_cuboid_id.setGeometry(130, 230, 60, 30)
        self.line_edit_cuboid_id.setPlaceholderText("Edit ID")  # 미리 보이는 힌트 텍스트

        self.slider_cuboid_id = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_cuboid_id.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_cuboid_id.setGeometry(20, 270, 360, 30)
        self.slider_cuboid_id.setTickInterval(1)
        self.slider_cuboid_id.setSingleStep(1)
        self.slider_cuboid_id.valueChanged.connect(self.update_cuboid_id)

        self.label_start_index = QLabel("Start Index: 1", self)
        self.label_start_index.setGeometry(20, 310, 100, 30)

        self.slider_start_index = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_start_index.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_start_index.setGeometry(130, 310, 250, 30)
        self.slider_start_index.setTickInterval(1)
        self.slider_start_index.setSingleStep(1)
        self.slider_start_index.valueChanged.connect(self.update_start_index)

        self.label_end_index = QLabel("End Index: 1", self)
        self.label_end_index.setGeometry(20, 350, 100, 30)

        self.slider_end_index = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_end_index.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider_end_index.setGeometry(130, 350, 250, 30)
        self.slider_end_index.setTickInterval(1)
        self.slider_end_index.setSingleStep(1)
        self.slider_end_index.valueChanged.connect(self.update_end_index)
        
        # Start Index 바와 관련된 버튼 위치 조정
        self.button_start_index_plus = QPushButton("+", self)
        self.button_start_index_plus.setGeometry(420, 310, 30, 30)
        self.button_start_index_plus.clicked.connect(self.increment_start_index)

        self.button_start_index_minus = QPushButton("-", self)
        self.button_start_index_minus.setGeometry(390, 310, 30, 30)
        self.button_start_index_minus.clicked.connect(self.decrement_start_index)

        # End Index 바와 관련된 버튼 위치 조정
        self.button_end_index_plus = QPushButton("+", self)
        self.button_end_index_plus.setGeometry(420, 350, 30, 30)
        self.button_end_index_plus.clicked.connect(self.increment_end_index)

        self.button_end_index_minus = QPushButton("-", self)
        self.button_end_index_minus.setGeometry(390, 350, 30, 30)
        self.button_end_index_minus.clicked.connect(self.decrement_end_index)


        self.label_class = QLabel("Class: ", self)
        self.label_class.setGeometry(20, 390, 100, 30)

        self.combo_class = QComboBox(self)
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

        self.label_subclass = QLabel("Subclass: ", self)
        self.label_subclass.setGeometry(20, 430, 100, 30)

        self.combo_subclass = QComboBox(self)
        self.combo_subclass.setGeometry(130, 430, 250, 30)
        self.combo_subclass.addItems(
            ["Normal", "Emergency", "SchoolBus", "None", "noRider", "Rider"]
        )

        self.button_select_files = QPushButton("Select XML Files", self)
        self.button_select_files.setGeometry(20, 470, 120, 30)
        self.button_select_files.clicked.connect(self.select_files)

        self.button_modify = QPushButton("Modify XML", self)
        self.button_modify.setGeometry(150, 470, 120, 30)
        self.button_modify.clicked.connect(self.modify_xml)
        self.button_modify.setEnabled(False)

        self.button_delete_object = QPushButton("Delete Object", self)
        self.button_delete_object.setGeometry(280, 470, 100, 30)
        self.button_delete_object.clicked.connect(self.delete_object)
        self.button_delete_object.setEnabled(False)

        self.label_file_info = QLabel("File Count: 0, Selected Count: 0, File Range: N/A", self)
        self.label_file_info.setGeometry(20, 510, 360, 30)

        # Combine Class and Subclass selection enable/disable checkboxes
        self.checkbox_enable_class_subclass = QCheckBox("Enable Class and Subclass Selection", self)
        self.checkbox_enable_class_subclass.setGeometry(20, 550, 350, 30)
        self.checkbox_enable_class_subclass.setChecked(False)  # 체크박스 초기에 체크되지 않은 상태로 설정
        self.checkbox_enable_class_subclass.stateChanged.connect(self.toggle_class_subclass_selection)

        # 초기에 클래스와 서브클래스의 선택 상태를 저장하는 변수 추가
        self.is_class_enabled = False
        self.is_subclass_enabled = False

        # Initially, disable Class and Subclass selection
        self.combo_class.setEnabled(False)
        self.combo_subclass.setEnabled(False)

        # Call the method to set initial state based on the checkbox
        self.toggle_class_subclass_selection(self.checkbox_enable_class_subclass.isChecked())
        

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
        # Add XML files to the watcher for monitoring
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
            print(f"ID {cuboid_id}에 연결된 객체가 {len(files_with_cuboid_id)}개의 파일에서 삭제되었습니다.")
        else:
            print(f"ID {cuboid_id}에 연결된 객체가 없습니다.")


    def toggle_class_subclass_selection(self, state):
        # 클래스와 서브클래스 선택 콤보 박스 활성화/비활성화
        if state == Qt.CheckState.Checked:  # 체크박스가 체크된 경우
            self.combo_class.setEnabled(True)
            self.combo_subclass.setEnabled(True)
            # 선택한 값을 저장해둡니다.
            self.current_class = self.combo_class.currentText()
            self.current_subclass = self.combo_subclass.currentText()
        else:  # 체크박스가 체크되지 않은 경우
            self.combo_class.setEnabled(False)
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
        self.label_truncation.setText(f"Truncation Value: {truncation_value:.2f}")

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
            self.last_selected_files = xml_files  # 선택한 파일들을 last_selected_files에 저장
            self.save_last_selected_files()  # 선택한 파일들을 파일로 저장
            self.xml_files.sort()

            self.label_files.setText(f"Selected Files: {', '.join(self.xml_files)}")
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
            # 파일을 선택하지 않았을 때, 이전에 선택한 파일들을 다시 불러옴
            self.xml_files = self.last_selected_files
            # 이전에 선택한 파일들로 프로그램 상태를 업데이트
            self.update_file_info()
            # "Modify XML" 버튼은 여전히 활성화되도록 설정
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

    def refresh_program(self):
        # 이전에 선택한 파일들로 프로그램 화면을 새로고침하여 반영
        self.xml_files = self.last_selected_files
        self.update_file_info()
        # "Modify XML" 버튼은 여전히 활성화되도록 설정
        self.button_modify.setEnabled(True)
        self.button_delete_object.setEnabled(True)


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
        if self.last_selected_files:
            total_files = len(self.last_selected_files)
            processed_files = 0

            selected_files = self.last_selected_files
            start_index = self.slider_start_index.value()
            end_index = self.slider_end_index.value()
            selected_files = selected_files[start_index - 1:end_index]

            cuboid_id_text = self.line_edit_cuboid_id.text().strip()
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
                                obj.find("cuboid_id").text = str(cuboid_id_text)

                            obj.find("truncation").text = str(truncation)
                            obj.find("occlusion").text = str(occlusion)

                            if self.checkbox_enable_class_subclass.isChecked():
                                obj.find("class").text = self.combo_class.currentText()
                                obj.find("subclass").text = self.combo_subclass.currentText()

                    tree.write(xml_file)
                    processed_files += 1
                    progress = int((processed_files / total_files) * 100)
                    self.progress_bar.setValue(progress)
                    print(f"XML 파일 '{xml_file}'이 성공적으로 수정되었습니다.")
                except ET.ParseError as e:
                    print(f"XML 파일 '{xml_file}' 파싱 중 오류가 발생하였습니다:", str(e))
                except FileNotFoundError:
                    print(f"XML 파일 '{xml_file}'이 존재하지 않습니다.")

            self.refresh_program()
            self.progress_bar.setValue(100)  # 작업 완료 후 100%로 설정

    def restart_program(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
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
                selected_files = self.xml_files[start_index - 1 : end_index]

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
