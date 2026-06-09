package cn.wubo.micro.rest.core.util;

import org.apache.commons.lang3.StringUtils;

public class CommonUtils {

    public static String formatUrl(String requestUrl) {
        requestUrl = requestUrl.replaceAll("/+", "/");
        if (requestUrl.lastIndexOf("/") == requestUrl.length() - 1) {
            requestUrl = requestUrl.substring(0, requestUrl.length() - 1);
        }
        return requestUrl;
    }

    /**
     * 将首字母转换为小写
     *
     * @param className
     * @return
     */
    public static String toLowerFirstLetterCase(String className) {
        if (StringUtils.isBlank(className)) {
            return "";
        }
        String firstLetter = className.substring(0, 1);
        return firstLetter.toLowerCase() + className.substring(1);
    }
}
