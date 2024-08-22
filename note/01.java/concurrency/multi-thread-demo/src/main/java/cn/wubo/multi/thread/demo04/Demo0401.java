package cn.wubo.multi.thread.demo04;

/**
 * 阻塞队列的实现
 */
public class Demo0401 {

    /**
     * 主函数：演示基于生产者-消费者模式的阻塞队列应用。
     * 参数：args - 传入的命令行参数数组。
     * 返回值：无。
     */
    public static void main(String[] args) {
        // 创建一个阻塞队列实例
        MyBlocking queue = new MyBlocking();

        // 启动生产者线程
        Thread t = new Thread(() -> {
            int num = 0;
            while (true) {
                System.out.println("生产了：" + num);
                try {
                    // 将产品（数字）放入队列
                    queue.put(num);
                    // 为保持生产与消费步调一致，生产者暂停1秒
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                num++;
            }
        });
        t.start();

        // 启动消费者线程
        Thread t2 = new Thread(() -> {
            int num = 0;
            while (true) {
                System.out.println("消费了：" + num);
                try {
                    // 从队列中取出一个产品（数字）
                    num = queue.take();
                    // 模拟消费过程，消费者暂停1秒
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });
        t2.start();
    }

}


class MyBlocking {
    //基于数组来实现阻塞队列
    private int[] tmp = new int[1000];
    //队列长度
    private int size = 0;
    //队首元素下标
    private int start = 0;
    //队尾元素下标
    private int end = 0;
    //创建一个对象，以便后续进行锁
    private  Object locker = new Object();
    /**
     * 实现将元素入队列的操作。
     * @param val 需要入队列的值。
     * @throws InterruptedException 如果在等待过程中被中断则抛出此异常。
     */
    public void put(int val) throws InterruptedException {
        synchronized (locker) { // 使用locker对象进行同步，保证线程安全
            // 当队列已满时，当前线程等待，直至队列未满
            if (size == tmp.length) {
                locker.wait();
            }
            // 将元素加入队列尾部，并更新尾指针
            tmp[end] = val;
            end++;
            // 如果尾指针超出数组长度，则将其重置为0
            if (end >= tmp.length) {
                end = 0;
            }
            // 队列元素数量加1
            size++;
            // 唤醒可能因队列为空而等待的其他线程
            locker.notify();
        }
    }

    /**
     * 实现出队的操作。该方法会阻塞直到队列中有元素可以出队。
     *
     * @return 出队的元素值，类型为Integer。
     * @throws InterruptedException 如果在等待过程中被中断则抛出此异常。
     */
    public Integer take() throws InterruptedException {
        synchronized (locker) {
            // 队列为空时，当前线程等待，直到有元素入队
            if (size == 0) {
                locker.wait();
            }

            // 出队操作：获取并删除队首元素
            int ret = tmp[start];
            start++;

            // 当出队后start等于数组长度时，重置start为0，实现循环队列
            if (start >= tmp.length) {
                start = 0;
            }

            // 出队后，队列大小减1
            size--;

            // 通知其他等待入队的线程，队列现在有空位了
            locker.notify();

            // 返回出队的元素值
            return ret;
        }
    }

}
