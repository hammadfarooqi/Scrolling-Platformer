import pygame

def load_map(path):
	f = open(path+'.txt', 'r')
	data = f.read()
	f.close()
	data = data.split('\n')
	game_map = []
	for row in data:
		game_map.append(list(row))
	return game_map

def load_animation(path, frame_durations, animation_frames):
	animation_name = path.split('/')[-1]
	animation_frame_data = []
	n = 0
	for frame in frame_durations:
		animation_frame_ID = animation_name + str(n)
		image_location = path + '/' + animation_frame_ID + '.png'
		animation_image = pygame.image.load(image_location).convert()
		animation_image.set_colorkey((255, 255, 255))
		animation_frames[animation_frame_ID] = animation_image.copy()
		for i in range (frame):
			animation_frame_data.append(animation_frame_ID)
		n += 1
	return animation_frame_data, animation_frames

def change_animation(action, frame, new_action):
	if action != new_action:
		action = new_action
		frame = 0
	return action, frame

class player():
	def __init__(self, rect_dimensions):
		self.rect = pygame.Rect(rect_dimensions)
		self.spawn = [rect_dimensions[0], rect_dimensions[1]]
		self.movement = [0, 0]
		self.air_timer = 0
		self.moving_right = False
		self.moving_left = False
		self.jump = False
		self.y_momentum = 0
		self.action = 'idle'
		self.frame = 0
		self.flip = False
		self.animation_frames = {}
		self.animation_database = {}
		self.hit_list = []
		self.collisions = {'top':False,'bottom':False,'right':False,'left':False}
		self.dead = False
		self.speed = 1
		
	def collision_test(self, tiles):
		self.hit_list.clear()
		for tile in tiles:
			if self.rect.colliderect(tile):
				self.hit_list.append(tile)
						
	def move(self, tiles, checkpoints):
		for item in self.collisions:
			self.collisions[item] = False
		self.rect.x += self.movement[0]
		self.collision_test(tiles)
		for tile in self.hit_list:
			if self.movement[0] > 0:
				self.rect.right = tile.left
				self.collisions['left'] = True
			elif self.movement[0] < 0:
				self.rect.left = tile.right
				self.collisions['right'] = True
		self.rect.y += self.movement[1]
		checkpoint_collision = self.rect.collidelist(checkpoints)
		self.collision_test(tiles)
		for tile in self.hit_list:
			if self.movement[1] > 0:
				self.rect.bottom = tile.top
				self.collisions['bottom'] = True
			elif self.movement[1] < 0:
				self.rect.top = tile.bottom
				self.collisions['top'] = True
		return checkpoint_collision


class button():
	def __init__(self, path, location):
		self.image = pygame.image.load("data/buttons/"+path+".png").convert()
		self.rect = pygame.Rect(location[0], location[1], self.image.get_width(), self.image.get_height())
		self.active = False
		self.show = False

class checkpoint():
	def __init__(self, location):
		self.rect = pygame.Rect(location[0], location[1], 16, 16)
		self.action = 'unused'
		self.frame = 0
		self.animation_database = {}
		self.animation_frames = {}
		self.animation_database['unused'], self.animation_frames = load_animation('data/checkpoint_animations/unused', [18, 6, 12, 6], self.animation_frames)
		self.animation_database['used'], self.animation_frames = load_animation('data/checkpoint_animations/used', [18, 6, 12, 6], self.animation_frames)
		self.animation_database['active'], self.animation_frames = load_animation('data/checkpoint_animations/active', [7, 6, 5, 4, 5, 6, 7], self.animation_frames)

class jump_pad():
	def __init__(self, location):
		self.rect = pygame.Rect(location[0], location[1], 16, 16)
		self.action = 'idle'
		self.frame = 0
		self.animation_database = {}
		self.animation_frames = {}
		self.animation_database['idle'], self.animation_frames = load_animation('data/jump_pad_animations/idle', [1], self.animation_frames)
		self.animation_database['active'], self.animation_frames = load_animation('data/jump_pad_animations/active', [2, 2, 1, 1, 1], self.animation_frames)

class spike():
	def __init__(self, location):
		self.rect = pygame.Rect(location[0], location[1], 16, 16)
		self.action = 'spike'
		self.frame = 0
		self.animation_database = {}
		self.animation_frames = {}
		self.animation_database['spike'], self.animation_frames = load_animation('data/spike', [6, 6, 6, 6], self.animation_frames)
		self.mask = pygame.mask.from_surface(self.animation_frames['spike0'])

class speed_pad():
	def __init__(self, location):
		self.rect = pygame.Rect(location[0], location[1], 16, 16)
		self.hitbox = pygame.Rect(location[0], location[1] + 14, 16, 2)
		self.image = pygame.image.load('data/environment/speed_pad.png').convert()
		self.image.set_colorkey((255, 255, 255))
		self.timer = 0
		
def clip(surf, x, y, width, height):
	handle_surf = surf.copy()
	clip_rect = pygame.Rect(x, y, width, height)
	handle_surf.set_clip(clip_rect)
	image = surf.subsurface(handle_surf.get_clip())
	return image.copy()

class font():
	def __init__(self, path, colors):
		self.text_color = (255, 0, 0)
		self.background_color = (0, 0, 0)
		self.character_order = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.-,:+\'!?0123456789()/_=\\[]*"<>;'
		original_font_image = pygame.image.load('data/fonts/'+path+'.png').convert()
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
