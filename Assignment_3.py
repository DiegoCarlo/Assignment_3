from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL.Image import *
from math import *
from random import randint
from random import random

### window ###
windowWidth = 1200
windowHeight = 600
windowX = 300
windowY = 150
_angle = 30

### view ###
maxViewDistance = 150
widthGround = 150

# gestisce la camera
player = None
# contiene gli oggetti da rappresentare
listSceneObjects = None
# lista di coordinate dei ciuffi d'erba
listGrass = None
# lista di coordinate, dimensini e tipo degli alberi
listThree = None
# contiene tutte le texture necessarie
listTextures = None

skybox = None

# mouse coords
mouseX = 0
mouseY = 0

class Player(object):
	"""
		questa contiene i vettori e i metodi necessari per muovere la telecamera.
	"""
	def __init__(self):
		# modulo della velocita' di movimento
		self.movementSpeed = 0.25

		# Specifies the position of the eye point.
		self.posX = -25
		self.posY = 2.75
		self.posZ = 36

		# Specifies the position of the reference point.
		self.centerX = 0
		self.centerY = 0
		self.centerZ = 0

		# distanza fra l'eye point e il reference point
		self.centerDistance = 1.0

		# la rotazione della camera e' calcolata in base alle coordinate geografiche di una sfera ideale
		# il centro della sfera e' eye, il raggio la distanza fra eye e il reference point
		self.latitude = 90	
		self.longitude = -35

		self.rotation(0, 0)

	def update(self):
		""" 
			aggiorna il punto di vista
			update the camera
		"""
		gluLookAt(self.posX, self.posY, self.posZ, self.centerX, self.centerY, self.centerZ, 0, 1, 0)

	def rotation(self, latitudeIncr,longitudeIncr):
		
		temp = self.latitude + latitudeIncr
		# limitazione di latitude
		if temp > 0 and temp < 180:
			self.latitude = temp

		self.longitude += longitudeIncr
		# longitude e' un valore in gradi (0 - 360) viene quindi limitato a tali valori nelle righe seguenti
		if self.longitude > 360:
			self.longitude = self.longitude - 360
		if self.longitude < 0:
			self.longitude = 360 + self.longitude

		# calcolo delle coordinate del reference point 
		self.centerY = self.posY + (self.centerDistance * cos(radians(self.latitude)))	
		self.centerX = self.posX + (self.centerDistance * sin(radians(self.latitude)) * cos(radians(self.longitude)))
		self.centerZ = self.posZ + (self.centerDistance * sin(radians(self.latitude)) * sin(radians(self.longitude)))

	def movement(self, selfAhead, selfLateral):
		"""
			applica la traslazione del vettore posizione e del vettore "punto di osservazione" 
			sia di un incremento (selfAhead) nella direzione di osservazione sia un incremento (selfLateral) nella direzione ortogonale
		"""
		translateX = (selfAhead * self.movementSpeed * cos(radians(self.longitude)))
		translateZ = (selfAhead * self.movementSpeed * sin(radians(self.longitude)))

		translateX += (selfLateral * self.movementSpeed * cos(radians(self.longitude-90)))
		translateZ += (selfLateral * self.movementSpeed * sin(radians(self.longitude-90)))

		self.posX += translateX
		self.posZ += translateZ
		self.centerX += translateX
		self.centerZ += translateZ

