import pygame

# Action Constants
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
JUMP = 'jump'
ATTACK = 'attack'
PAUSE = 'pause'
START = 'start'
SELECT = 'select'
BACK = 'back'

class InputManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InputManager, cls).__new__(cls)
            cls._instance.actions = {
                UP: False,
                DOWN: False,
                LEFT: False,
                RIGHT: False,
                JUMP: False,
                ATTACK: False,
                PAUSE: False,
                START: False,
                SELECT: False,
                BACK: False
            }
            cls._instance.prev_actions = cls._instance.actions.copy()
            cls._instance.joysticks = []
            cls._instance.init_joysticks()
        return cls._instance

    def init_joysticks(self):
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            for i in range(pygame.joystick.get_count()):
                j = pygame.joystick.Joystick(i)
                j.init()
                self.joysticks.append(j)
            print(f"InputManager: Detected {len(self.joysticks)} joysticks.")

    def update(self):
        # Update previous state
        self.prev_actions = self.actions.copy()

        # Reset current frame
        for key in self.actions:
            self.actions[key] = False

        keys = pygame.key.get_pressed()

        # Keyboard Mapping
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.actions[UP] = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.actions[DOWN] = True
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.actions[LEFT] = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.actions[RIGHT] = True
        # Explicit mapping for JUMP
        if keys[pygame.K_SPACE] or keys[pygame.K_z]:
             self.actions[JUMP] = True

        if keys[pygame.K_x] or keys[pygame.K_k]: self.actions[ATTACK] = True
        if keys[pygame.K_ESCAPE] or keys[pygame.K_p]: self.actions[PAUSE] = True
        if keys[pygame.K_RETURN]: self.actions[START] = True
        # Menu specific
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]: self.actions[SELECT] = True
        if keys[pygame.K_ESCAPE] or keys[pygame.K_BACKSPACE]: self.actions[BACK] = True


        # Joystick Mapping (Gamepad)
        if self.joysticks:
            joy = self.joysticks[0]
            try:
                # Axis (D-Pad or Analog)
                axis_x = joy.get_axis(0)
                axis_y = joy.get_axis(1)
                hat = joy.get_hat(0)

                if axis_y < -0.5 or hat[1] == 1: self.actions[UP] = True
                if axis_y > 0.5 or hat[1] == -1: self.actions[DOWN] = True
                if axis_x < -0.5 or hat[0] == -1: self.actions[LEFT] = True
                if axis_x > 0.5 or hat[0] == 1: self.actions[RIGHT] = True

                # Buttons (Generic mapping, may vary by controller)
                # 0: A/Cross (Jump/Select), 1: B/Circle (Back), 2: X/Square (Attack), 3: Y/Triangle
                if joy.get_button(0):
                    self.actions[JUMP] = True
                    self.actions[SELECT] = True
                if joy.get_button(1):
                    self.actions[BACK] = True
                    self.actions[ATTACK] = True # Maybe?
                if joy.get_button(2): self.actions[ATTACK] = True

                # Start / Select
                if joy.get_button(9) or joy.get_button(7): # Start
                    self.actions[START] = True
                    self.actions[PAUSE] = True

            except pygame.error:
                pass

    def is_pressed(self, action):
        return self.actions.get(action, False)

    def is_just_pressed(self, action):
        return self.actions.get(action, False) and not self.prev_actions.get(action, False)
