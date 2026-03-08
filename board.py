import sys
import os
import cv2
import random
import shutil
import numpy as np
import subprocess
import threading

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QGridLayout, QVBoxLayout, QHBoxLayout, QLineEdit,
    QMessageBox
)

from PyQt5.QtCore import Qt, QTimer


class ControlPanel(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Animal Detection Panel")
        self.setFixedSize(420,420)

        main_layout = QVBoxLayout()

        self.codes = {
            "0001": "monkey",
            "0002": "elephant",
            "0003": "deer",
            "0011": "pig"
        }

        self.sequence = ""
        self.current_input = ""
        self.selected_animals = []

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_invalid)

        self.blink_count = 0
        self.blink_visible = True

        self.train_light = self.create_light("grey")
        self.start_light = self.create_light("grey")
        self.stop_light = self.create_light("grey")

        self.detect_process = None
        self.best_model_path = None

        start_btn = QPushButton("Start")
        stop_btn = QPushButton("Stop")

        start_btn.clicked.connect(self.start_clicked)
        stop_btn.clicked.connect(self.stop_clicked)

        top_layout = QVBoxLayout()

        lights_row = QHBoxLayout()
        lights_row.setAlignment(Qt.AlignCenter)
        lights_row.setSpacing(60)

        lights_row.addWidget(self.train_light)
        lights_row.addWidget(self.start_light)
        lights_row.addWidget(self.stop_light)

        buttons_row = QHBoxLayout()
        buttons_row.setAlignment(Qt.AlignCenter)
        buttons_row.setSpacing(60)

        buttons_row.addSpacing(40)
        buttons_row.addWidget(start_btn)
        buttons_row.addWidget(stop_btn)

        top_layout.addLayout(lights_row)
        top_layout.addLayout(buttons_row)

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(55)

        self.display.setStyleSheet("""
        QLineEdit {
            border:3px solid black;
            font-size:20px;
        }
        """)

        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(8)

        buttons = ['0','1','2','3']

        for i,num in enumerate(buttons):

            btn = QPushButton(num)
            btn.setFixedSize(70,50)
            btn.clicked.connect(self.number_pressed)

            keypad_layout.addWidget(btn,0,i)

        add_btn = QPushButton("Add")
        self.train_btn = QPushButton("Train")
        backspace_btn = QPushButton("Delete")

        self.train_btn.setEnabled(False)

        add_btn.clicked.connect(self.add_pressed)
        self.train_btn.clicked.connect(self.train_pressed)
        backspace_btn.clicked.connect(self.backspace_pressed)

        keypad_layout.addWidget(add_btn,1,0)
        keypad_layout.addWidget(backspace_btn,1,1)
        keypad_layout.addWidget(self.train_btn,1,2,1,2)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.display)
        main_layout.addLayout(keypad_layout)

        self.setLayout(main_layout)

        self.set_lights(stop=True)
        self.display.setText("Stopped")

        # Try to load existing model from previous training session
        self._load_existing_model()

    def _load_existing_model(self):
        """Load an existing trained model if available from a previous session."""
        try:
            existing_model = self.get_latest_model()
            if os.path.exists(existing_model):
                self.best_model_path = existing_model
        except:
            # No existing model found, which is fine on first run
            pass

    def create_light(self,color):

        light = QLabel()
        light.setFixedSize(26,26)

        light.setStyleSheet(f"""
        background-color:{color};
        border-radius:13px;
        border:2px solid black;
        """)

        return light


    def set_lights(self,train=False,start=False,stop=False):

        self.train_light.setStyleSheet(
            f"background-color:{'yellow' if train else 'grey'}; border-radius:13px; border:2px solid black")

        self.start_light.setStyleSheet(
            f"background-color:{'green' if start else 'grey'}; border-radius:13px; border:2px solid black")

        self.stop_light.setStyleSheet(
            f"background-color:{'red' if stop else 'grey'}; border-radius:13px; border:2px solid black")


    def start_clicked(self):

        self.display.setText("Running")
        self.set_lights(start=True)

        self.run_detection()


    def stop_clicked(self):

        self.display.setText("Stopped")
        self.set_lights(stop=True)

        if self.detect_process and self.detect_process.poll() is None:
            self.detect_process.terminate()


    def number_pressed(self):

        btn = self.sender()

        self.current_input += btn.text()

        self.display.setText(self.sequence + self.current_input)


    def add_pressed(self):

        if self.current_input in self.codes:

            animal = self.codes[self.current_input]

            if animal not in self.selected_animals:

                self.selected_animals.append(animal)

                self.sequence += self.current_input + ","

                self.train_btn.setEnabled(True)

            self.current_input = ""

            self.display.setText(self.sequence)

        else:

            self.display.setText(self.current_input)

            self.blink_count = 0
            self.blink_visible = True

            self.blink_timer.start(300)


    def blink_invalid(self):

        if self.blink_visible:

            self.display.setStyleSheet("""
            QLineEdit {border:3px solid black;font-size:20px;color:red;}
            """)
        else:
            self.display.setStyleSheet("""
            QLineEdit {border:3px solid black;font-size:20px;color:black;}
            """)

        self.blink_visible = not self.blink_visible
        self.blink_count += 1

        if self.blink_count >= 6:

            self.blink_timer.stop()

            self.display.setStyleSheet("""
            QLineEdit {border:3px solid black;font-size:20px;color:black;}
            """)

            self.display.setText(self.sequence)
            self.current_input = ""


    def backspace_pressed(self):

        if self.current_input != "":
            self.current_input = ""

        else:
            if self.sequence != "":

                parts = self.sequence.strip(",").split(",")

                removed = parts.pop()

                self.sequence = ",".join(parts)

                if self.sequence != "":
                    self.sequence += ","

                if removed in self.codes:

                    animal = self.codes[removed]

                    if animal in self.selected_animals:
                        self.selected_animals.remove(animal)

        self.display.setText(self.sequence + self.current_input)

        if len(self.selected_animals) == 0:
            self.train_btn.setEnabled(False)


    def paste_animal(self,bg,animal_img):

        bg = bg.copy()

        h_bg,w_bg = bg.shape[:2]
        h,w = animal_img.shape[:2]

        target_w = int(w_bg * random.uniform(0.12,0.32))
        scale = target_w / w

        new_w = int(w * scale)
        new_h = int(h * scale)

        animal_img = cv2.resize(animal_img,(new_w,new_h))

        # ---- random rotation ----
        angle = random.uniform(-12,12)
        M = cv2.getRotationMatrix2D((new_w/2,new_h/2),angle,1)
        animal_img = cv2.warpAffine(
            animal_img,
            M,
            (new_w,new_h),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0,0,0,0)
        )

        h,w = animal_img.shape[:2]

        x = random.randint(0,w_bg-w)
        y = random.randint(0,h_bg-h)

        # ---- SHADOW ----
        shadow = np.zeros_like(bg)
        shadow_y = y + int(h*0.9)

        cv2.ellipse(
            shadow,
            (x + w//2, shadow_y),
            (int(w*0.45), int(h*0.15)),
            0,0,360,
            (0,0,0),
            -1
        )

        shadow = cv2.GaussianBlur(shadow,(31,31),0)

        bg = cv2.addWeighted(bg,1,shadow,0.35,0)

        # ---- paste animal ----
        if animal_img.shape[2] == 4:

            alpha = animal_img[:,:,3] / 255.0
            alpha = alpha[:,:,None]

            animal_rgb = animal_img[:,:,:3]

            roi = bg[y:y+h,x:x+w]

            blended = roi*(1-alpha) + animal_rgb*alpha

            bg[y:y+h,x:x+w] = blended.astype(np.uint8)

        else:
            bg[y:y+h,x:x+w] = animal_img

        cx = (x + w/2) / w_bg
        cy = (y + h/2) / h_bg
        bw = w / w_bg
        bh = h / h_bg

        return bg,(cx,cy,bw,bh)
    
    def motion_blur(self,img):

        k = random.choice([5,7,9])

        kernel = np.zeros((k,k))
        kernel[int((k-1)/2),:] = np.ones(k)
        kernel = kernel / k

        return cv2.filter2D(img,-1,kernel)
    
    def fog_effect(self,img):

        fog = np.full_like(img,255)

        alpha = random.uniform(0.05,0.15)

        return cv2.addWeighted(img,1-alpha,fog,alpha,0)
    
    def random_occlusion(self,img):

        h,w = img.shape[:2]

        for _ in range(random.randint(1,4)):

            x1 = random.randint(0,w)
            x2 = random.randint(0,w)

            y1 = random.randint(0,h)
            y2 = random.randint(0,h)

            color = (
                random.randint(0,70),
                random.randint(60,120),
                random.randint(0,70)
            )

            thickness = random.randint(4,12)

            cv2.line(img,(x1,y1),(x2,y2),color,thickness)

        return img
    
    def color_temperature(self,img):

        r_shift = random.randint(-20,20)
        b_shift = random.randint(-20,20)

        img = img.astype(np.int16)

        img[:,:,2] += r_shift
        img[:,:,0] += b_shift

        img = np.clip(img,0,255).astype(np.uint8)

        return img


    def create_folders(self):

        if os.path.exists("train_data"):
            shutil.rmtree("train_data")

        paths = [
        "train_data/pictures/train",
        "train_data/pictures/val",
        # "train_data/labels/train",
        # "train_data/labels/val"
        ]

        for p in paths:
            os.makedirs(p)


    def dataset_size(self,n):

        if n==1: return 60,12
        if n==2: return 100,22
        if n==3: return 135,28
        if n==4: return 160,32


    def create_dataset_yaml(self):

        base = os.path.abspath("train_data")

        with open("dataset.yaml","w") as f:

            f.write(f"path: {base}\n")
            f.write("train: pictures/train\n")
            f.write("val: pictures/val\n\n")

            f.write("nc: 1\n")
            f.write('names: ["animal"]\n')


    def save_sample(self, img, labels, index, val):
        if index < val:
            img_path = f"train_data/pictures/val/img_{index}.jpg"
        else:
            img_path = f"train_data/pictures/train/img_{index}.jpg"

        # Updated: Save labels in the same directory as images
        label_path = img_path.replace('.jpg', '.txt')

        cv2.imwrite(img_path, img)

        with open(label_path, "w") as f:
            for l in labels:
                f.write(l + "\n")

        return index + 1


    def generate_dataset(self,bg):

        total,val = self.dataset_size(len(self.selected_animals))

        self.create_folders()

        cap_map = {1:60,2:50,3:45,4:40}

        cap = cap_map[len(self.selected_animals)]

        index = 0

        augment_loop = ["high","low","dusty","multi"]

        for animal in self.selected_animals:

            folder = f"pictures/{animal}"

            files = os.listdir(folder)

            random.shuffle(files)

            count = 0

            # ---- Mandatory Normal Images ----
            for file in files:

                if count >= cap: break

                path = os.path.join(folder,file)

                animal_img = cv2.imread(path,cv2.IMREAD_UNCHANGED)

                img,bbox = self.paste_animal(bg,animal_img)

                label = f"0 {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}"

                index = self.save_sample(img,[label],index,val)

                count += 1


            aug_index = 0
            multi_counter = 0

            while count < cap:

                aug = augment_loop[aug_index % 4]

                aug_index += 1

                base_animal = animal

                file = random.choice(files)

                path = os.path.join(folder,file)

                animal_img = cv2.imread(path,cv2.IMREAD_UNCHANGED)

                img,bbox = self.paste_animal(bg,animal_img)

                labels = [
                    f"0 {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}"
                ]

                if aug=="high":
                    img = cv2.convertScaleAbs(img,alpha=1.1,beta=15)

                elif aug=="low":
                    img = cv2.convertScaleAbs(img,alpha=0.85,beta=-20)

                elif aug=="dusty":

                    noise = np.random.normal(0,12,img.shape).astype(np.int16)
                    img = np.clip(img.astype(np.int16)+noise,0,255).astype(np.uint8)

                    if random.random() < 0.4:
                        img = self.motion_blur(img)

                    if random.random() < 0.3:
                        img = self.fog_effect(img)

                    if random.random() < 0.4:
                        img = self.random_occlusion(img)

                    if random.random() < 0.5:
                        img = self.color_temperature(img)

                elif aug=="multi":

                    multi_counter += 1

                    extra = random.randint(1,3)

                    if multi_counter % 3 == 0:
                        species_pool = self.selected_animals
                    else:
                        species_pool = [animal]

                    for _ in range(extra):

                        sp = random.choice(species_pool)

                        folder2 = f"pictures/{sp}"

                        f2 = random.choice(os.listdir(folder2))

                        img2 = cv2.imread(os.path.join(folder2,f2),cv2.IMREAD_UNCHANGED)

                        img,b = self.paste_animal(img,img2)

                        labels.append(
                            f"0 {b[0]} {b[1]} {b[2]} {b[3]}"
                        )

                index = self.save_sample(img,labels,index,val)

                count += 1

    def train_yolo_model(self):

        try:

            command = [
                sys.executable,
                "train.py",
                "--img", "640",
                "--batch", "8",
                "--epochs", "25",
                "--data", "dataset.yaml",
                "--weights", "yolov5n.pt",
                "--name", "animal_model",
                "--exist-ok",
                "--single-cls"
            ]

            process = subprocess.Popen(command)
            process.wait()

            self.best_model_path = self.get_latest_model()

            self.display.setText("Training Complete")
            self.set_lights(stop=True)

        except Exception as e:

            QMessageBox.critical(self,"Training Error",str(e))

    def get_latest_model(self):

        train_dir = "runs/train"

        folders = [
            os.path.join(train_dir,f)
            for f in os.listdir(train_dir)
            if "animal_model" in f
        ]

        latest = max(folders, key=os.path.getctime)

        return os.path.join(latest,"weights","best.pt")

    def run_detection(self):

        if not self.best_model_path or not os.path.exists(self.best_model_path):
            QMessageBox.warning(self,"Error","Model not trained yet")
            return

        command = [
            sys.executable,
            "detect.py",
            "--weights", self.best_model_path,
            "--source", "0",
            "--img", "640",
            "--conf", "0.4",
            "--nosave",
            "--exist-ok"
        ]

        self.detect_process = subprocess.Popen(command)


    def capture_background(self):
        """Capture a frame from the webcam to use as background for data augmentation."""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Cannot access webcam. Using white background.")
            return np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            QMessageBox.critical(self, "Camera Error", "Failed to capture frame. Using white background.")
            return np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        return frame


    def train_pressed(self):

        if len(self.selected_animals)==0:

            QMessageBox.warning(self,"Error","Select animals first")
            return

        self.display.setText("Training")
        self.set_lights(train=True)

        bg = self.capture_background()

        self.generate_dataset(bg)

        self.create_dataset_yaml()

        thread = threading.Thread(target=self.train_yolo_model)
        thread.start()

        self.sequence=""
        self.current_input=""
        self.selected_animals=[]

        self.train_btn.setEnabled(False)


if __name__=="__main__":

    app=QApplication(sys.argv)

    window=ControlPanel()
    window.show()

    sys.exit(app.exec_())