class Parallelepiped(object):
	"""
		questa classe crea un parallelepipedo.
		la forma viene posizionata alle coordinate del vettore center
		le dimensioni vengono specificate dal vettore dimension
		texture rateo indica le ripetizioni delle texture sui tre assi
		idTextures contiene i 6 indici delle texture da rappresentare su ciascun lato, se un id e' nullo il lato relativo non verra' rappresentato
		alpha verra' utilizzato su ogni faccia, va utilizzato solo con texture semitrasparenti

		vertices contiene l'elenco dei vertici del parallelepipedo
		listSymmetries agisce rispetto agli assi e l'origine. l'oggetto e le sue versioni simmetriche saranno considerati un oggetto unico dalle traslazioni e rotazioni
		listRotationTranslation e' una lista di traslazioni e rotazioni applicate all'oggetto e alle sue simmetrie
		lightEnable attiva e disattiva il vettore normale per la rifrazione della luce
	"""
	def __init__(self, center, dimension, textureRateo, idTextures, alpha = None):
		self.center = center
		self.dimension = dimension

		self.textureRateo = textureRateo
		self.vertices = self.getAllVertices(self.center, self.dimension)

		self.idTextures = idTextures # up down 1_side 2_side, 3_side, 4_side
	
		self.listSymmetries = None

		self.listRotationTanslation = None

		self.lightEnable = True

		self.alpha = alpha

	def getAllVertices(self, center, dimension):
		"""	dato il centro e le dimensioni del parallelepipedo calcola le coordinate dei vertici """
		v0 = [center[0] + dimension[0]/2.0, center[1] + dimension[1]/2.0, center[2] + dimension[2]/2.0]
		v1 = [center[0] + dimension[0]/2.0, center[1] + dimension[1]/2.0, center[2] - dimension[2]/2.0]
		v2 = [center[0] - dimension[0]/2.0, center[1] + dimension[1]/2.0, center[2] - dimension[2]/2.0]
		v3 = [center[0] - dimension[0]/2.0, center[1] + dimension[1]/2.0, center[2] + dimension[2]/2.0]
		v4 = [center[0] + dimension[0]/2.0, center[1] - dimension[1]/2.0, center[2] + dimension[2]/2.0]
		v5 = [center[0] + dimension[0]/2.0, center[1] - dimension[1]/2.0, center[2] - dimension[2]/2.0]
		v6 = [center[0] - dimension[0]/2.0, center[1] - dimension[1]/2.0, center[2] - dimension[2]/2.0]
		v7 = [center[0] - dimension[0]/2.0, center[1] - dimension[1]/2.0, center[2] + dimension[2]/2.0]
		pointList = [v0, v1, v2, v3, v4, v5, v6, v7]
		return pointList

	def addSymmetry(self, symmetry):

		if self.listSymmetries == None:
			self.listSymmetries = []
		self.listSymmetries.append(symmetry)

	def draw(self):
		""" questa funzione disegna il parallelepipedo e le sue simmetrie"""

		center = self.center
		dimension = self.dimension
		vertices = self.vertices

		self.drawFaces(center, dimension, vertices)


		if self.listSymmetries != None:
			for i in self.listSymmetries:
				if i != None:
					centerX = self.center[0]
					centerY = self.center[1]
					centerZ = self.center[2]
					if i[0] == True:
						centerX = -self.center[0]
					if i[1] == True:
						centerY = -self.center[1]
					if i[2] == True:
						centerZ = -self.center[2]
					center = [centerX, centerY, centerZ]
					#print center
					#print self.center
					dimensionX = self.dimension[0]
					dimensionY = self.dimension[1]
					dimensionZ = self.dimension[2]
					if i[0] == True:
						dimensionX = -self.dimension[0]
					if i[1] == True:
						dimensionY = -self.dimension[1]
					if i[2] == True:
						dimensionZ = -self.dimension[2]
					dimension = [dimensionX, dimensionY, dimensionZ]
					#print dimension
					#print self.dimension

					vertices = self.getAllVertices(center, self.dimension)

					self.drawFaces(center, self.dimension, vertices)

	def rotationTranslation(self):
		""" questa funzione esegue la sequenza di rotazioni e traslazioni """
		for i in self.listRotationTanslation:
			if len(i) == 4:
				glRotate(i[0],i[1],i[2],i[3])
			if len(i) == 3:
				glTranslate(i[0],i[1],i[2])

	def addRotation(self, intensity, vector):
		if self.listRotationTanslation == None:
			self.listRotationTanslation = []
		self.listRotationTanslation.append([intensity, vector[0], vector[1], vector[2]])

	def addTranslation(self, vector):	
		if self.listRotationTanslation == None:
			self.listRotationTanslation = []
		self.listRotationTanslation.append([vector[0], vector[1], vector[2]])

	def drawFaces(self, center, dimension, vertices):
		""" esegue le traslazioni e disegna le 6 facce """

		pushMatrixActivated = False
		if self.listRotationTanslation != None:
			glPushMatrix()
			self.rotationTranslation()
			pushMatrixActivated = True

		if self.alpha != None:
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			glEnable(GL_ALPHA_TEST)
			glAlphaFunc(GL_GREATER, self.alpha)

		glEnable(GL_TEXTURE_2D)
		# -y +y +x -z -x +z

		if self.lightEnable == False:
			glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [1, 1, 1, .0]) #with this, the sun EMITS light
			glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 70)
		else:
			glMaterialfv(GL_FRONT, GL_EMISSION, [.0, .0, .0, 1])
			glMaterialfv(GL_FRONT, GL_SHININESS, 50)
			glMaterialfv(GL_FRONT, GL_DIFFUSE, [.5, .5, .5, 1.0])
			glMaterialfv(GL_FRONT, GL_SPECULAR, [.1, .1, .1, 1])

		# +y
		if self.idTextures[0] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[0]))
			glBegin(GL_QUADS)
			if self.lightEnable == True:
				glNormal3f(0,1,0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(0.0, self.textureRateo[0])
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glTexCoord2f(self.textureRateo[2], self.textureRateo[0])
			glVertex3f(vertices[2][0], vertices[2][1], vertices[2][2])
			glTexCoord2f(self.textureRateo[2], 0.0)
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glEnd()

		# -y
		if self.idTextures[1] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[1]))
			glBegin(GL_QUADS)
			if self.lightEnable == True:
				glNormal3f(0,-1,0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glTexCoord2f(0.0, self.textureRateo[0])
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glTexCoord2f(self.textureRateo[2], self.textureRateo[0])
			glVertex3f(vertices[6][0], vertices[6][1], vertices[6][2])
			glTexCoord2f(self.textureRateo[2], 0)
			glVertex3f(vertices[7][0], vertices[7][1], vertices[7][2])
			glEnd()
		# +x
		if self.idTextures[2] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[2]))
			glBegin(GL_QUADS)
			if self.lightEnable == True:
				glNormal3f(1,0,0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glTexCoord2f(0.0, self.textureRateo[1])
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(self.textureRateo[2], self.textureRateo[1])
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glTexCoord2f(self.textureRateo[2], 0.0)
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glEnd()
		# -z
		if self.idTextures[3] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[3]))
			glBegin(GL_QUADS)
			if self.lightEnable == True:
				glNormal3f(0,0,-1)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glTexCoord2f(0.0, self.textureRateo[1])
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glTexCoord2f(self.textureRateo[0], self.textureRateo[1])
			glVertex3f(vertices[2][0], vertices[2][1], vertices[2][2])
			glTexCoord2f(self.textureRateo[0], 0.0)
			glVertex3f(vertices[6][0], vertices[6][1], vertices[6][2])
			glEnd()
		# -x
		if self.idTextures[4] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[4]))
			glBegin(GL_QUADS)
			if self.lightEnable == True:
				glNormal3f(-1,0,0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[6][0], vertices[6][1], vertices[6][2])
			glTexCoord2f(0.0, self.textureRateo[1])
			glVertex3f(vertices[2][0], vertices[2][1], vertices[2][2])
			glTexCoord2f(self.textureRateo[2], self.textureRateo[1])
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glTexCoord2f(self.textureRateo[2], 0.0)
			glVertex3f(vertices[7][0], vertices[7][1], vertices[7][2])
			glEnd()
		# +z
		if self.idTextures[5] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[5]))
			glBegin(GL_QUADS)
			if self.lightEnable == True:
				glNormal3f(.0,.0,1.0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[7][0], vertices[7][1], vertices[7][2])
			glTexCoord2f(0.0, self.textureRateo[1])
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glTexCoord2f(self.textureRateo[0], self.textureRateo[1])
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(self.textureRateo[0], 0.0)
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glEnd()

		glDisable(GL_TEXTURE_2D)
		if self.alpha != None:
			glDisable(GL_ALPHA_TEST)
			glDisable(GL_BLEND)

		if pushMatrixActivated == True:
			glPopMatrix()

	
