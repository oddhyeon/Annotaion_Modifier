# Annotaion_Modifier
해당 XML Editor는 현재 사용중인 Alchera Annotation Tool에 생산성을 돕기 위해 만든 프로그램입니다.


# GUI

## 1. Active Tab : 

### Truncation 슬라이더와 레이블
Truncation Value 레이블: 현재 Truncation 값을 보여줍니다.
Truncation 슬라이더: Truncation 값을 조정할 수 있는 슬라이더입니다. 0부터 0.99 사이의 값을 선택할 수 있습니다.

### Occlusion 슬라이더와 레이블
Occlusion Value 레이블: 현재 Occlusion 값을 보여줍니다.
Occlusion 슬라이더: Occlusion 값을 조정할 수 있는 슬라이더입니다. 0부터 4까지의 값을 선택할 수 있습니다.

### Cuboid ID 슬라이더와 레이블, QLineEdit
Cuboid ID: 레이블: 현재 선택된 Cuboid ID를 보여줍니다.
Modify ID: Cuboid ID를 직접 입력할 수 있는 텍스트 상자입니다. 입력한 Cuboid ID는 슬라이더의 값과 동기화됩니다.
Cuboid ID 슬라이더: Cuboid ID 값을 조정할 수 있는 슬라이더입니다. 1부터 설정된 최대 Cuboid ID까지 값을 선택할 수 있습니다.

### Start Index 슬라이더와 레이블
Start Index: 1 레이블: 현재 선택된 Start Index를 보여줍니다.
Start Index 슬라이더: XML 파일 목록에서 편집할 파일의 시작 인덱스를 선택할 수 있는 슬라이더입니다. 1부터 설정된 최대 파일 개수까지 값을 선택할 수 있습니다.

### End Index 슬라이더와 레이블
End Index: 1 레이블: 현재 선택된 End Index를 보여줍니다.
End Index 슬라이더: XML 파일 목록에서 편집할 파일의 마지막 인덱스를 선택할 수 있는 슬라이더입니다. 1부터 설정된 최대 파일 개수까지 값을 선택할 수 있습니다.

### Start Index와 End Index를 조작하는 버튼
"+" 버튼: Start Index 또는 End Index를 1 증가시킵니다.
"-" 버튼: Start Index 또는 End Index를 1 감소시킵니다.

### Enable Class and Subclass Selection 체크박스
Class와 Subclass 선택을 활성화하는 체크박스입니다. 체크되면 Class와 Subclass 선택 콤보 박스가 활성화됩니다.

### Class와 Subclass 선택 콤보 박스
Class: 현재 선택된 클래스를 보여주고 변경할 수 있는 콤보 박스입니다.
Subclass: 현재 선택된 서브클래스를 보여주고 변경할 수 있는 콤보 박스입니다. Class가 변경되면 Subclass 목록이 업데이트됩니다.

### Select XML Files 버튼
XML 파일을 선택하는 파일 선택 대화상자를 엽니다.

### Modify XML 버튼
선택한 XML 파일들의 객체 정보를 수정합니다. Truncation, Occlusion, Cuboid ID 등을 선택한 값으로 변경합니다.

### Delete Object 버튼
선택한 Class, Subclass, Cuboid ID에 해당하는 객체를 XML 파일에서 삭제합니다.

### File Count, Selected Count, File Range 정보 텍스트 레이블 :
선택한 파일의 개수, 편집 대상으로 선택된 파일의 개수, 선택한 파일 범위를 보여줍니다.

### Copyright 텍스트 레이블 :
프로그램에 대한 저작권 정보를 보여줍니다.


## 2. Lotation Tab :

### Select XML Files 버튼:

이 버튼을 클릭하면 파일 대화상자가 열리며, 여러 개의 XML 파일들을 선택할 수 있습니다.
이 XML 파일들에는 서로 다른 큐보이드에 대한 정보가 들어 있어야 합니다.
XML 파일들을 선택한 후, 프로그램은 파일들을 읽고, "cuboid_id" 값을 추출하여 보여줍니다.

### Coboid ID 슬라이더:

이 슬라이더를 사용하여 원하는 특정 "cuboid_id" 값을 선택할 수 있습니다.
슬라이더의 최소값과 최대값은 선택된 XML 파일들에 있는 "cuboid_id" 값들을 기준으로 결정됩니다.
슬라이더를 이동하면 현재 선택된 "cuboid_id" 값을 표시합니다.


### Start Index 슬라이더:

이 슬라이더를 사용하여 작업하려는 XML 파일들의 범위의 시작 인덱스를 선택할 수 있습니다.
슬라이더의 최소값은 1이고, 최대값은 선택된 XML 파일들의 총 개수입니다.
슬라이더를 이동하면 현재 선택된 시작 인덱스와 해당하는 파일 이름을 표시합니다.

### End Index 슬라이더:

이 슬라이더를 사용하여 작업하려는 XML 파일들의 범위의 끝 인덱스를 선택할 수 있습니다.
슬라이더의 최소값은 1이고, 최대값은 선택된 XML 파일들의 총 개수입니다.
슬라이더를 이동하면 현재 선택된 끝 인덱스와 해당하는 파일 이름을 표시합니다.

### Selected Index 슬라이더:

이 슬라이더를 사용하여 시작과 끝 인덱스 슬라이더로 지정된 범위 내의 특정 XML 파일을 선택할 수 있습니다.
슬라이더의 최소값은 1이고, 최대값은 선택된 XML 파일들의 총 개수입니다.
슬라이더를 이동하면 현재 선택된 인덱스와 해당하는 파일 이름을 표시합니다.

### Copy 버튼:

이 버튼을 클릭하여 선택한 큐보이드의 정보를 지정한 범위 내의 다른 XML 파일로 복사할 수 있습니다.
"cuboid_id" 값으로 선택한 큐보이드의 객체 정보를 "selected_index"에 해당하는 XML 파일로부터 읽어온 후, "start_index"와 "end_index" 슬라이더로 지정한 범위 내의 다른 XML 파일들에 해당 정보를 복사합니다.
복사하기 전에, 선택한 큐보이드의 위치 정보가 없거나 "N/A" 값만 포함되어 있는지 확인합니다. 만약 그런 경우에는 확인 대화상자를 표시하여 복사를 진행할지 물어봅니다.
복사 후, 성공적으로 정보가 추가된 파일들의 목록을 출력합니다.

### Object Information:

이 부분은 현재 선택된 큐보이드에 대한 다양한 속성들을 표시합니다. (객체 정보)
표시되는 속성들은 "차원" (높이, 너비, 길이), "위치" (x3d, y3d, z3d), "박스" (최소 X, 최소 Y, 최대 X, 최대 Y), "알파", "거리" 등입니다.
표시되는 값들은 현재 선택된 "cuboid_id"와 "selected_index"를 기준으로 선택된 XML 파일로부터 추출됩니다.

## 3. Help Tab
해당 깃헙으로 연결됩니다.
