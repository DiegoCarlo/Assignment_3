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
maxViewDistance = 50
widthGround = 50

player = None
listSceneObjects = None
listGrass = None
listTextures = None
listMaterials = None



mouseX = 0
mouseY = 0

class Player(object):

	def __init__(self):
		self.movementSpeed = 0.1

		self.posX = 0
		self.posY = 2.75
		self.posZ = 11

		self.centerX = 0
		self.centerY = 0
		self.centerZ = 0

		self.centerDistance = 1.0

		self.latitude = 90	
		self.longitude = -90

		self.rotation(0, 0)

	def update(self):
		""" 
			aggiorna il punto di vista
			update the camera
		"""
		gluLookAt(self.posX, self.posY, self.posZ, self.centerX, self.centerY, self.centerZ, 0, 1, 0)

	def rotation(self, latitudeIncr,longitudeIncr):
		"""
			latitude and longitude refer to angles (0:360) with the axes of the subject
		"""
		temp = self.latitude + latitudeIncr
		if temp > 0 and temp < 180:
			self.latitude = temp

		self.longitude += longitudeIncr

		if self.latitude > 360:
			self.latitude = self.latitude - 360
		if self.latitude < 0:
			self.latitude = 360 + self.latitude

		if self.longitude > 360:
			self.longitude = self.longitude - 360
		if self.longitude < 0:
			self.longitude = 360 + self.longitude

		self.centerY = self.posY + (self.centerDistance * cos(radians(self.latitude)))
		
		if self.latitude >= 0 and self.latitude < 180:
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

		
'''
		print self.posX
		print self.posZ
		print self.centerX
		print self.centerZ'''
class TriangularPrism(object):
	def __init__(self, center, dimension, textureRateo, idTextures):
		self.center = center
		self.dimension = dimension

		self.textureRateo = textureRateo
		self.vertices = self.getAllVertices()

		self.idTextures = idTextures # up down 1_side 2_side, 3_side, 4_side

		self.listSymmetries = None # x, y, z from center

	def getAllVertices(self):

		v0 = [self.center[0] + self.dimension[0]/2.0, self.center[1] - self.dimension[1]/2.0, self.center[2] + self.dimension[2]/2.0]
		v1 = [self.center[0] + self.dimension[0]/2.0, self.center[1] - self.dimension[1]/2.0, self.center[2] - self.dimension[2]/2.0]
		v2 = [self.center[0] - self.dimension[0]/2.0, self.center[1] - self.dimension[1]/2.0, self.center[2] - self.dimension[2]/2.0]
		v3 = [self.center[0] - self.dimension[0]/2.0, self.center[1] - self.dimension[1]/2.0, self.center[2] + self.dimension[2]/2.0]
		v4 = [self.center[0], self.center[1] + self.dimension[1]/2.0, self.center[2] + self.dimension[2]/2.0]
		v5 = [self.center[0], self.center[1] + self.dimension[1]/2.0, self.center[2] - self.dimension[2]/2.0]
	
		pointList = [v0, v1, v2, v3, v4, v5]
		return pointList


	def draw(self):

		center = self.center
		dimension = self.dimension
		vertices = self.vertices
		
		glEnable(GL_TEXTURE_2D)
		
		if self.idTextures[1] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
			glBindTexture(GL_TEXTURE_2D, self.soffitto)
			glBegin(GL_TRIANGLES)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(0.0, self.textureRateo[2])
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glTexCoord2f(self.textureRateo[0], self.textureRateo[2])
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glTexCoord2f(self.textureRateo[0], 0.0)
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glEnd()
		
		if self.idTextures[0] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
			glBindTexture(GL_TEXTURE_2D, self.soffitto)
			glBegin(GL_QUADS)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(0.0, self.textureRateo[2])
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glTexCoord2f(self.textureRateo[0], self.textureRateo[2])
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glTexCoord2f(self.textureRateo[0], 0.0)
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glEnd()

		if self.idTextures[2] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
			glBindTexture(GL_TEXTURE_2D, self.soffitto)
			glBegin(GL_QUADS)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[2][0], vertices[2][1], vertices[2][2])
			glTexCoord2f(0.0, self.textureRateo[2])
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glTexCoord2f(self.textureRateo[1], self.textureRateo[2])
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glTexCoord2f(self.textureRateo[1], 0.0)
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glEnd()

		if self.idTextures[3] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
			glBindTexture(GL_TEXTURE_2D, self.soffitto)
			glBegin(GL_TRIANGLES)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(self.textureRateo[0], 0)
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glTexCoord2f(0.5, 1)
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glEnd()

		if self.idTextures[4] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
			glBindTexture(GL_TEXTURE_2D, self.soffitto)
			glBegin(GL_TRIANGLES)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glTexCoord2f(0.0, self.textureRateo[2])
			glVertex3f(vertices[2][0], vertices[2][1], vertices[2][2])
			glTexCoord2f(self.textureRateo[1], self.textureRateo[2])
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glEnd()
	

		glDisable(GL_TEXTURE_2D)

