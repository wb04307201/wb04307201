# 统计API接口调用耗时

## 添加依赖
```xml
<!--将通过javassit来修改类信息-->
<dependency>  
    <groupId>org.javassist</groupId>  
    <artifactId>javassist</artifactId>  
    <version>3.29.2-GA</version>
</dependency>
```

## 编写`Transformer`类用来转换修改要加载的类
```java
public class MonitorTransformer implements ClassFileTransformer {

    @Override
    public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
        // 在上面的API说明中已经说了，这里的className不是. 而是'/'    
        className = className.replace("/", ".");
        // 这里只拦截com.pack及子包下的类    
        if (className.startsWith("com.pack")) {
            try {
                // 以下的相关API就是javassit；可自行查看javassit相关的文章        
                CtClass ctClass = ClassPool.getDefault().get(className);
                CtMethod[] ctMethods = ctClass.getDeclaredMethods();
                for (CtMethod ctMethod : ctMethods) {
                    // 获取执行的方法名称          
                    String methodName = ctMethod.getName();
                    // 打印方法执行耗时时间          
                    String executeTime = "\nSystem.out.println(\"" + methodName + " 耗时:\" + (end - start) + " + "\" ms\");\n";
                    // 添加2个局部变量          
                    ctMethod.addLocalVariable("start", CtClass.longType);
                    ctMethod.addLocalVariable("end", CtClass.longType);
                    // 为上面2个局部变量赋值          
                    ctMethod.insertBefore("start = System.currentTimeMillis() ;\n");
                    ctMethod.insertAfter("end = System.currentTimeMillis();\n");
                    // 将打印时间的语句插入到方法体的最后一行          
                    ctMethod.insertAfter(executeTime);
                }
                // 返回修改后的字节码（这里就是重写字节码文件）        
                return ctClass.toBytecode();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return null;
    }
}
```

## 编写Agent入口
```java
public class MonitorAgent {
    // 这里的premain是我们Agent的入口，首先执行的就是该premain，然后才是main  
    // agentArgs是agent运行时添加的参数，我们可以在下面看到如何定义参数  
    public static void premain(String agentArgs, Instrumentation instrumentation) {
        // 添加转换器    
        instrumentation.addTransformer(new MonitorTransformer());
    }

    // 这里完全没必要main，只是为了在eclipse中生成jar包方便  
    public static void main(String[] args) {

    }
}
```

## 编写MANIFEST.MF文件
```text
Manifest-Version: 1.0
Premain-Class: com.pack.agent.MonitorAgent
Can-Redefine-Classes: true
```
以上步骤完成后就可以打包了。

## 编写SpringBoot程序
随便写一个API接口即可
```java
@RestController@RequestMapping("/demos")public class DemoController {
    @GetMapping("/index")  
    public Object index() throws Exception {    
        TimeUnit.SECONDS.sleep(new Random().nextInt(5)) ;    
        return "success" ;  
    }
}
```
将该测试程序打包成jar。

通过命令指定agent jar包
```shell
java -javaagent:CostAgent.jar -jar test.jar
```

启动后访问测试接口/demos/index
```text
index 耗时:0 ms
index 耗时:0 ms
index 耗时:0 ms
index 耗时:1008 ms
index 耗时:2012 ms
```