# JVM 调优命令

## 常用命令

- **jps (JVM Process Status Tool)**：用于显示指定系统内所有的HotSpot虚拟机进程；
- **jstat (JVM statistics Monitoring)**：用于监视虚拟机运行时状态信息的命令，它可以显示出虚拟机进程中的类装载、内存、垃圾收集、JIT编译等运行数据；
- **jmap (JVM Memory Map)**：用于生成 heap dump 文件，如果不使用这个命令，还可以使用-XX：+HeapDumpOnOutOfMemoryError参数来让虚拟机出现 OOM 的时候自动生成 dump 文件；
- **jhat (JVM Heap Analysis Tool)**：该命令通常与 jmap 搭配使用，用来分析 jmap 生成的 dump 文件，jhat 内置了一个微型的HTTP/HTML服务器，生成 dump 的分析结果后，可以在浏览器中查看；
- **jstack (Java Virtual Machine Stack Trace)**：用于生成 Java 虚拟机当前时刻的线程快照；
- **jinfo (JVM Configuration info)**：用于实时查看和调整后的虚拟机运行参数；

### jps
jps 用于显示指定系统内所有的`HotSpot`虚拟机进程。命令的使用格式如下。（其中`[options]`、`[hostid]`参数为非必填）
```shell
jps [options] [hostid]
```
options 参数详解：
- -l：输出主类全名或jar路径
- -q：只输出LVMID
- -m：输出JVM启动时传递给 main() 的参数
- -v：输出JVM启动时显示指定的JVM参数

在操作系统终端输入如下命令，即可查看 Java 相关的服务进程，示例如下。
```shell
$ jps -l -m
6628 sun.tools.jps.Jps -l -m
20094 springboot-example-web.jar --server.port=80
```
不带参数的显示结果。
```shell
$ jps
7669 Jps
20094 jar
```
左边是进程号，右边是 Java 服务名称。

### jstat
jstat 用于监视虚拟机运行时状态信息的命令，它可以显示出虚拟机进程中的类装载、内存、垃圾收集、JIT 编译等运行数据。命令的使用格式如下。
```shell
jstat [option] LVMID [interval] [count]
```
各个参数详解：
- option：操作参数
- LVMID：本地虚拟机进程ID
- interval：连续输出的时间间隔
- count：连续输出的次数

option 参数内容详解：

| option 参数         | 注释                                 |
|-------------------|------------------------------------|
| -class            | class loader的行为统计                  |
| -compiler         | HotSpt JIT编译器行为统计                  |
| -gc               | 垃圾回收堆的行为统计                         |
| -gccapacity       | 各个垃圾回收代容量和他们相应的空间统计                |
| -gcutil           | 垃圾回收统计概述                           |
| -gccause          | 垃圾收集统计概述（同-gcutil），附加最近两次垃圾回收事件的原因 |
| -gcnew            | 新生代行为统计                            |
| -gcnewcapacity    | 新生代与其相应的内存空间的统计                    |
| -gcold            | 年老代和永生代行为统计                        |
| -gcoldcapacity    | 年老代行为统计                            |
| -gcmetacapacity   | 元空间行为统计                            |
| -printcompilation | HotSpot编译方法统计                      |

#### 参数：class
`-class`参数用于监视类装载、卸载数量、总空间以及耗费的时间。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -class 20094
Loaded  Bytes  Unloaded  Bytes     Time
 12988 23508.0        0     0.0      30.21
```
各个参数解读如下：
- Loaded：加载class的数量
- Bytes：class字节大小
- Unloaded：未加载class的数量
- Bytes：未加载class的字节大小
- Time：加载时间

#### 参数：compiler
`-compiler`参数用于输出 JIT 编译过的方法数量耗时等。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -compiler 20094
Compiled Failed Invalid   Time   FailedType FailedMethod
   14524      5       0    43.33          1 org/springframework/core/annotation/AnnotationsScanner processMethodHierarchy
```
各个参数解读如下：
- Compiled：编译数量
- Failed：编译失败数量
- Invalid：无效数量
- Time：编译耗时
- FailedType：失败类型
- FailedMethod：失败方法的全限定名

#### 参数：gc
`-gc`参数用于垃圾回收堆的行为统计，属于常用命令。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gc 20094
 S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU    CCSC   CCSU   YGC     YGCT    FGC    FGCT     GCT
