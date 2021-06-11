from cx_Freeze import setup, Executable


executables = [Executable('main.py', target_name='vkSendMessage.exe')]

excludes = ['pygame', 'unittest', 'tkinter', 'numpy', 'asyncio', 'concurrent', 'ctypes',
            'distutils', 'msilib', 'pkg_resources', 'pycparser', 'pydoc_data', 'xml', 'xmlrpc']

include_files = ['.env']


options = {'build_exe': {
      'include_msvcr': True,
      'excludes': excludes,
      'include_files': include_files,
      }
}


setup(name='vkSendMessage',
      version='1.0',
      description='отвечаем на нет ты',
      executables=executables,
      options=options
      )
