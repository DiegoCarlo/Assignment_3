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

### view ###
maxViewDistance = 50

class Player(object):

	def __init__(self, speed):
		self.speed = speed

def createGround():
	glPushMatrix()
	
	glPopMatrix()
def initScene():

	glEnable(GL_DEPTH_TEST)
	createGround()


def keyPressed(key, x, y):

	if key == chr(27):
		sys.exit()


def drawScene():

	a = 0

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

	glutMainLoop()

if __name__ == "__main__":
	print "\nHit ESC key to quit."
	main()