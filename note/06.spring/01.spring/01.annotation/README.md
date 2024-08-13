# 注解

## SpringMVC 相关注解
### @Controller
> 通常用于修饰`controller`层的组件，由控制器负责将用户发来的URL请求转发到对应的服务接口，通常还需要配合注解`@RequestMapping`使用。
### @RequestMapping
> 提供路由信息，负责`URL`到`Controller`中具体函数的映射，当用于方法上时，可以指定请求协议，比如`GET`、`POST`、`PUT`、`DELETE`等等。
### @RequestBody
> 表示请求体的`Content-Type`必须为`application/json`格式的数据，接收到数据之后会自动将数据绑定到`Java`对象上去
### @ResponseBody
> 表示该方法的返回结果直接写入`HTTP response body`中，返回数据的格式为`application/json`
```java
/**
 * 登录服务
 */
@Controller
@RequestMapping("api")
public class LoginController {
    
    /**
     * 登录请求，post请求协议，请求参数数据格式为json
     * @param request
     */
    @RequestMapping(value = "login", method = RequestMethod.POST)
    @ResponseBody
    public ResponseEntity login(@RequestBody UserLoginDTO request){
        //...业务处理
        return new ResponseEntity(HttpStatus.OK);
    }
}
```
### @RestController
> 和`@Controller`一样，用于标注控制层组件，不同的地方在于：它是`@ResponseBody`和`@Controller`的合集，也就是说，在当`@RestController`用在类上时，表示当前类里面所有对外暴露的接口方法，返回数据的格式都为`application/json`
```java
@RestController
@RequestMapping("api")
public class LoginController {
    
    /**
     * 登录请求，post请求协议，请求参数数据格式为json
     * @param request
     */
    @RequestMapping(value = "login", method = RequestMethod.POST)
    public ResponseEntity login(@RequestBody UserLoginDTO request){
        //...业务处理
        return new ResponseEntity(HttpStatus.OK);
    }
}
```
### @RequestParam
> 用于接收请求参数为表单类型的数据，通常用在方法的参数前面
```java
/**
 * 登录请求，post请求协议，请求参数数据格式为表单
 */
@RequestMapping(value = "login", method = RequestMethod.POST)
@ResponseBody
public ResponseEntity login(@RequestParam(value = "userName",required = true) String userName,
                            @RequestParam(value = "userPwd",required = true) String userPwd){
    //...业务处理
    return new ResponseEntity(HttpStatus.OK);
}
```
### @PathVariable
> 用于获取请求路径中的参数，通常用于`restful`风格的`api`上
```java
/**
 * restful风格的参数请求
 * @param id
 */
@RequestMapping(value = "queryProduct/{id}", method = RequestMethod.POST)
@ResponseBody
public ResponseEntity queryProduct(@PathVariable("id") String id){
    //...业务处理
    return new ResponseEntity(HttpStatus.OK);
}
```
### @GetMapping
> 除了`@RequestMapping`可以指定请求方式之外，还有一些其他的注解，可以用于标注接口路径请求，比如`GetMapping`用在方法上时，表示只支持get请求方法，等价于`@RequestMapping(value="/get",method=RequestMethod.GET)`
```java
@GetMapping("get")
public ResponseEntity get(){
    return new ResponseEntity(HttpStatus.OK);
}
```
### @PostMapping
> 用在方法上，表示只支持`post`方式的请求。
```java
@PostMapping("post")
public ResponseEntity post(){
    return new ResponseEntity(HttpStatus.OK);
}
```
### @PutMapping
> 用在方法上，表示只支持`put`方式的请求，通常表示更新某些资源的意思
```java
@PutMapping("put")
public ResponseEntity put(){
    return new ResponseEntity(HttpStatus.OK);
}
```
### @DeleteMapping
> 用在方法上，表示只支持`delete`方式的请求，通常表示删除某些资源的意思
```java
@DeleteMapping("delete")
public ResponseEntity delete(){
    return new ResponseEntity(HttpStatus.OK);
}
```

