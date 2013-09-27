import sublime, sublime_plugin, os, re, glob, itertools, subprocess

class RubyTestRunAllFolders(object):
    # Initializes the folders object.
    #
    # file_path - the file to look folders for
    def __init__(self, file_path, root_path):
        self.__file_path = file_path
        self.__root_path = root_path
        self.__folders = []
        self.__descriptions = []
        self.__build()

    # # Retrieves a list of all descriptions.
    def descriptions(self):
        return self.__descriptions

    # # Retrieves a list of all parent folders paths.
    def folders(self):
        return self.__folders

    # Retrieves the folder name without the root part.
    def __folder_without_root(self, folder):
        return os.path.basename(self.__root_path) + folder[len(self.__root_path):]

    # Converts paths to posixpaths.
    def __to_posixpath(self, path):
        return re.sub("\\\\", "/", path)

    # Builds a list with all folders until the parent folder.
    def __build(self):
        folders = list()

        # appends the current file
        folders.append(self.__file_path)

        current_dir = os.path.dirname(self.__to_posixpath(self.__file_path))

        while current_dir != self.__root_path :
            folders.append(current_dir)
            current_dir = os.path.dirname(current_dir)

        self.__folders = folders
        self.__descriptions = [self.__folder_without_root(folder) for folder in folders]

class RubyTestRunCommand(sublime_plugin.WindowCommand):
  # Command entry point
  def run(self, index=None):
    self.run_spec(self.active_file_path())

  # Pushes paths to spin
  def run_spec(self, path):
      subprocess.call("/home/fabio/.rbenv/bin/rbenv exec spin push {0}".format(path), shell=True, cwd=self.root_path(path))

  # Returns the root folder for the given file and folders
  def root_path(self, path):
      for folder in sublime.active_window().folders():
          if path.startswith(os.path.join(folder, "")):
              return folder

  # Returns the activelly open file path from sublime.
  def active_file_path(self):
      if self.window.active_view():
          file_path = self.window.active_view().file_name()

          if file_path and len(file_path) > 0:
              return file_path

  # Displays a status message on sublime.
  def status_msg(self, message):
      sublime.status_message(message)

class RubyTestRunAllCommand(RubyTestRunCommand):
  def run(self, index=None):
    active_file_path = self.active_file_path()

    if active_file_path:
        self.folders = RubyTestRunAllFolders(active_file_path, self.root_path(active_file_path))

        self.window.show_quick_panel(self.folders.descriptions(), self.run_spec)
    else:
        self.status_msg("No open files")

  # Runs the specs in the folder
  def run_spec(self, index):
      if index >= 0:
          super(RubyTestRunAllCommand, self).run_spec(self.folders.folders()[index])
