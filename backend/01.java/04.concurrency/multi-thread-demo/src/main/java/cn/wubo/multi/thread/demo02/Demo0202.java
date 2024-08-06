package cn.wubo.multi.thread.demo02;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.IntStream;

/**
 * Lock锁
 * 虽然我们可以理解同步代码块和同步方法的锁对象问题，
 * 但是我们并没有直接看到在哪里上了锁，在哪里释放了锁，
 * 为了更清晰的表达如何加锁和释放锁，JDK5以后提供了一个新的锁对象Lock,
 * Lock实现提供比使用synchronized方法和语句更广泛的锁定操作
 */
public class Demo0202 {
    //定义总张数
    public static int tickets = 10;
    //定义Lock锁，要用它的实现类完成
    //true公平lock 先进先出的特点, false 不公平的lock
    public static Lock lock = new ReentrantLock();

    /**
     * 程序的主入口函数。
     *
     * @param args 命令行传入的参数数组，本程序中未使用。
     */
    public static void main(String[] args) {
        // 使用IntStream的range方法生成0到14的整数流，然后对每个整数启动一个新线程执行ticket方法
        IntStream.range(0, 15).forEach(i -> new Thread(Demo0202::ticket).start());
    }

    /**
     * 模拟售票操作。该方法尝试获取锁，如果获取成功，检查票数是否大于0，如果是，则卖出一张票并打印相关信息。
     * 如果票数小于等于0，则不进行售票操作。该方法使用了ReentrantLock进行同步控制。
     */
    public static void ticket() {
        // 尝试让线程睡眠一段时间，模拟不同线程间的随机间隔
        try {
            Thread.sleep((int) (Math.random() * 100));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // 尝试加锁，以确保并发访问时的线程安全
        try {
            Demo0202.lock.lock();
            // 检查票数是否大于0
            if (Demo0202.tickets > 0) {
                System.out.println(Thread.currentThread().getName() + "卖出第" + Demo0202.tickets + "张车票");
                Demo0202.tickets--;
                // 模拟出票过程，让线程睡眠100ms
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            } else {
                // 如果票数小于等于0，则打印无票信息
                System.out.println(Thread.currentThread().getName() + "无票");
            }
        } finally {
            // 无论是否成功售票，最后都要释放锁
            Demo0202.lock.unlock();
        }
    }

}