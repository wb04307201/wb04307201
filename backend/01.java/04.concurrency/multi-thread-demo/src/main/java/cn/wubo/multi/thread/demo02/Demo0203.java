package cn.wubo.multi.thread.demo02;

import java.util.concurrent.Semaphore;
import java.util.stream.IntStream;

/**
 * 通过Semaphore信号量加锁
 * 1、Semaphore信号量作为一种流控手段，可以对特定资源的允许同时访问的操作数量进行控制，例如池化技术(连接池)中的并发数，有界阻塞容器的容量等。
 * 2、Semaphore中包含初始化时固定个数的许可，在进行操作的时候，需要先acquire获取到许可，才可以继续执行任务，如果获取失败，则进入阻塞；处理完成之后需要release释放许可。
 * 3、acquire与release之间的关系：在实现中不包含真正的许可对象，并且Semaphore也不会将许可与线程关联起来，因此在一个线程中获得的许可可以在另一个线程中释放。可以将acquire操作视为是消费一个许可，而release操作是创建一个许可，Semaphore并不受限于它在创建时的初始许可数量。也就是说acquire与release并没有强制的一对一关系，release一次就相当于新增一个许可，许可的数量可能会由于没有与acquire操作一对一而导致超出初始化时设置的许可个数。
 */
public class Demo0203 {
    //定义总张数
    public static int tickets = 10;
    private static Semaphore semaphore = new Semaphore(1);

    /**
     * 程序的主入口函数。
     *
     * @param args 命令行传入的参数数组，本程序中未使用。
     */
    public static void main(String[] args) {
        // 使用IntStream的range方法生成0到14的整数流，然后对每个整数启动一个新线程执行ticket方法
        IntStream.range(0, 15).forEach(i -> new Thread(Demo0203::ticket).start());
    }

    /**
     * 尝试出售车票的函数。
     * 该函数模拟了一个线程安全的车票售卖过程，使用了Semaphore来控制并发访问。
     * 函数没有参数和返回值。
     */
    public static void ticket() {
        // 尝试让当前线程睡眠一个随机时间，模拟不同线程间的延时
        try {
            Thread.sleep((int) (Math.random() * 100));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // 尝试获取锁，以确保对车票数量的操作是线程安全的
        try {
            // 加锁
            semaphore.acquire();
            // 判断车票是否还有剩余
            if (Demo0203.tickets > 0) {
                // 如果有票，则卖出，并模拟出票过程
                System.out.println(Thread.currentThread().getName() + "卖出第" + Demo0203.tickets + "张车票");
                Demo0203.tickets--;
                // 模仿出票操作，让当前线程睡眠100毫秒
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            } else {
                // 如果没有票，则打印无票信息
                System.out.println(Thread.currentThread().getName() + "无票");
            }
        } catch (InterruptedException e) {
            // 如果在尝试获取锁或者释放锁的过程中被中断，抛出运行时异常
            throw new RuntimeException(e);
        } finally {
            // 无论是否成功出售车票，最后都要释放锁
            semaphore.release();
        }
    }

}