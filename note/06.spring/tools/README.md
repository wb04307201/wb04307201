# Spring 自带24个工具类

## Bean相关
此类工具位于spring-beans包中，提供了4个非常实用的工具类。

### BeanUtils
针对 JavaBeans 的静态工具方法：用于实例化 Bean、检查 Bean 属性类型、复制 Bean 属性等。

如下示例：
```java
/**1.对象属性复制*/
User source = newUser(1L,"PackXg");
User target = newUser();
BeanUtils.copyProperties(source, target);

/**2.通过无参构造方法实例化对象*/
User instance = BeanUtils.instantiateClass(User .class);

/**3.检查给定类型是否为 Bean 属性和数据绑定场景下的“简单”值类型*/
Class<?> type = User.class.getDeclaredField("name").getType();
boolean isSimpleType = BeanUtils.isSimpleValueType(type);
```

### BeanFactoryUtils
针对 Bean 工厂的便捷操作方法，尤其针对 ListableBeanFactory 接口的扩展功能这些方法提供以下功能：
- 返回 Bean 的数量、名称或实例
- 关键特性：支持处理 Bean 工厂的嵌套层级结构（而 ListableBeanFactory 接口原生方法不支持此特性，这与 BeanFactory 接口定义的方法形成对比）

如下示例：
```java
ListableBeanFactory beanFactory = ...;
/**1.返回指定类型或其子类型的单个 Bean（不向上查找祖先工厂）*/
CommonDAO dao = BeanFactoryUtils.beanOfType(beanFactory, CommonDAO.class);
/**2.获取所有类上带有指定注解类型的 Bean 名称*/
String[] beanNames = BeanFactoryUtils.beanNamesForAnnotationIncludingAncestors(beanFactory, Pack.class);
/**3.返回指定类型或其子类型的所有 Bean*/
Map<String, CommonDAO> beans = BeanFactoryUtils.beansOfTypeIncludingAncestors(beanFactory, CommonDAO.class);
```

### BeanFactoryAnnotationUtils
针对 Spring 特定注解（如 Spring 的@Qualifier注解）执行 Bean 查找的便捷方法。

如下示例：
```java
// 首先，定义如下beans
@Component
@Qualifier("product")
public class ProductDAO implements CommonDAO{
    
}
@Component
@Qualifier("user")
public class UserDAO implements CommonDAO{}
ConfigurableListableBeanFactory beanFactory = ... ;
// 指定获取使用了@Qualifier注解并且名称为user
CommonDAO userDAO = BeanFactoryAnnotationUtils.qualifiedBeanOfType(beanFactory, CommonDAO.class,"user") ;
// 指定获取使用了@Qualifier注解并且名称为product
CommonDAO productDAO = BeanFactoryAnnotationUtils.qualifiedBeanOfType(beanFactory, CommonDAO.class,"product") ;
```

### BeanDefinitionReaderUtils
适用于 Bean 定义读取器实现的实用工具方法，主要供内部使用。

如下示例：
```java
BeanDefinitionRegistry registry = ...;
// 1.通过BeanDefinition生成beanName
AbstractBeanDefinition beanDefinition = BeanDefinitionBuilder.genericBeanDefinition(UserDAO.class).getBeanDefinition();
String beanName = BeanDefinitionReaderUtils.generateBeanName(beanDefinition, registry);
// 2.注册bean
BeanDefinitionHol derdefinitionHolder = newBeanDefinitionHolder(beanDefinition, beanName);
BeanDefinitionReaderUtils.registerBeanDefinition(definitionHolder, registry);
```

## AOP相关
此类工具位于spring-aop包中，提供了6个非常实用的工具类。

### AopConfigUtils
用于处理 AOP 自动代理创建器注册的实用工具类。