## bean 相关注解
### @Service
> 通常用于修饰`service`层的组件，声明一个对象，会将类对象实例化并注入到`bean`容器里面
```java
@Service
public class DeptService {
    
    //具体的方法
}
```
### @Component
> 泛指组件，当组件不好归类的时候，可以使用这个注解进行标注，功能类似于于`@Service`
```java
@Component
public class DeptService {
    
    //具体的方法
}
```
### @Repository
> 通常用于修饰dao层的组件，@Repository注解属于Spring里面最先引入的一批注解，它用于将数据访问层 (DAO层 ) 的类标识为Spring Bean，具体只需将该注解标注在 DAO类上即可
```java
@Repository
public interface RoleRepository extends JpaRepository<Role,Long> {

    //具体的方法
}
```
### @Bean
> 当于 xml 中配置 Bean，意思是产生一个 bean 对象，并交给spring管理
```java

@Configuration
public class AppConfig {
    
   //相当于 xml 中配置 Bean
    @Bean
    public Uploader initFileUploader() {
        return new FileUploader();
    }

}
```
### @Autowired
> 自动导入依赖的bean对象，默认时按照byType方式导入对象，而且导入的对象必须存在，当需要导入的对象并不存在时，我们可以通过配置required = false来关闭强制验证。
```java
@Autowired
private DeptService deptService;
```
### @Resource
> 也是自动导入依赖的bean对象，由JDK提供，默认是按照byName方式导入依赖的对象；而@Autowired默认时按照byType方式导入对象，当然@Resource还可以配置成通过byType方式导入对象。
```java
/**
 * 通过名称导入（默认通过名称导入依赖对象）
 */
@Resource(name = "deptService")
private DeptService deptService;

/**
 * 通过类型导入
 */
@Resource(type = RoleRepository.class)
private DeptService deptService;
```
### @Qualifier
> 当有多个同一类型的bean时，使用@Autowired导入会报错，提示当前对象并不是唯一，Spring不知道导入哪个依赖，这个时候，我们可以使用@Qualifier进行更细粒度的控制，选择其中一个候选者，一般于@Autowired搭配使用
```java
@Autowired
@Qualifier("deptService")
private DeptService deptService;
```
### @Scope
> 用于生命一个spring bean的作用域，作用的范围一共有以下几种：
> - **`singleton`**：唯一 bean 实例，Spring 中的 bean 默认都是单例的。
> - **`prototype`**：每次请求都会创建一个新的 bean 实例，对象多例。
> - **`request`**：每一次 HTTP 请求都会产生一个新的 bean，该 bean 仅在当前 HTTP request 内有效。
> - **`session`**：每一次 HTTP 请求都会产生一个新的 bean，该 bean 仅在当前 HTTP session 内有效。
```java
/**
 * 单例对象
 */
@RestController
@Scope("singleton")
public class HelloController {

}
```

## JPA 相关注解
### @Entity和@Table
> 表明这是一个实体类，这两个注解一般一块使用，但是如果表名和实体类名相同的话，@Table可以省略。
### @Id
> 表示该属性字段对应数据库表中的主键字段。
### @Column
> 表示该属性字段对应的数据库表中的列名，如果字段名与列名相同，则可以省略。
### @GeneratedValue
> 表示主键的生成策略，有四个选项，分别如下：
> - **`AUTO`**：表示由程序控制，是默认选项 ，不设置就是这个
> - **`IDENTITY`**：表示由数据库生成，采用数据库自增长，Oracle 不支持这种方式
> - **`SEQUENCE`**：表示通过数据库的序列生成主键ID，MYSQL 不支持
> - **`Table`**：表示由特定的数据库产生主键，该方式有利于数据库的移植
### @SequenceGeneretor
> 用来定义一个生成主键的序列，它需要与@GeneratedValue联合使用才有效，以TB_ROLE表为例，对应的注解配置如下：
```java
@Entity
@Table(name = "TB_ROLE")
@SequenceGenerator(name = "id_seq", sequenceName = "seq_repair",allocationSize = 1)
public class Role implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID，采用【id_seq】序列函数自增长
     */
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE,generator = "id_seq")
    private Long id;


    /* 角色名称
     */
    @Column(nullable = false)
    private String roleName;

    /**
     * 角色类型
     */
    @Column(nullable = false)
    private String roleType;
}
```
### @Transient
> 表示该属性并非与数据库表的字段进行映射，ORM 框架会将忽略该属性。
```java
/**
 * 忽略该属性
 */
@Column(nullable = false)
@Transient
private String lastTime;
```
### @Basic(fetch=FetchType.LAZY)
> 用在某些属性上，可以实现懒加载的效果，也就是当用到这个字段的时候，才会装载这个属性，如果配置成fetch=FetchType.EAGER，表示即时加载，也是默认的加载方式！
```java
/**
 * 延迟加载该属性
 */
@Column(nullable = false)
@Basic(fetch = FetchType.LAZY)
private String roleType;
```
### @JoinColumn
> 用于标注表与表之间关系的字段，通常与@OneToOne、@OneToMany搭配使用
```java
@Entity
@Table(name = "tb_login_log")
public class LoginLog implements Serializable {
    
    /**
     * 查询登录的用户信息
     */
    @OneToOne
    @JoinColumn(name = "user_id")
    private User user;
    
    //...get、set
}
```
### @OneToOne、@OneToMany和@ManyToOne
> 这三个注解，相当于hibernate配置文件中的一对一，一对多，多对一配置，比如下面的客户地址表，通过客户 ID，实现客户信息的查询。
```java
@Entity
@Table(name="address")
public class AddressEO implements java.io.Serializable {
    
  @ManyToOne(cascade = { CascadeType.ALL })
  @JoinColumn(name="customer_id")
  private CustomerEO customer;
    
  //...get、set
}
```

