from cx_Freeze import setup, Executable


executables = [Executable('main.py', target_name='vkSendMessage.exe')]


excludes = ['pygame', 'unittest', 'tkinter', 'numpy', 'asyncio', 'concurrent', 'ctypes',
            'distutils', 'msilib', 'pkg_resources', 'pycparser', 'pydoc_data']

include_files = ['.env', 'ids.txt', 'sessions', 'memes', 'logs', 'all_answers.txt', 'polina_answers.txt', 'help.txt']


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