18432.0 18944.0  0.0   10133.7 281088.0 197255.5  139776.0   55324.5   70420.0 66352.5 9020.0 8405.8     25    0.599   3      0.673    1.273
```
其中 C 表示 Capacity 总容量，U 表示 Used 已使用的容量。  
各个参数解读如下：
- S0C：survivor0区的总容量
- S1C：survivor1区的总容量
- S0U：survivor0区已使用的容量
- S1U：survivor1区已使用的容量
- EC：Eden区的总容量
- EU：Eden区已使用的容量
- OC：Old区的总容量
- OU：Old区已使用的容量
- MC：泛指Metaspace区的总容量
- MU：泛指Metaspace区已使用的容量
- CCSC：泛指类压缩空间（Compressed class space，属于Metaspace区的一部分）的总容量
- CCSU：泛指类压缩空间（Compressed class space，属于Metaspace区的一部分）已使用的容量
- YGC：新生代GC次数
- YGCT：新生代GC总耗时
- FGC：Full GC次数
- FGCT：Full GC总耗时
- GCT：GC总耗时

还可以通过如下方式，来详细的监控 gc 回收情况，示例如下。
```shell
jstat -gc 20094 2000 20
```
以上的命令表示每隔 2000ms 输出进程号为 7140 的 gc 回收情况，一共输出 20次。

#### 参数：gccapacity
`-gccapacity`参数和`-gc`一样，不过还会输出 Java 堆各区域使用到的最大、最小空间。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gccapacity 20094
 NGCMN    NGCMX     NGC     S0C   S1C       EC      OGCMN      OGCMX       OGC         OC       MCMN     MCMX      MC     CCSMN    CCSMX     CCSC    YGC    FGC
 43520.0 698880.0 355840.0 18432.0 18944.0 281088.0    87552.0  1398272.0   139776.0   139776.0      0.0 1110016.0  70420.0      0.0 1048576.0   9020.0     25     3
```
各个参数解读如下：
- NGCMN：新生代占用的最小空间
- NGCMX：新生代占用的最大空间
- NGC：当前新生代的容量
- OGCMN：老年代占用的最小空间
- OGCMX：老年代占用的最大空间
- OGC：当前老年代的容量
- MCMN：Metaspace区占用的最小空间
- MCMX：Metaspace区占用的最大空间
- MC：当前Metaspace区的容量
- CCSMN：Compressed class space区占用的最小空间
- CCSMX：Compressed class space区占用的最大空间
- CCSC：当前Compressed class space区的容量

#### 参数：gcutil
`-gcutil`参数同`-gc`，不过输出的是已使用空间占总空间的百分比。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gcutil 20094
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
  0.00  53.49  91.96  39.58  94.22  93.19     25    0.599     3    0.673    1.273
```

#### 参数：gccause
`-gccause`参数用于垃圾收集统计概述（同`-gcutil`），附加最近两次垃圾回收事件的原因。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gccause 20094
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT    LGCC                 GCC
  0.00  53.49  92.65  39.58  94.22  93.19     25    0.599     3    0.673    1.273 Allocation Failure   No GC
```
各个参数解读如下：
- LGCC：最近垃圾回收的原因
- GCC：当前垃圾回收的原因

#### 参数：gcnew
`-gcnew`参数用于统计新生代的行为。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gcnew 20094
 S0C    S1C    S0U    S1U   TT MTT  DSS      EC       EU     YGC     YGCT
18432.0 18944.0    0.0 10133.7  2  15 18432.0 281088.0 265231.7     25    0.599
```
各个参数解读如下：
- TT：Tenuring threshold(提升阈值)
- MTT：最大的tenuring threshold
- DSS：survivor区域大小 (KB)

#### 参数：gcnewcapacity
`-gcnewcapacity`参数用于新生代与其相应的内存空间的统计。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gcnewcapacity 20094
 NGCMN      NGCMX       NGC      S0CMX     S0C     S1CMX     S1C       ECMX        EC      YGC   FGC
   43520.0   698880.0   355840.0 232960.0  18432.0 232960.0  18944.0   697856.0   281088.0    25     3
```
各个参数解读如下：
- S0CMX:最大的S0空间 (KB)
- S0C:当前S0区的容量 (KB)
- ECMX:最大eden空间 (KB)
- EC:当前eden区的容量 (KB)

