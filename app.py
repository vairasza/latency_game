import os, random, math, time
from enum import Enum
from threading import Timer

from pyglet import window, app
from pyglet.window import key
from pyglet.shapes import Circle
from pyglet.clock import schedule_once
from pyglet.text import Label


class State(Enum):
  WAIT = 0
  DELAY = 1
  DRAWN = 2
  HIT = 3
  

class Label_Config:
  COLOUR = (255,255,255,255)
  TEXT = "..."
  NAME = "Verdana"
  TEXT_X = 50
  TEXT_Y = 50
  TEXT_SIZE = 15


class LCircle:

  RAD_MIN = 20
  RAD_MAX = 50
  COLOR = (255,0,0,255)
  VELOCITY_MULTIPLYER = 3

  def __init__(self, width: int, height: int) -> None:
    self._width = width
    self._height = height
    
    radius = random.uniform(self.RAD_MIN, self.RAD_MAX)
    x = random.uniform(radius, self._width-radius)
    y = random.uniform(radius, self._height-radius)
    
    self.circle = Circle(x=x, y=y, radius=radius, color=self.COLOR)

    self._dir_x = random.random() * self.VELOCITY_MULTIPLYER
    self._dir_y = random.random() * self.VELOCITY_MULTIPLYER

    self._start_time = time.time()

  def draw(self) -> None:
    self.circle.draw()

  def move(self) -> None:
    self.circle.x += self._dir_x
    self.circle.y += self._dir_y

    if self.circle.x <  self.circle.radius:
      self._dir_x *= -1

    elif self.circle.x + self.circle.radius > self._width:
      self._dir_x *= -1

    if self.circle.y <  self.circle.radius:
      self._dir_y *= -1

    elif self.circle.y + self.circle.radius > self._height:
      self._dir_y *= -1

  def check_collision(self, x: int, y: int) -> float:
    '''
      -1 is no collsion; rest is collsion
    '''
    dy = (self.circle.y - y)
    dx = (self.circle.x - x)
    distance_fingers = math.sqrt(dy ** 2 + dx ** 2 )

    if distance_fingers <= self.circle.radius:
      return time.time() - self._start_time
    else: 
      return - 1.0


class Application:

  FPS = 1 / 60
  WIDTH = 1280
  HEIGTH = 720
  NAME = "Latency App"
  RAND_BOUNDARY = (0, 3)
  MOUSE_RADIUS = 4

  def __init__(self) -> None:
    self.window = window.Window(fullscreen=True, caption=self.NAME)
    self.on_draw = self.window.event(self.on_draw)
    self.on_key_release = self.window.event(self.on_key_release)

    #mouse events
    self.window.set_mouse_visible(False)
    self.on_mouse_press = self.window.event(self.on_mouse_press)
    self.on_mouse_motion = self.window.event(self.on_mouse_motion)

    self.mouse_circle = Circle(x=0, y=0, radius=3)
    self.result_label = Label(Label_Config.TEXT, Label_Config.NAME, Label_Config.TEXT_SIZE, True, False, False, Label_Config.COLOUR, 50, 50, 1)

    self._current_circle: LCircle = None
    self.state = State.WAIT

    self._update_delays()

    #starts first circle
    schedule_once(self._create_new_shape, self.appear_delay)

  def _update_delays(self) -> None:
    self.appear_delay = random.uniform(self.RAND_BOUNDARY[0], self.RAND_BOUNDARY[1])
    self.mouse_press_delay = random.uniform(self.RAND_BOUNDARY[0], self.RAND_BOUNDARY[1])
    self.mouse_motion_delay = random.uniform(self.RAND_BOUNDARY[0], self.RAND_BOUNDARY[1])
  
  def run(self) -> None:
    app.run()

  def on_draw(self) -> None:
    self.window.clear()
  
    if self._current_circle:
      self._current_circle.move()
      self._current_circle.draw()

    self.mouse_circle.draw()
    self.result_label.draw()

    time.sleep(self.FPS)

  def _create_new_shape(self, *_) -> None:
    self._current_circle = LCircle(self.window.width, self.window.height)
    self.state = State.DRAWN

  def _process_mouse_event(self, x: int, y: int, *_) -> None:
    if self._current_circle == None:
      return
    t = self._current_circle.check_collision(x,y)
    if t != -1:
      self.result_label.text = f"reaction time was {t}s"
      self.state = State.HIT
      self._current_circle = None
      schedule_once(self._create_new_shape, self.appear_delay)

  def on_mouse_press(self, x: int, y: int, *_) -> None:
    if self.state == State.DRAWN:
      Timer(self.mouse_press_delay, self._process_mouse_event, kwargs={"x": x, "y": y}).start()
      self.state == State.DELAY
    
    self._update_delays()

  def _update_mouse(self, x: int, y: int, *_) -> None:
    self.mouse_circle.x = x
    self.mouse_circle.y = y

  def on_mouse_motion(self, x: int, y: int, *_) -> None:
    Timer(self.mouse_motion_delay, self._update_mouse, kwargs={"x": x, "y": y}).start()

    self._update_delays()

  def on_key_release(self, symbol: int, *_) -> None:
    if symbol == key.ESCAPE:
      app.exit()


if __name__ == "__main__":
  application = Application()
  application.run()