class Material(object):

	def __init__(self, ambient, diffuse, specular, shine):
		self.ambient = ambient
		self.diffuse = diffuse
		self.specular = specular
		self.shine = shine

	def draw(self):
		glMaterialfv(GL_FRONT, GL_AMBIENT, self.ambient)
		glMaterialfv(GL_FRONT, GL_DIFFUSE, self.diffuse)
		glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular)
		glMaterialfv(GL_FRONT, GL_SHININESS, self.shine)

class Parallelepiped(object):
	def __init__(self, center, dimension, textureRateo, idTextures, alpha = None):
		self.center = center
		self.dimension = dimension

		self.textureRateo = textureRateo
		self.vertices = self.getAllVertices(self.center, self.dimension)

		self.idTextures = idTextures # up down 1_side 2_side, 3_side, 4_side
	
		self.listSymmetries = None

		self.alpha = alpha

	def getAllVertices(self, center, dimension):

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

	def drawFaces(self, center, dimension, vertices):

		if self.alpha != None:
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			glEnable(GL_ALPHA_TEST)
			glAlphaFunc(GL_GREATER, self.alpha)

		glEnable(GL_TEXTURE_2D)
		# -y +y +x -z -x +z
		# -y
		if self.idTextures[0] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[0]))
			glBegin(GL_QUADS)
			glNormal3f(0,-1,0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glTexCoord2f(0.0, self.textureRateo[2])
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glTexCoord2f(self.textureRateo[0], self.textureRateo[2])
			glVertex3f(vertices[6][0], vertices[6][1], vertices[6][2])
			glTexCoord2f(self.textureRateo[0], 0)
			glVertex3f(vertices[7][0], vertices[7][1], vertices[7][2])
			glEnd()

		# +y
		if self.idTextures[1] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[1]))
			glBegin(GL_QUADS)
			glNormal3f(0,1,0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(0.0, self.textureRateo[2])
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glTexCoord2f(self.textureRateo[0], self.textureRateo[2])
			glVertex3f(vertices[2][0], vertices[2][1], vertices[2][2])
			glTexCoord2f(self.textureRateo[0], 0.0)
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glEnd()
		# +x
		if self.idTextures[2] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[2]))
			glBegin(GL_QUADS)
			glNormal3f(1,0,0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glTexCoord2f(0.0, self.textureRateo[1])
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glTexCoord2f(self.textureRateo[2], self.textureRateo[1])
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(self.textureRateo[2], 0.0)
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glEnd()
		# -z
		if self.idTextures[3] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[3]))
			glBegin(GL_QUADS)
			glNormal3f(0,0,-1)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[6][0], vertices[6][1], vertices[6][2])
			glTexCoord2f(0.0, self.textureRateo[1])
			glVertex3f(vertices[2][0], vertices[2][1], vertices[2][2])
			glTexCoord2f(self.textureRateo[0], self.textureRateo[1])
			glVertex3f(vertices[1][0], vertices[1][1], vertices[1][2])
			glTexCoord2f(self.textureRateo[0], 0.0)
			glVertex3f(vertices[5][0], vertices[5][1], vertices[5][2])
			glEnd()
		# -x
		if self.idTextures[4] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[4]))
			glBegin(GL_QUADS)
			glNormal3f(-1,0,0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[7][0], vertices[7][1], vertices[7][2])
			glTexCoord2f(0.0, self.textureRateo[1])
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glTexCoord2f(self.textureRateo[2], self.textureRateo[1])
			glVertex3f(vertices[2][0], vertices[2][1], vertices[2][2])
			glTexCoord2f(self.textureRateo[2], 0.0)
			glVertex3f(vertices[6][0], vertices[6][1], vertices[6][2])
			glEnd()
		# +z
		if self.idTextures[5] != None:
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
			glBindTexture(GL_TEXTURE_2D, getTexture(self.idTextures[5]))
			glBegin(GL_QUADS)
			glNormal3f(.0,.0,1.0)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(vertices[4][0], vertices[4][1], vertices[4][2])
			glTexCoord2f(0.0, self.textureRateo[1])
			glVertex3f(vertices[0][0], vertices[0][1], vertices[0][2])
			glTexCoord2f(self.textureRateo[0], self.textureRateo[1])
			glVertex3f(vertices[3][0], vertices[3][1], vertices[3][2])
			glTexCoord2f(self.textureRateo[0], 0.0)
			glVertex3f(vertices[7][0], vertices[7][1], vertices[7][2])
			glEnd()

		glDisable(GL_TEXTURE_2D)
		if self.alpha != None:
			glDisable(GL_ALPHA_TEST)
			glDisable(GL_BLEND)