def drawCrossPanel(center, dimension, texture):
	""" questa funzione disegna oggetti come erba ed alberi """
	v0 = [center[0] + dimension[0]/2.0, center[1] + dimension[1]/2.0, center[2] + dimension[2]/2.0]
	v1 = [center[0] + dimension[0]/2.0, center[1] + dimension[1]/2.0, center[2] - dimension[2]/2.0]
	v2 = [center[0] - dimension[0]/2.0, center[1] + dimension[1]/2.0, center[2] - dimension[2]/2.0]
	v3 = [center[0] - dimension[0]/2.0, center[1] + dimension[1]/2.0, center[2] + dimension[2]/2.0]
	v4 = [center[0] + dimension[0]/2.0, center[1] - dimension[1]/2.0, center[2] + dimension[2]/2.0]
	v5 = [center[0] + dimension[0]/2.0, center[1] - dimension[1]/2.0, center[2] - dimension[2]/2.0]
	v6 = [center[0] - dimension[0]/2.0, center[1] - dimension[1]/2.0, center[2] - dimension[2]/2.0]
	v7 = [center[0] - dimension[0]/2.0, center[1] - dimension[1]/2.0, center[2] + dimension[2]/2.0]

	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glEnable(GL_ALPHA_TEST)
	glAlphaFunc(GL_GREATER, 0.3)

	glEnable(GL_TEXTURE_2D)
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
	glBindTexture(GL_TEXTURE_2D, texture)
	glBegin(GL_QUADS)
	glNormal3f(-1,0,1)
	glTexCoord2f(0.0, 0.0)
	glVertex3f(v6[0], v6[1], v6[2])
	glTexCoord2f(0.0, 0.99)
	glVertex3f(v2[0], v2[1], v2[2])
	glTexCoord2f(1, 0.99)
	glVertex3f(v0[0], v0[1], v0[2])
	glTexCoord2f(1, 0)
	glVertex3f(v4[0], v4[1], v4[2])
	glEnd()

	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
	glBindTexture(GL_TEXTURE_2D, texture)
	glBegin(GL_QUADS)
	glNormal3f(1,0,1)
	glTexCoord2f(0.0, 0.0)
	glVertex3f(v7[0], v7[1], v7[2])
	glTexCoord2f(0.0, 0.99)
	glVertex3f(v3[0], v3[1], v3[2])
	glTexCoord2f(1, 0.99)
	glVertex3f(v1[0], v1[1], v1[2])
	glTexCoord2f(1, 0)
	glVertex3f(v5[0], v5[1], v5[2])
	glEnd()
	glDisable(GL_TEXTURE_2D)
	glDisable(GL_BLEND)	

