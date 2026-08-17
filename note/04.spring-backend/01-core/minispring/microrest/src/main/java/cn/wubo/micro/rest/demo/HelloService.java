package cn.wubo.micro.rest.demo;

import cn.wubo.micro.rest.core.annotation.Service;

@Service(value = "hello_service")
public class HelloService {

    public String hello(String name){
        return String.format("Hello %s!",name);
    }

    public String hello1(String name,String name1){
        return String.format("Hello %s and %s!",name,name1);
    }
}
