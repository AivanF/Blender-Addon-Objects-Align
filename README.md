# Blender objects alignment addon

A while ago a friend of mine asked me to create a simple addon for objects alignment. I have experience of Python and some tiny one of Blender, thus I agreed and then created what you see here.

BTW, the addon works with both Blender 2.8 and 2.7x. And I'm not obsessed with this project, so don't expect frequent updates. Any adequate contributions are welcome.


## Usage

The addon adds `View3D > Object > Align` submenu, there you can see these commands:

- Align between bounds – it will place selected objects...

  1) using specified order (based on source axis; it can be the same axis as target)
  2) between the most distant (based on target axis) objects setting same distance between objects.

- Align with padding – it will place selected objects...

  1) using specified order (based on source axis; it can be the same axis as target)
  2) with the same specified distance between objects starting from Cursor.

All the relocations affect the target axis only.


## Installation 

1) Copy the content of [the Python file](https://github.com/AivanF/Blender-Addon-Objects-Align/blob/master/AddonObjectsAlign.py);

2) Paste it as a new file to the Scripting section of your Blender project;

3) And click `Run script` button.

After that you will be able to use the Align submenu.  
<sub>If you know a better installation way – [let me know](https://github.com/AivanF/Blender-Addon-Objects-Align/issues).</sub>

## ToDo list

- Add ability to locate object using their max/min X/Y/Z, not only object origin.

- Something else?..

## License

[GPL 3.0](https://github.com/AivanF/Blender-Addon-Objects-Align/blob/master/LICENSE)
