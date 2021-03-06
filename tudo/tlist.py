# tlist.py
from urwid import ListBox, Edit, AttrSpec, AttrMap, Filler, Frame, LineBox
from tudo.conf_prompt import ConfPrompt
from tudo.task import Task
from tudo.title_bar import TitleBar
from tudo.group_foot import GroupFoot
import urwid
import uuid


class TList(urwid.WidgetWrap):

  def __init__(self, list_data=None):

    self.is_editing = False
    self.tasks = []
    self.name = None
    self.group = None
    self.id = None

    if list_data: 
      # Parse the data.
      self.parse_data(list_data)
    else:
      # Must be a new list
      self.name = 'untitled'
      self.group = 'none'
      self.id = uuid.uuid4().hex

    # AttrSpecs
    self.attr_spec = AttrSpec('', '')
    self.focus_nav = AttrSpec('h12', '')
    self.focus_ins = AttrSpec('h160', '')

    # Build widget stack
    self.title = TitleBar(self.name)
    self.group_foot = GroupFoot(self.group)
    self.body = urwid.SimpleFocusListWalker(self.tasks)
    self.list_box = ListBox(self.body)
    self.list_frame = Frame(self.list_box, header=self.title, footer=self.group_foot)
    self.line_box = LineBox(self.list_frame)
    self.line_attr = AttrMap(self.line_box, self.attr_spec, self.focus_nav)
    super().__init__(self.line_attr)

  def parse_data(self, list_data):
    self.name = list_data['name']
    self.group = list_data['group']
    self.id = list_data['id']
    task_data = list_data['tasks']

    index = 1
    for task_dict in task_data:
      task = Task(index, task_dict)
      urwid.connect_signal(task, 'delete', self.delete)
      index += 1
      self.tasks.append(task)

  def delete(self, obj):
    self.tasks.remove(obj)
    self.body.remove(obj)
    self.index_tasks()

  def move_task(self, trans):
    # FIX INDEX ERROR WHEN TRYING TO MOVE TO FAR DOWN OR UP
    focus_task = self.list_box.focus
    task_index = focus_task.tag.tag_index
    new_index = task_index + trans - 1 
    self.delete(focus_task)
    if new_index < 0: new_index = 0
    elif new_index > len(self.tasks): new_index = len(self.tasks)
    self.tasks.insert(new_index, focus_task)
    self.body.insert(new_index, focus_task)
    self.list_box.focus_position = new_index
    self.index_tasks()

  def set_edit(self, editing):
    if editing:
      self.is_editing = True
      self.line_attr.set_focus_map({None: self.focus_ins})
    else:
      self.is_editing = False
      self.line_attr.set_focus_map({None: self.focus_nav})

  def export(self):
    data = {'name': self.title.get_title(), 'group': self.group_foot.get_group(), 'id': self.id, 'tasks': []}
    for task in self.tasks:
      task_dict = {} 
      task_dict['id'] = task.id
      if task.tag.strikethrough:
        task_dict['tag'] = 'x' + task.tag.get_text()
      else:
        task_dict['tag'] = 'o' + task.tag.get_text()
      task_dict['expan'] = task.expan.get_lines()
      data['tasks'].append(task_dict)

    return data

  def keypress(self, size, key):
    if not self.is_editing: 
      return self.nav_keypress(size, key)
    else:
      return self.input_keypress(size, key)

  def nav_keypress(self, size, key):
    if key == 'i':
      self.set_edit(True)
    # Move focus up/down
    elif key == 'j':
      self.move_focus(1)
    elif key == 'k':
     self.move_focus(-1)
    # Move cursor left/right
    elif key == 'J':
      self.move_task(1)
    elif key == 'K':
      self.move_task(-1)
    elif key == 'h':
      try:
        self.list_box.focus.move_cursor(-1)
      except AttributeError:
        pass
    elif key == 'l':
      try:
        self.list_box.focus.move_cursor(1)
      except AttributeError:
        pass
    # Open/close expan list
    elif key == 'e':
      try:
        self.list_box.focus.toggle_expan()
      except AttributeError:
        pass
    elif key == 'E':
      try:
        if not self.list_box.focus.show_expan:
          for task in self.tasks:
            task.open_expan()
        else:
          for task in self.tasks:
            task.close_expan()
      except AttributeError:
        pass
    # Cross out a line
    elif key == 'x':
      try:
        self.list_box.focus.toggle_strike()
      except AttributeError:
        pass
    elif key == 'n':
      self.title.edit()
    elif key == 'g':
      self.group_foot.edit()
    elif key == 'D':
      if self.list_box.focus:
        self.list_box.focus.prompt_delete() 
    elif key == 't':
      new_task = Task()
      urwid.connect_signal(new_task, 'delete', self.delete)
      if self.list_box.focus:
        self.tasks.insert(self.list_box.focus_position+1, new_task)
        self.body.insert(self.list_box.focus_position+1, new_task)
        self.list_box.focus_position += 1
      else:
        self.tasks.append(new_task)
        self.body.append(new_task)
      self.index_tasks()
      self.set_edit(True)
    elif key == 'T':
      if self.list_box.focus:
        focus = self.list_box.focus
        focus.new()
        self.set_edit(True)
    else: return key

  def input_keypress(self, size, key):
    if (key == 'esc' or key == 'enter'):
      self.set_edit(False)
      if self.list_frame.focus_position != 'body':
        self.name = self.title.edit.edit_text
        self.group = self.group_foot.edit.edit_text
        self.list_frame.focus_position = 'body'
    else: return super().keypress(size, key)

  def get_focus(self):
    task = self.list_box.focus
    return task
    

  def move_focus(self, trans):
    focus_task = self.list_box.focus
    if focus_task:
      sub_focus = focus_task.pile.focus
      if sub_focus == focus_task.expan:
        try:
          sub_focus.expan_pile.focus_position += trans
        except IndexError:
          try:
            focus_task.pile.focus_position += trans
          except IndexError:
            try:
              self.list_box.focus_position += trans
            except IndexError:
              pass
      else:
        try:
          focus_task.pile.focus_position += trans
        except IndexError:
          try:
            self.list_box.focus_position += trans
          except IndexError:
            pass

  def index_tasks(self):
    index = 1
    for task in self.body:
      task.tag.tag_index = index
      task.tag.edit.set_caption(task.tag.build_caption())
      index += 1