def initTexture(pathImage):
	""" 
		data la directory carica la texture in memoria
		load texture
	"""
	image = open(pathImage)
	ix = image.size[0]
	iy = image.size[1]

	# load image using PIL
	image_bytes = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

	# generate one texture name
	texture = glGenTextures(1)

	# bind a named texture to a texturing targhet
	glBindTexture(GL_TEXTURE_2D, texture)
	
	# parameters 
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )

	# build a two-dimensional mipmap
	gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image_bytes)

	#print pathImage
	return texture

def loadListTextures():
	""" Carica le texture necessarie """
	global listTextures
	print "loadTextures"
	listTextures = []
	listTextures.append(["grass", initTexture("grass.jpg")])
	listTextures.append(["wall", initTexture("whiteWall.jpg")])
	listTextures.append(["grassLeaf", initTexture("grassLeaf.png")])
	listTextures.append(["parquet", initTexture("parquet.jpg")])
	listTextures.append(["window1", initTexture("window1.png")])
	listTextures.append(["window2", initTexture("window2.png")])
	listTextures.append(["window3", initTexture("window3.png")])
	listTextures.append(["window4", initTexture("window4.png")])
	listTextures.append(["mbl1", initTexture("mbl1.png")])
	listTextures.append(["mbl2", initTexture("mbl2.png")])
	listTextures.append(["mbl3", initTexture("mbl3.png")])
	listTextures.append(["mbl4", initTexture("mbl4.png")])
	listTextures.append(["mblBorder", initTexture("mblBorder.png")])
	listTextures.append(["tv", initTexture("tv.png")])
	listTextures.append(["picture1", initTexture("picture1.jpg")])
	listTextures.append(["picture2", initTexture("picture2.jpg")])
	listTextures.append(["three1", initTexture("three1.png")])
	listTextures.append(["three2", initTexture("three2.png")])
	listTextures.append(["three3", initTexture("three3.png")])
	listTextures.append(["poolBorder2", initTexture("poolBorder.jpg")])
	listTextures.append(["pool", initTexture("pool.jpg")])
	listTextures.append(["sky1", initTexture("sky1.png")])
	listTextures.append(["sky2", initTexture("sky2.png")])
	listTextures.append(["sky3", initTexture("sky3.png")])
	listTextures.append(["sky4", initTexture("sky4.png")])
	listTextures.append(["skyTop", initTexture("skyTop.png")])
	listTextures.append(["roof", initTexture("roof.jpg")])

