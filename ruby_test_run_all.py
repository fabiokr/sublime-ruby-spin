import sublime, sublime_plugin, os, re, glob, itertools, subprocess

class RubyTestRunAllFolders(object):
    # Initializes the folders object.
    #
    # file_path - the file to look folders for
    def __init__(self, file_path, folders):
        self.__file_path = file_path
        self.__root = self.__root(folders)
        self.__folders = []
        self.__descriptions = []
        self.__build()

    # # Retrieves a list of all descriptions.
    def descriptions(self):
        return self.__descriptions

    # # Retrieves a list of all parent folders paths.
    def folders(self):
        return self.__folders

    # # Retrieves the root folder.
    def root(self):
        return self.__root

    # Returns the root folder for the given file and folders
    def __root(self, folders):
        for folder in folders:
            if self.__file_path.startswith(os.path.join(folder, "")):
                return folder

    # Retrieves the folder name without the root part.
    def __folder_without_root(self, folder):
        return os.path.basename(self.__root) + folder[len(self.__root):]

    # Converts paths to posixpaths.
    def __to_posixpath(self, path):
        return re.sub("\\\\", "/", path)

    # Builds a list with all folders until the parent folder.
    def __build(self):
        folders = list()

        # appends the current file
        folders.append(self.__file_path)

        current_dir = os.path.dirname(self.__to_posixpath(self.__file_path))

        while current_dir != self.__root :
            folders.append(current_dir)
            current_dir = os.path.dirname(current_dir)

        self.__folders = folders
        self.__descriptions = [self.__folder_without_root(folder) for folder in folders]


class RubyTestRunAllCommand(sublime_plugin.WindowCommand):
  def run(self, index=None):
    active_file_path = self.__active_file_path()

    if active_file_path:
        self.__folders = RubyTestRunAllFolders(active_file_path, sublime.active_window().folders())

        self.window.show_quick_panel(self.__folders.descriptions(), self.__run_spec)
    else:
        self.__status_msg("No open files")

  # Runs the specs in the folder
  def __run_spec(self, index):
        if index >= 0:
            print(self.__folders.root())
            print("~/.rbenv/bin/rbenv exec spin push {0}".format(self.__folders.folders()[index]))

            subprocess.call("/home/fabio/.rbenv/bin/rbenv exec spin push {0}".format(self.__folders.folders()[index]), shell=True, cwd=self.__folders.root())

  # Retrieves the patterns from settings.
  def __patterns(self):
      return sublime.load_settings("RelatedFiles.sublime-settings").get('patterns')

  # Returns the activelly open file path from sublime.
  def __active_file_path(self):
      if self.window.active_view():
          file_path = self.window.active_view().file_name()

          if file_path and len(file_path) > 0:
              return file_path

  # Displays a status message on sublime.
  def __status_msg(self, message):
      sublime.status_message(message)
