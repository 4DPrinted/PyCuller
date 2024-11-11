import cv2
import rawpy
from PIL import Image
import numpy as np
import os
def detect_blur(image, method, thresh,size = 300):
	'''
	image: the image that we are looking to evaluate (NEEDS TO BE GRAYSCALE)
	size: size of the radius of the FFT about the center
	thresh: threshold for determining blurriness
	method: FFT or LPL, gives how we should evaluate
	'''
	if method == "Fast Fourier Transform":
		# Get dimensions and center of image
		(h,w) = image.shape
		(cX, cY) = (int(w / 2.0), int(h / 2.0))
		# Calculate FFT of image
		fft = np.fft.fft2(image)
		fftShift = np.fft.fftshift(fft)
		# Calculate Inverse FFT
		fftShift[cY - size:cY + size, cX - size:cX + size] = 0
		fftShift = np.fft.ifftshift(fftShift)
		recon = np.fft.ifft2(fftShift)

		# Calculate magnitudes and compare to threshold
		magnitude = 20 * np.log(np.abs(recon))
		mean = np.mean(magnitude)
		print(mean)
		return mean <= thresh * -1
	if method == "Laplacian Variance":
		# One liner for LPL
		return cv2.Laplacian(image, cv2.CV_64F).var() <= thresh

def getRaws(raw_directory, raw_extension = ".ARW"):
			'''
			raw_directory: folder with the raws that we have downloaded
			output: list of paths to raws
			'''
			paths = []
			# Scan the directory to collect raws
			with os.scandir(raw_directory) as it:
				for entry in it:
					if entry.name.endswith(raw_extension) and entry.is_file():
						paths.append(entry.path)
						#  Print the raws that we have collected
						print("Collected Raw:" + entry.path.split("/")[-1].strip(raw_extension))
			return paths

def rawToThumbnail(raw_paths, thumbnail_storage, raw_extension = ".ARW"):
	'''
	raw_paths: the paths to raw files
	raw_extension: file extension for raw format
	thumbnail_storage: location to store thumbnails derived from RAWs
	'''
	paths = []
	for path in raw_paths:
		file_name = path.split("/")[-1].strip(raw_extension)
		with rawpy.imread(path) as raw:
				thumb = raw.extract_thumb()
				with open(f'{thumbnail_storage}/{file_name}.jpeg', 'wb') as file:
					try:
						file.write(thumb.data)
						paths.append(f'{thumbnail_storage}/{file_name}.jpeg')
						print("Thumbnail write succeeded: " + file_name)
					except:
						print("Thumbnail write failed: " + file_name)
	return paths

def createThumbnailStorage(raw_directory):
	'''
	raw_directory: path to folder with RAWs

	Uses os to create a directory to store mined thumbnails, if not created already
	'''
	thumbnail_storage = f"{raw_directory}/thumbnail_storage"
	try:
		os.mkdir(thumbnail_storage)
		print("Created thumbnail storage directory: " + thumbnail_storage)
	except FileExistsError:
		print("\n Thumbnail Storage already exists under path: " + thumbnail_storage + "\n")
		pass
	return thumbnail_storage

# Imports
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QSlider, QHBoxLayout, QVBoxLayout, QComboBox, QProgressBar
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtCore import Qt
from PIL.ImageQt import ImageQt
import sys

