package cn.wubo.micro.rest.core.handler;

import lombok.Data;

import java.lang.reflect.Method;
import java.util.Map;

@Data
public class HandlerMapping {
    private String requestUrl;
    private Object target;//保存方法对应的实例
    private Method method;//保存映射的方法
    private Map<Integer,String> methodParams;//记录方法参数
}
