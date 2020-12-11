# SingingPiano
[中文版](docs/README-zh_CN.md)
## Tutorials

### Supported Platform
* Windows 10 (64 bit version) 
* Linux (64 bit version) [UNCHECKED]
* Android [PARTIAL]
* OS X [UNCHECKED]

### Installation
0. Obtain [Python](https://python.org);
0. Use <code>pip -r requirments.txt</code> to install all the requirements for this tool;
0. For non-windows users: Manually build the [native module](libs/mydft), here is the command: (under the source directory)<code>python3 setup.py build</code>, and put the binary module file into the [libs](libs) directory;
0. Run [SingingpianoQt.pyw](SingingpianoQt.pyw) and enjoy!

### Troubleshooting
#### Unable to open "SingingpianoQt.pyw"
* Make sure that you have done the former installation steps successfully;
* Use [QTDEBUG.BAT](QTDEBUG.BAT)(windows user) or <code>python3 SingingpianoQt.pyw</code>(in "terminal" window) to start the tool, if any error occured, come up with a new issue [here](https://github.com/wave2midi/SingingPiano/issues/new).

## Playing generated MIDI files 
* PFA is recommended as it provides a simple choice to customize track colors;
* A MIDI Driver such as [OmniMIDI](https://github.com/KeppySoftware/OmniMIDI) is needed in order to apply the specified [soundfont](/utils/Sine_MNJS_N1_50ms.sf2) before playing;

Suggested Track Color:
(Color #4 is a color close to the background color the most)
| Track # | Color |
| :--- | :--- |
| 0    | Color #4    |
| 1    | Color #3    |
| 2    | Color #2    |
| 3    | Color #1    |
| 4    | Color #1    |
| 5    | Color #2    |
| 6    | Color #3    |
| 7    | Color #4    |

See also [PFA Configuration File](/utils/Config.xml).
