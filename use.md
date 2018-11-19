一、安装python依赖库
    pip install pbxproj
	pip install Cheetah
二、配置工程
    1.新建一个工作目录
    2.在工作目录下建立资源目录,如resources.
    3.建立一个马甲包的子目录，如Test，里面存放配置文件、图标、起动图等，用于替换主包的资源。
    4.把配置文件从repack/data里copy一份放入Test目录，修改相应配置，如包名，工程名，签名。
    5.执行命令进行打包
        python repack/repack.py -s 源工程目录 -o 输出目录 -r 资源目录(指向刚才建立的resources) -d repack/data -c 工程配置(resources/Test/project.json) --step-config 执行步骤配置(resources/Test/step.json)