def getTexture(name):
	global listTextures
	for i in listTextures:
		if i[0] == name:
			return i[1]

def lightLine(point): 
	glLineWidth(2.5)  
	glColor3f(1.0, 1.0, 1.0) 
	glBegin(GL_LINES); 
	glVertex3f(0, 0, 0) 
	glVertex3f(point[0], point[1], point[2]) 
	glEnd() 

def initScene():
	global player, listSceneObjects, listTextures, listGrass, listThree, skybox

	glEnable(GL_COLOR_MATERIAL)
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glEnable(GL_DEPTH_TEST)

	player = Player()

	loadListTextures()

	listSceneObjects = []
	houseHeight = 3
	upFromGrass = 0.01
	doorHeight = 2.25
	pavimentoH = 0.5
	soffittoH = 5.5
	
	listSceneObjects.append(Parallelepiped([.0,pavimentoH,10.0], [16.0,1,8.0], [16.0,1,8.0], ["parquet", None, None, "wall", None, "wall"]))
	temp = Parallelepiped([12.0,pavimentoH,0], [8.0,1,28.0], [8.0,1,28.0], ["parquet", None, "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	listSceneObjects.append(Parallelepiped([.0,soffittoH,10.0], [16.0,1,8.0], [16.0,1,8.0], ["parquet", "wall", None, "wall", None, "wall"]))
	temp = Parallelepiped([12.0,soffittoH,0], [8.0,1,28.0], [8.0,1,28.0], ["parquet", "wall", "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([15.5,3,9], [1,4,10.0], [1,4,10.0], [None, None, "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	temp.addSymmetry([True, False, True])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,3,6.5], [16,4,1], [16,4,1], [None, None, "wall", "wall", "wall", "wall"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([12,8,6.5], [8,4,1], [16,4,1], [None, None, "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([8.5,8,10], [1,4,8], [16,4,1], [None, None, "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([12,10.5,10], [8,1,8], [8,1,8], ["roof", "wall", "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([12,8.5,-13.5], [8,5,1], [8,1,8], ["roof", "wall", "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)


	temp = Parallelepiped([0,0,0], [16,8.89,1], [16,8.89,1], ["wall", "wall", "wall", "roof", "wall", "wall"])
	temp.addTranslation([0,8,10])
	temp.addRotation(90-32.98,[1,0,0])
	listSceneObjects.append(temp)
	temp = Parallelepiped([0,0,0], [20,8.89,1], [20,8.89,1], ["wall", "wall", None, "roof", None, "wall"])
	temp.addTranslation([12,8,-4])
	temp.addRotation(90,[0,1,0])
	temp.addRotation(90-32.98,[1,0,0])

	listSceneObjects.append(temp)

	temp = Parallelepiped([0,0,0], [20,8.89,1], [20,8.89,1], ["wall", "wall", None, "roof", None, "wall"])
	temp.addTranslation([-12,8,-4])
	temp.addRotation(-90,[0,1,0])
	temp.addRotation(90-32.98,[1,0,0])
	
	listSceneObjects.append(temp)


	alpha = 0.5
	
	temp = Parallelepiped([0,3,13], [6,4,0.01], [1,1,0.01], [None, None, "window1", "window1", "window1", "window1"], alpha)
	listSceneObjects.append(temp)

	temp = Parallelepiped([5,3,13], [4,4,0.01], [1,1,0.01], [None, None, "window3", "window3", "window3", "window3"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,13], [4,4,0.01], [1,1,0.01], [None, None, "window1", "window1", "window1", "window1"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([13,3,13], [4,4,0.01], [1,1,0.01], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([15,3,0], [0.01,4,8], [0.01,1,1], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)




	temp = Parallelepiped([8.5,3,7], [1,4,0.01], [1,1,.01], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,5], [0.01,4,4], [0.01,1,1], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)
	
	temp = Parallelepiped([9,3,1], [0.01,4,4], [0.01,1,1], [None, None, "window1", "window1", "window1", "window1"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,-3], [0.01,4,4], [0.01,1,1], [None, None, "window3", "window3", "window3", "window3"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,-7], [0.01,4,4], [0.01,1,1], [None, None, "window1", "window1", "window1", "window1"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,-11], [0.01,4,4], [0.01,1,1], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([12,3,-13], [6,4,0.01], [1,1,0.01], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)
	

	temp = Parallelepiped([0,3,7.5], [9,4,1], [1,1,1], ["mblBorder", None, "mblBorder", None, "mblBorder", "mbl4"], alpha)
	listSceneObjects.append(temp)
	temp = Parallelepiped([0,3,7.5], [-3.01,-2.01,-1], [1,1,1], ["mblBorder", "mblBorder", "mblBorder", None, "mblBorder", None])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,3.0,7.75], [2.5,1.5,0.05], [1,1,1], ["mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder", "tv"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,0,0], [4.5,3.25,0.05], [1,1,1], ["mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder", "picture2"])
	temp.addTranslation([15,3,8.75])
	temp.addRotation(-90,[0,1,0])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,0,0], [4.5,3.25,0.05], [1,1,1], ["mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder", "picture1"])
	temp.addTranslation([15,3,-8.75])
	temp.addRotation(-90,[0,1,0])
	listSceneObjects.append(temp)


	temp = Parallelepiped([-6,1.5,10], [1,1,1], [1,1,1], [None, None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([-11,1.5,10], [1,1,1], [1,1,1], [None, None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([-8.5,1.30,11.25], [6.5,0.6,0.5], [7,1,1], ["mblBorder", None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([-8.5,1.30,8.75], [6.5,0.6,0.5], [7,1,1], ["mblBorder", None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([-8.5,2,10], [7,0.1,2], [7,0.1,1], ["mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)


	temp = Parallelepiped([0,1.5,11], [5,1,0.5], [5,1,1], ["mblBorder", None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,1.25,11], [6,0.5,1.5], [5,1,1], ["mblBorder", None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)



	temp = Parallelepiped([12,1.5,10], [1,1,1], [1,1,1], [None, None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)

	temp = Parallelepiped([12,1.5,3], [1,1,1], [1,1,1], [None, None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)

	temp = Parallelepiped([11,1.30,6.5], [0.5,0.6,8.5], [1,1,7], ["mblBorder", None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)

	temp = Parallelepiped([13,1.30,6.5], [0.5,0.6,8.5], [1,1,7], ["mblBorder", None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)

	temp = Parallelepiped([12,2,6.5], [2,0.1,9], [1,0.1,7], ["mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)


	temp = Parallelepiped([6.25,2.5,7.25], [2,3,0.5], [1,1,1], ["mblBorder", None, "mblBorder", None, "mblBorder", "mbl2"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([-14.75,2.5,9], [0.5,3,3], [1,1,1], ["mblBorder", None, "mbl2", "mblBorder", None, "mblBorder"])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)

	temp = Parallelepiped([-9.5,1.5,4], [1,1,4], [1,1,1], ["mblBorder", None, "mblBorder", "mblBorder", "mbl1", "mblBorder"])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)


	temp = Parallelepiped([.0,0.1,-6.0], [8.0,0.2,16.0], [1.0,1,1.0], ["pool", None, None, None, None, None])
	listSceneObjects.append(temp)

	temp = Parallelepiped([4.5,0.15,-6.0], [1.0,0.3,18.0], [1.0,1,18.0], ["poolBorder2", None, "poolBorder2", "poolBorder2", "poolBorder2", "poolBorder2"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,0.15,2.5], [8.0,0.3,1.0], [8.0,1,1.0], ["poolBorder2", None, "poolBorder2", "poolBorder2", "poolBorder2", "poolBorder2"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,0.15,-14.5], [8.0,0.3,1.0], [8.0,1,1.0], ["poolBorder2", None, "poolBorder2", "poolBorder2", "poolBorder2", "poolBorder2"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,0.25,5], [8.0,0.5,2], [8.0,1,1.0], ["mblBorder", None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)
	temp = Parallelepiped([0,0.75,5.75], [8.0,0.5,0.5], [8.0,1,1.0], ["mblBorder", None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)



	temp = Parallelepiped([0,7.68,13], [8,3.38,0.01], [1,1,0.01], [None, None, "window3", "window3", "window3", "window3"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([6,7.68,13], [4,3.38,0.01], [1,1,0.01], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([12,8,13], [6,4,0.01], [1,1,0.01], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)
	
	temp = Parallelepiped([15,8,10], [0.01,4,6], [0.01,1,1], [None, None, "window3", "window3", "window3", "window3"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([15,7.68,3], [0.01,3.38,6], [0.01,1,1], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([15,7.68,-3.5], [0.01,3.38,7], [0.01,1,1], [None, None, "window2", "window2", "window2", "window2"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([15,7.68,-10], [0.01,3.38,6], [0.01,1,1], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	skybox = Parallelepiped([0.0,.0,.0], [-maxViewDistance*2,maxViewDistance*2,maxViewDistance*2], [1,1,1], ["skyTop", "skyTop", "sky2", "sky3", "sky4", "sky1"])
	skybox.addRotation(90,[0,1,0])
	skybox.lightEnable = False


	# erba ed alberi
	max = 1000
	radius = 16
	listGrass = []
	listThree = []
	temp = getGrassRand()
	for i in range(0, max):
		
		if i%10 == 0:
			temp = getGrassRand()
			listThree.append(temp)
		listGrass.append([temp[0]+random()*radius-radius/2, temp[1]+random()*radius-radius/2, random()])

def getGrassRand():
	""" ricava una coppia di coordinate esterne alla casa """
	border = 3
	tempX = random()*(widthGround*2-border*2)-(widthGround-border)
	tempY = random()*(widthGround*2-border*2)-(widthGround-border)
	temp = [tempX, tempY, random(), randint(0,2)]
	gap = 25
	if temp[0] >= -gap and temp[0] <= gap and temp[1] >= -gap and temp[1] <= gap:
		return getGrassRand()
	return temp

def drawGrass():
	global listGrass
	texture = getTexture("grassLeaf")
	for i in listGrass:
		radius = i[2] + 2
		drawCrossPanel([i[0],radius/2.,i[1]],[radius,radius,radius], texture)

def drawThrees():
	global listThree
	texture1 = getTexture("three1")
	texture2 = getTexture("three2")
	texture3 = getTexture("three3")

	for i in listThree:
		r = i[3]
		texture = texture1
		if r == 1:
			texture = texture2
		elif r == 2:
			texture = texture3

		radius = i[2] * 4 + 18
		drawCrossPanel([i[0],radius/2,i[1]],[radius,radius,radius], texture)

def drawScene():

	global _angle, player, listSceneObjects, skybox
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity() 
	
	player.update()

	createGround()
	drawGrass()
	drawThrees()

	for i in listSceneObjects:
		i.draw()

	skybox.draw()
	light()

	glutSwapBuffers()

def createGround():
	global listTextures, widthGround, listGrass

	glEnable(GL_TEXTURE_2D)
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
	glBindTexture(GL_TEXTURE_2D, getTexture("grass"))
	glBegin(GL_QUADS)
	
	textCoeff = 25
	glNormal3f(0,1,0)
	glTexCoord2f(0.0, 0.0)
	glVertex3f(widthGround, 0, widthGround)
	glTexCoord2f(0.0, textCoeff)
	glVertex3f(widthGround, 0, -widthGround)
	glTexCoord2f(textCoeff, textCoeff)
	glVertex3f(-widthGround, 0, -widthGround)
	glTexCoord2f(textCoeff, 0.0)
	glVertex3f(-widthGround, 0, widthGround)
	glEnd()
	glDisable(GL_TEXTURE_2D)
	
def light():
	
	pos = [-18, 22, 52, 0]
	glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2,0.2,0.2,1])
	glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8,0.8,0.8,1])
	glLightfv(GL_LIGHT0, GL_SPECULAR, [.0,.0,.0,1])
	glLightfv(GL_LIGHT0, GL_POSITION, pos)
	#lightLine(pos)

def keyPressed1(key, x, y):
	global player
	if key == chr(27):
		sys.exit()
	
	if key == '8':
		player.rotation(-1, 0)
	
	if key == '2':
		player.rotation(+1, 0)
	
	if key == '4':
		player.rotation(0, -1)

	if key == '6':
		player.rotation(0, +1)
	
	if key == '7':
		player.centerDistance -= 10

	if key == '9':
		player.centerDistance += 10

	if key == 'w' or key == 'W':
		player.movement(+1, 0)
	
	if key == 's' or key == 'S':
		player.movement(-1, 0)
	
	if key == 'a' or key == 'A':
		player.movement(0, +1)

	if key == 'd' or key == 'D':
		player.movement(0, -1)

def keyPressed2(key,x,y):  
	global player
	xGap = 0
	yGap = 0
	if key == GLUT_KEY_UP:
		yGap = -1
	if key == GLUT_KEY_DOWN:
		yGap = 1
	if key == GLUT_KEY_LEFT:
		xGap = -1
	if key == GLUT_KEY_RIGHT:
		xGap = 1
	player.rotation(yGap, xGap)
    
def mouseMotion(x, y):
	global mouseX, mouseY
	coeff = 0.40
	xGap = (x - mouseX) * coeff
	yGap = (y - mouseY) * coeff

	mouseX = x
	mouseY = y
	#print mouseX
	player.rotation(yGap, xGap)

def resizeScene(width, height):
	global maxViewDistance
	if height == 0:
		height = 1

	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(60, float(width)/float(height), 0.1, maxViewDistance*3) # todo
	glMatrixMode(GL_MODELVIEW)

def main():
	global windowWidth, windowHeight, physicsThread

	glutInit()
	glutInitWindowSize(windowWidth, windowHeight)
	glutInitWindowPosition(windowX, windowY)
	glutCreateWindow("Assignment_3_Dream_House.py")
	glutReshapeFunc(resizeScene)
	initScene()

	glutDisplayFunc(drawScene)
	glutIdleFunc(drawScene)
	glutKeyboardFunc(keyPressed1)
	glutSpecialFunc(keyPressed2)
	glutPassiveMotionFunc(mouseMotion)

	glutMainLoop()

if __name__ == "__main__":
	print "\nHit ESC key to quit."
	main()
