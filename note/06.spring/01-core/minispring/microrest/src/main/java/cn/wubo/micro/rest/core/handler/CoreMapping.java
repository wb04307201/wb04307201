package cn.wubo.micro.rest.core.handler;

import cn.wubo.micro.rest.core.DefaultConfig;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CoreMapping {

    private CoreMapping() {
    }

    public static DefaultConfig defaultConfig = new DefaultConfig();
    public static List<String> classNameList = new ArrayList<>();
    public static Map<String, Object> iocContainerMap = new HashMap<>();
    public static Map<String, HandlerMapping> handlerMappingMap = new HashMap<>();
}
