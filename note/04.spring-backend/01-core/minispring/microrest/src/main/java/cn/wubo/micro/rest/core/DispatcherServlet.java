package cn.wubo.micro.rest.core;

import cn.wubo.micro.rest.core.handler.HandlerMapping;
import cn.wubo.micro.rest.core.util.CommonUtils;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.util.Map;

import static cn.wubo.micro.rest.core.handler.CoreMapping.handlerMappingMap;

@WebServlet(
        name = "dispatcherServlet",
        value = "/*"
)
public class DispatcherServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        this.doPost(request, response);
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        try {
            this.doDispatch(request, response);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

        /**
     * 执行请求分发处理
     *
     * @param request  HTTP请求对象
     * @param response HTTP响应对象
     * @throws Exception 处理过程中可能抛出的异常
     */
    private void doDispatch(HttpServletRequest request, HttpServletResponse response) throws Exception {
        String requestUrl = CommonUtils.formatUrl(request.getRequestURI());
        HandlerMapping handlerMapping = handlerMappingMap.get(requestUrl);
        if (null == handlerMapping) {
            response.getWriter().write("404 Not Found");
            return;
        }

        // 获取方法中的参数类型
        Class<?>[] paramTypeArr = handlerMapping.getMethod().getParameterTypes();
        Object[] paramArr = new Object[paramTypeArr.length];

        // 根据参数类型填充参数值
        for (int i = 0; i < paramTypeArr.length; i++) {
            Class<?> clazz = paramTypeArr[i];
            // 参数只考虑三种类型，其他不考虑
            if (clazz == HttpServletRequest.class) {
                paramArr[i] = request;
            } else if (clazz == HttpServletResponse.class) {
                paramArr[i] = response;
            } else if (clazz == String.class) {
                Map<Integer, String> methodParam = handlerMapping.getMethodParams();
                paramArr[i] = request.getParameter(methodParam.get(i));
            } else {
                // TODO 暂不支持的参数类型
            }
        }

        // 反射调用controller方法
        handlerMapping.getMethod().invoke(handlerMapping.getTarget(), paramArr);
    }

}
