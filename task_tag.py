# task_tag.py

from urwid import WidgetWrap, Edit, AttrSpec, AttrMap, Filler
from urwid import MainLoop


class TaskTag(WidgetWrap):

  def __init__(self, tag_index, tag_text):
    
    op_char = tag_text[0]
    if op_char == 'o':
      self.strikethrough = False
    elif op_char == 'x':
      self.strikethrough = True
    tag_text = tag_text.lstrip(op_char)

    self.tag_index = str(tag_index)
    self.tag_text = tag_text

    # Default color specs
    self.index_attr = AttrSpec('h11', '')
    self.index_STRIKE = AttrSpec('h11, strikethrough', '')
    self.text_attr = AttrSpec('', '')
    self.text_STRIKE = AttrSpec(', strikethrough', '')
    self.focus_attr = AttrSpec(', bold', '')
    self.focus_STRIKE = AttrSpec(', bold, strikethrough', '')

    # Build widget stack
    self.tag_edit = Edit(
        caption=self.build_caption(),
        edit_text=self.tag_text,
        multiline=False,
        wrap ='clip')
    if not self.strikethrough:
      self.tag_map = AttrMap(
          self.tag_edit,
          attr_map=self.text_attr,
          focus_map=self.focus_attr)
    else:
      self.tag_map = AttrMap(
          self.tag_edit,
          attr_map=self.text_STRIKE,
          focus_map=self.focus_STRIKE)
    self.tag_fill = Filler(self.tag_map, 'top')

    super().__init__(self.tag_fill)

  def build_caption(self):
    trailing_space = ' '
    caption_tag = ''
    if not self.strikethrough: caption_tag = self.tag_index
    else: caption_tag = 'X'
    leading_space = ' ' if len(caption_tag) < 2 else ''

    if not self.strikethrough: caption = (self.index_attr, leading_space + caption_tag + trailing_space)
    else: caption = (self.index_STRIKE, leading_space + caption_tag + trailing_space)

    return caption

  def get_text(self):
    return self.tag_edit.edit_text

  def move_cursor(self, translation):
    self.tag_edit.edit_pos += translation

  def toggle_strike(self):
    if self.strikethrough:
      self.strikethrough = False
      caption = self.build_caption()
      self.tag_edit.set_caption(caption)
      self.tag_map.set_attr_map({None: self.text_attr})
      self.tag_map.set_focus_map({None: self.focus_attr}) 
    else:
      self.strikethrough = True
      caption = self.build_caption()
      self.tag_edit.set_caption(caption)
      self.tag_map.set_attr_map({None: self.text_STRIKE})
      self.tag_map.set_focus_map({None: self.focus_STRIKE})

if __name__ == "__main__":
  task = TaskTag(1, "todo task")
  loop = MainLoop(task)
  loop.run()
