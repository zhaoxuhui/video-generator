# video-generator
生成视频共包含5个步骤：
* 1.读取数据文件
* 2.结合数据文件和图片生成Item并输出
* 3.将所有Item拼接为一个图片并输出
* 4.根据全图生成视频帧图片并输出
* 5.根据视频帧生成视频

考虑到原始图片上传到Github太大，因此直接上传了以及生成好的Items图片的压缩包，直接解压。在运行的时候直接从第三步开始即可，将前面两个步骤代码注释掉就可以。

依赖库：
* OpenCV
* Numpy
* PIL
* OS