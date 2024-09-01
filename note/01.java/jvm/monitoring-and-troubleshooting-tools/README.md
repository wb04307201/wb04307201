# JDK监控和故障处理工具

## JDK 命令行工具
> - **jps (JVM Process Status)**：类似 UNIX 的 ps 命令。用于查看所有 Java 进程的启动类、传入参数和 Java 虚拟机参数等信息；
> - **jstat（JVM Statistics Monitoring Tool)**：用于收集 HotSpot 虚拟机各方面的运行数据;
> - **jinfo (Configuration Info for Java)**：Configuration Info for Java,显示虚拟机配置信息;
> - **jmap (Memory Map for Java)**：生成堆转储快照;
> - **jhat (JVM Heap Dump Browser)**：用于分析 heapdump 文件，它会建立一个 HTTP/HTML 服务器，让用户可以在浏览器上查看分析结果。JDK9 移除了 jhat；
> - **jstack (Stack Trace for Java)**：生成虚拟机当前时刻的线程快照，线程快照就是当前虚拟机内每一条线程正在执行的方法堆栈的集合。

## JDK 可视化分析工具
> - **JConsole**：Java 监视与管理控制台
> - **Visual VM**：多合一故障处理工具
> - **MAT**：内存分析器工具