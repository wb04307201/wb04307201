package cn.wubo.multi.thread.demo02;

import java.util.stream.IntStream;

/**
 * 同步锁
 * 保证在同一时刻， 被修饰的代码块或方法只会有一个线程执行，以达到保证并发安全的效果。
 * synchronized的作用主要有三个：
 * 原子性：确保线程互斥地访问同步代码；
 * 可见性：保证共享变量的修改能够及时可见，其实是通过Java内存模型中的“对一个变量unlock操作之前，必须要同步到主内存中；如果对一个变量进行lock操作，则将会清空工作内存中此变量的值，在执行引擎使用此变量前，需要重新从主内存中load操作或assign操作初始化变量值” 来保证的；
 * 有序性：有效解决重排序问题，即 “一个unlock操作先行发生(happen-before)于后面对同一个锁的lock操作”；
 * synchronized的3种使用方式：
 * 修饰实例方法：作用于当前实例加锁
 * 修饰静态方法：作用于当前类对象加锁
 * 修饰代码块：指定加锁对象，对给定对象加锁
 */
public class Demo0201 {
    //定义总张数
    public static int tickets = 10;

    /**
     * 程序的主入口函数。
     *
     * @param args 命令行传入的参数数组，本程序中未使用。
     */
    public static void main(String[] args) {
        // 使用IntStream的range方法生成0到14的整数流，然后对每个整数启动一个新线程执行ticket方法
        IntStream.range(0, 15).forEach(i -> new Thread(Demo0201::ticket).start());
    }

    /**
     * 模拟售票操作。该方法为静态同步方法，用于模拟多个线程同时出售车票的过程。
     * 无参数。
     * 无返回值。
     */
    public static synchronized void ticket() {
        // 模拟线程等待，模拟不同线程到达售票窗口的时间差
        try {
            Thread.sleep((int) (Math.random() * 100));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // 检查剩余车票是否大于0，若大于0则进行售票操作
        if (Demo0201.tickets > 0) {
            System.out.println(Thread.currentThread().getName() + "卖出第" + Demo0201.tickets + "张车票");
            Demo0201.tickets--; // 出售车票
            // 模拟售票过程，增加真实感
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        } else {
            // 当无票时，输出提示信息
            System.out.println(Thread.currentThread().getName() + "无票");
        }
    }

}