package cn.wubo.multi.thread.demo01;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.stream.IntStream;

/**
 * 线程池
 * 1、背景：经常创建和销毁，使用量特别大的资源，比如并发情况下的线程，对性能影响很大。
 * 2、思路：提前创建好多个线程，放入线程池中，使用时直接获取，使用完放回池中，可以避免频繁创建销毁，实现重复利用。
 * 3、好处：提高响应速度(减少了创建新线程的时间)、降低资源消耗、便于线程管理
 */
public class Demo0105 {

    /**
     * 主函数：演示如何使用ExecutorService接口和ThreadPoolExecutor类来创建和管理线程池。
     * 使用线程池执行多个任务，每个任务仅打印当前线程的名称。
     *
     * @param args 命令行参数（未使用）
     */
    public static void main(String[] args) {
        // 创建一个固定大小的线程池，最多同时运行5个线程
        ExecutorService executorService = Executors.newFixedThreadPool(5);
        // 通过类型转换，获取ThreadPoolExecutor实例以进一步配置线程池
        ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) executorService;

        // 使用IntStream生成0到9的整数流，然后对每个整数执行以下操作
        IntStream.range(0, 10).forEach(i -> threadPoolExecutor.execute(() -> {
            // 模拟每个任务的短暂延迟
            try {
                Thread.sleep((int) (Math.random() * 100));
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            // 执行任务：打印当前执行任务的线程名称
            System.out.println(Thread.currentThread().getName());
        }));

        // 关闭线程池，等待所有任务完成
        threadPoolExecutor.shutdown();
    }

}
