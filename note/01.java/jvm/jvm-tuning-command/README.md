# JVM 调优命令

## 常用命令

> - **jps (JVM Process Status Tool)**：用于显示指定系统内所有的HotSpot虚拟机进程；
> - **jstat (JVM statistics Monitoring)**：用于监视虚拟机运行时状态信息的命令，它可以显示出虚拟机进程中的类装载、内存、垃圾收集、JIT编译等运行数据；
> - **jmap (JVM Memory Map)**：用于生成 heap dump 文件，如果不使用这个命令，还可以使用-XX:+HeapDumpOnOutOfMemoryError参数来让虚拟机出现 OOM 的时候自动生成 dump 文件；
> - **jhat (JVM Heap Analysis Tool)**：该命令通常与 jmap 搭配使用，用来分析 jmap 生成的 dump 文件，jhat 内置了一个微型的HTTP/HTML服务器，生成 dump 的分析结果后，可以在浏览器中查看；
> - **jstack (Java Virtual Machine Stack Trace)**：用于生成 Java 虚拟机当前时刻的线程快照；
> - **jinfo (JVM Configuration info)**：用于实时查看和调整后的虚拟机运行参数；

### jps








