"""
Level Editor
"""
import pygame
import sys
import time
from pygame.locals import *
clock = pygame.time.Clock()
pygame.init()

map_path = 'Game/data/map'
optimization = 0


pygame.display.set_caption("Level Editor")
WINDOW_SCALE = 3
WINDOW_SIZE = [384*WINDOW_SCALE, 216*WINDOW_SCALE]
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
DISPLAY_SIZE = [320, 216]
display = pygame.Surface(DISPLAY_SIZE)
UI_SIZE = [64, 216]
user_interface = pygame.Surface(UI_SIZE)


class button:
	def __init__(self, path, location):
		self.image = pygame.image.load(path+".png").convert()
		self.rect = pygame.Rect(location[0], location[1], self.image.get_width(), self.image.get_height())
		self.active = False


def load_map(path):
	f = open(path+'.txt', 'r')
	data = f.read()
	f.close()
	data = data.split('\n')
	game_map = []
	for row in data:
		if len(row) != 0:
			game_map.append(list(row))
	return game_map


def save_map(path, game_map):
	f = open(path+'.txt', 'w')
	for row in game_map:
		for tile in row:
			f.write(tile)
		f.write("\n")
	f.close()


def clip(surf, x, y, width, height):
	handle_surf = surf.copy()
	clip_rect = pygame.Rect(x, y, width, height)
	handle_surf.set_clip(clip_rect)
	image = surf.subsurface(handle_surf.get_clip())
	return image.copy()


class font:
	def __init__(self, path, colors):
		self.text_color = (255, 0, 0)
		self.background_color = (0, 0, 0)
		self.character_order = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.-,:+\'!?0123456789()/_=\\[]*"<>;'
		original_font_image = pygame.image.load('data/'+path+'.png').convert()
		current_char_width = 0
		self.color_renders = {}
		for color in colors:
			self.color_renders[color] = {}
			font_image = original_font_image.copy()
			font_image_copy = pygame.Surface(font_image.get_size())
			font_image.set_colorkey(self.text_color)
			font_image_copy.fill(color)
			font_image_copy.blit(font_image, (0, 0))
			font_image_copy.set_colorkey(self.background_color)
			character_count = 0
			for x in range(font_image_copy.get_width()):
				pixel_color = font_image_copy.get_at((x, 0))
				if pixel_color[0] == 127:
					char_img = clip(font_image_copy, x - current_char_width, 0, current_char_width, font_image_copy.get_height())
					self.color_renders[color][self.character_order[character_count]] = char_img.copy()
					character_count += 1
					current_char_width = 0
				else:
					current_char_width += 1

		self.space_width = self.color_renders[colors[0]]['A'].get_width()

	def render(self, surf, text, loc, color, spacing = 1):
		x_offset = 0
		for char in text:
			if char != ' ':
				self.color_renders[color][char].set_colorkey(self.background_color)
				surf.blit(self.color_renders[color][char], (loc[0] + x_offset, loc[1]))
				x_offset += self.color_renders[color][char].get_width() + spacing
			else:
				x_offset += self.space_width + spacing


game_map = load_map(map_path)
small_font = font('small_font', [(1, 1, 1)])

buttons = {}
buttons['save'] = button('data/buttons/save', (1, 1))
buttons['add_row_above'] = button('data/buttons/add_row_above', (1, buttons['save'].rect.h+3))
buttons['add_row_below'] = button('data/buttons/add_row_below', (1, buttons['add_row_above'].rect.y+buttons['add_row_above'].rect.h+2))
buttons['remove_row_above'] = button('data/buttons/remove_row_above', (1, buttons['add_row_below'].rect.y+buttons['add_row_below'].rect.h+2))
buttons['remove_row_below'] = button('data/buttons/remove_row_below', (1, buttons['remove_row_above'].rect.y+buttons['remove_row_above'].rect.h+2))
buttons['clear'] = button('data/buttons/clear', (1, 1))
buttons['add_column_left'] = button('data/buttons/add_column_left', (1, buttons['clear'].rect.h+3))
buttons['add_column_right'] = button('data/buttons/add_column_right', (1, buttons['add_column_left'].rect.y+buttons['add_column_left'].rect.h+2))
buttons['remove_column_left'] = button('data/buttons/remove_column_left', (1, buttons['add_column_right'].rect.y+buttons['add_column_right'].rect.h+2))
buttons['remove_column_right'] = button('data/buttons/remove_column_right', (1, buttons['remove_column_left'].rect.y+buttons['remove_column_left'].rect.h+2))
buttons['clear'].rect.x = UI_SIZE[0] - buttons['clear'].rect.w - 1
buttons['add_column_left'].rect.x = UI_SIZE[0] - buttons['add_column_left'].rect.w - 1
buttons['add_column_right'].rect.x = UI_SIZE[0] - buttons['add_column_right'].rect.w - 1
buttons['remove_column_left'].rect.x = UI_SIZE[0] - buttons['remove_column_left'].rect.w - 1
buttons['remove_column_right'].rect.x = UI_SIZE[0] - buttons['remove_column_right'].rect.w - 1

images = []
for i in range(10):
	try:
		images.append(pygame.image.load("data/images/image_"+str(i)+".png").convert())
	except:
		images.append(images[0].copy())

keys = [K_e, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]
key_pressed = []
for key in keys:
	key_pressed.append(False)

pos = [0,0]
tile_length = 16
scroll = [0, 0]
scroll_speed = 2
scroll_direction = {'right':False, 'left':False, 'up':False, 'down':False}