def drawCrossPanel(center, dimension, texture):

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
	glNormal3f(1,0,-1)
	glTexCoord2f(0.0, 0.0)
	glVertex3f(v6[0], v6[1], v6[2])
	glTexCoord2f(0.0, 0.9)
	glVertex3f(v2[0], v2[1], v2[2])
	glTexCoord2f(1, 0.9)
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
	glTexCoord2f(0.0, 0.9)
	glVertex3f(v3[0], v3[1], v3[2])
	glTexCoord2f(1, 0.9)
	glVertex3f(v1[0], v1[1], v1[2])
	glTexCoord2f(1, 0)
	glVertex3f(v5[0], v5[1], v5[2])
	glEnd()
	glDisable(GL_TEXTURE_2D)
	glDisable(GL_BLEND)	

def initTexture(pathImage):
	""" load texture """
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
	global listTextures
	print "loadTextures"
	listTextures = []
	listTextures.append(["grass", initTexture("grass.jpg")])
	listTextures.append(["wall2", initTexture("wallTest.jpg")])
	listTextures.append(["wall", initTexture("whiteWall.jpg")])
	listTextures.append(["frontDoor", initTexture("frontDoor.jpg")])
	listTextures.append(["windowDoor", initTexture("windowDoor.jpg")])
	listTextures.append(["test", initTexture("test.png")])
	listTextures.append(["grassLeaf", initTexture("grassLeaf.png")])
	listTextures.append(["parquet", initTexture("parquet.jpg")])
	listTextures.append(["window1", initTexture("window1.png")])
	listTextures.append(["window2", initTexture("window2.png")])
	listTextures.append(["window3", initTexture("window3.png")])
	listTextures.append(["window4", initTexture("window4.png")])
	listTextures.append(["mbl1", initTexture("mbl1.png")])
	listTextures.append(["mbl2", initTexture("mbl2.png")])
	listTextures.append(["mbl3", initTexture("mbl3.png")])
	listTextures.append(["mblBorder", initTexture("mblBorder.png")])
	listTextures.append(["tv", initTexture("tv.png")])

def getTexture(name):
	global listTextures
	for i in listTextures:
		if i[0] == name:
			return i[1]