如下示例：
```java
eanDefinitionRegistry registry = ...;
/**1.该方法会自动注册InfrastructureAdvisorAutoProxyCreator*/
// 注册该类的作用用于动态代理
AopConfigUtils.isterAutoProxyCreatorIfNecessary(registry);
/**2.该方法会自动注册AnnotationAwareAspectJAutoProxyCreator*/
// 同样该类的作用也适用于动态代理
AopConfigUtils.registerAspectJAnnotationAutoProxyCreatorIfNecessary(registry);
```

### AopProxyUtils
AOP 代理工厂的实用工具方法。

如下示例：
```java
/**1.获取给定代理类背后的单例目标对象（原始对象）*/
// 如果该对象是被Spring创建的代理对象
UserDAO proxy = ...;
// 该方法将返回代理对象背后的那个原始对象
Object targetObject = AopProxyUtils.getSingletonTarget(proxy);
/**2.返回当前代理对象实现了哪些接口（排除Spring规范实现的那几个接口）*/
Class<?>[] userInterfaces = AopProxyUtils.proxiedUserInterfaces(proxy);
```

### AutoProxyUtils
为支持自动代理的组件提供的实用工具，主要供框架内部使用。

如下示例：
```java
ConfigurableListableBeanFactory beanFactory = ...;
/**1.获取指定bean对应的原始目标类*/
Class<?> targetClass = AutoProxyUtils.determineTargetClass(beanFactory, "userDAO");
/**2.判断给定的 Bean 是否应基于其目标类（而非接口）进行代理*/
// 也就是判断是通过jdk代理还是cglib代理
AutoProxyUtils.shouldProxyTargetClass(beanFactory, "userDAO");
```

#### ScopedProxyUtils
用于创建作用域代理的实用工具类，通常是由 ScopedProxyBeanDefinitionDecorator 和 ClassPathBeanDefinitionScanner 使用。

如下示例：
```java
try (GenericApplicationContext context = new GenericApplicationContext()) {
    BeanDefinition beanDefinition = BeanDefinitionBuilder.genericBeanDefinition(UserDAO.class).getBeanDefinition();
    BeanDefinitionHolder definition = new BeanDefinitionHolder(beanDefinition , "userDAO");  
    BeanDefinitionHolder scopedProxy = ScopedProxyUtils.createScopedProxy(definition, context, true);  
    context.registerBeanDefinition("userDAO", scopedProxy.getBeanDefinition());
    
    context.refresh();
    
    UserDAO dao = context.getBean(UserDAO.class);
    System.err.println(dao.getClass());
}
```

运行上面代码，输出如下：
`class com.pack.UserDAO$$SpringCGLIB$$0`

### bAopUtils
用于支持 AOP 的实用工具方法。

如下示例：
```java
UserDAO userDAO = ...;
/**1.获取bean对应的原始目标Class*/
AopUtils.getTargetClass(userDAO);
/**2.判断是否是代理对象（包括jdk和cglib）*/
AopUtils.isAopProxy(userDAO);
/**3.判断指定的Advisor（切面）是否能应用到给到的Class对象上*/
Advisor advisor = ...;
AopUtils.canApply(advisor, UserDAO.class);
```

### ClassFilters
用于组合 ClassFilter 的静态实用工具方法。Spring底层在判断一个类是否能被代理时，会先通过ClassFilter判断，而该工具类则可以将多个ClassFilter合并进行判断（多条件判断）。

如下示例：
```java
ClassFilter f1 = new ClassFilter() {
    public boolean matches(Class<?> clazz) {
        return clazz.getPackageName().startsWith("com.pack.aop");
    }
};
ClassFilter f2 = new ClassFilter() {
    public boolean matches(Class<?> clazz) {
        return clazz.isAssignableFrom(CommonDAO.class);
    }
};
ClassFilter[] classFilters = new ClassFilter[]{f1, f2};
/**1.用一组给定的‘类过滤器’（ClassFilter）来筛选类，只要一个类能被其中一个过滤器（或者全部过滤器）匹配上，这个类就会被选中。*/
ClassFilter classFilter = ClassFilters.union(classFilters);
/**2.返回一个类过滤器，该过滤器表示对指定过滤器实例的逻辑取反（即匹配所有不满足原过滤条件的类）。取反的意思*/
classFilter =ClassFilters.negate(f1);
/**3.给定的ClassFilter集合必须全部匹配*/
classFilter =ClassFilters.intersection(classFilters);
```