## 配置相关注解
### @Configuration
> 表示声明一个 Java 形式的配置类，Spring Boot 提倡基于 Java 的配置，相当于你之前在 xml 中配置 bean，比如声明一个配置类AppConfig，然后初始化一个Uploader对象。
```java
@Configuration
public class AppConfig {

    @Bean
    public Uploader initOSSUploader() {
        return new OSSUploader();
    }

}
```
### @EnableAutoConfiguration
> @EnableAutoConfiguration可以帮助SpringBoot应用将所有符合条件的@Configuration配置类，全部都加载到当前SpringBoot里，并创建对应配置类的Bean，并把该Bean实体交给IoC容器进行管理。  
> 某些场景下，如果我们想要避开某些配置类的扫描（包括避开一些第三方jar包下面的配置，可以这样处理。
```java
@Configuration
@EnableAutoConfiguration(exclude = { org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class
})
public class AppConfig {

    //具有业务方法
}
```
### @ComponentScan
> 标注哪些路径下的类需要被Spring扫描，用于自动发现和装配一些Bean对象，默认配置是扫描当前文件夹下和子目录下的所有类，如果我们想指定扫描某些包路径，可以这样处理。
```java
@ComponentScan(basePackages = {"com.xxx.a", "com.xxx.b", "com.xxx.c"})
```
### @SpringBootApplication
> 等价于使用@Configuration、@EnableAutoConfiguration、@ComponentScan这三个注解，通常用于全局启动类上
```java

@SpringBootApplication
public class PropertyApplication {

    public static void main(String[] args) {
        SpringApplication.run(PropertyApplication.class, args);
    }
}
```
> 把@SpringBootApplication换成@Configuration、@EnableAutoConfiguration、@ComponentScan这三个注解，一样可以启动成功，@SpringBootApplication只是将这三个注解进行了简化！
### @EnableTransactionManagement
> 表示开启事务支持，等同于 xml 配置方式的<tx:annotation-driven />
```java
@SpringBootApplication
@EnableTransactionManagement`
public class PropertyApplication {

    public static void main(String[] args) {
        SpringApplication.run(PropertyApplication.class, args);
    }
}
```
### @Conditional
> 从 Spring4 开始，可以通过@Conditional注解实现按条件装载bean对象，目前 Spring Boot 源码中大量扩展了@Condition注解，用于实现智能的自动化配置，满足各种使用场景。下面我给大家列举几个常用的注解：
> - **`@ConditionalOnBean`**：当某个特定的Bean存在时，配置生效
> - **`@ConditionalOnMissingBean`**：当某个特定的Bean不存在时，配置生效
> - **`@ConditionalOnClass`**：当Classpath里存在指定的类，配置生效
> - **`@ConditionalOnMissingClass`**：当Classpath里不存在指定的类，配置生效
> - **`@ConditionalOnExpression`**：当给定的SpEL表达式计算结果为true，配置生效
> - **`@ConditionalOnProperty`**：当指定的配置属性有一个明确的值并匹配，配置生效
```java
@Configuration
public class ConditionalConfig {


    /**
     * 当AppConfig对象存在时，创建一个A对象
     * @return
     */
    @ConditionalOnBean(AppConfig.class)
    @Bean
    public A createA(){
        return new A();
    }

    /**
     * 当AppConfig对象不存在时，创建一个B对象
     * @return
     */
    @ConditionalOnMissingBean(AppConfig.class)
    @Bean
    public B createB(){
        return new B();
    }


