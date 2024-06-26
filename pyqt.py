import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox,QPushButton
from PyQt5.QtCore import Qt, QMimeDatabase
import subprocess
from pathlib import Path
from .settings import PORT_NUM, IP, USER, HOME, HOME_PATH


"""
프로젝트 이름: PiSync
라즈베리파이 서버랑 로컬 컴퓨터랑 연동하여 파일 이동이 쉽게 하는 프로그램
ToDo:
- SW 
    - 프로그램 프로젝트 폴더 구성
    
- UI
    - running 상태인지 확인하는 상태 바?
    - 현재 폴더 구조 시각적으로 표현
        - 현재 서버랑 네트워크 연결 상태

- Feature
    - 보내는 폴더인지 파일인지 구분
    - 가져오기도 가능하게
    - 보냈을 때 파일 권한 바로 주기
    - 보내거나 가져오는 상태 바
    - 로그 및 이력 기능 (아직 어디에 할 진 모르겠다)
    - 보낼 때 파일 크기 알려주기
    - 이미지 파일 자동 태깅? 및 파일 분류?
    - 얼굴 인식 기능(맥 화면에서 하면 될 듯?) or 행동 인식
"""

#파일 끌어오는 부분
class FileLabel(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel('파일을 끌어오세요', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet('''
                                    QLabel{
                                        border: 4px dashed #aaa;
                                        font-size: 15pt;
                                    }
                                ''')
        
        self.quit_button = QPushButton('그만 하기', self)
        self.quit_button.clicked.connect(self.quit_app)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.quit_button)
        self.setLayout(layout)

    def quit_app(self):
        reply = QMessageBox(self)
        reply.setStyleSheet('''
            QPushButton {
                background-color: #aaa;
                color: white;
            }
            QLabel{
                font-size: 15pt;
            }
        ''')
        reply.setWindowTitle('종료 확인')
        reply.setText('정말로 종료하시겠습니까?')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if reply.exec_() == QMessageBox.Yes:
            QApplication.quit()
        
class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(400, 400)
        self.setAcceptDrops(True)

        layout = QVBoxLayout()

        self.filebox = FileLabel()
        layout.addWidget(self.filebox)

        self.setLayout(layout)
        self.setWindowTitle('File Drap&Drop')

    #파일 끌어오기
    def dragEnterEvent(self, event):
        if self.find_pdf(event.mimeData()):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self.find_pdf(event.mimeData()):
            event.accept()
        else:
            event.ignore()

    #파일 놓기
    def dropEvent(self, event):
        urls = self.find_pdf(event.mimeData())
        if urls:
            for url in urls:

                reply = QMessageBox.question(self, '마칠까요?', '서버로 파일을 전송하시겠습니까?',
                                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.rsync(str(url.toLocalFile())) # 서버로 파일 보내기
                    QMessageBox.information(self, '완료', '서버로 파일 전송이 완료되었습니다!', QMessageBox.Ok)
                else:
                    QMessageBox.information(self, '취소', '서버로 파일 전송이 취소되었습니다.', QMessageBox.Ok)
            event.accept()
        else:
            event.ignore()
            
    #파일 보내기
    def rsync(self, path):
        # rsync 명령어와 옵션을 설정합니다.
        command = ['rsync', '-avz', '-e', f'ssh -i {HOME}/.ssh/my_server -p {PORT_NUM}',
                   path,'{USER}@{IP}:{HOME_PATH}/mnt/']
        # subprocess.run()을 사용하여 rsync를 실행합니다.
        subprocess.run(command)
        
    def find_pdf(self, mimedata):
        urls = list()
        db = QMimeDatabase()
        for url in mimedata.urls():
            mimetype = db.mimeTypeForUrl(url)
            if mimetype.name() == "inode/directory":
                urls.append(url)
        return urls

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyApp()
    myWindow.show()
    app.exec_()