## Spring核心工具类
此类工具位于spring-core包中，提供了14个非常实用的工具类。

### ReflectUtils
该工具主要用于通过反射进行相关的操作。

如下示例：
```java
/**1.创建实例*/
ReflectUtils.newInstance(UserDAO .class);
/**2.查找Method对象*/
ReflectUtils.findDeclaredMethod(UserDAO .class, "create",new Class<?>[] {
        String.class
});
/**3.获取java bean对应的所有getter方法*/
PropertyDescriptor[] getters = ReflectUtils.getGetters();
```

### ResourcePatternUtils
用于判断给定 URL 是否为可通过 ResourcePatternResolver 加载的资源位置的实用工具类。

如下示例：
```java
String resourceLocation = "classpath:com/pack.properties";
boolean isUrl = ResourcePatternUtils.isUrl(resourceLocation) ;
System.err.println(isUrl) ;
resourceLocation = "com/pack.properties";
isUrl = ResourcePatternUtils.isUrl(resourceLocation) ;
System.err.println(isUrl) ;
resourceLocation = "file:///d:/pack.properties";
isUrl = ResourcePatternUtils.isUrl(resourceLocation) ;
System.err.println(isUrl) ; 
resourceLocation = "http://www.pack.com/pack.properties";
isUrl = ResourcePatternUtils.isUrl(resourceLocation) ;
System.err.println(isUrl) ;
```

输出结果：
```
true
false
true
true
```

### DigestUtils
用于计算摘要（哈希值）。

如下示例：
```java
String hex = DigestUtils.md5DigestAsHex("测试计算哈希值".getBytes()) ;
System.err.println(hex) ;
```

### LogFormatUtils
日志格式化工具类，控制日志长度。

如下示例：
```java
/**1.输出不限制长度*/
String ret = LogFormatUtils.formatValue(new User(1L, "PackXg"), false);
System.err.println(ret);
/**2.输出限制长度*/
ret = LogFormatUtils.formatValue(new User(1L, "PackXg"), 10, true);
System.err.println(ret);
/**3.自定义日志输出*/
Log logger = LogFactory.getLog(User.class) ;
LogFormatUtils.traceDebug(logger , traceEnabled -> "测试日志工具类");
```

输出结果：
```java
User [id=1, name=PackXg]
User [id=1 (truncated)...
```

### PropertiesLoaderUtils
用于加载 java.util.Properties 的便捷工具方法，提供对输入流的标准处理。

如下示例：
```java
/**1.加载资源*/
Properties properties = PropertiesLoaderUtils.loadAllProperties("pack.properties");
System.err.println(properties);

/**2.填充资源*/
Properties prop = new Properties();
Resource resource = new ClassPathResource("pack.properties");
PropertiesLoaderUtils.fillProperties(prop, resource);
System.err.println(prop);
```

输出结果：
```
{pack.app.version=1.0.0, pack.app.title=xxxooo}
{pack.app.version=1.0.0, pack.app.title=xxxooo}
```

### AnnotatedElementUtils
用于在 AnnotatedElement（如类、方法、字段等可被注解的元素）上查找注解、元注解（meta-annotations）及重复注解（repeatable annotations）的通用工具方法。

如下示例：
```java
/**1.查找类上的@Component注解*/
Set<Component> annotations = AnnotatedElementUtils.findAllMergedAnnotations(UserDAO.class, Component.class) ;
// 输出：[@org.springframework.stereotype.Component("")]System.err.println(annotations) ; 
/**获取指定注解（@Qualifier）所有属性*/
MultiValueMap<String,Object> attributes = AnnotatedElementUtils.getAllAnnotationAttributes(UserDAO.class, Qualifier.class.getName()) ;
// 输出：{value=[user]}System.err.println(attributes) ;
```

