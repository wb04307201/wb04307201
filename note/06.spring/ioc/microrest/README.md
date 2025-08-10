# 使用servlet模拟Spring IoC运行

1. 启动时通过StartServlet初始化bean，注入service
   1. 加载配置文件
   2. 根据获取到的扫描路径进行扫描
   3. 将扫描到的类进行初始化，并存放到IOC容器 
   4. 依赖注入
2. 运行时通过DispatcherServlet调用方法
   1. 获取请求路径
   2. 根据请求路径获取bean
   3. 根据参数类型填充参数值
   4. 反射调用方法

通过jetty:run启动服务

