## 关于c++的代码优化
- 编译优化
	如果开启优化选项，ollvm的三种代码混淆方法就会失效。Instructions Substitution(-mllvm -sub);Bogus Control Flow(-mllvm -bcf);Control Flow Flattening( -mllvm -fla)。
	不被优化的方法：
  - 使用全局变量。
  - 使用参数。
  - 调用类的属性或方法
  - 使用复杂while和if的嵌套。参考obf.cpp.
     可以使用等于，大于，小于来构建多种不同的代码结构。
- 链接优化
  -	类的没有调用的非虚函数会,会被优化掉。
  - 类的没有调用的虚函数，会被保留。
  - 类的有调用的简单非虚函数，会被内联优化掉
  - 类的简单非虚函数，被其它类调用，会被保留。
  - 如果类没有被引用，则会被优化掉。如果被引用，确保引用的位置不被优化掉。
		总结：可以把代码放在虚函数中，并且保持这个类被使用到。

## 代码链接的位置
- ios
  按照Compile Source定义的顺序最后出现在二进制文件的位置。Compile Sourcec对应project.pbxproj里的PBXSourcesBuildPhase。在混淆的时候把这里面的内容做乱序处理。
     