### ClassUtils
关于 java.lang.Class 的杂项实用工具方法集合。

如下示例：
```java
/**1.加载类*/
Class<?> clazz = ClassUtils.forName("com.pack.utils.zdomain.User", ClassUtilsTest.class.getClassLoader());
System.err.println(clazz);

/**2.获取方法Method对象*/
Method method = ClassUtils.getMethod(clazz, "getId");
System.err.println(method);

/**3.获取对象的实现的所有接口*/
Class<?>[] interfaces = ClassUtils.getAllInterfaces(new UserDAO());
System.err.println(Arrays.toString(interfaces));
```

### OrderUtils
用于根据对象类型声明确定其执行顺序的通用工具类，支持 Spring 的 @Order 注解和 Jakarta EE 的 @Priority 注解。

如下示例：
```java
/**1.获取类上的注解@Order配置的值*/
Integer order = OrderUtils.getOrder(UserDAO.class);
System.err.println(order);
/**2.获取方法上@Order的值*/
order = OrderUtils.getOrder(AppConfig.class.getMethod("userDAO"));
System.err.println(order);
```

### FileCopyUtils
用于文件和流复制的简单工具方法集合。所有复制方法均采用 4096 字节的块大小，并在操作完成后自动关闭所有受影响的流。

如下示例：
```java
byte[] data = "测试文件复制类".getBytes(StandardCharsets.UTF_8);
/**1.将数据写入文件*/
FileCopyUtils.copy(data, new File("f:\\1.txt"));
/**2.将数据写入到字节流*/
ByteArrayOutputStream baos = new ByteArrayOutputStream();
FileCopyUtils.copy(data, baos) ;
/**3.读取文件内容*/
byte[] array = FileCopyUtils.copyToByteArray(new File("f:\\1.txt"));
System.err.println(new String(array, StandardCharsets.UTF_8));
```

### FileSystemUtils
用于操作文件系统的实用工具方法集合。

如下示例：
```java
File src = null ;
File dest = null ;
/**1.递归复制文件*/
FileSystemUtils.copyRecursively(src , dest) ;
/**2.删除指定的文件——若目标为目录，则递归删除其包含的所有嵌套目录和文件。*/
FileSystemUtils.deleteRecursively(src) ;
```

### MimeTypeUtils
关于 MIME 类型（媒体类型）的杂项实用工具方法集合。

如下示例：
```java
/**1.将字符串解析为MimeType类型*/
MimeType mimeType = MimeTypeUtils.parseMimeType("application/json");
System.err.println(mimeType) ;
```

### NumberUtils
关于数字转换与解析的杂项实用工具方法集合。

如下示例：
```java
/**1.字符串解析为指定的类型*/
Double number = NumberUtils.parseNumber("20", Double.class);
System.err.println(number) ;
/**2.从一种类型转换为指定的类型*/
Number n = 20;
Integer ret = NumberUtils.convertNumberToTargetClass(n, Integer.class);
System.err.println(ret) ;
```

### StreamUtils
用于处理流（Stream）的简单工具方法集合。本类中的复制方法与 FileCopyUtils 中的类似，但区别在于所有受影响的流在操作完成后不会自动关闭（保持打开状态）。所有复制方法均采用 8192 字节（8KB）的块大小进行数据传输。

如下示例：
```java
InputStream in = ... ;
OutputStream out = ... ;
/**1.从输入流复制到输出流*/
StreamUtils.copy(in, out) ;
/**2.将输入流复制到byte数组*/
StreamUtils.copyToByteArray(in) ;
```

### StringUtils
字符串操作工具合集。

如下示例：
```java
String s = "";
/**1.判断字符串是否为空*/
StringUtils.hasLength(s);

/**2. 判断字符串是否存在空白字符;是否有空白字符则是通过Character.isWhitespace判断*/
StringUtils.containsWhitespace(s);

/**3.将集合转换为字符串数组*/
StringUtils.toStringArray(List.of("a", "b","c"));
```