#### 参数：gcold
`-gcold`参数用于统计老年代的行为。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gcold 20094
   MC       MU      CCSC     CCSU       OC          OU       YGC    FGC    FGCT     GCT
 70420.0  66352.5   9020.0   8405.8    139776.0     55324.5     25     3    0.673    1.273
```

#### 参数：gcoldcapacity
`-gcoldcapacity`参数用于统计老年代的大小和空间。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gcoldcapacity 20094
   OGCMN       OGCMX        OGC         OC       YGC   FGC    FGCT     GCT
    87552.0   1398272.0    139776.0    139776.0    25     3    0.673    1.273
```

#### 参数：gcmetacapacity
`-gcmetacapacity`参数用于统计元空间的大小和空间。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -gcmetacapacity 20094
   MCMN       MCMX        MC       CCSMN      CCSMX       CCSC     YGC   FGC    FGCT     GCT
       0.0  1112064.0    72468.0        0.0  1048576.0     9276.0    26     3    0.673    1.513
```

#### 参数：printcompilation
`-printcompilation`参数用于HotSpot编译方法统计。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jstat -printcompilation 20094
Compiled  Size  Type Method
    4387    123    1 org/apache/catalina/core/StandardContext getLoader
```
各个参数解读如下：
- Compiled：被执行的编译任务的数量
- Size：方法字节码的字节数
- Type：编译类型
- Method：编译方法的类名和方法名。类名使用”/” 代替 “.” 作为空间分隔符. 方法名是给出类的方法名

### jmap
jmap 用于生成 heap dump 文件，如果不使用这个命令，还可以使用`-XX:+HeapDumpOnOutOfMemoryError`参数来让虚拟机出现 OOM 的时候自动生成 dump 文件。

jmap 不仅可以生成 dump 文件，还可以查询`finalize`执行队列、Java 堆的详细信息，如当前使用率、当前使用的是哪种收集器等。

命令的使用格式如下。
```shell
jmap [option] LVMID
```
option 参数详解：
- dump：生成堆转储快照
- finalizerinfo：显示在F-Queue队列等待Finalizer线程执行finalizer方法的对象
- heap：显示Java堆详细信息
- histo：显示堆中对象的统计信息
- clstats：显示类加载器信息
- F：当-dump没有响应时，强制生成dump快照

#### 参数：dump
`-dump`参数用于生成堆内存快照文件。

命令的使用格式如下。
```shell
-dump::live,format=b,file=<filename> pid
```
option 参数详解：
- live : 指的是活着的对象
- format : 表示指定的输出格式
- file : 表示指定的文件名
- pid : 表示 Java 服务进程ID

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jmap -dump:live,format=b,file=dump.hprof 20094
Dumping heap to /xxx/dump.hprof ...
Heap dump file created
```
dump.hprof这个后缀是为了后续可以直接用 MAT (Memory Anlysis Tool) 工具打开。

#### 参数：finalizerinfo
`-finalizerinfo`参数用于打印等待回收对象的信息。在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jmap -finalizerinfo 20094
Attaching to process ID 20094, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.202-b08
Number of objects pending for finalization: 0
```
从日志中可以得出，当前 F-QUEUE 队列中并没有等待 Finalizer 线程执行 finalizer 方法的对象。

#### 参数：heap
`-heap`参数用于打印 heap 的概要信息，GC 使用的算法，heap 的配置及 wise heap 的使用情况，可以用此来判断内存目前的使用情况以及垃圾回收情况。

