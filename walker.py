
import random, pygame, sys
import math
from pygame.locals import *
import numpy as np


from qiskit import IBMQ, Aer, execute, QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.providers.aer.noise import NoiseModel

from QArithmetic import sub, add

FPS = 5

WINDOWWIDTH = 320
WINDOWHEIGHT = 320
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

"""
Board

    1   2 ...... 16
    17  18.......32
    .
    .
    .
    241..........255

0. Random position 1-255
1. Calculate position
2. Get movement instruction
3. Calculate new position by adding or substracting N (i.e. 17-UP must go to 1, so subsctract 16)
4. Generate N addition / substraction gates, and execute the simulation with a noise model
5. Move the position to the output, whether it was the intended or an error due to noise.

"""


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    while True:
        runGame()


def runGame():

    noiseless_new_position = new_position = position = getRandomLocation()

    # Get Noise levels from Melbourne Q Computer
    provider = IBMQ.load_account()
    backend = provider.get_backend('ibmq_16_melbourne')
    noise_model = NoiseModel.from_backend(backend)


    while True: # main game loop

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawPosition(new_position)

        position_binary = toBinary(position)

        # Key control
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a):
                    new_position = calculateQuantumPosition(position, 1, "sub", noise_model)
                    noiseless_new_position = position - 1
                elif (event.key == K_RIGHT or event.key == K_d):
                    new_position = calculateQuantumPosition(position, 1, "add", noise_model)
                    noiseless_new_position = position + 1
                elif (event.key == K_UP or event.key == K_w):
                    new_position = calculateQuantumPosition(position, 16, "sub", noise_model)
                    noiseless_new_position = position - 16
                elif (event.key == K_DOWN or event.key == K_s):
                    new_position = calculateQuantumPosition(position, 16, "add", noise_model)
                    noiseless_new_position = position + 16
                elif event.key == K_ESCAPE:
                    terminate()

        if (new_position != noiseless_new_position):
            print("Error due to Noise! Wanted: ", noiseless_new_position, " Got: ", new_position)

        drawPosition(new_position)
        position = new_position

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

def getRandomLocation():
    return random.randint(1, 255)


def drawPosition(position):
    x = (position - 1) % 16
    y = math.floor((position - 1) / 16)

    x *= CELLSIZE
    y *= CELLSIZE
    wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
    wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
    pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

def calculateQuantumPosition(position, movement, operation, noise_model):
    binary_position = toBinary(position)

    # Registers and circuit.
    a = QuantumRegister(8)
    b = QuantumRegister(8)
    ca = ClassicalRegister(8)
    cb = ClassicalRegister(8)
    qc = QuantumCircuit(a, b, ca, cb)

    binary_movement = toBinary(movement)

    prepareState(qc, binary_position, a)
    prepareState(qc, binary_movement, b)

    if (operation == 'add'):
        add(qc, a, b, 8)
    else:
        sub(qc, a, b, 8)

    # Measure the results.
    qc.measure(a, ca)
    qc.measure(b, cb)

    qc.measure_all()
    backend = Aer.get_backend("qasm_simulator")
    job = execute(qc, backend, shots=1, noise_model=noise_model).result()
    counts = job.get_counts(qc)
    print(counts)
    for t in counts:
        t = t[17:17+8]
        return int(t, 2)

def toBinary(decimal_number):
    return format(decimal_number, '08b')

def prepareState(qc, binary_position, register):
    t = 0
    for j, i in reversed(list(enumerate(binary_position))):
        if i == '1':
            qc.x(register[t])
        t += 1
    return qc

if __name__ == '__main__':
    main()
