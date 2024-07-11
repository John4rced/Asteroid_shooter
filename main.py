import pygame
import os
import random

import cProfile

created_objects = 0
removed_objects = 0
score = 0


def main_loop():
    global removed_objects, created_objects, score

    # Basic setup
    pygame.init()
    WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1020
    game_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Asteroid_Shooter V.2.0')
    pygame.display.set_icon(pygame.image.load('favicon.ico'))
    clock = pygame.time.Clock()
    DISPLAY_WIDTH, DISPLAY_HEIGHT = (WINDOW_WIDTH * 2), (WINDOW_HEIGHT * 2)
    display_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # Uploading images of space objects

    exclude_file = 'gas_ring1.png'
    font = pygame.font.Font(os.path.join('../graphics/fonts/darknet.ttf'), 15)
    #
    space_objects_images = []
    folder_path = '../graphics/space_copy2'
    file_names = os.listdir(folder_path)

    for file_name in file_names:
        if file_name != exclude_file:
            file_path = os.path.join(folder_path, file_name)
            image_star = pygame.image.load(file_path)
            space_objects_images.append(image_star)

    # Uploading asteroids images
    asteroid_images = []
    asteroid_path = '../graphics/asteroids'
    asteroid_names = os.listdir(asteroid_path)
    for asteroid_name in asteroid_names:
        asteroid_full_path = os.path.join(asteroid_path, asteroid_name)
        image_a = pygame.image.load(asteroid_full_path).convert_alpha()
        asteroid_images.append(image_a)

    laser_images = []
    laser_path = '../graphics/laser_sprites'
    laser_names = os.listdir(laser_path)
    for laser_name in laser_names:
        laser_full_path = os.path.join(laser_path, laser_name)
        image_l = pygame.image.load(laser_full_path).convert_alpha()
        laser_images.append(image_l)

    ship_images = []
    ship_path = '../graphics/space_ship'
    ship_names = os.listdir(ship_path)
    for ship_name in ship_names:
        ship_full_path = os.path.join(ship_path, ship_name)
        image_ship = pygame.image.load(ship_full_path).convert_alpha()
        ship_images.append(image_ship)

    class BackgroundLayer:
        def __init__(self, image_path, speed, window_width, window_height):
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (window_width, window_height))
            self.speed = speed
            self.y1 = 0
            self.y2 = -window_height

        def update(self, dt):
            self.y1 += self.speed * dt
            self.y2 += self.speed * dt
            if self.y1 >= WINDOW_HEIGHT:
                self.y1 = -WINDOW_HEIGHT
            if self.y2 >= WINDOW_HEIGHT:
                self.y2 = -WINDOW_HEIGHT

        def draw(self, surface):
            surface.blit(self.image, (0, self.y1))
            surface.blit(self.image, (0, self.y2))

        def increase_speed(self, amount, dt):
            self.speed += amount
            if self.speed >= 200:
                self.speed = 200

        def decrease_speed(self, amount, dt):
            self.speed -= amount * dt
            if self.speed <= 5:
                self.speed = 5

    class Score:
        def __init__(self):
            self.time_score = 0
            self.font = pygame.font.Font(os.path.join('../graphics/fonts/darknet.ttf'), 20)

            self.collision_points = 0
            self.start_time = pygame.time.get_ticks()

        def collision_increase(self):
            self.collision_points += 100

        def collision_decrease(self):
            self.collision_points -= 150

        def update_time_score(self):
            current_time = pygame.time.get_ticks()
            self.time_score = (current_time - self.start_time) // 100

        def game_over(self):
            total_score = round(self.collision_points + self.time_score)
            return total_score < 0

        def display(self, surface):
            self.update_time_score()
            total_score = self.collision_points + self.time_score

            score_text = self.font.render(f'Score: {total_score}', True, pygame.Color(3, 160, 98))
            surface.blit(score_text, (10, 30))

    # class ImageCacheMixin:
    #     def __init__(self):
    #         self.original_images = []
    #
    #     # def load_image(self, filepath):
    #     #     if filepath not in self.image_cache:
    #     #         image = pygame.image.load(filepath).convert_alpha()
    #     #         self.image_cache[filepath] = image
    #     #     return self.image_cache[filepath]
    #
    #     def load_images(self, path):
    #         images = []
    #         for filename in os.listdir(path):
    #             if filename.endswith(".png"):
    #                 image = pygame.image.load(os.path.join(path, filename)).convert_alpha()
    #                 images.append(image)
    #         self.original_images = images
    #         return images

    class AccumulationMixin:
        def __init__(self):
            self.x_accumulation = 0.0
            self.y_accumulation = 0.0

        def accumulate(self, dx, dy):
            self.x_accumulation += dx
            self.y_accumulation += dy

        def apply_accumulation(self, rect):
            rect.x += round(self.x_accumulation)
            rect.y += round(self.y_accumulation)
            self.x_accumulation -= round(self.x_accumulation)
            self.y_accumulation -= round(self.y_accumulation)

    class AccumulationMixinFrames:
        def __init__(self):
            super().__init__()
            self.accumulated_value = 0

        def accumulate(self, value):
            self.accumulated_value += value

    class MovementMixin(AccumulationMixin):
        def __init__(self, speed):
            super().__init__()
            self.p0 = None
            self.p1 = None
            self.p2 = None
            self.p3 = None
            self.current_time_ms = 0
            self.speed = speed
            self.direction = pygame.math.Vector2(0, 0)

        def set_direction(self, direction):
            self.direction = direction.normalize()

        def increase_speed(self, amount, dt):
            print(f'DT =: {dt}')
            self.speed += amount * dt
            if self.speed >= 200:
                self.speed = 200

        def decrease_speed(self, amount, dt):
            self.speed -= amount * dt
            if self.speed <= 5:
                self.speed = 5

        def set_direction_formula(self, formula):
            self.direction = pygame.math.Vector2(formula).normalize()

        def update_position(self, dt):
            self.accumulate(self.speed * self.direction.x * dt, self.speed * self.direction.y * dt)

        def apply_movement(self, rect):
            self.apply_accumulation(rect)

        def set_bezier(self, p0, p1, p2, p3):
            self.p0 = p0
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3

        def update_bezier(self, dt):
            if self.p0 and self.p1 and self.p2 and self.p3:
                self.current_time_ms += dt * self.speed / 1000
                t = max(0, min(1, self.current_time_ms))

                x = ((1 - t) ** 3 * self.p0[0] +
                     3 * (1 - t) ** 2 * t * self.p1[0] +
                     3 * (1 - t) * t ** 2 * self.p2[0] +
                     t ** 3 * self.p3[0])
                y = ((1 - t) ** 3 * self.p0[1] +
                     3 * (1 - t) ** 2 * t * self.p1[1] +
                     3 * (1 - t) * t ** 2 * self.p2[1] +
                     t ** 3 * self.p3[1])
                print(f"Bezier update: t={t}, x={x}, y={y}, current_time_ms={self.current_time_ms}")
                if t >= 1:
                    self.current_time_ms = 0
                elif t <= 0:
                    self.current_time_ms = 0
                return x, y
            else:
                return None

    class AnimationMixin(AccumulationMixin, AccumulationMixinFrames):

        def __init__(self):
            super().__init__()
            self.start_size = (10, 10)
            self.target_size = (300, 300)
            self.animation_frames = []
            self.current_frame = 0
            self.animation_speed = 60
            self.last_update = pygame.time.get_ticks()
            self.frame_accumulator = 0
            self.num_frames = 0

        def generate_animation_frames(self, image):
            self.num_frames = image.get_width() // image.get_height()
            frame_width = image.get_width() // self.num_frames
            frame_height = image.get_height()

            self.animation_frames.clear()

            for i in range(self.num_frames):
                frame = image.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame_scaled = pygame.transform.scale(frame, self.start_size)
                self.animation_frames.append(frame_scaled)

        def update_size(self, dt):
            pass

        def set_animation_speed(self, speed_factor=1.0):
            self.animation_speed = int(len(self.animation_frames) * speed_factor)

        def animate(self, current_time_ms, dt):
            dt = current_time_ms - self.last_update
            if not self.animation_frames:
                raise ValueError("Ошибка: нет кадров для анимации.")
            self.frame_accumulator += dt

            frame_duration = 1000 // self.animation_speed
            if self.frame_accumulator >= frame_duration:
                self.frame_accumulator -= frame_duration
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.last_update = current_time_ms

            return self.animation_frames[self.current_frame]

    class Ship(pygame.sprite.Sprite, AnimationMixin):
        def __init__(self, groups):
            super().__init__(groups)
            AnimationMixin.__init__(self)
            self.image = ship_images

            # self.image = pygame.transform.scale(self.image, (100, 140))
            self.animation_frames = [pygame.transform.smoothscale(image, (400, 200)) for image in ship_images]

            self.set_animation_speed(0.1)

            self.image = self.animation_frames[35]
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)

            # Timer
            self.can_shoot = True
            self.shoot_time = None

            # laser sound
            self.laser_sound = pygame.mixer.Sound('../music/laser_blast.mp3')
            self.laser_sound.set_volume(0.2)

            self.explosion_sound_ship = pygame.mixer.Sound('../music/space-explosion-with-reverb-101449.mp3')
            self.energy_down = pygame.mixer.Sound('../music/energy_down.mp3')
            self.energy_down.set_volume(1)
            self.explosion_sound_ship.set_volume(0.2)

        def laser_timer(self):
            if not self.can_shoot:
                if current_time_ms - self.shoot_time > 500:
                    self.can_shoot = True

        def input_position(self):
            ship_pos = pygame.mouse.get_pos()
            self.rect.center = ship_pos

        def laser_shoot(self):
            if pygame.mouse.get_pressed()[0] and self.can_shoot:
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()
                print('laser shoot')
                laser_pos = self.rect.midtop
                Laser(laser_pos, laser_group, laser_images)
                self.laser_sound.play()

        def ship_collision(self):
            global removed_objects
            collision = pygame.sprite.spritecollide(self, asteroid_group, True, pygame.sprite.collide_mask)

        def update(self, current_time_ms, dt):

            self.ship_collision()
            self.laser_timer()
            self.input_position()
            self.laser_shoot()
            # self.image = self.animate(current_time_ms, dt)

    class Star(pygame.sprite.Sprite, MovementMixin, AnimationMixin, AccumulationMixinFrames):
        def __init__(self, image, x, y, groups, speed=5):
            super().__init__(groups)
            MovementMixin.__init__(self, speed)
            AnimationMixin.__init__(self)
            AccumulationMixinFrames.__init__(self)

            self.original_images = image

            self.start_size = (50, 50)

            self.image = pygame.transform.scale(self.original_images, self.start_size)  # Начальное изображение
            self.rect = self.image.get_rect(center=(x, y))
            self.size_speed = 5
            self.history = []
            self.tail_length = 300
            self.head_length = 300
            # Set initial points for Bezier curve
            self.p0 = (
                random.randint(-200, game_surface.get_width() + 100), random.randint(-100, 0))
            self.p1 = (random.randint(game_surface.get_width() + 600, game_surface.get_width() + 800),
                       random.randint(0, 100))

            self.p2 = (random.randint(game_surface.get_width() + 100, game_surface.get_width() + 400),
                       random.randint(400, 800))

            self.p3 = (-300, WINDOW_HEIGHT + 100)
            print(f"Initial control points: p0={self.p0}, p1={self.p1}, p2={self.p2}, p3={self.p3}")
            self.set_bezier(self.p0, self.p1, self.p2, self.p3)  # Set the Bézier curve points
            self.current_time_ms = 0

            # Other attributes
            self.target_size = (300, 300)
            self.size_speed = 5

            self.generate_animation_frames(self.original_images)

        def update(self, current_time_ms, dt):
            global removed_objects
            bezier_position = self.update_bezier(dt)
            if bezier_position:
                self.rect.center = bezier_position
                self.history.append(bezier_position)
                if len(self.history) > self.tail_length + self.head_length:
                    self.history.pop(0)
                if self.rect.top >= game_surface.get_height() or self.rect.left <= -220 or (
                        self.p0 and self.p1 and self.p2 and self.current_time_ms >= 1):
                    self.kill()
                    removed_objects += 1

            self.apply_movement(self.rect)
            self.update_size(dt)
            self.update_position(dt)

        def update_size(self, dt):
            if self.start_size != self.target_size:
                delta_width = self.size_speed * dt
                delta_height = self.size_speed * dt
                new_width = min(self.target_size[0], self.start_size[0] + delta_width)
                new_height = min(self.target_size[1], self.start_size[1] + delta_height)
                self.start_size = (new_width, new_height)
                self.image = pygame.transform.scale(self.original_images, self.start_size)
                self.rect = self.image.get_rect(center=self.rect.center)

                self.generate_animation_frames(self.original_images)
                self.set_animation_speed(1)

                self.image = self.animate(current_time_ms, dt)

        def draw_trace(self, surface):
            for i in range(len(self.history) - 1):
                if i >= dt * (len(self.history) - self.head_length - 1):
                    pygame.draw.line(game_surface, (180, 180, 180), self.history[i], self.history[i + 1], 1)
                elif i < self.tail_length:
                    pygame.draw.line(game_surface, (180, 180, 180), self.history[i], self.history[i + 1], 1)

    class Asteroid(pygame.sprite.Sprite, MovementMixin, AnimationMixin, AccumulationMixinFrames):
        def __init__(self, image, x, y, groups, speed=800):
            super().__init__(groups)
            MovementMixin.__init__(self, speed)
            AnimationMixin.__init__(self, )
            AccumulationMixinFrames.__init__(self)

            self.original_image = image
            self.start_size = (50, 50)
            self.image = pygame.transform.scale(self.original_image, self.start_size)
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.rect.x = x
            self.rect.y = y
            self.set_direction_formula((random.uniform(-0.8, 0.8), 2))
            self.target_size = (150, 150)
            self.size_speed = 3  # pixels per second
            self.generate_animation_frames(self.original_image)
            self.set_animation_speed(1)

        def update(self, current_time_ms, dt):
            global removed_objects
            self.mask = pygame.mask.from_surface(self.image)
            self.apply_movement(self.rect)
            self.update_size(dt)
            self.update_position(dt)
            self.image = self.animate(current_time_ms, dt)
            if self.rect.top > WINDOW_HEIGHT:
                self.kill()
                removed_objects += 1

        def update_size(self, dt):
            if self.start_size != self.target_size:
                delta_width = self.size_speed * dt
                delta_height = self.size_speed * dt
                new_width = min(self.target_size[0], self.start_size[0] + delta_width)
                new_height = min(self.target_size[1], self.start_size[1] + delta_height)
                self.start_size = (new_width, new_height)
                self.image = pygame.transform.scale(self.original_image, self.start_size)
                self.rect = self.image.get_rect(center=self.rect.center)

                self.generate_animation_frames(self.original_image)

    class Laser(pygame.sprite.Sprite):
        def __init__(self, pos, groups, laser_images):
            super().__init__(groups)
            self.image = laser_images[47]
            self.image = pygame.transform.smoothscale(self.image, (50, 75))
            self.rect = self.image.get_rect(midtop=pos)
            self.mask = pygame.mask.from_surface(self.image)

            self.pos = pygame.math.Vector2(self.rect.midtop)
            self.direction = pygame.math.Vector2(0, -1)
            self.speed = 2000

            self.explosion_sound = pygame.mixer.Sound('../music/explosion-36210.mp3')
            self.explosion_sound.set_volume(0.1)

        def update(self, current_time_ms, dt):
            self.asteroid_collision()
            global removed_objects
            self.pos += self.direction * self.speed * dt
            self.rect.center = (round(self.pos.x), round(self.pos.y))

        def asteroid_collision(self):
            global removed_objects, score
            if self.rect.bottom <= 0:
                self.kill()
                removed_objects += 1
            collision = pygame.sprite.spritecollide(self, asteroid_group, True, pygame.sprite.collide_mask)
            if collision:
                score.collision_increase()
                score.update_time_score()
                removed_objects += 1
                self.explosion_sound.play()

    bg_layer = [
        BackgroundLayer('../graphics/background/bg_space_seamless.png', 1, WINDOW_WIDTH, WINDOW_HEIGHT),
        BackgroundLayer('../graphics/background/bg_space_seamless.png', 5, WINDOW_WIDTH, WINDOW_HEIGHT),
        BackgroundLayer('../graphics/background/bg_space_seamless_fl2.png', 10, WINDOW_WIDTH, WINDOW_HEIGHT),
        BackgroundLayer('../graphics/background/star_small_01.png', 15, WINDOW_WIDTH, WINDOW_HEIGHT),
        BackgroundLayer('../graphics/background/star_big_01.png', 20, WINDOW_WIDTH, WINDOW_HEIGHT),
        BackgroundLayer('../graphics/background/bg_space_seamless_fl2.png', 25, WINDOW_WIDTH, WINDOW_HEIGHT),
    ]

    # Sprite groups
    spaceship_group = pygame.sprite.Group()
    star_group = pygame.sprite.Group()
    laser_group = pygame.sprite.Group()
    all_sprite = pygame.sprite.Group()
    asteroid_group = pygame.sprite.Group()
    # Create ship
    new_ship = Ship(spaceship_group)
    all_sprite.add(spaceship_group)

    back_sound = pygame.mixer.Sound('../music/outer-space-188045.mp3')
    back_sound.set_volume(0.5)
    back_sound.play(loops=-1)
    # Game constants and variables

    running = True
    asteroid_spawn_interval = 3000
    star_spawn_interval = 3000
    last_asteroid_spawn = 0
    last_star_spawn = 0
    min_spawn_interval = 30000
    max_spawn_interval = 60000
    min_asteroid_spawn = 1000
    max_asteroid_spawn = 3000
    # log data
    fps_font = font
    fps_text_pos = (10, 90)  # Position to render FPS text
    fps_counter = 0
    fps_display_interval = 1000
    next_fps_update = 0
    score = Score()
    speed_change = 1

    collision_text_choice = ['AVOID ASTEROIDS',
                             'DESTROY ASTEROIDS',
                             'DONT PLAY LOW SKILL']
    show_collision_text = False
    collision_text_start_time = 0
    collision_text_duration = 2000

    while running:
        dt = clock.tick(144) / 1000
        current_time_ms = pygame.time.get_ticks()
        game_surface.fill('black')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if score.game_over():
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    for layer in bg_layer:
                        layer.increase_speed(speed_change, dt)

                elif event.y < 0:
                    for layer in bg_layer:
                        layer.decrease_speed(speed_change, dt)

        fps_counter += 1
        all_sprite.update(current_time_ms, dt)
        spaceship_group.update(current_time_ms, dt)
        laser_group.update(current_time_ms, dt)
        star_group.update(current_time_ms, dt)
        asteroid_group.update(current_time_ms, dt)

        if current_time_ms >= next_fps_update:
            fps = fps_counter / (fps_display_interval / 1000.0)
            fps_counter = 0
            next_fps_update = current_time_ms + fps_display_interval
            print(f'FPS: {fps:.2f}')

        if current_time_ms - last_star_spawn > star_spawn_interval:
            last_star_spawn = current_time_ms
            star_image = random.choice(space_objects_images)
            new_star = Star(star_image, random.randint(-100, 0), random.randint(-100, 0), (),
                            speed=random.randint(20, 150))
            star_group.add(new_star)

            # new_star.increase_speed(speed_change)
            star_spawn_interval = random.randint(min_spawn_interval, max_spawn_interval)
            created_objects += 1
            print(f"Star spawned at: {current_time_ms}, next spawn interval: {star_spawn_interval}")

        if current_time_ms - last_asteroid_spawn > asteroid_spawn_interval:
            last_asteroid_spawn = current_time_ms
            asteroid_image = random.choice(asteroid_images)
            new_asteroid = Asteroid(asteroid_image, random.randint(-100 - WINDOW_HEIGHT, WINDOW_WIDTH),
                                    -asteroid_image.get_height(), asteroid_group)
            asteroid_group.add(new_asteroid)
            asteroid_spawn_interval = random.randint(min_asteroid_spawn, max_asteroid_spawn)
            created_objects += 1
            print(f"Asteroid spawned at {current_time_ms}, next spawn interval: {asteroid_spawn_interval}")

        for layer in bg_layer:
            layer.update(dt)
            layer.draw(game_surface)
        for star in star_group:
            star.draw_trace(game_surface)
        score.display(game_surface)
        score.update_time_score()

        collision_detected = pygame.sprite.spritecollide(new_ship, asteroid_group, True, pygame.sprite.collide_mask)
        if collision_detected:
            show_collision_text = True
            collision_text_start_time = pygame.time.get_ticks()
            score.collision_decrease()
            new_ship.explosion_sound_ship.play()
            new_ship.energy_down.play()
        if show_collision_text:
            current_time_ms = pygame.time.get_ticks()
            if current_time_ms - collision_text_start_time < collision_text_duration:
                collision_text = font.render(random.choice(collision_text_choice), True, (165, 82, 76))
                game_surface.blit(collision_text, (WINDOW_WIDTH // 2 - 50, 300))
            else:
                show_collision_text = False

        star_group.draw(game_surface)
        asteroid_group.draw(game_surface)
        laser_group.draw(game_surface)
        spaceship_group.draw(game_surface)

        game_rect = game_surface.get_rect()
        game_rect.center = display_surface.get_rect().center
        fps_text = fps_font.render(f'FPS: {fps:.2f}', True, pygame.Color(3, 160, 98))
        game_surface.blit(fps_text, fps_text_pos)
        object_count_text = fps_font.render(f'Created: {created_objects}, Removed: {removed_objects}', True,
                                            pygame.Color(3, 160, 98))
        game_surface.blit(object_count_text, (10, 120))

        display_surface.blit(pygame.transform.scale(display_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT)), (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main_loop()