    /**
     * 当KafkaTemplate类存在时，创建一个C对象
     * @return
     */
    @ConditionalOnClass(KafkaTemplate.class)
    @Bean
    public C createC(){
        return new C();
    }

    /**
     * 当KafkaTemplate类不存在时，创建一个D对象
     * @return
     */
    @ConditionalOnMissingClass(KafkaTemplate.class)
    @Bean
    public D createD(){
        return new D();
    }


    /**
     * 当enableConfig的配置为true，创建一个E对象
     * @return
     */
    @ConditionalOnExpression("${enableConfig:false}")
    @Bean
    public E createE(){
        return new E();
    }


    /**
     * 当filter.loginFilter的配置为true，创建一个F对象
     * @return
     */
    @ConditionalOnProperty(prefix = "filter",name = "loginFilter",havingValue = "true")
    @Bean
    public F createF(){
        return new F();
    }
}
```
### @value
> 可以在任意 Spring 管理的 Bean 中通过这个注解获取任何来源配置的属性值，比如你在application.properties文件里，定义了一个参数变量！
```properties
config.name=zhangsan
```
> 在任意的bean容器里面，可以通过@Value注解注入参数，获取参数变量值。
```java
@RestController
public class HelloController {

    @Value("${config.name}")
    private String config;

    @GetMapping("config")
    public String config(){
        return JSON.toJSONString(config);
    }
}
```
### @ConfigurationProperties
> 上面@Value在每个类中获取属性配置值的做法，其实是不推荐的。  
> 一般在企业项目开发中，不会使用那么杂乱无章的写法而且维护也麻烦，通常会一次性读取一个 Java 配置类，然后在需要使用的地方直接引用这个类就可以多次访问了，方便维护，示例如下：  
> 首先，在application.properties文件里定义好参数变量。
```properties
config.name=demo_1
config.value=demo_value_1
```
> 然后，创建一个 Java 配置类，将参数变量注入即可！
```java
@Component
@ConfigurationProperties(prefix = "config")
public class Config {

    public String name;

    public String value;

    //...get、set
}
```
> 最后，在需要使用的地方，通过ioc注入Config对象即可！
### @PropertySource
> 这个注解是用来读取我们自定义的配置文件的，比如导入test.properties和bussiness.properties两个配置文件
```java
@SpringBootApplication
@PropertySource(value = {"test.properties","bussiness.properties"})
public class PropertyApplication {

    public static void main(String[] args) {
        SpringApplication.run(PropertyApplication.class, args);
    }
}
```
### @ImportResource
> 用来加载 xml 配置文件，比如导入自定义的aaa.xml文件
```java
@ImportResource(locations = "classpath:aaa.xml")
@SpringBootApplication
public class PropertyApplication {

    public static void main(String[] args) {
        SpringApplication.run(PropertyApplication.class, args);
    }
}
```

## 异常处理相关注解
### @ControllerAdvice和@ExceptionHandler
> 通常组合使用，用于处理全局异常
```java
@ControllerAdvice
@Configuration
@Slf4j
public class GlobalExceptionConfig {
    
    private static final Integer GLOBAL_ERROR_CODE = 500;
    
    @ExceptionHandler(value = Exception.class)
    @ResponseBody
    public void exceptionHandler(HttpServletRequest request, HttpServletResponse response, Exception e) throws Exception {
        log.error("【统一异常处理器】", e);
        ResultMsg<Object> resultMsg = new ResultMsg<>();
        resultMsg.setCode(GLOBAL_ERROR_CODE);
        if (e instanceof CommonException) {
            CommonException ex = (CommonException) e;
            if(ex.getErrCode() != 0) {
                resultMsg.setCode(ex.getErrCode());
            }
            resultMsg.setMsg(ex.getErrMsg());
        }else {
            resultMsg.setMsg(CommonErrorMsg.SYSTEM_ERROR.getMessage());
        }
        WebUtil.buildPrintWriter(response, resultMsg);
    }
}
```

## 测试相关注解
### @ActiveProfiles
> 一般作用于测试类上， 用于声明生效的 Spring 配置文件，比如指定application-dev.properties配置文件。
### @RunWith和@SpringBootTest
> 一般作用于测试类上， 用于单元测试用
```java
@ActiveProfiles("dev")
@RunWith(SpringRunner.class)
@SpringBootTest
public class TestJunit {

    @Test
    public void executeTask() {
        //测试...
    }
}
```