在操作系统终端输入如下命令，即可查看相关信息，示例如下。
```shell
$ jmap -heap 20094
Attaching to process ID 20094, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.202-b08

using thread-local object allocation.
Mark Sweep Compact GC

Heap Configuration:
   MinHeapFreeRatio         = 40
   MaxHeapFreeRatio         = 70
   MaxHeapSize              = 461373440 (440.0MB)
   NewSize                  = 9764864 (9.3125MB)
   MaxNewSize               = 153747456 (146.625MB)
   OldSize                  = 19595264 (18.6875MB)
   NewRatio                 = 2
   SurvivorRatio            = 8
   MetaspaceSize            = 21807104 (20.796875MB)
   CompressedClassSpaceSize = 1073741824 (1024.0MB)
   MaxMetaspaceSize         = 17592186044415 MB
   G1HeapRegionSize         = 0 (0.0MB)

Heap Usage:
New Generation (Eden + 1 Survivor Space):
   capacity = 17825792 (17.0MB)
   used     = 239848 (0.22873687744140625MB)
   free     = 17585944 (16.771263122558594MB)
   1.345511043772978% used
Eden Space:
   capacity = 15859712 (15.125MB)
   used     = 239848 (0.22873687744140625MB)
   free     = 15619864 (14.896263122558594MB)
   1.5123099334969008% used
From Space:
   capacity = 1966080 (1.875MB)
   used     = 0 (0.0MB)
   free     = 1966080 (1.875MB)
   0.0% used
To Space:
   capacity = 1966080 (1.875MB)
   used     = 0 (0.0MB)
   free     = 1966080 (1.875MB)
   0.0% used
tenured generation:
   capacity = 39444480 (37.6171875MB)
   used     = 23665256 (22.568946838378906MB)
   free     = 15779224 (15.048240661621094MB)
   59.99636958073728% used

21919 interned Strings occupying 2683112 bytes.
```
从日志中，可以很清楚的看到 Java 堆中各个区域目前的情况。

#### 参数：histo
`-histo`参数用于打印堆的对象统计，包括对象数、内存大小等等。也可以带上`live`参数，比如`-histo[:live]`表示只打印存活的对象，如果不加就是查询全部对象。

