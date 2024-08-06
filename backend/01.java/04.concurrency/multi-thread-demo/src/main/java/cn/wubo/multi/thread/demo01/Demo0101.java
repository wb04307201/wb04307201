package cn.wubo.multi.thread.demo01;

import java.util.stream.IntStream;

/**
 * Runnable 一个接口
 */
public class Demo0101 {

    /**
     * 程序的主入口函数。
     *
     * @param args 命令行传入的参数数组，本程序中未使用。
     */
    public static void main(String[] args) {
        // 使用IntStream的range方法生成0到9的整数流，然后对每个整数启动一个新线程并执行Demo0101Runnable任务
        IntStream.range(0, 10).forEach(i -> new Thread(new Demo0101Runnable()).start());
    }
}
