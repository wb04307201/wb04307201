package cn.wubo.multi.thread.demo01;

/**
 * 死锁
 * 什么是死锁：不同的线程分别占用对方需要的同步资源不放弃，都在等待对方放弃自己需要的同步资源，形成了线程的死锁。
 * 死锁的表现：出现死锁后不会出现异常，不会出现提示，只是所有的线程都处于阻塞状态，无法继续。
 */
public class Demo0106 {

    /**
     * 主函数，演示了通过两个线程对共享资源进行操作时可能出现的死锁问题。
     * 两个线程分别尝试以不同的顺序锁定两个对象，从而可能导致死锁。
     *
     * @param args 命令行参数（未使用）
     */
    public static void main(String[] args) {

        StringBuffer s1 = new StringBuffer();
        StringBuffer s2 = new StringBuffer();

        // 创建并启动第一个线程，该线程尝试先锁定s1，然后锁定s2
        Thread thread1 = new Thread(() -> {
            synchronized (s1) {
                // 尝试添加字符并打印当前状态
                s1.append("a");
                System.out.println(Thread.currentThread().getName() + " " + s1);

                // 对s2进行操作并打印当前状态
                s2.append("b");
                System.out.println(Thread.currentThread().getName() + " " + s2);

                // 暂停一段时间，增加死锁的概率
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                // 尝试锁定s2，此时可能与另一个线程争夺锁，造成死锁
                synchronized (s2) {
                    // 再次对s1和s2进行操作并打印
                    s1.append("b");
                    System.out.println(Thread.currentThread().getName() + " " + s1);
                    s2.append("c");
                    System.out.println(Thread.currentThread().getName() + " " + s2);
                }
            }
        }, "Thread1");

        // 创建并启动第二个线程，该线程尝试先锁定s2，然后锁定s1
        Thread thread2 = new Thread(() -> {
            synchronized (s2) {
                // 类似于线程1的操作，但顺序相反
                s1.append("a");
                System.out.println(Thread.currentThread().getName() + " " + s1);

                s2.append("b");
                System.out.println(Thread.currentThread().getName() + " " + s2);

                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                synchronized (s1) {
                    s1.append("b");
                    System.out.println(Thread.currentThread().getName() + " " + s1);
                    s2.append("c");
                    System.out.println(Thread.currentThread().getName() + " " + s2);
                }
            }
        }, "Thread2");

        // 启动两个线程，观察死锁现象
        thread1.start();
        thread2.start();
    }

}
