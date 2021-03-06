from functools import partial
import os
import re

import sublime
import sublime_plugin

_settings_file_name = "Scratch2.sublime-settings"

def get_save_path(settings, create=False):
  """Returns the absolute path that scratch files should be saved in as configured in the
  passed settings.  The directory to store scratch files can optionally be created.

  Args:
    settings: Sublime settings to read the save path from.
    create: bool indicating whether the save path should be created if it doesn't exist.

  Returns:
    The absolute path that scratch files should be saved in.
  """
  path = settings.get("save_path")
  if not path:
    path = "~/scratch"
  path = os.path.expanduser(path)

  if create and not os.path.exists(path):
    os.mkdir(path)
  return path

def get_extension(settings):
  """Returns the extension that should be used for scratch files by default.

  Args:
    settings: Sublime settings to read the extension from.

  Returns:
    The file extension without the leading period to be used for scratch files.
  """
  ext = settings.get("extension")
  if not ext:
    ext = ".md"
  ext = re.sub(r"^\.+", "", ext)
  return ext

def _safe_int(value):
  try:
    return int(value)
  except:
    return None

class NewScratchDocumentCommand(sublime_plugin.WindowCommand):

  def setup(self):
    """Reads the plugin settings and ensures that the class instance is configured
    correctly."""
    settings = sublime.load_settings(_settings_file_name)
    self.path = get_save_path(settings, create=True)
    self.ext = get_extension(settings)

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
    files = [v for v in files if v is not None]

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
