import pygame
import os

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# --- Function to load animation frames ---
def load_animation(folder_path):
    frames = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".png"):
            img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
            frames.append(img)
    return frames

# --- Load Animations ---
animations = {
    "run_left": load_animation("assets/jimbruz/Left - Running"),
    "walk_left": load_animation("assets/jimbruz/Left - Walking"),
    "idle_right": load_animation("assets/jimbruz/Right - Idle"),
}

# --- Animation Settings ---
current_animation = "idle_right"
frame_index = 0
animation_speed = 0.2  # lower = slower

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update frame
    frame_index += animation_speed
    if frame_index >= len(animations[current_animation]):
        frame_index = 0

    # Draw background
    screen.fill((30, 30, 30))

    # Draw current frame of animation
    frame = animations[current_animation][int(frame_index)]
    screen.blit(frame, (400, 300))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
