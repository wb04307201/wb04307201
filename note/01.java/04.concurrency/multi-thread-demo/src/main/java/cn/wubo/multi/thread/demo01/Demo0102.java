package cn.wubo.multi.thread.demo01;

import java.util.stream.IntStream;

/**
 * Thread 实现了Runnable接口并进行了扩展
 */
public class Demo0102 {

    /**
     * 主函数：创建多个线程并行执行，每个线程打印当前线程的名称。
     *
     * @param args 命令行参数（未使用）
     */
    public static void main(String[] args) {
        // 生成一个从0到9的整数流，然后对每个整数执行下面的lambda表达式
        IntStream.range(0, 10).forEach(i -> new Thread(() ->{
            // 让当前线程睡眠一段时间，睡眠时间随机
            try {
                Thread.sleep((int) (Math.random() * 100)); // 线程休眠，模拟延迟
            } catch (InterruptedException e) {
                e.printStackTrace(); // 中断异常处理
            }
            // 打印当前执行线程的名称
            System.out.println(Thread.currentThread().getName());
        }).start()); // 启动新线程
    }
}