class ImageCullingApp(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		# Set up the window
		self.setWindowTitle("Image Culler")
		# self.setFixedHeight(900)
		# self.setFixedWidth(1400)
		# Set up layout and widgets
		layout = QGridLayout()
		layout.setVerticalSpacing(0)
		layout.setContentsMargins(0,0,0,0)

	# Set up column1 Layout
		self.column1_layout = QVBoxLayout()

	# Title for Thumbnail Creation
		self.GeneratorTitle = QLabel("Generating Thumbnails")
		font = QFont('Helvetica Neue', 20)
		font.setUnderline(True)
		self.GeneratorTitle.setFont(font)
		self.column1_layout.addWidget(self.GeneratorTitle)

	# Label for Path
		self.PathLabel = QLabel("Enter Path Below:")
		self.column1_layout.addWidget(self.PathLabel)

	# Text input field
		self.PathInput = QLineEdit(self)
		self.PathInput.setPlaceholderText("/path/to/raws")
		self.column1_layout.addWidget(self.PathInput)
	# Raw Extension
		self.RawExtensionInput = QLineEdit(self)
		self.RawExtensionInput.setPlaceholderText("Raw Extension")
		self.column1_layout.addWidget(self.RawExtensionInput)

	# Button to submit text
		self.SubmitButton = QPushButton("Generate Thumbnails from Raws")
		self.SubmitButton.clicked.connect(self.thumbnailGenerator)
		self.column1_layout.addWidget(self.SubmitButton)
	

	# Terminal layout
		self.vertical_layout = QVBoxLayout()
	# Label for text/terminal output
		self.TerminalLabel = QLabel("Output: ")
		self.vertical_layout.addWidget(self.TerminalLabel)
	# Display submitted text
		self.OutputLabel = QLabel("")
		self.OutputLabel.setStyleSheet("border: 1px solid; border-color:black; background-color:white; color: #000000")
		self.OutputLabel.setFixedHeight(20)
		self.vertical_layout.addWidget(self.OutputLabel)
		self.column1_layout.addLayout(self.vertical_layout)

	# Add the layout to main window
		layout.addLayout(self.column1_layout,0,0)

	# Set up column2 layout
		self.column2_layout = QVBoxLayout()
	# Title For Image Creation and Rendering
		self.ImageManipulationLabel = QLabel("Image Rendering and Culling")
		font = QFont('Helvetica Neue', 20)
		font.setUnderline(True)
		self.ImageManipulationLabel.setFont(font)
		self.column2_layout.addWidget(self.ImageManipulationLabel)
	# Label for Image Path Input
		self.RenderedPath = QLabel("Enter Image Rendering Directory Below:")
		self.column2_layout.addWidget(self.RenderedPath)
	# Input for Image Path
		self.RenderedPathInput = QLineEdit(self)
		self.RenderedPathInput.setPlaceholderText("/path/to/images")
		self.column2_layout.addWidget(self.RenderedPathInput)
	# Button to Input Image Path
		self.RenderPathButton = QPushButton("Submit")
		self.RenderPathButton.clicked.connect(self.setRenderingPath)
		self.column2_layout.addWidget(self.RenderPathButton)
	# Label for Image Size Slider
		self.RenderedPath = QLabel("Image Size Slider")
		self.column2_layout.addWidget(self.RenderedPath)
	# Image Size Slider
		self.ImageSizeSlider = QSlider(Qt.Orientation.Horizontal)
		self.ImageSizeSlider.setMinimum(200)
		self.ImageSizeSlider.setMaximum(1131)
		self.ImageSizeSlider.setSingleStep(10)
		self.ImageSizeSlider.setFixedHeight(20)
		self.ImageSizeSlider.setValue(500)
		self.ImageSizeSlider.valueChanged.connect(self.setScale)
		self.column2_layout.addWidget(self.ImageSizeSlider)
	# Button to Render Image
		self.current_image_index = 0
		self.render_path = False
		self.RenderImageButton = QPushButton("Render Image")
		self.RenderImageButton.clicked.connect(lambda:self.renderThumbnail(self.render_path, self.current_image_index))
		self.column2_layout.addWidget(self.RenderImageButton)
		layout.addLayout(self.column2_layout,0,1)


	# OPENCV Functions
		self.openCV_layout = QVBoxLayout()
	# Label for Blur Annotation
		self.BlurAnnotationTitle = QLabel("Blur Annotation")
		font = QFont('Helvetica Neue', 20)
		font.setUnderline(True)
		self.BlurAnnotationTitle.setFont(font)
		self.openCV_layout.addWidget(self.BlurAnnotationTitle)
	# Label for Method Selection
		self.MethodSelectionLabel = QLabel("Method for Blur Detection:")
		self.openCV_layout.addWidget(self.MethodSelectionLabel)
	# Dropdown for Method Selection
		methods = ["Fast Fourier Transform", "Laplacian Variance"]
		self.MethodSelection = QComboBox()
		self.MethodSelection.addItems(methods)
		self.openCV_layout.addWidget(self.MethodSelection)
	# Input for threshold
		self.blurThresholdInput = QLineEdit(self)
		self.blurThresholdInput.setText("10")
		self.blurThresholdInput.setPlaceholderText("Blur Threshold [lower more sensitive]")
		self.blurThresholdInput.setInputMask("000000")
		self.openCV_layout.addWidget(self.blurThresholdInput)

	# Label for running blur detection
		self.BlurAnnotationButton = QPushButton("Identify Blurry Images")
		self.BlurAnnotationButton.clicked.connect(self.updateThreshold)
		self.BlurAnnotationButton.clicked.connect(self.identifyBlurryPaths)
		self.openCV_layout.addWidget(self.BlurAnnotationButton)
	# Blur Progress Bar Label
		self.BlurAnnotationProgressBarLabel = QLabel("Blur Detection Progress")
		self.openCV_layout.addWidget(self.BlurAnnotationProgressBarLabel)
	# Blur detection progress bar
		self.BlurAnnotationProgressBar = QProgressBar()
		self.openCV_layout.addWidget(self.BlurAnnotationProgressBar)
	# Change rendering to blurry images
		self.BlurryRenderingButton = QPushButton("Get Blurry Images")
		self.BlurryRenderingButton.clicked.connect(self.blurryImageRenderingPrep)
		self.BlurryRenderingButton.clicked.connect(lambda: self.renderThumbnail(self.blurry_paths, self.current_image_index))
		self.openCV_layout.addWidget(self.BlurryRenderingButton)

		layout.addLayout(self.openCV_layout, 1,0)
	# Rendered Image 
		self.scale = 500
		self.ImageLabel = QLabel(self)
		layout.addWidget(self.ImageLabel, 0,3,7,3)
		self.ImageLabel.setStyleSheet("border: 1px solid; border-color:black; background-color:white")
		self.ImageLabel.setFixedSize(1131,756)
	# Set layout for image moving and what not
		self.left_right = QHBoxLayout()		
	# Get previous image
		self.PreviousImage = QPushButton("Previous Image")
		self.PreviousImage.clicked.connect(self.previous_image)
		self.left_right.addWidget(self.PreviousImage)
	# Get next image
		self.NextImage = QPushButton("Next Image")
		self.NextImage.clicked.connect(self.next_image)
		self.left_right.addWidget(self.NextImage)
	# Delete Image from Disk
		self.DeleteImage = QPushButton("Delete Image")
		self.DeleteImage.clicked.connect(self.delete_image)
		self.left_right.addWidget(self.DeleteImage)
		layout.addLayout(self.left_right, 8,3)
	

	# Set layout
		self.setLayout(layout)

	
	def setScale(self):
		'''
		Helper function to get values of user input to image sizing
		'''
		self.scale = self.ImageSizeSlider.value()

	def setRenderingPath(self):
		'''
		Set path to the image rendering
		'''
		try:
			self.render_path = getRaws(self.RenderedPathInput.text(), raw_extension = ".jpeg")
			self.OutputLabel.setText(f"Directory Chosen: {self.RenderedPathInput.text()}")
		except FileNotFoundError:
			self.OutputLabel.setText("Error: Image directory not found!")

	# General Thumbnail Rendering Function
	def renderThumbnail(self, path, current_image_index):
		'''
		path: path to the thumbnails or image displays
		current_image_index: image index in the list of paths
		General thumbnail rendering function that begins the rendering cycle
		'''
		if path == False:
			self.OutputLabel.setText("Did not designate path yet!")
			return None
		# Get the image paths
		self.image_paths = path
		# Start the image loading to QLabel
		try:
			self.load_image(self.image_paths[current_image_index])
		except IndexError:
			self.OutputLabel.setText("No Images to Render")
			return None

	def load_image(self, image_path):
		'''
		image_path: path to displayable image type
		Renders the image into the image display grid on the GUI using PIL and QPixmap
		'''
		try:
			pil_image = Image.open(image_path)
		except FileNotFoundError:
			self.OutputLabel.setText("Path to Image not found!")
			return None
		img = ImageQt(pil_image)
		# Convert QImage to QPixmap and set it on QLabel
		pixmap = QPixmap.fromImage(img)
		pixmap = pixmap.scaled(self.scale, self.scale, Qt.AspectRatioMode.KeepAspectRatio)
		self.ImageLabel.setPixmap(pixmap)
		self.resize(pixmap.width(), pixmap.height())

	def next_image(self):
		'''
		Cycles to the subsequent image and loads it
		'''
		try:
			# Change index and then load image with new index
			self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
			self.load_image(self.image_paths[self.current_image_index])
		except:
			self.OutputLabel.setText("Error: Please check image directory was set")
			return None
	def previous_image(self):
		'''
		Cycles to the previous image and loads it
		'''
		try:
			# Change index and then load image with new index
			self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
			self.load_image(self.image_paths[self.current_image_index])
		except:
			self.OutputLabel.setText("Error: Please check image directory was set")
			return None
	def delete_image(self):
		'''
		Deletes the currently shown raw from disk and the corresponding display image
		'''
		raw_location = self.image_paths[self.current_image_index].split("/")
		del(raw_location[-2])
		raw_location = "/".join(raw_location)
		raw_location = raw_location.rsplit('.', 1)[0] + self.raw_extension

		print(self.image_paths[self.current_image_index])
		self.OutputLabel.setText("Deleted Image and RAW:" + self.image_paths[self.current_image_index])
		os.remove(self.image_paths[self.current_image_index])
		os.remove(raw_location)
		self.next_image()
		del(self.image_paths[self.current_image_index])

	def thumbnailGenerator(self):
		'''
		Using input fields, we generate the necessary directories as well as extract any jpegs or renderable images from the raw files in the raw directory
		'''
		# Retrieve text from input field and display it
		raw_directory = self.PathInput.text()
		try:
			raw_paths = getRaws(raw_directory)
		except FileNotFoundError:
			self.OutputLabel.setText("Path to Raws not found!")
			return None
		thumbnail_storage = createThumbnailStorage(raw_directory)
		self.raw_extension = self.RawExtensionInput.text()

		if self.raw_extension == None:
			self.OutputLabel.setText("Did not designate raw extension!")
			return None

		rawToThumbnail(raw_paths, thumbnail_storage, self.raw_extension)
		self.OutputLabel.setText(f"Thumbnails generated in: {thumbnail_storage}")
	
	# Blurry flagging helper function
	def flagBlurry(self, thumbnail_paths, method, thresh, size = 300):
		'''
		thumbnail_paths: paths to the thumbnail images
		method: FFT or LPL
		'''
		blurry_list = set()
		for path in thumbnail_paths:
			self.BlurAnnotationProgressBar.setValue(self.BlurAnnotationProgressBar.value()+1)
			image = cv2.imread(path)
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			if detect_blur(gray, method, thresh, size):
				blurry_list.add(path)
		return list(blurry_list)

	def blurryImageRenderingPrep(self):
		'''
		Sets up indexing for blurry image identification
		'''
		self.current_image_index = 0
	def updateThreshold(self):
		'''
		Updates threshold for blur detection
		'''
		if len(self.blurThresholdInput.text()) == 0:
			self.blurThreshold = 0
		else:
			self.blurThreshold = int(self.blurThresholdInput.text())

	def identifyBlurryPaths(self):
		'''
		Identifies any blurry images in the render path
		'''
		if self.render_path == False:
			self.OutputLabel.setText("Did not designate blur detection path yet!")
			return None
		if self.blurThreshold == 0:
			self.OutputLabel.setText("Did not designate blur detection threshold yet! or designated 0")
			return None
		self.BlurAnnotationProgressBar.setRange(1, len(self.render_path))
		self.blurry_paths = self.flagBlurry(self.image_paths, self.MethodSelection.currentText(), self.blurThreshold)
		print(self.blurry_paths)

app = QApplication(sys.argv)
window = ImageCullingApp()
window.show()
app.exec()

	





