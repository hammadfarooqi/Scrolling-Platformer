import pygame, sys, time
from Engine import *

clock = pygame.time.Clock()

from pygame.locals import *
pygame.init()

WINDOW_SCALE = 3
WINDOW_SIZE = (int(384*WINDOW_SCALE), int(216*WINDOW_SCALE))
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
TRUE_WINDOW_SIZE = (384, 216)
display = pygame.Surface(TRUE_WINDOW_SIZE)

game_map = load_map("data/map")
start_spawn = [40, (len(game_map)-10)*16 - 21]
man = player([start_spawn[0], start_spawn[1], 11, 21])
man.animation_database['idle'], man.animation_frames = load_animation('data/player_animations/idle', [10, 10, 10, 10], man.animation_frames)
man.animation_database['run'], man.animation_frames = load_animation('data/player_animations/run', [5, 5, 5, 5, 5], man.animation_frames)
man.animation_database['jump_up'], man.animation_frames = load_animation('data/player_animations/jump_up', [1], man.animation_frames)
man.animation_database['jump_down'], man.animation_frames = load_animation('data/player_animations/jump_down', [1], man.animation_frames)
man.animation_database['death'], man.animation_frames = load_animation('data/player_animations/death', [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 12], man.animation_frames)
true_scroll = [1000, 0]

checkpoints = []
y = 0
for layer in game_map:
	x = 0
	for tile in layer:
		if tile == "3":
			checkpoints.append(checkpoint((x*16, y*16)))
		x += 1
	y += 1

jump_pads = []
y = 0
for layer in game_map:
	x = 0
	for tile in layer:
		if tile == "4":
			jump_pads.append(jump_pad((x*16, y*16)))
		x += 1
	y += 1

spikes = []
y = 0
for layer in game_map:
	x = 0
	for tile in layer:
		if tile == "5":
			spikes.append(spike((x*16, y*16)))
		x += 1
	y += 1

speed_pads = []
y = 0
for layer in game_map:
	x = 0
	for tile in layer:
		if tile == "6":
			speed_pads.append(speed_pad((x*16, y*16)))
		x += 1
	y += 1

grass_image = pygame.image.load("data/environment/grass.png").convert()
dirt_image = pygame.image.load("data/environment/dirt.png").convert()
checkpoint_image = pygame.image.load("data/environment/checkpoint.png").convert()

small_font = font('small_font', [(100, 100, 100), (1, 1, 1), (255, 0, 0)])
large_font = font('large_font', [(1, 1, 1)])

icon_image = pygame.image.load('data/icon_image.png').convert()
icon_image = pygame.transform.scale(icon_image, (32, 32))
icon_surface = pygame.Surface(icon_image.get_size())
icon_surface.blit(icon_image, (0,0))
icon_surface.set_colorkey((255, 255, 255))

pygame.display.set_icon(icon_surface)
pygame.display.set_caption("Amazing Game")

buttons = {}

def run_menu(screen, display):
	return True, False
	#Menu isn't done yet, so for now, it will just skip it
	
	pos = [0,0]
	display.fill((255, 140, 0))
	large_font.render(display, 'Menu', (10, 10), (1, 1, 1))
	while True:
		for event in pygame.event.get():
			mouse_position = pygame.mouse.get_pos()
			pos[0] = mouse_position[0] / WINDOW_SCALE
			pos[1] = mouse_position[1] / WINDOW_SCALE
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
				if event.key == K_f:
					screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
				if event.key == K_q:
					return True, False
			for key in buttons:
				if button[key].show == True:
					user_interface.blit(buttons[key].image, (buttons[key].rect.x, buttons[key].rect.y))
				if buttons[button].rect.collidepoint(pos):
					if pygame.mouse.get_pressed()[0]:
						buttons[button].active = True

		screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
		pygame.display.update()

def run_options(screen, display):
	return True
	
	pos = [0,0]
	display.fill((255, 0, 155))
	while True:
		for event in pygame.event.get():
			mouse_position = pygame.mouse.get_pos()
			pos[0] = mouse_position[0] / WINDOW_SCALE
			pos[1] = mouse_position[1] / WINDOW_SCALE
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
				if event.key == K_f:
					screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
				if event.key == K_q:
					return True
			for key in buttons:
				if button[key].show == True:
					user_interface.blit(buttons[key].image, (buttons[key].rect.x, buttons[key].rect.y))
				if buttons[button].rect.collidepoint(pos):
					if pygame.mouse.get_pressed()[0]:
						buttons[button].active = True

		screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
		pygame.display.update()

