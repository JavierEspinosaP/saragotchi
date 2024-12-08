import time
import gc
import random  # Importar el módulo random para generar tiempos aleatorios
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_RGB565
from machine import Pin, Timer
from pngdec import PNG

class Menu:
    DEBOUNCE_TIME = 200  # Tiempo de debounce en milisegundos

    def __init__(self):
        # Inicialización de los botones
        self.buttons = {
            'a': Pin(12, Pin.IN, Pin.PULL_UP),
            'b': Pin(13, Pin.IN, Pin.PULL_UP),
            'x': Pin(14, Pin.IN, Pin.PULL_UP),
            'y': Pin(15, Pin.IN, Pin.PULL_UP)
        }
        # Registro de los últimos tiempos de pulsación para debounce
        self.last_press = {
            'a': 0,
            'b': 0,
            'x': 0,
            'y': 0
        }

        # Configuración del display
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB565, rotate=0)
        self.display.set_backlight(0.8)

        # Inicialización del gestor de PNG
        self.png = PNG(self.display)

        # Definición de colores
        self.BLACK = self.display.create_pen(0, 0, 0)
        self.WHITE = self.display.create_pen(255, 255, 255)
        self.HIGHLIGHT = self.display.create_pen(0, 255, 0)
        self.RED = self.display.create_pen(255, 0, 0)

        # Obtener las dimensiones del display
        self.WIDTH, self.HEIGHT = self.display.get_bounds()

        # Inicialización de estadísticas
        self.hambre = 100
        self.sueno = 100
        self.felicidad = 100
        self.salud = 100

        # Estado del menú
        self.in_food_menu = False
        self.in_entertainment_menu = False
        self.in_health_menu = False
        self.in_menu = False
        self.in_sleep_menu = False  # Nuevo estado para el menú de sueño
        self.selected_food = 0
        self.selected_entertainment = 0
        self.selected_health = 0
        self.selected_sleep_option = 0  # Opción seleccionada en el menú de sueño
        self.selected_icon = 0

        # Tiempos de últimas acciones
        self.last_festival_time = 0
        self.last_ibuprofen_time = 0

        # Estado de sueño
        self.is_sleeping = False  # Indica si la mascota está durmiendo
        self.sleep_end_time = 0    # Tiempo en que termina el sueño

        # Inicialización para la funcionalidad de 'poop.png'
        self.poop_visible = False
        self.poop_position = (0, 0)
        self.next_poop_time = time.time() + random.uniform(60, 120)  # Tiempo aleatorio entre 1 y 2 minutos
        self.poop_image = 'poop.png'
        self.poop_size = (31, 29)  # Tamaño de la imagen 'poop.png'

        # Temporizador para disminuir las estadísticas cada minuto
        self.timer = Timer()
        self.timer.init(period=60000, mode=Timer.PERIODIC, callback=self.decrease_stats)

        # Definición de iconos
        self.icons = [
            ("food.png", "food_s.png"),
            ("sleep.png", "sleep_s.png"),
            ("clear.png", "clear_s.png"),
            ("meter.png", "meter_s.png"),
            ("game.png", "game_s.png"),
            ("health.png", "health_s.png")
        ]

        # Configuración de las animaciones del murciélago
        self.sprite_sheets = {
            'default': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_default.png',
                'frame_width': 82,
                'num_frames': 4,
                'frame_height': 72
            },
            'eat': {
                'type': 'frames',
                'frames': [
                    'eat/pink_bean_eat-1.png.png',
                    'eat/pink_bean_eat-2.png.png',
                    'eat/pink_bean_eat-3.png.png',
                    'eat/pink_bean_eat-4.png.png',
                    'eat/pink_bean_eat-5.png.png',
                    'eat/pink_bean_eat-6.png.png',
                    'eat/pink_bean_eat-7.png.png',
                    'eat/pink_bean_eat-8.png.png',
                    'eat/pink_bean_eat-9.png.png',
                    'eat/pink_bean_eat-10.png.png',
                    'eat/pink_bean_eat-11.png.png',
                    'eat/pink_bean_eat-12.png.png',
                    'eat/pink_bean_eat-13.png.png',
                    'eat/pink_bean_eat-14.png.png',
                    'eat/pink_bean_eat-15.png.png',
                    'eat/pink_bean_eat-16.png.png'
                ],
                'frame_width': 112,  # Cada frame es de 112 px de ancho
                'frame_height': 72    # Cada frame es de 72 px de alto
            },
            'hug': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_ass.png',
                'frame_width': 56,  # 112 / 2 = 56
                'num_frames': 2,
                'frame_height': 70
            },
            'drunk': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_drunk.png',
                'frame_width': 78,  # 468 / 6 = 78
                'num_frames': 6,
                'frame_height': 84
            },
            'talk': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_talk.png',
                'frame_width': 86,  # 344 / 4 = 86
                'num_frames': 4,
                'frame_height': 80
            },
            'angry_1': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_angry_1.png',
                'frame_width': 118,  # 472 / 4 = 118
                'num_frames': 4,
                'frame_height': 96
            },
            'angry_2': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_angry_2.png',
                'frame_width': 118,  # 472 / 4 = 118
                'num_frames': 4,
                'frame_height': 96
            },
            'sleep_1': {  # Nueva animación agregada
                'type': 'sprite_sheet',
                'file': 'pink_bean_sleeping_1.png',
                'frame_width': 114,  # Ajusta según tus PNG
                'num_frames': 4,      # Ajusta según tus PNG
                'frame_height': 64
            },
            'sleep_2': {  # Nueva animación agregada
                'type': 'sprite_sheet',
                'file': 'pink_bean_sleeping_2.png',
                'frame_width': 114,  # Ajusta según tus PNG
                'num_frames': 4,      # Ajusta según tus PNG
                'frame_height': 64
            },
            'love_1': {  # Nueva animación agregada
                'type': 'sprite_sheet',
                'file': 'pink_bean_love_1.png',
                'frame_width': 156,  # 624 / 4 = 156 px por frame
                'num_frames': 4,
                'frame_height': 64
            },
            'love_2': {  # Nueva animación agregada
                'type': 'sprite_sheet',
                'file': 'pink_bean_love_2.png',
                'frame_width': 156,  # 624 / 4 = 156 px por frame
                'num_frames': 4,
                'frame_height': 64
            },
            # Nuevas animaciones para Play Deftones
            'guitar_1': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_guitar_1.png',
                'frame_width': 130,
                'num_frames': 3,
                'frame_height': 86
            },
            'guitar_2': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_guitar_2.png',
                'frame_width': 130,
                'num_frames': 3,
                'frame_height': 86
            },
            'guitar_3': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_guitar_3.png',
                'frame_width': 130,
                'num_frames': 3,
                'frame_height': 86
            },
            'guitar_4': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_guitar_4.png',
                'frame_width': 130,
                'num_frames': 3,
                'frame_height': 86
            },
            'guitar_5': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_guitar_5.png',
                'frame_width': 130,
                'num_frames': 3,
                'frame_height': 86
            },
            'guitar_6': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_guitar_6.png',
                'frame_width': 130,
                'num_frames': 3,
                'frame_height': 86
            },
            'guitar_7': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_guitar_7.png',
                'frame_width': 130,
                'num_frames': 3,
                'frame_height': 86
            },
            # Nuevos sprite sheets agregados
            'ass': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_ass.png',
                'frame_width': 56,   # 112 / 2 = 56
                'num_frames': 2,
                'frame_height': 70
            },
            'happy2': {
                'type': 'sprite_sheet',
                'file': 'pink_bean_happy2.png',
                'frame_width': 98,   # 196 / 2 = 98
                'num_frames': 2,
                'frame_height': 72
            }
        }

        # Cola de animaciones
        self.animation_queue = []

        # Verificación de la carga de PNGs
        self.verify_pngs()

        # Iniciar la animación por defecto
        self.start_animation('default')

        # Inicialización del historial de selecciones
        self.selection_history = {}

    def verify_pngs(self):
        """Verifica que todos los PNGs estén correctamente cargados."""
        for anim, details in self.sprite_sheets.items():
            try:
                if details['type'] == 'sprite_sheet':
                    self.png.open_file(details['file'])
                    # Intentar decodificar el primer frame para verificar la carga
                    self.png.decode(0, 0, source=(0, 0, details['frame_width'], details['frame_height']))
                elif details['type'] == 'frames':
                    for frame in details['frames']:
                        self.png.open_file(frame)
                        self.png.decode(0, 0, source=(0, 0, details['frame_width'], details['frame_height']))
                print(f"Animación '{anim}' cargada correctamente.")
            except Exception as e:
                print(f"Error al cargar {details['file']} o uno de sus frames para la animación '{anim}': {e}")

        # Cargar la imagen 'poop.png'
        try:
            self.png.open_file(self.poop_image)
            self.png.decode(0, 0, source=(0, 0, self.poop_size[0], self.poop_size[1]))
            print(f"Imagen '{self.poop_image}' cargada correctamente.")
        except Exception as e:
            print(f"Error al cargar {self.poop_image}: {e}")

    def record_selection(self, option_name):
        """Registra la selección de una opción con la marca de tiempo actual."""
        current_time = time.time()
        if option_name not in self.selection_history:
            self.selection_history[option_name] = []
        self.selection_history[option_name].append(current_time)
        # Eliminar marcas de tiempo que tienen más de 60 segundos
        self.selection_history[option_name] = [t for t in self.selection_history[option_name] if current_time - t <= 60]

    def check_selection_frequency(self, option_name):
        """Verifica si una opción ha sido seleccionada más de dos veces en el último minuto."""
        if option_name in self.selection_history and len(self.selection_history[option_name]) > 2:
            return True
        return False

    def check_high_parameters(self):
        """Verifica si alguno de los parámetros supera el 90%."""
        return any(param > 90 for param in [self.hambre, self.felicidad, self.sueno, self.salud])

    def decrease_stats(self, timer):
        """Disminuye las estadísticas cada minuto."""
        self.hambre = max(0, self.hambre - 1)
        self.sueno = max(0, self.sueno - 1)
        self.felicidad = max(0, self.felicidad - 1)
        self.salud = max(0, self.salud - 1)

    def enqueue_animation(self, animation_name, repeats=1):
        """Añade una animación a la cola de animaciones."""
        for _ in range(repeats):
            self.animation_queue.append(animation_name)
        print(f"Encolando animación '{animation_name}' {repeats} vez(es).")
        # Si la animación por defecto está en curso y no hay otra animación en cola, iniciar la nueva animación
        if self.current_animation == 'default' and len(self.animation_queue) == repeats:
            self.trigger_next_animation()

    def trigger_next_animation(self):
        """Inicia la siguiente animación en la cola, si existe."""
        if self.animation_queue:
            next_anim = self.animation_queue.pop(0)
            self.start_animation(next_anim)
            print(f"Iniciando animación '{next_anim}'.")
        else:
            # No hay más animaciones en la cola, volver a la animación por defecto
            if self.current_animation != 'default':
                self.start_animation('default')
                print("Volviendo a la animación por defecto.")

    def start_animation(self, animation_name):
        """Inicia una animación específica."""
        if animation_name not in self.sprite_sheets:
            print(f"Animación '{animation_name}' no definida.")
            return

        anim_details = self.sprite_sheets[animation_name]
        self.current_animation = animation_name

        if anim_details['type'] == 'sprite_sheet':
            self.current_sprite_sheet = anim_details['file']
            self.frame_width = anim_details['frame_width']
            self.num_frames = anim_details['num_frames']
            self.frame_height = anim_details['frame_height']
        elif anim_details['type'] == 'frames':
            self.eat_frames = anim_details['frames']
            self.num_frames = len(self.eat_frames)
            self.frame_width = anim_details['frame_width']
            self.frame_height = anim_details['frame_height']
            self.current_frame = 0

        self.current_frame = 0
        self.last_frame_time = time.time()
        self.frame_interval = 0.05  # Puedes ajustar el intervalo para controlar la velocidad de la animación

        # Repeticiones de animación
        self.max_repeats = 1  # Cada animación en la cola se reproduce una vez
        self.current_repeats = 0

        # Recalcular posición para centrar el sprite con el nuevo tamaño
        self.bat_x = (self.WIDTH - self.frame_width) // 2
        self.bat_y = ((self.HEIGHT - self.frame_height) // 2) + 25
        print(f"Animación '{animation_name}' iniciada.")

    def update_animation(self):
        """Actualiza el frame de la animación si ha pasado el intervalo."""
        current_time = time.time()
        if current_time - self.last_frame_time >= self.frame_interval:
            self.current_frame += 1
            if self.current_frame >= self.num_frames:
                self.current_repeats += 1
                if self.current_repeats >= self.max_repeats:
                    if self.current_animation in [
                        'eat', 'eat_1', 'eat_2', 'eat_3', 'eat_4',
                        'hug', 'drunk', 'sleep_1', 'sleep_2', 'talk',
                        'angry_1', 'angry_2', 'love_1', 'love_2',
                        'guitar_1', 'guitar_2', 'guitar_3', 'guitar_4',
                        'guitar_5', 'guitar_6', 'guitar_7',
                        'ass', 'happy2'  # Añadido para las nuevas animaciones
                    ]:
                        # Termina la animación actual y verifica la cola
                        self.trigger_next_animation()
                    else:
                        # Looping para animaciones por defecto
                        self.current_frame = 0
                else:
                    # Reiniciar la animación para repetir
                    self.current_frame = 0
            else:
                # Para animaciones por defecto, hacer looping
                if self.current_animation == 'default':
                    self.current_frame %= self.num_frames
            self.last_frame_time = current_time

    def draw_bat(self):
        """Dibuja el murciélago animado en el centro de la pantalla."""
        self.update_animation()
        anim_details = self.sprite_sheets[self.current_animation]

        if anim_details['type'] == 'sprite_sheet':
            source_x = self.current_frame * self.frame_width
            source = (source_x, 0, self.frame_width, self.frame_height)
            try:
                self.png.open_file(self.current_sprite_sheet)
                self.png.decode(self.bat_x, self.bat_y, source=source)
                # No es necesario cerrar el archivo aquí
            except Exception as e:
                print(f"Error al cargar {self.current_sprite_sheet}: {e}")
        elif anim_details['type'] == 'frames':
            if self.current_frame < len(self.eat_frames):
                current_frame_file = self.eat_frames[self.current_frame]
                try:
                    self.png.open_file(current_frame_file)
                    self.png.decode(self.bat_x, self.bat_y)
                    # No es necesario cerrar el archivo aquí
                except Exception as e:
                    print(f"Error al cargar {current_frame_file}: {e}")
            else:
                # Si el frame actual está fuera de rango, volver al inicio
                self.current_frame = 0

    def draw_menu(self):
        """Dibuja el menú actual en la pantalla."""
        # Limpiar la pantalla
        self.display.set_pen(self.BLACK)
        self.display.clear()

        # Dibujar el murciélago animado si no está en ningún menú
        if not self.in_menu and not self.in_food_menu and not self.in_entertainment_menu and not self.in_health_menu and not self.in_sleep_menu:
            self.draw_bat()

        # Dibujar la imagen 'poop.png' si está visible
        if self.poop_visible:
            self.draw_icon(self.poop_image, self.poop_position[0], self.poop_position[1])

        # Dibujar el menú correspondiente
        if self.in_food_menu:
            self.show_food_menu()
        elif self.in_entertainment_menu:
            self.show_entertainment_menu()
        elif self.in_health_menu:
            self.show_health_menu()
        elif self.in_sleep_menu:
            self.show_sleep_menu()
        elif self.in_menu:
            self.show_stats()
        else:
            # Dibujar los iconos principales
            for i, (icon, icon_selected) in enumerate(self.icons[:3]):
                if self.selected_icon == i:
                    self.draw_icon(icon_selected, 10, 10 + i * 45)
                else:
                    self.draw_icon(icon, 10, 10 + i * 45)

            for i, (icon, icon_selected) in enumerate(self.icons[3:]):
                idx = i + 3
                if self.selected_icon == idx:
                    self.draw_icon(icon_selected, self.WIDTH - 30, 10 + i * 45)
                else:
                    self.draw_icon(icon, self.WIDTH - 30, 10 + i * 45)

        # Actualizar el display
        self.display.update()
        gc.collect()

    def draw_icon(self, filename, x, y):
        """Carga y dibuja un icono en la posición especificada."""
        try:
            self.png.open_file(filename)
            self.png.decode(x, y)
            # No es necesario cerrar el archivo aquí
        except Exception as e:
            print(f"Error al cargar {filename}: {e}")

    def show_food_menu(self):
        """Muestra el menú de comida."""
        food_options = ['Coffee', 'Tofu', 'Moscow Mule']
        self.display.set_pen(self.WHITE)
        self.display.text("Select food", 10, 10, scale=3)

        for i, food in enumerate(food_options):
            if self.selected_food == i:
                self.display.set_pen(self.HIGHLIGHT)
            else:
                self.display.set_pen(self.WHITE)
            self.display.text(food, 10, 50 + i * 30, scale=3)

    def show_entertainment_menu(self):
        """Muestra el menú de entretenimiento."""
        entertainment_options = ['Play Deftones', 'Read Book', 'Go Festival']
        current_time = time.time()

        self.display.set_pen(self.WHITE)
        self.display.text("Select type", 10, 10, scale=3)

        for i, entertainment in enumerate(entertainment_options):
            if self.selected_entertainment == i:
                if i == 2 and (current_time - self.last_festival_time) < 120:
                    self.display.set_pen(self.RED)
                else:
                    self.display.set_pen(self.HIGHLIGHT)
            else:
                self.display.set_pen(self.WHITE)
            self.display.text(entertainment, 10, 50 + i * 30, scale=3)

    def show_health_menu(self):
        """Muestra el menú de salud."""
        health_options = ['A hug', 'Ibuprofeno']
        current_time = time.time()

        self.display.set_pen(self.WHITE)
        self.display.text("Select type", 10, 10, scale=3)

        for i, health in enumerate(health_options):
            if self.selected_health == i:
                if i == 1 and (current_time - self.last_ibuprofen_time) < 28800:
                    self.display.set_pen(self.RED)
                else:
                    self.display.set_pen(self.HIGHLIGHT)
            else:
                self.display.set_pen(self.WHITE)
            self.display.text(health, 10, 50 + i * 30, scale=3)

    def show_sleep_menu(self):
        """Muestra el menú de sueño."""
        if self.is_sleeping:
            options = ['Wake Up']
        else:
            options = ['A nap', 'Go to sleep']

        self.display.set_pen(self.WHITE)
        self.display.text("Sleep Menu", 10, 10, scale=3)

        for i, option in enumerate(options):
            if self.selected_sleep_option == i:
                self.display.set_pen(self.HIGHLIGHT)
            else:
                self.display.set_pen(self.WHITE)
            self.display.text(option, 10, 50 + i * 30, scale=3)

    def show_stats(self):
        """Muestra las estadísticas actuales."""
        self.display.set_pen(self.WHITE)
        self.display.text(f"Hunger: {self.hambre}", 10, 20, scale=3)
        self.display.text(f"Sleep: {self.sueno}", 10, 50, scale=3)
        self.display.text(f"Happiness: {self.felicidad}", 10, 80, scale=3)
        self.display.text(f"Health: {self.salud}", 10, 110, scale=3)

    def navigate(self):
        """Gestiona la navegación del menú y las interacciones de los botones."""
        current_time_ms = int(time.ticks_ms())

        if not self.in_menu and not self.in_food_menu and not self.in_entertainment_menu and not self.in_health_menu and not self.in_sleep_menu:
            # Navegación en el menú principal
            if not self.buttons['a'].value():
                if current_time_ms - self.last_press['a'] > self.DEBOUNCE_TIME:
                    self.selected_icon = (self.selected_icon - 1) % len(self.icons)
                    self.last_press['a'] = current_time_ms
            if not self.buttons['b'].value():
                if current_time_ms - self.last_press['b'] > self.DEBOUNCE_TIME:
                    self.selected_icon = (self.selected_icon + 1) % len(self.icons)
                    self.last_press['b'] = current_time_ms
            if not self.buttons['y'].value():
                if current_time_ms - self.last_press['y'] > self.DEBOUNCE_TIME:
                    selected = self.selected_icon
                    if selected == 3:  # Menu de estadísticas
                        self.in_menu = True
                        print("Ingresando al menú de estadísticas.")
                    elif selected == 0:  # Comida
                        self.in_food_menu = True
                        print("Ingresando al menú de comida.")
                    elif selected == 4:  # Entretenimiento
                        self.in_entertainment_menu = True
                        print("Ingresando al menú de entretenimiento.")
                    elif selected == 5:  # Salud
                        self.in_health_menu = True
                        print("Ingresando al menú de salud.")
                    elif selected == 1:  # Sueño
                        self.in_sleep_menu = True  # Cambiado para abrir el menú de sueño
                        print("Ingresando al menú de sueño.")
                    elif selected == 2:  # Clear
                        self.clear()
                    self.last_press['y'] = current_time_ms
        elif self.in_food_menu:
            # Navegación en el menú de comida
            if not self.buttons['a'].value():
                if current_time_ms - self.last_press['a'] > self.DEBOUNCE_TIME:
                    self.selected_food = (self.selected_food - 1) % 3
                    self.last_press['a'] = current_time_ms
            if not self.buttons['b'].value():
                if current_time_ms - self.last_press['b'] > self.DEBOUNCE_TIME:
                    self.selected_food = (self.selected_food + 1) % 3
                    self.last_press['b'] = current_time_ms
            if not self.buttons['y'].value():
                if current_time_ms - self.last_press['y'] > self.DEBOUNCE_TIME:
                    self.apply_food_effects(self.selected_food)
                    self.in_food_menu = False
                    self.last_press['y'] = current_time_ms
            if not self.buttons['x'].value():
                if current_time_ms - self.last_press['x'] > self.DEBOUNCE_TIME:
                    self.in_food_menu = False
                    self.last_press['x'] = current_time_ms
        elif self.in_entertainment_menu:
            # Navegación en el menú de entretenimiento
            if not self.buttons['a'].value():
                if current_time_ms - self.last_press['a'] > self.DEBOUNCE_TIME:
                    self.selected_entertainment = (self.selected_entertainment - 1) % 3
                    self.last_press['a'] = current_time_ms
            if not self.buttons['b'].value():
                if current_time_ms - self.last_press['b'] > self.DEBOUNCE_TIME:
                    self.selected_entertainment = (self.selected_entertainment + 1) % 3
                    self.last_press['b'] = current_time_ms
            if not self.buttons['y'].value():
                if current_time_ms - self.last_press['y'] > self.DEBOUNCE_TIME:
                    if self.selected_entertainment == 2 and (time.time() - self.last_festival_time) < 120:
                        print("Go Festival no está disponible aún")
                    else:
                        self.apply_entertainment_effects(self.selected_entertainment)
                        if self.selected_entertainment == 2:
                            self.last_festival_time = time.time()
                        self.in_entertainment_menu = False
                    self.last_press['y'] = current_time_ms
            if not self.buttons['x'].value():
                if current_time_ms - self.last_press['x'] > self.DEBOUNCE_TIME:
                    self.in_entertainment_menu = False
                    self.last_press['x'] = current_time_ms
        elif self.in_health_menu:
            # Navegación en el menú de salud
            if not self.buttons['a'].value():
                if current_time_ms - self.last_press['a'] > self.DEBOUNCE_TIME:
                    self.selected_health = (self.selected_health - 1) % 2
                    self.last_press['a'] = current_time_ms
            if not self.buttons['b'].value():
                if current_time_ms - self.last_press['b'] > self.DEBOUNCE_TIME:
                    self.selected_health = (self.selected_health + 1) % 2
                    self.last_press['b'] = current_time_ms
            if not self.buttons['y'].value():
                if current_time_ms - self.last_press['y'] > self.DEBOUNCE_TIME:
                    if self.selected_health == 1 and (time.time() - self.last_ibuprofen_time) < 28800:
                        print("Ibuprofeno no está disponible aún")
                    else:
                        self.apply_health_effects(self.selected_health)
                        if self.selected_health == 1:
                            self.last_ibuprofen_time = time.time()
                        self.in_health_menu = False
                    self.last_press['y'] = current_time_ms
            if not self.buttons['x'].value():
                if current_time_ms - self.last_press['x'] > self.DEBOUNCE_TIME:
                    self.in_health_menu = False
                    self.last_press['x'] = current_time_ms
        elif self.in_sleep_menu:
            # Navegación en el menú de sueño
            if not self.is_sleeping:
                options = ['A nap', 'Go to sleep']
            else:
                options = ['Wake Up']

            if not self.buttons['a'].value():
                if current_time_ms - self.last_press['a'] > self.DEBOUNCE_TIME:
                    if not self.is_sleeping and len(options) > 1:
                        self.selected_sleep_option = (self.selected_sleep_option - 1) % len(options)
                    self.last_press['a'] = current_time_ms
            if not self.buttons['b'].value():
                if current_time_ms - self.last_press['b'] > self.DEBOUNCE_TIME:
                    if not self.is_sleeping and len(options) > 1:
                        self.selected_sleep_option = (self.selected_sleep_option + 1) % len(options)
                    self.last_press['b'] = current_time_ms
            if not self.buttons['y'].value():
                if current_time_ms - self.last_press['y'] > self.DEBOUNCE_TIME:
                    if self.is_sleeping:
                        self.wake_up()
                    else:
                        if self.selected_sleep_option == 0:
                            self.start_sleep(nap=True)
                        elif self.selected_sleep_option == 1:
                            self.start_sleep(nap=False)
                    self.in_sleep_menu = False
                    self.last_press['y'] = current_time_ms
            if not self.buttons['x'].value():
                if current_time_ms - self.last_press['x'] > self.DEBOUNCE_TIME:
                    self.in_sleep_menu = False
                    self.last_press['x'] = current_time_ms
        else:
            # Salir del menú de estadísticas
            if not self.buttons['x'].value():
                if current_time_ms - self.last_press['x'] > self.DEBOUNCE_TIME:
                    self.in_menu = False
                    self.last_press['x'] = current_time_ms

    def is_stat_over_limit(self, stats):
        """Verifica si alguna de las estadísticas proporcionadas ya está por encima del 90%."""
        return any(getattr(self, stat) > 90 for stat in stats)

    def apply_food_effects(self, food_index):
        """Aplica los efectos según la comida seleccionada."""
        food_options = ['Coffee', 'Tofu', 'Moscow Mule']
        selected_food = food_options[food_index]
        self.record_selection(f'food_{selected_food}')  # Registrar la selección

        # Define qué estadísticas se aumentan para cada opción de comida
        food_stat_increases = {
            0: ['hambre', 'felicidad', 'sueno'],      # Coffee
            1: ['hambre', 'felicidad', 'salud'],      # Tofu
            2: ['hambre', 'felicidad']                # Moscow Mule
        }

        # Verificar si alguna de las estadísticas que se aumentarían ya está por encima del 90%
        stats_to_increase = food_stat_increases.get(food_index, [])
        if self.is_stat_over_limit(stats_to_increase):
            print(f"Acción '{selected_food}' rechazada: alguna estadística está por encima del 90%.")
            self.play_immediately('ass', repeats=3)
            return

        if food_index == 0:  # Coffee
            self.hambre = min(100, self.hambre + 5)
            self.felicidad = min(100, self.felicidad + 10)
            self.sueno = min(100, self.sueno + 5)
            self.salud = max(0, self.salud - 2)
            print("Café seleccionado")
            # Encolar únicamente la animación 'happy2' tres veces
            self.enqueue_animation('happy2', repeats=3)
        elif food_index == 1:  # Tofu
            self.hambre = min(100, self.hambre + 30)
            self.felicidad = min(100, self.felicidad + 5)
            self.salud = min(100, self.salud + 5)
            print("Tofu seleccionado")
            # Encolar las animaciones 'eat' que consiste en 16 frames individuales
            self.enqueue_animation('eat', repeats=1)
        elif food_index == 2:  # Moscow Mule
            self.hambre = min(100, self.hambre + 10)
            self.felicidad = min(100, self.felicidad + 20)
            self.salud = max(0, self.salud - 10)
            print("Moscow Mule seleccionado")
            # Encolar la animación 'drunk' dos veces después de seleccionar "Moscow Mule"
            self.enqueue_animation('drunk', repeats=2)

        # Verificar condiciones para reproducir la animación 'ass' inmediatamente
        if self.check_high_parameters() or self.check_selection_frequency(f'food_{selected_food}'):
            self.play_immediately('ass', repeats=3)

    def apply_entertainment_effects(self, entertainment_index):
        """Aplica los efectos según la opción de entretenimiento seleccionada."""
        entertainment_options = ['Play Deftones', 'Read Book', 'Go Festival']
        selected_entertainment = entertainment_options[entertainment_index]
        self.record_selection(f'entertainment_{selected_entertainment}')  # Registrar la selección

        # Define qué estadísticas se aumentan para cada opción de entretenimiento
        entertainment_stat_increases = {
            0: ['felicidad'],          # Play Deftones
            1: ['felicidad'],          # Read Book
            2: ['felicidad']           # Go Festival
        }

        # Verificar si alguna de las estadísticas que se aumentarían ya está por encima del 90%
        stats_to_increase = entertainment_stat_increases.get(entertainment_index, [])
        if self.is_stat_over_limit(stats_to_increase):
            print(f"Acción '{selected_entertainment}' rechazada: alguna estadística está por encima del 90%.")
            self.play_immediately('ass', repeats=3)
            return

        if entertainment_index == 0:  # Play Deftones
            self.felicidad = min(100, self.felicidad + 20)
            print("Play Deftones seleccionado")
            # Encolar las animaciones 'guitar_1' hasta 'guitar_7' para reproducirlas secuencialmente
            for i in range(1, 8):
                self.enqueue_animation(f'guitar_{i}')
        elif entertainment_index == 1:  # Read Book
            self.felicidad = min(100, self.felicidad + 10)
            print("Read Book seleccionado")
        elif entertainment_index == 2:  # Go Festival
            self.felicidad = min(100, self.felicidad + 50)
            print("Go Festival seleccionado")

        # Verificar condiciones para reproducir la animación 'ass' inmediatamente
        if self.check_high_parameters() or self.check_selection_frequency(f'entertainment_{selected_entertainment}'):
            self.play_immediately('ass', repeats=3)

    def apply_health_effects(self, health_index):
        """Aplica los efectos según la opción de salud seleccionada."""
        health_options = ['A hug', 'Ibuprofeno']
        selected_health = health_options[health_index]
        self.record_selection(f'health_{selected_health}')  # Registrar la selección

        # Define qué estadísticas se aumentan para cada opción de salud
        health_stat_increases = {
            0: ['salud', 'felicidad'],   # A hug
            1: ['salud']                  # Ibuprofeno
        }

        # Verificar si alguna de las estadísticas que se aumentarían ya está por encima del 90%
        stats_to_increase = health_stat_increases.get(health_index, [])
        if self.is_stat_over_limit(stats_to_increase):
            print(f"Acción '{selected_health}' rechazada: alguna estadística está por encima del 90%.")
            self.play_immediately('ass', repeats=3)
            return

        if health_index == 0:  # A hug
            self.salud = min(100, self.salud + 10)
            self.felicidad = min(100, self.felicidad + 15)
            print("A hug seleccionado")
            # Encolar las animaciones 'love_1' y 'love_2' en secuencia, repetidas dos veces
            for _ in range(2):
                self.enqueue_animation('love_1')
                self.enqueue_animation('love_2')
        elif health_index == 1:  # Ibuprofeno
            self.salud = min(100, self.salud + 30)
            print("Ibuprofeno seleccionado")
            # Encolar la animación 'talk' dos veces después de seleccionar "Ibuprofeno"
            self.enqueue_animation('talk', repeats=2)

        # Verificar condiciones para reproducir la animación 'ass' inmediatamente
        if self.check_high_parameters() or self.check_selection_frequency(f'health_{selected_health}'):
            self.play_immediately('ass', repeats=3)

    def start_sleep(self, nap=False):
        """Inicia el sueño de la mascota por la duración especificada."""
        self.is_sleeping = True
        if nap:
            self.sleep_end_time = time.time() + 20 * 60  # 20 minutos
            self.sueno = min(100, self.sueno + 20)      # Incremento de sueño por la siesta
            print(f"Sueño incrementado a: {self.sueno}")
            sleep_duration = "20 minutos"
        else:
            self.sleep_end_time = time.time() + 6 * 60 * 60  # 6 horas
            self.sueno = min(100, self.sueno + 60)           # Incremento de sueño por dormir
            print(f"Sueño incrementado a: {self.sueno}")
            sleep_duration = "6 horas"

        print(f"Pet started sleeping for {sleep_duration}.")
        # Encolar las animaciones 'sleep_1' y 'sleep_2' repetidamente
        self.enqueue_animation('sleep_1', repeats=20)  # Ajusta el número de repeticiones según sea necesario
        self.enqueue_animation('sleep_2', repeats=20)

    def wake_up(self):
        """Despierta a la mascota."""
        self.is_sleeping = False
        self.sleep_end_time = 0
        print("Pet woke up.")
        # Limpiar la cola de animaciones de sueño y volver a la animación por defecto
        self.animation_queue = []
        self.start_animation('default')

    def check_sleep_status(self):
        """Verifica si el tiempo de sueño ha terminado."""
        if self.is_sleeping and time.time() >= self.sleep_end_time:
            self.wake_up()

    def clear(self):
        """Incrementa las estadísticas de salud y felicidad y ejecuta animaciones de enojo."""
        self.salud = min(100, self.salud + 10)
        self.felicidad = min(100, self.felicidad + 5)
        self.poop_visible = False  # Ocultar la imagen 'poop.png' al limpiar
        self.next_poop_time = time.time() + random.uniform(60, 120)  # Reprogramar la próxima aparición
        print(f"Salud incrementado a: {self.salud}")
        print(f"Felicidad incrementado a: {self.felicidad}")
        # Encolar las animaciones 'angry_1' y 'angry_2' dos veces cada una
        self.enqueue_animation('angry_1', repeats=2)
        self.enqueue_animation('angry_2', repeats=2)

    def play_immediately(self, animation_name, repeats=1):
        """Reproduce una animación inmediatamente, interrumpiendo la cola actual."""
        # Limpiar la cola de animaciones
        self.animation_queue = []
        # Encolar la animación con las repeticiones deseadas
        self.enqueue_animation(animation_name, repeats=repeats)
        # Iniciar la animación inmediatamente
        self.trigger_next_animation()
        print(f"Reproduciendo animación '{animation_name}' inmediatamente con {repeats} repetición(es).")

    def update_poop(self):
        """Gestiona la aparición aleatoria de la imagen 'poop.png'."""
        current_time = time.time()
        if not self.poop_visible and current_time >= self.next_poop_time:
            # Determinar en qué lado aparecerá la imagen (izquierda o derecha)
            side = random.choice(['left', 'right'])
            margin = 5  # Margen para evitar sobreposición

            if side == 'left':
                x = self.bat_x - self.poop_size[0] - margin
                # Asegurar que la posición X no sea negativa
                if x < 0:
                    x = margin
            else:
                x = self.bat_x + self.frame_width + margin
                # Asegurar que la imagen no salga del borde derecho
                if x + self.poop_size[0] > self.WIDTH:
                    x = self.WIDTH - self.poop_size[0] - margin

            # Ajustar la posición Y para que 'poop.png' esté en el suelo
            y = self.HEIGHT - self.poop_size[1] - margin

            self.poop_position = (x, y)
            self.poop_visible = True
            print(f"'poop.png' apareció en el lado {side} en posición {self.poop_position}")

# Creación de la instancia del menú
menu = Menu()

# Bucle principal
while True:
    menu.draw_menu()
    menu.navigate()
    menu.check_sleep_status()  # Verificar el estado de sueño
    menu.update_poop()         # Verificar y actualizar la aparición de 'poop.png'
    time.sleep(1.0 / 20)       # Actualizar a 20 FPS
