import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.xml_files = []
        self.object_data = []  # 오브젝트 정보를 저장할 리스트
        self.cuboid_ids = set()  # XML 파일에 포함된 고유한 cuboid_id 값들을 저장할 집합

        self.setWindowTitle("Annotation Modifier")
        self.setGeometry(200, 200, 400, 400)

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

        self.button_select_files = QPushButton("Select XML Files", self)
        self.button_select_files.setGeometry(20, 390, 120, 30)
        self.button_select_files.clicked.connect(self.select_files)

        self.button_modify = QPushButton("Modify XML", self)
        self.button_modify.setGeometry(150, 390, 120, 30)
        self.button_modify.clicked.connect(self.modify_xml)
        self.button_modify.setEnabled(False)

        self.button_delete_object = QPushButton("Delete Object", self)
        self.button_delete_object.setGeometry(280, 390, 100, 30)
        self.button_delete_object.clicked.connect(self.delete_object)
        self.button_delete_object.setEnabled(False)

        self.label_file_count = QLabel("File Count: 0", self)
        self.label_file_count.setGeometry(20, 430, 200, 30)

        self.label_selected_count = QLabel("Selected Count: 0", self)
        self.label_selected_count.setGeometry(20, 470, 200, 30)

        self.label_file_range = QLabel("File Range: ", self)
        self.label_file_range.setGeometry(20, 510, 200, 30)

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
        self.update_selected_count()
        self.update_file_range()

    def update_end_index(self, value):
        end_index = value
        self.label_end_index.setText(f"End Index: {end_index}")
        self.update_selected_count()
        self.update_file_range()

    def select_files(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
        self.xml_files, _ = file_dialog.getOpenFileNames(self, "Select XML Files", "", "XML Files (*.xml)", options=options)
        self.xml_files.sort()

        if self.xml_files:
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
            self.update_file_count()
            self.update_selected_count()
            self.update_file_range()

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
        if self.xml_files:
            start_index = self.slider_start_index.value()
            end_index = self.slider_end_index.value()
            cuboid_id = self.slider_cuboid_id.value()
            truncation = self.slider_truncation.value() / 100.0
            occlusion = self.slider_occlusion.value()

            selected_files = self.xml_files[start_index - 1 : end_index]

            for xml_file in selected_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    for obj in root.iter("object"):
                        obj_cuboid_id = int(obj.find("cuboid_id").text)
                        if obj_cuboid_id == cuboid_id:
                            obj.find("truncation").text = str(truncation)
                            obj.find("occlusion").text = str(occlusion)

                    tree.write(xml_file)
                    print(f"XML 파일 '{xml_file}'이 성공적으로 수정되었습니다.")
                except ET.ParseError as e:
                    print(f"XML 파일 '{xml_file}' 파싱 중 오류가 발생하였습니다:", str(e))
                except FileNotFoundError:
                    print(f"XML 파일 '{xml_file}'이 존재하지 않습니다.")

    def delete_object(self):
        if self.xml_files:
            start_index = self.slider_start_index.value()
            end_index = self.slider_end_index.value()
            cuboid_id = self.slider_cuboid_id.value()

            selected_files = self.xml_files[start_index - 1 : end_index]

            for xml_file in selected_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    for obj in root.findall("object"):
                        obj_cuboid_id = int(obj.find("cuboid_id").text)
                        if obj_cuboid_id == cuboid_id:
                            root.remove(obj)

                    tree.write(xml_file)
                    print(f"XML 파일 '{xml_file}'에서 cuboid_id '{cuboid_id}'를 가진 객체가 삭제되었습니다.")
                except ET.ParseError as e:
                    print(f"XML 파일 '{xml_file}' 파싱 중 오류가 발생하였습니다:", str(e))
                except FileNotFoundError:
                    print(f"XML 파일 '{xml_file}'이 존재하지 않습니다.")

    def update_file_count(self):
        file_count = len(self.xml_files)
        self.label_file_count.setText(f"File Count: {file_count}")

    def update_selected_count(self):
        selected_count = max(0, self.slider_end_index.value() - self.slider_start_index.value() + 1)
        self.label_selected_count.setText(f"Selected Count: {selected_count}")

    def update_file_range(self):
        start_index = self.slider_start_index.value()
        end_index = self.slider_end_index.value()

        if self.xml_files:
            start_range = self.xml_files[start_index - 1][-8:-4]
            end_range = self.xml_files[end_index - 1][-8:-4]
            file_range = f"File Range: {start_range} to {end_range}"
        else:
            file_range = "File Range: N/A"

        self.label_file_range.setText(file_range)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
