# SingingPiano

## 教程

### 支持平台
* Windows 10 (64位) 
* Linux (64位) [未经验证]
* Android [部分]
* OS X [未经验证]

### 安装步骤
0. 取得 [Python](https://python.org);
0. 使用 <code>pip -r requirments.txt</code> 安装所有必需依赖库;
0. 非Windows用户: 用如下命令手动构建[本地库](libs/mydft): (在其源代码目录下)<code>python3 setup.py build</code>, 并将编译好的二进制模块文件放入[libs](libs)目录;
0. 运行[SingingpianoQt.pyw](SingingpianoQt.pyw), 大功告成!

### 遇到问题？
#### 无法打开 "SingingpianoQt.pyw"
* 确保你完成了以上的安装步骤;
* 用[QTDEBUG.BAT](QTDEBUG.BAT)(windows 用户)或<code>python3 SingingpianoQt.pyw</code>(in "terminal" window)打开工具, 如果发生错误, 在[这里](https://github.com/wave2midi/SingingPiano/issues/new)提一个issue.

## 关于播放生成的MIDI文件的建议
* 经典的方法是使用PFA播放
* 需要使用波表加载指定的[音色库文件](utils/Sine_MNJS_N1_50ms.sf2)
为取得最佳视觉效果，建议将音轨的颜色如下设置（四种渐变色，数字越大越接近背景色）：
| 音轨 | 对应颜色 |
| :--- | :--- |
| 0    | 颜色4    |
| 1    | 颜色3    |
| 2    | 颜色2    |
| 3    | 颜色1    |
| 4    | 颜色1    |
| 5    | 颜色2    |
| 6    | 颜色3    |
| 7    | 颜色4    |
也可参考这一[PFA配置文件](utils/Config.xml)。
