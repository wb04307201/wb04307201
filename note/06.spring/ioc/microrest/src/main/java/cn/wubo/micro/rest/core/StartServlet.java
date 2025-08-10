package cn.wubo.micro.rest.core;

import cn.wubo.micro.rest.core.annotation.*;
import cn.wubo.micro.rest.core.handler.HandlerMapping;
import cn.wubo.micro.rest.core.util.CommonUtils;
import jakarta.servlet.ServletConfig;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.lang.annotation.Annotation;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.*;

import static cn.wubo.micro.rest.core.handler.CoreMapping.*;

@Slf4j
public class StartServlet extends HttpServlet {

    @Override
    public void init(ServletConfig config) throws ServletException {
        log.info("StartServlet Init Start...");

        //1.加载配置文件
        doLoadConfig(config.getInitParameter("defaultConfig"));

        //2.根据获取到的扫描路径进行扫描
        doScanPacakge(defaultConfig.getScanBasePackages());

        //3.将扫描到的类进行初始化，并存放到IOC容器
        doInitializedClass();

        //4.依赖注入
        doDependencyInjection();

        super.init(config);
        log.info("StartServlet Init End...");
    }

    /**
     * 执行依赖注入和处理器映射的初始化操作。
     * <p>
     * 该方法主要完成以下两部分功能：
     * 1. 遍历 IOC 容器中的所有 Bean，对带有 {@link Autowired} 注解的字段进行依赖注入；
     * 2. 扫描带有 {@link RestController} 注解的类及其带有 {@link GetMapping} 注解的方法，
     *    构建请求路径与处理器方法之间的映射关系，并存入 {@code handlerMappingMap} 中。
     * </p>
     */
    private void doDependencyInjection() {
        // 循环IOC容器中的类
        iocContainerMap.forEach((key, value) -> {
            Class<?> clazz = value.getClass();
            Field[] fields = clazz.getDeclaredFields();

            // 属性注入：处理带有 @Autowired 注解的字段
            Arrays.stream(fields).forEach(field -> {
                // 如果属性有 Autowired 注解则注入值（暂时不考虑其他注解）
                if (field.isAnnotationPresent(Autowired.class)) {
                    String beanName = CommonUtils.toLowerFirstLetterCase(field.getType().getSimpleName());//默认bean的value为类名首字母小写
                    if (field.getType().isAnnotationPresent(Service.class)) {
                        Service service = field.getType().getAnnotation(Service.class);
                        beanName = service.value();
                    }
                    field.setAccessible(true);
                    try {
                        Object target = iocContainerMap.get(beanName);
                        if (null == target) {
                            log.error("{} required bean:{},but we not found it", clazz.getName(), beanName);
                        }
                        field.set(value, iocContainerMap.get(beanName));//初始化对象，后面注入
                    } catch (IllegalAccessException e) {
                        log.error("注入失败", e);
                    }
                }
            });

            // 初始化 HandlerMapping：构建请求路径与方法的映射关系
            String baseRequestUrl = "";
            // 获取 Controller 类上的请求路径
            if (clazz.isAnnotationPresent(RestController.class)) {
                baseRequestUrl = clazz.getAnnotation(RestController.class).value();
            }

            // 循环类中的方法，获取方法上的路径
            Method[] methods = clazz.getMethods();
            for (Method method : methods) {
                // 假设只有 GetMapping 这一种注解
                if (!method.isAnnotationPresent(GetMapping.class)) {
                    continue;
                }
                GetMapping wolfGetMapping = method.getDeclaredAnnotation(GetMapping.class);
                String requestUrl = baseRequestUrl + wolfGetMapping.value();// 拼成完整的请求路径

                // 不考虑正则匹配路径/xx/* 的情况，只考虑完全匹配的情况
                if (handlerMappingMap.containsKey(requestUrl)) {
                    log.debug("重复路径 {}", requestUrl);
                    continue;
                }

                Annotation[][] annotationArr = method.getParameterAnnotations();// 获取方法中参数的注解
                Map<Integer, String> methodParam = new HashMap<>();// 存储参数的顺序和参数名
                for (int i = 0; i < annotationArr.length; i++) {
                    for (Annotation annotation : annotationArr[i]) {
                        if (annotation instanceof RequestParam) {
                            RequestParam wolfRequestParam = (RequestParam) annotation;
                            methodParam.put(i, wolfRequestParam.value());// 存储参数的位置和注解中定义的参数名
                            break;
                        }
                    }
                }

                requestUrl = CommonUtils.formatUrl(requestUrl);// 主要是防止路径多了/导致路径匹配不上
                HandlerMapping handlerMapping = new HandlerMapping();
                handlerMapping.setRequestUrl(requestUrl);// 请求路径
                handlerMapping.setMethod(method);// 请求方法
                handlerMapping.setTarget(value);// 请求方法所在controller对象
                handlerMapping.setMethodParams(methodParam);// 请求方法的参数信息
                handlerMappingMap.put(requestUrl, handlerMapping);// 存入hashmap
            }
        });
    }



