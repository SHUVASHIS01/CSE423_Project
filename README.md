# 3D Pac-Man Project

## Overview

In this enhanced 3D Pac-Man game, players navigate a redesigned maze collecting power-ups while avoiding enemies. The maze features green walls with a brick-like pattern, taller outer walls, and a cross-shaped inner layout. New gameplay elements, such as falling obstacles that destroy maze paths, increase the challenge. Multiple camera views, a dynamic HUD, and a vibrant color scheme (orange Pac-Man, purple enemies, cyan power-ups) ensure an engaging experience.

## Member 1 - Pac-Man Movement & Maze

### Pac-Man Controls
- Move Forward (W)
- Move Backward (S)
- Turn Left (A)
- Turn Right (D)

### Maze Design
- Design a 3D maze with green outer walls (60 units tall) and light green inner walls (40 units tall) in a cross shape
- Implement a brick-like texture with alternating green/light green segments
- Ensure collision detection with walls and destroyed paths

## Member 2 - Enemy Movement & Power-Ups

### Enemy Behavior
- Implement purple enemies that chase Pac-Man
- Random spawning at valid positions
- Collision with Pac-Man reduces lives

### Power-Up System
- Cyan power-ups restore lives when collected
- Random spawning and pulsing animation

## Member 3 - UI & HUD

### HUD Display
- Display lives, score, bullets missed, and camera mode in light blue text
- Show pause, game over, and speed boost status

### Pause/Resume
- Toggle pause with P key
- Display "Paused" text

### Game Over
- Display "Game Over" with restart option (R key)

## Member 4 - Environment & Gameplay Effects

### Falling Obstacles
- Dark red obstacles fall every 5 seconds  
- Create dark gray destroyed paths on impact  
- Pac-Man cannot cross destroyed paths  

### Camera System
- Top-down view (1 key)  
- Third-person view (2 key)  
- First-person view  
- Cycle views with right mouse click  

### Shooting & Special Ability
- Fire yellow bullets with the left mouse click  
- Activate 5-second speed boost with Spacebar  

---

## Key / Mouse Controls:
- W - Move Pac-Man Forward  
- S - Move Pac-Man Backward  
- A - Turn Left  
- D - Turn Right  
- 1 - Top-down Camera View  
- 2 - Third-person Camera View  
- P - Pause/Resume Game  
- Spacebar - Activate Speed Boost  
- Left Click - Fire Bullet  
- Right Click - First-person view  
- R - Restart Game  

## Summary of Distribution:
- Member 1 - Pac-Man controls, Maze design  
- Member 2 - Enemy logic, Power-up mechanics  
- Member 3 - HUD interface, Pause/Resume, Game Over screen  
- Member 4 - Falling obstacles, Camera system, Shooting & Speed boost