在操作系统终端输入如下命令，即可查看相关信息，部分示例如下。
```shell
$ jmap -histo 20094

 num     #instances         #bytes  class name
----------------------------------------------
1:         61030        8438336  [C
   2:          9918        2169120  [I
   3:         59981        1439544  java.lang.String
   4:          5112        1331136  [B
   5:         13532        1190816  java.lang.reflect.Method
   6:         10071        1125192  java.lang.Class
   7:         32196        1030272  java.util.concurrent.ConcurrentHashMap$Node
   8:          9593         572904  [Ljava.lang.Object;
   9:         15416         493312  java.util.HashMap$Node
  10:         12115         484600  java.util.LinkedHashMap$Entry
  ...
```
其中`class name`列指的是对象类型，部分内容详解：
- B：byte
- C：char
- D：double
- F：float
- I：int
- J：long
- Z：boolean
- [I：表示 int[]的数组
- [L+类名：其他数组对象

#### 参数：clstats
`-clstats`参数用于打印类加载器信息。

在操作系统终端输入如下命令，即可查看相关信息，部分示例如下。
```shell
$ jmap -clstats 20094
Attaching to process ID 20094, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.202-b08
```
表示当前并没有相关类加载的信息。

#### 参数：F
`-F`参数表示强制模式。在 pid 没有响应的时候使用`-dump`或者`-histo`参数，在这个模式下`live`子参数会无效。

### jhat
jhat 命令通常与 jmap 搭配使用，用来分析 jmap 生成的 dump 文件，jhat 内置了一个微型的`HTTP/HTML`服务器，生成 dump 的分析结果后，可以在浏览器中查看。

命令的使用格式如下。（其中`heap-dump-file`为必填项）
```shell
jhat [-stack <bool>] [-refs <bool>] [-port <port>] [-baseline <file>] [-debug <int>] [-version] [-h|-help] <heap-dump-file>
```
可选参数详解：
- -stack false|true：表示关闭对象分配调用栈跟踪。如果分配位置信息在堆转储中不可用，则必须将此标志设置为 false，默认值为 true；
- -refs false|true：表示关闭对象引用跟踪。默认值为 true，默认情况下，返回的指针是指向其他特定对象的对象，如反向链接或输入引用，会统计/计算堆中的所有对象；
- -port port-number：表示设置 jhat HTTP server 的端口号，默认值 7000；
- -baseline exclude-file：表示指定一个基准堆转储。在两个 heap dumps 中有相同 object ID 的对象会被标记为不是新的，其他对象被标记为新的，在比较两个不同的堆转储时很有用；
- -debug int：表示设置 debug 级别，0 表示不输出调试信息。值越大则表示输出更详细的 debug 信息；
- -version：启动后只显示版本信息就退出；-J< flag >：因为 jhat 命令实际上会启动一个JVM来执行，通过 -J 可以在启动JVM时传入一些启动参数。例如，-J-Xmx512m 可以指定运行 jhat 的 Java 虚拟机使用的最大堆内存为 512 MB，如果需要使用多个 JVM 启动参数，则传入多个 -Jxxx即可；
- -h or -help：显示jhat命令的帮助信息；在操作系统终端输入如下命令，即可查看相关信息，部分示例如下。
```shell
$ jhat -J-Xmx512m /xxx/dump.hprof
Reading from dump.hprof...
Dump file created Mon Feb 05 17:41:33 CST 2024
Snapshot read, resolving...
Resolving 383026 objects...
Chasing references, expect 76 dots............................................................................
Eliminating duplicate references............................................................................
Snapshot resolved.
Started HTTP server on port 7000
Server is ready.
```
运行成功之后在浏览器访问http://127.0.0.1:7000，可以查询快照文件分析结果。

### jstack
jstack 命令用于生成 Java 虚拟机当前时刻的线程快照。

线程快照是当前 Java 虚拟机内每一条线程正在执行的方法堆栈的集合，生成线程快照的主要目的是定位线程出现长时间停顿的原因，如线程间死锁、死循环、请求外部资源导致的长时间等待等。

命令的使用格式如下。
```shell
jstack [option] LVMID
```
option 参数详解：
- -F : 当正常输出请求不被响应时，强制输出线程堆栈
- -l : 除堆栈外，显示关于锁的附加信息
- -m : 如果调用到本地方法的话，可以显示C/C++的堆栈

在操作系统终端输入如下命令，即可查看相关信息，部分示例如下。
```shell
$ jstack -F 20094
Attaching to process ID 20094, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.202-b08
Deadlock Detection:

No deadlocks found.

Thread 15138: (state = BLOCKED)


Thread 30966: (state = BLOCKED)
 - sun.misc.Unsafe.park(boolean, long) @bci=0 (Compiled frame; information may be imprecise)
 - java.util.concurrent.locks.LockSupport.park(java.lang.Object) @bci=14, line=175 (Compiled frame)
 - java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await() @bci=42, line=2039 (Compiled frame)
 - java.util.concurrent.ScheduledThreadPoolExecutor$DelayedWorkQueue.take() @bci=100, line=1088 (Compiled frame)
 - java.util.concurrent.ScheduledThreadPoolExecutor$DelayedWorkQueue.take() @bci=1, line=809 (Compiled frame)
 - java.util.concurrent.ThreadPoolExecutor.getTask() @bci=149, line=1074 (Compiled frame)
 - java.util.concurrent.ThreadPoolExecutor.runWorker(java.util.concurrent.ThreadPoolExecutor$Worker) @bci=26, line=1134 (Interpreted frame)
 - java.util.concurrent.ThreadPoolExecutor$Worker.run() @bci=5, line=624 (Interpreted frame)
 - java.lang.Thread.run() @bci=11, line=748 (Interpreted frame)
...
```
关于 jstack 命令，更加详细的使用案例，可以参数这篇文章 jstack命令解析。

### jinfo
jinfo 命令用于实时查看和调整虚拟机运行参数。

命令的使用格式如下。
```shell
jinfo [option] [args] LVMID
```
option 参数详解：
- -flag：输出指定 args 参数的值
- -flags：不需要 args 参数，输出所有 JVM 参数的值
- -sysprops：输出系统属性，等同于 System.getProperties()

在操作系统终端输入如下命令，即可查看相关信息，部分示例如下。
```shell
$ jinfo -flags 20094
Attaching to process ID 20094, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.202-b08
Non-default VM flags: -XX:CICompilerCount=2 -XX:InitialHeapSize=29360128 -XX:MaxHeapSize=461373440 -XX:MaxNewSize=153747456 -XX:MinHeapDeltaBytes=196608 -XX:NewSize=9764864 -XX:OldSize=19595264 -XX:+UseCompressedClassPointers -XX:+UseCompressedOops -XX:+UseFastUnorderedTimeStamps 
Command line:  
```











