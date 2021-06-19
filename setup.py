from cx_Freeze import setup, Executable


executables = [Executable('main.py', target_name='vkSendMessage.exe')]


excludes = ['pygame', 'unittest', 'tkinter', 'numpy', 'concurrent', 'ctypes', 'distutils']

include_files = ['.env', 'txt', 'sessions', 'memes', 'logs']


options = {'build_exe': {
      'include_msvcr': True,
      'excludes': excludes,
      'include_files': include_files,
      }
}


setup(name='vkSendMessage',
      version='1.0',
      description='отвечаем на сообщения',
      executables=executables,
      options=options
      )
