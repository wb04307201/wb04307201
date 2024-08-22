package cn.wubo.multi.thread.demo01;

import java.util.Timer;
import java.util.TimerTask;
import java.util.stream.IntStream;

/**
 * TimerTask 定时任务
 */
public class Demo0103 {

    /**
     * 主函数：创建多个定时任务，每个任务随机延迟后执行，并输出当前线程名称。
     * @param args 命令行参数（未使用）
     */
    public static void main(String[] args) {
        // 生成0到9的整数流，对每个整数执行以下操作
        IntStream.range(0, 10).forEach(i -> {
            Timer timer = new Timer();
            // 定义一个定时任务
            timer.schedule(new TimerTask() {
                @Override
                public void run() {
                    // 让当前线程随机睡眠一段时间
                    try {
                        Thread.sleep((int) (Math.random() * 100));
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    // 打印当前执行任务的线程名称
                    System.out.println(Thread.currentThread().getName());
                }
            }, 0); // 设定任务立即开始
        });
    }
}
