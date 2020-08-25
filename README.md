# Noisy Walker

A quick demonstration of the effects of noise in Quantum computers

This game is terrible easy. Just use the arrows to move across the board. The board goes from 1 to 255, so 1...16, 17...., etc. So to move to the right it adds one, to the left decreases 1, up decreases 16 and down increases 16.

Really easy with the QArithmetic library: https://github.com/hkhetawat/QArithmetic

In a noiseless environment, one shot to the simulator will give you the right movement. But with the Melbourne_16 noise, things are different. Can you get safely to the other side of the board?


## Dependencies
- Python3
- Qiskit 0.20
- Pygame 1.9.6