    /**
     * 初始化类，并放入容器iocContainerMap内
     * 该方法遍历类名列表，通过反射机制创建被RestController或Service注解标记的类的实例，
     * 并将这些实例存入IOC容器中，key为注解的value值或类名首字母小写的默认值
     */
    private void doInitializedClass() {
        // 遍历所有类名，初始化符合条件的类
        classNameList.forEach(className -> {
            if (StringUtils.isNotEmpty(className)) {
                try {
                    Class<?> clazz = Class.forName(className);//反射获取对象
                    // 处理RestController注解的类
                    if (clazz.isAnnotationPresent(RestController.class)) {
                        String value = (clazz.getAnnotation(RestController.class)).value();
                        //如果直接指定了value则取value，否则取首字母小写类名作为key值存储类的实例对象
                        iocContainerMap.put(StringUtils.isBlank(value) ? CommonUtils.toLowerFirstLetterCase(clazz.getSimpleName()) : value, clazz.getDeclaredConstructor().newInstance());
                    // 处理Service注解的类
                    } else if (clazz.isAnnotationPresent(Service.class)) {
                        String value = (clazz.getAnnotation(Service.class)).value();
                        iocContainerMap.put(StringUtils.isBlank(value) ? CommonUtils.toLowerFirstLetterCase(clazz.getSimpleName()) : value, clazz.getDeclaredConstructor().newInstance());
                    } else {
                        // TODO 暂不考虑其他注解的情况
                    }
                } catch (Exception e) {
                    log.error("初始化类失败，className为{}" + className, e);
                }
            }
        });
    }



    /**
     * 扫描包下所有文件获取全限定类名
     *
     * @param basePackages 基础包名，用于扫描该包及其子包下的所有类
     */
    private void doScanPacakge(String basePackages) {
        if (StringUtils.isBlank(basePackages)) {
            return;
        }
        //把包名的.替换为/
        String scanPath = String.format("/%s", basePackages.replaceAll("\\.", "/"));
        //获取到当前包所在磁盘的全路径
        Optional.ofNullable(this.getClass().getClassLoader().getResource(scanPath)//获取到当前包所在磁盘的全路径
        ).ifPresent(u -> {
            File files = new File(u.getFile());//获取当前路径下所有文件
            Optional.ofNullable(files.listFiles()).ifPresent(f -> Arrays.stream(f).forEach(file -> {
                // 递归处理文件夹或添加文件到类名列表
                if (file.isDirectory()) //如果是文件夹则递归
                    doScanPacakge(basePackages + "." + file.getName());
                else //如果是文件则添加到集合。因为上面是通过类加载器获取到的文件路径，所以实际上是class文件所在路径
                    classNameList.add(basePackages + "." + file.getName().replace(".class", ""));
            }));
        });
    }



    /**
     * 加载配置文件
     *
     * @param configPath - 配置文件所在路径
     */
    private void doLoadConfig(String configPath) {
        // 获取配置文件输入流
        InputStream inputStream = this.getClass().getClassLoader().getResourceAsStream(configPath);
        Properties properties = new Properties();
        try {
            // 加载配置文件到Properties对象
            properties.load(inputStream);
        } catch (IOException e) {
            log.error("加载配置文件失败", e);
        }

        // 遍历配置项，通过反射设置到defaultConfig对象的对应字段中
        properties.forEach((k, v) -> {
            try {
                Field field = defaultConfig.getClass().getDeclaredField((String) k);
                field.setAccessible(true);
                field.set(defaultConfig, v);
            } catch (Exception e) {
                log.error("初始化配置类失败", e);
            }
        });
    }

}