menu = True
options = False
run = False
framerate = 60
max_height = 0.0
while True:
	if menu:
		run, options = run_menu(screen, display)
		menu = False

	if options:
		menu = run_options(screen, display)
		options = False

	FPS_list = []
	FPS = 60
	last_time = time.time()
	while run:
		display.fill((146, 244, 255))

		true_scroll[0] += (man.rect.x - true_scroll[0] - TRUE_WINDOW_SIZE[0]//2 - (man.rect.w//2))/15
		if man.y_momentum > 8:
			true_scroll[1] += man.y_momentum - 0.4
		else:
			true_scroll[1] += (man.rect.y - true_scroll[1] - TRUE_WINDOW_SIZE[1]//2 - (man.rect.h//2))/15
		scroll = true_scroll.copy()
		scroll[0] = int(scroll[0])
		scroll[1] = int(scroll[1])

		tile_rects = []
		y = 0
		for layer in game_map:
			x = 0
			for tile in layer:
				if x*16 - scroll[0] > -16 and y*16 - scroll[1] > -16 and x*16 - scroll[0] < TRUE_WINDOW_SIZE[0] and y*16 - scroll[1] < TRUE_WINDOW_SIZE[1]:
					if tile == "1":
						display.blit(dirt_image, (x*16 - scroll[0], y*16 - scroll[1]))
					elif tile == "2":
						display.blit(grass_image, (x*16 - scroll[0], y*16 - scroll[1]))
					elif tile == '3':
						for item in checkpoints:
							if item.rect.x / 16 == x and item.rect.y / 16 == y:
								item.frame += 1
								if item.frame >= len(item.animation_database[item.action]):
									if item.action == 'active':
										item.action, item.frame = change_animation(item.action, item.frame, 'used')
									item.frame = 0
								checkpoint_image_ID = item.animation_database[item.action][item.frame]
								checkpoint_image = item.animation_frames[checkpoint_image_ID]
								display.blit(checkpoint_image, (item.rect.x - scroll[0], item.rect.y - scroll[1]))
					elif tile == '4':
						for item in jump_pads:
							if item.rect.x / 16 == x and item.rect.y / 16 == y:
								item.frame += 1
								if item.frame >= len(item.animation_database[item.action]):
									if item.action == 'active':
										item.action, item.frame = change_animation(item.action, item.frame, 'idle')
									item.frame = 0
								jump_pad_image_ID = item.animation_database[item.action][item.frame]
								jump_pad_image = item.animation_frames[jump_pad_image_ID]
								display.blit(jump_pad_image, (item.rect.x - scroll[0], item.rect.y - scroll[1]))
					elif tile == '5':
						for item in spikes:
							if item.rect.x / 16 == x and item.rect.y / 16 == y:
								item.frame += 1
								if item.frame >= len(item.animation_database[item.action]):
									item.frame = 0
								spike_image_ID = item.animation_database[item.action][item.frame]
								spike_image = item.animation_frames[spike_image_ID]
								display.blit(spike_image, (item.rect.x - scroll[0], item.rect.y - scroll[1]))
					elif tile == '6':
						for item in speed_pads:
							display.blit(item.image, (x*16 - scroll[0], y*16 - scroll[1]))
				if tile != '0' and tile != '4' and tile != '5' and tile != '6':
					tile_rects.append(pygame.Rect(x*16, y*16, 16, 16))
				
				x += 1
			y += 1

		man.movement = [0, 0]
		if man.action != 'death':
			if man.moving_right:
				man.movement[0] += 2 * man.speed
			if man.moving_left:
				man.movement[0] -= 2 * man.speed
			man.movement[1] += man.y_momentum
			man.y_momentum += 0.2
		# if man.y_momentum > 5:
		# 	man.y_momentum = 5
			if man.air_timer >= 6:
				if man.y_momentum <= 0:
					man.action, man.frame = change_animation(man.action, man.frame, 'jump_up')
				else:
					man.action, man.frame = change_animation(man.action, man.frame, 'jump_down')
			else:
				if man.movement[0] != 0:
					man.action, man.frame = change_animation(man.action, man.frame, 'run')
				else:
					man.action, man.frame = change_animation(man.action, man.frame, 'idle')
		else:
			man.y_momentum = 0

		if man.movement[0] > 0:
			man.flip = False
		elif man.movement[0] < 0:
			man.flip = True

		checkpoint_collisions = man.move(tile_rects, checkpoints)

		if man.collisions['bottom']:
			man.air_timer = 0
			man.y_momentum = 0
		else:
			man.air_timer += 1
		if man.collisions['top']:
			man.y_momentum = 0

		man.frame += 1
		if man.frame >= len(man.animation_database[man.action]):
			if man.action == 'death':
				man.dead = True
				man.action, man.frame = change_animation(man.action, man.frame, 'idle')
			man.frame = 0
		player_image_ID = man.animation_database[man.action][man.frame]
		player_image = man.animation_frames[player_image_ID]

		if man.dead:
			man.rect.x = man.spawn[0]
			man.rect.y = man.spawn[1]
			man.y_momentum = 0
			man.dead = False
			for item in speed_pads:
				item.timer = 0

		display.blit(pygame.transform.flip(player_image, man.flip, False), (man.rect.x - scroll[0], man.rect.y - scroll[1]))
		player_mask = pygame.mask.from_surface(pygame.transform.flip(player_image, man.flip, False))

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_RIGHT:
					man.moving_right = True
				if event.key == K_LEFT:
					man.moving_left = True
				if event.key == K_UP:
					man.jump = True
				if event.key == K_ESCAPE:
					screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
				if event.key == K_f:
					screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
				if event.key == K_r:
					man.action, man.frame = change_animation(man.action, man.frame, 'death')
			if event.type == KEYUP:
				if event.key == K_RIGHT:
					man.moving_right = False
				if event.key == K_LEFT:
					man.moving_left = False
				if event.key == K_UP:
					man.jump = False
		
		if man.jump:
			if man.air_timer < 6:
				man.y_momentum = -4
				man.air_timer = 6

		for item in jump_pads:
			if item.rect.colliderect(man.rect):
				item.action, item.frame = change_animation(item.action, item.frame, 'active')
				man.air_timer = 6
				man.y_momentum = -man.y_momentum + 2
				if man.y_momentum > -6:
					man.y_momentum = -6

		man.speed = 1
		for item in speed_pads:
			if item.hitbox.colliderect(man.rect):
				item.timer = 60
			if item.timer != 0:
				item.timer -= 1
				man.speed = 2

		for item in spikes:
			if item.rect.colliderect(man.rect):
				if player_mask.overlap(item.mask, (item.rect.x - man.rect.x, item.rect.y - man.rect.y)) != None:
					man.action, man.frame = change_animation(man.action, man.frame, 'death')

		for item in checkpoints:
			if checkpoints.index(item) == checkpoint_collisions and item.action == 'unused':
				item.action, item.frame = change_animation(item.action, item.frame, 'active')
				man.spawn[0] = item.rect.x + item.rect.w//2 - man.rect.w//2
				man.spawn[1] = item.rect.y - man.rect.h

		if man.rect.y > (len(game_map)-8)*16:
			man.action, man.frame = change_animation(man.action, man.frame, 'death')
		
		delta_time = time.time() - last_time
		last_time = time.time()
		
		if len(FPS_list) >= 5:
			FPS = 0
			for item in FPS_list:
				FPS += item
			FPS = FPS // 5
			FPS_list = []
		FPS_list.append(int(1/delta_time+0.5))
		
		small_font.render(display, 'FPS: ' + str(FPS), (5, 25), (100, 100, 100))
		height = (-man.rect.y + len(game_map) * 16 - 197)/5
		small_font.render(display, 'Height: ' + str(height) + 'ft', (5, 5), (100, 100, 100))
		if max_height < height:
			max_height = height
		small_font.render(display, 'Heighest Height: ' + str(max_height) + 'ft', (5, 15), (100, 100, 100))
		
		screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
		pygame.display.update()
		clock.tick(60)