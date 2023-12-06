# ushbu kod kamera orqali yuz holatini ko'rishn uchun
import cv2 
import mediapipe as mp
import time 


cap = cv2.VideoCapture(0) #agar nolda xato bersa 1, yoki 2 raqamni yozing bu qo'shimcha kameralar hisoblanadi

pVaqt = 0

mpDraw = mp.solutions.drawing_utils
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(max_num_faces=2)
drawSpec = mpDraw.DrawingSpec(thickness=1, circle_radius=1)


while True:
	success, img = cap.read()
	
	imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	results = faceMesh.process(imgRGB)
	if results.multi_face_landmarks:
		for faceLms in results.multi_face_landmarks:
			mpDraw.draw_landmarks(img, faceLms, mpFaceMesh.FACE_CONNECTIONS,
				drawSpec,drawSpec)


	cVaqt = time.time()
	fps = 1 / (cVaqt - pVaqt)
	pVaqt = cVaqt
	cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
	cv2.imshow("Image", img)
	cv2.waitKey(2)



# Dasturchi Suyunov Husan