user_interface.fill((255, 255, 255))
for key in buttons:
	user_interface.blit(buttons[key].image, (buttons[key].rect.x, buttons[key].rect.y))

FPS_list = []
FPS = 60
last_time = time.time()
while True:
	display.fill((255, 255, 255))

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
			if event.key == K_d:
				scroll_direction['right'] = True
			if event.key == K_a:
				scroll_direction['left'] = True
			if event.key == K_w:
				scroll_direction['up'] = True
			if event.key == K_s:
				scroll_direction['down'] = True
			if event.key == K_o:
				if optimization == 0:
					optimization = 1
				else:
					optimization = 0
			for key in keys:
				if event.key == key:
					key_pressed[keys.index(key)] = True
		if event.type == KEYUP:
			if event.key == K_d:
				scroll_direction['right'] = False
			if event.key == K_a:
				scroll_direction['left'] = False
			if event.key == K_w:
				scroll_direction['up'] = False
			if event.key == K_s:
				scroll_direction['down'] = False
			for key in keys:
				if event.key == key:
					key_pressed[keys.index(key)] = False
		if pygame.mouse.get_pressed()[0]:
			for button in buttons:
				if buttons[button].rect.collidepoint((int(pos[0] - DISPLAY_SIZE[0]), int(pos[1]))):
					buttons[button].active = True

	if scroll_direction['right']:
		scroll[0] += scroll_speed
	if scroll_direction['left']:
		scroll[0] -= scroll_speed
	if scroll_direction['up']:
		scroll[1] -= scroll_speed
	if scroll_direction['down']:
		scroll[1] += scroll_speed

	if len(game_map)*tile_length - scroll[1] < DISPLAY_SIZE[1]:
		scroll[1] = len(game_map)*tile_length - DISPLAY_SIZE[1]
	if len(game_map[0])*tile_length - scroll[0] < DISPLAY_SIZE[0]:
		scroll[0] = len(game_map[0])*tile_length - DISPLAY_SIZE[0]
	if scroll[0] < 0:
		scroll[0] = 0
	if scroll[1] < 0:
		scroll[1] = 0

	if buttons['save'].active:
		save_map(map_path, game_map)
		buttons['save'].active = False
	if buttons['add_row_above'].active:
		game_map.insert(0, [])
		for item in game_map[1]:
			game_map[0].append('0')
		buttons['add_row_above'].active = False
	if buttons['add_row_below'].active:
		game_map.append([])
		for item in game_map[0]:
			game_map[-1].append('0')
		buttons['add_row_below'].active = False
	if buttons['remove_row_above'].active:
		if len(game_map) > 1:
			game_map.pop(0)
		buttons['remove_row_above'].active = False
	if buttons['remove_row_below'].active:
		if len(game_map) > 1:
			game_map.pop(-1)
		buttons['remove_row_below'].active = False
	if buttons['clear'].active:
		for y in range(len(game_map)):
			for x in range(len(game_map[y])):
				game_map[y][x] = '0'
		buttons['clear'].active = False
	if buttons['add_column_left'].active:
		for row in game_map:
			row.insert(0, '0')
		buttons['add_column_left'].active = False
	if buttons['add_column_right'].active:
		for row in game_map:
			row.append('0')
		buttons['add_column_right'].active = False
	if buttons['remove_column_left'].active:
		if len(game_map[0]) > 1:
			for row in game_map:
				row.pop(0)
		buttons['remove_column_left'].active = False
	if buttons['remove_column_right'].active:
		if len(game_map[0]) > 1:
			for row in game_map:
				row.pop(-1)
		buttons['remove_column_right'].active = False

	tiles_blitted = 0
	y = 0
	for layer in game_map:
		x = 0
		for tile in layer:
			for i in range(optimization, 10):
				if tile == str(i):
					if x*tile_length - scroll[0] > -tile_length and y*tile_length - scroll[1] > -tile_length and x*tile_length - scroll[0] < DISPLAY_SIZE[0] and y*tile_length - scroll[1] < DISPLAY_SIZE[1]:
						display.blit(images[i], (x*tile_length - scroll[0], y*tile_length - scroll[1]))
						tiles_blitted += 1
			if pos[0] > x*tile_length - scroll[0] and pos[0] < x*tile_length - scroll[0] + tile_length and pos[1] > y*tile_length - scroll[1] and pos[1] < y*tile_length - scroll[1] + tile_length:
				for i in range(len(key_pressed)):
					if key_pressed[i]:
						game_map[y][x] = str(i)
			x += 1
		y += 1
	
	dt = time.time() - last_time
	last_time = time.time()
	
	if len(FPS_list) >= 5:
		FPS = 0
		for item in FPS_list:
			FPS += item
		FPS = FPS // 5
		FPS_list = []
	FPS_list.append(int(1/dt+0.5))
	small_font.render(display, 'FPS: ' + str(FPS), (5, 5), (1, 1, 1))

	screen.blit(pygame.transform.scale(display, (DISPLAY_SIZE[0]*WINDOW_SCALE, DISPLAY_SIZE[1]*WINDOW_SCALE)), (0,0))
	screen.blit(pygame.transform.scale(user_interface, (UI_SIZE[0]*WINDOW_SCALE, UI_SIZE[1]*WINDOW_SCALE)), (DISPLAY_SIZE[0]*WINDOW_SCALE,0))
	pygame.display.update()
	clock.tick(60)