def initScene():
	global player, listSceneObjects, listTextures, listGrass

	glEnable(GL_COLOR_MATERIAL)
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	#glEnable(GL_LIGHT1)
	glEnable(GL_DEPTH_TEST)

	player = Player()

	loadListTextures()

	listSceneObjects = []
	houseHeight = 3
	upFromGrass = 0.01
	doorHeight = 2.25
	pavimentoH = 0.5
	soffittoH = 5.5
	#listSceneObjects.append(Parallelepiped([1,1,1],[1,1,1],[1,1,1],["wall", "wall", "wall", "wall", "wall", "wall"]))
	#listSceneObjects.append(Parallelepiped([-1,1,-1],[1,1,1],[1,1,1],["wall", "wall", "wall", "wall", "wall", "wall"]))
	# -y +y +x -z -x +z
	
	listSceneObjects.append(Parallelepiped([.0,pavimentoH,10.0], [16.0,1,8.0], [16.0,1,8.0], [None, "parquet", None, "wall", None, "wall"]))
	temp = Parallelepiped([12.0,pavimentoH,0], [8.0,1,28.0], [8.0,1,28.0], [None, "parquet", "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	listSceneObjects.append(Parallelepiped([.0,soffittoH,10.0], [16.0,1,8.0], [16.0,1,8.0], ["wall", "wall", None, "wall", None, "wall"]))
	temp = Parallelepiped([12.0,soffittoH,0], [8.0,1,28.0], [8.0,1,28.0], ["wall", "wall", "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([15.5,3,9], [1,4,10.0], [1,4,10.0], [None, None, "wall", "wall", "wall", "wall"])
	temp.addSymmetry([True, False, False])
	temp.addSymmetry([True, False, True])
	temp.addSymmetry([False, False, True])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,3,6.5], [16,4,1], [16,4,1], [None, None, "wall", "wall", "wall", "wall"])
	listSceneObjects.append(temp)

	alpha = 0.5
	
	temp = Parallelepiped([0,3,12.5], [6,4,0.1], [1,1,0.01], [None, None, "window1", "window1", "window1", "window1"], alpha)
	listSceneObjects.append(temp)

	temp = Parallelepiped([5,3,12.5], [4,4,0.1], [1,1,0.01], [None, None, "window3", "window3", "window3", "window3"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,12.5], [4,4,0.1], [1,1,0.01], [None, None, "window1", "window1", "window1", "window1"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([13,3,12.5], [4,4,0.1], [1,1,0.01], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([15,3,0], [0.1,4,8], [0.01,1,1], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)


	temp = Parallelepiped([8.5,3,7], [1,4,0.1], [1,1,.01], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,5], [0.1,4,4], [0.01,1,1], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)
	
	temp = Parallelepiped([9,3,1], [0.1,4,4], [0.01,1,1], [None, None, "window1", "window1", "window1", "window1"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,-3], [0.1,4,4], [0.01,1,1], [None, None, "window3", "window3", "window3", "window3"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,-7], [0.1,4,4], [0.01,1,1], [None, None, "window1", "window1", "window1", "window1"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([9,3,-11], [0.1,4,4], [0.01,1,1], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([12,3,-13], [6,4,0.1], [1,1,0.01], [None, None, "window4", "window4", "window4", "window4"], alpha)
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)
	

	temp = Parallelepiped([0,3,7.5], [8,4,1], [1,1,1], [None, "mblBorder", "mblBorder", None, "mblBorder", "mbl3"], alpha)
	listSceneObjects.append(temp)
	gap = 2.2
	temp = Parallelepiped([0,1.05+gap,7.5], [4.8,-gap,-1], [1,1,1], ["mblBorder", "mblBorder", "mblBorder", None, "mblBorder", None])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,3.25,7.5], [4.5,2,0.05], [1,1,1], ["mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder", "tv"])
	listSceneObjects.append(temp)


	temp = Parallelepiped([6,1.5,10], [1,1,1], [1,1,1], [None, None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([11,1.5,10], [1,1,1], [1,1,1], [None, None, "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([8.5,1.30,11.25], [6.5,0.6,0.5], [7,1,1], [None,  "mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([8.5,1.30,8.75], [6.5,0.6,0.5], [7,1,1], [None,  "mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)

	temp = Parallelepiped([8.5,2,10], [7,0.1,2], [7,0.1,1], ["mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	temp.addSymmetry([True, False, False])
	listSceneObjects.append(temp)


	temp = Parallelepiped([0,1.5,11], [5,1,0.5], [5,1,1], [None, "mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)

	temp = Parallelepiped([0,1.25,11], [6,0.5,1.5], [5,1,1], [None, "mblBorder", "mblBorder", "mblBorder", "mblBorder", "mblBorder"])
	listSceneObjects.append(temp)

	'''listSceneObjects.append(Parallelepiped([2.0,10/2 + upFromGrass,-5.0], [1.0,10,1.0], [1.0,10,1.0], ["wall", "wall", "wall", "wall", "wall", "wall"]))
	listSceneObjects.append(Parallelepiped([8.0,7/2 + upFromGrass,-1.0], [4.0,7,10.0], [4.0,7,10.0], ["wall", "wall", "wall", "wall", "wall", "wall"]))
	listSceneObjects.append(Parallelepiped([-8.0,7/2 + upFromGrass,-1.0], [4.0,7,10.0], [4.0,7,10.0], ["wall", "wall", "wall", "wall", "wall", "wall"]))
	listSceneObjects.append(Parallelepiped([.0,doorHeight/2 + upFromGrass,-3.0], [1.5,doorHeight,0.1], [1,1,0.1], ["frontDoor", "frontDoor", "frontDoor", "frontDoor", "frontDoor", "frontDoor"]))
	listSceneObjects.append(Parallelepiped([4.0,doorHeight/2 + upFromGrass,-3.0], [1.5,doorHeight,0.1], [1,1,0.1], ["windowDoor", "windowDoor", "windowDoor", "windowDoor", "windowDoor", "windowDoor"]))
	listSceneObjects.append(Parallelepiped([-4.0,doorHeight/2 + upFromGrass,-3.0], [1.5,doorHeight,0.1], [1,1,0.1], ["windowDoor", "windowDoor", "windowDoor", "windowDoor", "windowDoor", "windowDoor"]))
	listSceneObjects.append(Parallelepiped([8.0,doorHeight/2 + upFromGrass,-6.0], [1.5,doorHeight,0.1], [1,1,0.1], ["windowDoor", "windowDoor", "windowDoor", "windowDoor", "windowDoor", "windowDoor"]))
	listSceneObjects.append(Parallelepiped([-8.0,doorHeight/2 + upFromGrass,-6.0], [1.5,doorHeight,0.1], [1,1,0.1], ["windowDoor", "windowDoor", "windowDoor", "windowDoor", "windowDoor", "windowDoor"]))
	'''

	#house ended

	listSceneObjects.append(Parallelepiped([0.0,.0,.0], [1,1,1], [1,1,1], [None, "test", "test", None, None, "test"]))

	max = 1000
	radius = 3
	listGrass = []
	temp = getGrassRand()
	for i in range(0, max):
		
		if i%10 == 0:
			temp = getGrassRand()
		listGrass.append([temp[0]+random()*radius-radius/2, temp[1]+random()*radius-radius/2])

def getGrassRand():

	border = 3
	tempX = random()*(widthGround*2-border*2)-(widthGround-border)
	tempY = random()*(widthGround*2-border*2)-(widthGround-border)
	temp = [tempX, tempY]
	gap = 19
	if temp[0] >= -gap and temp[0] <= gap and temp[1] >= -gap and temp[1] <= gap:
		return getGrassRand()
	return temp

def drawGrass():
	global listGrass
	texture = getTexture("grassLeaf")
	#drawCrossPanel([0,1.5,0],[1,1,1],texture)
	radius = 2.
	for i in listGrass:
		drawCrossPanel([i[0],radius/2.,i[1]],[radius,radius,radius], texture)

def drawScene():

	global _angle, player, listSceneObjects
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glMatrixMode(GL_MODELVIEW) #Switch to the drawing perspective
	glLoadIdentity() #Reset the drawing perspective
	
	player.update()

	

	createGround()
	drawGrass()
	drawGrid()
	#test()
	for i in listSceneObjects:
		i.draw()
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
	glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2,0.2,0.2,1])
	glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8,0.8,0.8,1])
	glLightfv(GL_LIGHT0, GL_SPECULAR, [.0,.0,.0,1])
	pos = [3, 1, 2, 0]
	glLightfv(GL_LIGHT0, GL_POSITION, pos)
	lightLine(pos)
	'''pos = [2, 2, 0, 1]
	glLightfv(GL_LIGHT1, GL_AMBIENT, [0.2,0,0.2,0])
	glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.1,0.0,0.8,1])
	glLightfv(GL_LIGHT1, GL_SPECULAR, [.0,.0,.0,1])
	glLightfv(GL_LIGHT1, GL_POSITION, pos)
	lightLine(pos)'''

def test():

	glTranslatef(0.0, 0.0, -5.0) #Move forward 5 units

	#Ex 1: Half the size
	glScalef(0.5,0.5,0.5)

	glPushMatrix() #Save the transformations performed thus far
	glTranslatef(0.0, -1.0, 0.0) #Move to the center of the trapezoid
	glRotatef(_angle, 0.0, 0.0, 1.0) #Rotate about the z-axis
	glBegin(GL_QUADS)

	#Trapezoid
	glVertex3f(-0.7, -0.5, 0.0)
	glVertex3f(0.7, -0.5, 0.0)
	glVertex3f(0.4, 0.5, 0.0)
	glVertex3f(-0.4, 0.5, 0.0)

	glEnd()

	glPopMatrix() #Undo the move to the center of the trapezoid

	glPushMatrix() #Save the current state of transformations

	glTranslatef(0.5,0.0,0.0)
	glPushMatrix()

	glTranslatef(1.0, 1.0, 0.0) #Move to the center of the pentagon
	glRotatef(2*_angle, 0.0, 1.0, 0.0) #Rotate about the y-axis
	glScalef(0.7, 0.7, 0.7) #Scale by 0.7 in the x, y, and z directions

	glBegin(GL_TRIANGLES)

	#Pentagon
	glVertex3f(-0.5, -0.5, 0.0)
	glVertex3f(0.5, -0.5, 0.0)
	glVertex3f(-0.5, 0.0, 0.0)

	glVertex3f(-0.5, 0.0, 0.0)
	glVertex3f(0.5, -0.5, 0.0)
	glVertex3f(0.5, 0.0, 0.0)

	glVertex3f(-0.5, 0.0, 0.0)
	glVertex3f(0.5, 0.0, 0.0)
	glVertex3f(0.0, 0.5, 0.0)

	glEnd()

	glPopMatrix() #Undo the move to the center of the pentagon
	glPushMatrix() #Save the current state of transformations
	glTranslatef(-1.0, 1.0, 0.0) #Move to the center of the triangle
	glRotatef(3*_angle, 1.0, 2.0, 3.0) #Rotate about the the vector (1, 2, 3)

	glBegin(GL_TRIANGLES)

	#Triangle
	glVertex3f(0.5, -0.5, 0.0)
	glVertex3f(0.0, 0.5, 0.0)
	glVertex3f(-0.5, -0.5, 0.0)

	glEnd()

	glPopMatrix()
	glPopMatrix()


	glColor3f(1.0, 0.0, 0.0);

	glBegin(GL_POLYGON);  #start house 
	glColor3f(1.0, 1.0, 0.0);
	glVertex2i(50, 0);
	glColor3f(0.0, 1.0, 0.0);
	glVertex2i(50, 100);
	glColor3f(0.0, 1.0, 1.0);
	glVertex2i(150, 100);
	glColor3f(1.0, 1.0, 0.0);
	glVertex2i(150,0);
	glEnd();   #end house

	glBegin(GL_POLYGON);  #start window 
	glColor3f(0.3, 0.2, 0.0);
	glVertex2i(60, 80);
	glVertex2i(80, 80);
	glVertex2i(80, 65);
	glVertex2i(60, 65);
	glEnd();   #end window

	glBegin(GL_POLYGON);  #start window
	glColor3f(0.3, 0.2, 0.0);
	glVertex2i(120, 80);
	glVertex2i(140, 80);
	glVertex2i(140, 65);
	glVertex2i(120, 65);
	glEnd();   #end window

	glBegin(GL_POLYGON); #start ceiling
	glColor3f(0.8, 0.0, 0.0);
	glVertex2i(50, 100);
	glColor3f(0.5, 0.0, 0.3);
	glVertex2i(150, 100);
	glColor3f(1.0, 0.0, 0.0);
	glVertex2i(100, 130);
	glEnd(); #end ceiling

	glBegin(GL_POLYGON);  #start door
	glColor3f(0.3, 0.2, 0.0);
	glVertex2i(80, 0);
	glVertex2i(80, 50);
	glVertex2i(120, 50);
	glVertex2i(120,0);
	glEnd();  #end door

def drawGrid():

	for i in range(0,50):

		glLineWidth(.1) 
		glBegin(GL_LINES)
		glVertex3f(i-25, -0.1, -25)
		glVertex3f(i-25, -0.1, 25)
		glEnd()

		glLineWidth(.1) 
		glBegin(GL_LINES)
		glVertex3f(-25, -0.1, i-25)
		glVertex3f(25, -0.1, i-25)
		glEnd()

def lightLine(point):
	glLineWidth(2.5) 
	glColor3f(1.0, 1.0, 1.0)
	glBegin(GL_LINES);
	glVertex3f(0, 0, 0)
	glVertex3f(point[0], point[1], point[2])
	glEnd()


def keyPressed(key, x, y):
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
	gluPerspective(60, float(width)/float(height), 0.1, maxViewDistance*2) # todo
	glMatrixMode(GL_MODELVIEW)

def main():
	global windowWidth, windowHeight, physicsThread

	glutInit()
	glutInitWindowSize(windowWidth, windowHeight)
	glutInitWindowPosition(windowX, windowY)
	glutCreateWindow("Assignment_3_Dream_House.py")
	glutReshapeFunc(resizeScene)
	#glutFullScreen()
	initScene()

	glutDisplayFunc(drawScene)
	glutIdleFunc(drawScene)
	glutKeyboardFunc(keyPressed)

	#glutMouseFunc(mousePressed)
	#glutMotionFunc(mouseMotion)
	glutPassiveMotionFunc(mouseMotion)

	glutMainLoop()

if __name__ == "__main__":
	print "\nHit ESC key to quit."
	main()
