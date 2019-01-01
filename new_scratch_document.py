from functools import partial
import os
import re

import sublime
import sublime_plugin

def _safe_int(value):
  try:
    return int(value)
  except:
    return None

class NewScratchDocumentCommand(sublime_plugin.WindowCommand):

  def setup(self):
    """Reads the plugin settings and ensures that the class instance is configured
    correctly."""

    settings = sublime.load_settings("Scratch2.sublime-settings")

    # Setup the scratch directory
    path = settings.get("save_path")
    if not path:
      path = "~/scratch"
    path = os.path.expanduser(path)
    if not os.path.exists(path):
      os.mkdir(path)
    self.path = path

    # Setup the default extension
    ext = settings.get("extension")
    if not ext:
      ext = ".md"
    ext = re.sub(r"^\.+", "", ext)
    self.ext = ext

  def _next_file_path(self, path=None, ext=None):

    if not path:
      path = self.path

    if not ext:
      ext = self.ext

    # Get all of the files in the scratch directory
    files = os.listdir(os.path.expanduser(path))

    # Strip off the extension leaving just the numerical part of the filename
    files = [os.path.splitext(name)[0] for name in files]

    # Convert the filenames into integers.  Anything that can't be converted to an integer is
    # converted to None.
    files = [_safe_int(value) for value in files]

    # Remove the non-integer values.
    files = [v for v in files if v]

    if len(files) > 0:
      filename = "%d.%s" % (sorted(files, reverse=True)[0] + 1, ext)
    else:
      filename = "%d.%s" % (0, ext)

    filename = os.path.join(path, filename)

    return filename

  def touch(self, filename):
    """Given an absolute path to a file, create an empty file at that location."""
    with open(filename, "w") as f:
      pass

  def create_scratch_file(self, path=None, ext=None):
    """Creates a new scratch file and opens it.

    Args:
      path: (Optional) str containing the absolute path to the directory that
        the scratch file should be created in.  If not specified the value of
        the ``save_path`` setting will be used.
      ext: (Optional) str containing the extension for the scratch file.  If
        not specified, the value of the ``extension`` setting will be used.
    """
    filename = self._next_file_path(path, ext)
    self.touch(filename)
    self.window.open_file(filename)

  def run(self, execute=False):
    self.setup()
    
    print(self.path)

    if execute:
        self.create_scratch_file()
    else:
      self.window.show_input_panel("Extension", self.ext, partial(self.create_scratch_file, self.path), None, None)
