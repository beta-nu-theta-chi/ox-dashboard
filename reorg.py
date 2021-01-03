import os

folder_arr = ['dashboard', 'views', '_brother']
path_arr = folder_arr + ['__init__.py']

import_file = os.path.join(*path_arr)

with open(import_file, "w") as f:
    dirname = os.path.dirname(import_file)
    files = os.listdir(dirname)

    for p in files:
        if p != "__init__.py":
            f.write("from {} import *\n".format('.'.join(folder_arr + [p.replace(".py", "")])))



