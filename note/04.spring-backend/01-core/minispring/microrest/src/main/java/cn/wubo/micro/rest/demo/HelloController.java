package cn.wubo.micro.rest.demo;

import cn.wubo.micro.rest.core.annotation.Autowired;
import cn.wubo.micro.rest.core.annotation.GetMapping;
import cn.wubo.micro.rest.core.annotation.RequestParam;
import cn.wubo.micro.rest.core.annotation.RestController;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;

@RestController
public class HelloController {

    @Autowired
    private HelloService helloService;

    @GetMapping("/hello")
    public void hello(HttpServletRequest request, HttpServletResponse response, @RequestParam("name") String name) throws IOException {
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().write(helloService.hello(name));
    }

    @GetMapping("/hello1")
    public void hello1(HttpServletRequest request, HttpServletResponse response, @RequestParam("name") String name, @RequestParam("name1") String name1) throws IOException {
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().write(helloService.hello1(name, name1));
    }
}
