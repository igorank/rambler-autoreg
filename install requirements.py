import os
with open('requirements.txt', 'r') as f:
    modules = f.readlines()
modules = [m.strip() for m in modules]
for m in modules:
    os.system(f'pip install {m}')
input('Success. Press enter to exit...')