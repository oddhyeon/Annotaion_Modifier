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
)
from PyQt5.QtCore import Qt
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

        self.setWindowTitle("Annotation Modifier")
        self.setGeometry(200, 200, 400, 700)

        self.label_copyright = QLabel("Copyright 2023.oddhyeon.All right reserved. ", self)
        self.label_copyright.setGeometry(20, 650, 360, 30)

        self.label_files = QLabel("Selected Files: ", self)
        self.label_files.setGeometry(20, 30, 360, 30)

        self.label_truncation = QLabel("Truncation Value: 0.00", self)
        self.label_truncation.setGeometry(20, 70, 200, 30)

        self.slider_truncation = QSlider(Qt.Horizontal, self)
        self.slider_truncation.setFocusPolicy(Qt.NoFocus)
        self.slider_truncation.setGeometry(20, 110, 360, 30)
        self.slider_truncation.setRange(0, 99)
        self.slider_truncation.setTickInterval(1)
        self.slider_truncation.setSingleStep(1)
        self.slider_truncation.valueChanged.connect(self.update_truncation)

        self.label_occlusion = QLabel("Occlusion Value: 0", self)
        self.label_occlusion.setGeometry(20, 150, 200, 30)

        self.slider_occlusion = QSlider(Qt.Horizontal, self)
        self.slider_occlusion.setFocusPolicy(Qt.NoFocus)
        self.slider_occlusion.setGeometry(20, 190, 360, 30)
        self.slider_occlusion.setRange(0, 4)
        self.slider_occlusion.setTickInterval(1)
        self.slider_occlusion.setSingleStep(1)
        self.slider_occlusion.valueChanged.connect(self.update_occlusion)

        self.label_cuboid_id = QLabel("Cuboid ID: ", self)
        self.label_cuboid_id.setGeometry(20, 230, 100, 30)

        self.line_edit_cuboid_id = QLineEdit(self)  # 추가: Cuboid ID를 입력받는 QLineEdit
        self.line_edit_cuboid_id.setGeometry(130, 230, 250, 30)
        self.line_edit_cuboid_id.setPlaceholderText("Enter Cuboid ID")  # 미리 보이는 힌트 텍스트

        self.slider_cuboid_id = QSlider(Qt.Horizontal, self)
        self.slider_cuboid_id.setFocusPolicy(Qt.NoFocus)
        self.slider_cuboid_id.setGeometry(20, 270, 360, 30)
        self.slider_cuboid_id.setTickInterval(1)
        self.slider_cuboid_id.setSingleStep(1)
        self.slider_cuboid_id.valueChanged.connect(self.update_cuboid_id)

        self.label_start_index = QLabel("Start Index: 1", self)
        self.label_start_index.setGeometry(20, 310, 100, 30)

        self.slider_start_index = QSlider(Qt.Horizontal, self)
        self.slider_start_index.setFocusPolicy(Qt.NoFocus)
        self.slider_start_index.setGeometry(130, 310, 250, 30)
        self.slider_start_index.setTickInterval(1)
        self.slider_start_index.setSingleStep(1)
        self.slider_start_index.valueChanged.connect(self.update_start_index)

        self.label_end_index = QLabel("End Index: 1", self)
        self.label_end_index.setGeometry(20, 350, 100, 30)

        self.slider_end_index = QSlider(Qt.Horizontal, self)
        self.slider_end_index.setFocusPolicy(Qt.NoFocus)
        self.slider_end_index.setGeometry(130, 350, 250, 30)
        self.slider_end_index.setTickInterval(1)
        self.slider_end_index.setSingleStep(1)
        self.slider_end_index.valueChanged.connect(self.update_end_index)

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
        self.checkbox_enable_class_subclass.stateChanged.connect(self.toggle_class_subclass_selection)

        # Initially, disable Class and Subclass selection
        self.combo_class.setEnabled(False)
        self.combo_subclass.setEnabled(False)

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
        self.combo_class.setEnabled(state == Qt.Checked)
        self.combo_subclass.setEnabled(state == Qt.Checked)

        # 활성화 상태일 때 현재 선택된 Class와 Subclass 값을 저장
        if state == Qt.Checked:
            self.current_class = self.combo_class.currentText()
            self.current_subclass = self.combo_subclass.currentText()
        else:
            # 비활성화 상태일 때 이전에 저장한 값을 그대로 유지
            self.combo_class.setCurrentText(self.current_class)
            self.combo_subclass.setCurrentText(self.current_subclass)

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
        self.combo_class.setEnabled(state == Qt.Checked)

    def toggle_subclass_selection(self, state):
        self.combo_subclass.setEnabled(state == Qt.Checked)


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
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
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
        if self.last_selected_files:  # last_selected_files를 이용하여 XML 파일 수정
            selected_files = self.last_selected_files  # 이전에 선택한 파일들을 가져옴
            cuboid_id_text = self.line_edit_cuboid_id.text()
            cuboid_id = self.slider_cuboid_id.value()
            truncation = self.slider_truncation.value() / 100.0
            occlusion = self.slider_occlusion.value()
            start_index = self.slider_start_index.value()
            end_index = self.slider_end_index.value()
            selected_files = selected_files[start_index - 1:end_index]  # 선택된 파일들로 제한

            cuboid_id_text = self.line_edit_cuboid_id.text().strip()  # Cuboid ID 입력 값 가져오기

            for xml_file in selected_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    for obj in root.iter("object"):
                        obj_cuboid_id = int(obj.find("cuboid_id").text)
                        if obj_cuboid_id == self.slider_cuboid_id.value():
                            # Cuboid ID가 1로 변경되지 않도록 처리
                            if cuboid_id_text:
                                obj.find("cuboid_id").text = str(cuboid_id_text)

                            # 나머지 정보들은 항상 수정
                            obj.find("truncation").text = str(truncation)
                            obj.find("occlusion").text = str(occlusion)

                            # 현재 Class와 Subclass 값이 비활성화 상태라면 이전에 저장한 값을 사용
                            if self.checkbox_enable_class_subclass.isChecked():
                                obj.find("class").text = self.combo_class.currentText()
                                obj.find("subclass").text = self.combo_subclass.currentText()

                    tree.write(xml_file)
                    print(f"XML 파일 '{xml_file}'이 성공적으로 수정되었습니다.")
                except ET.ParseError as e:
                    print(f"XML 파일 '{xml_file}' 파싱 중 오류가 발생하였습니다:", str(e))
                except FileNotFoundError:
                    print(f"XML 파일 '{xml_file}'이 존재하지 않습니다.")
            self.refresh_program()


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
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
