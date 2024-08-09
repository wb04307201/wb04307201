package cn.wubo.multi.thread.demo01;

public class Demo0101Runnable implements Runnable{

    /**
     * 该方法是线程的运行方法。
     * 无参数。
     * 无返回值。
     */
    @Override
    public void run() {
        // 暂停一段时间，模拟线程执行的延迟
        try {
            Thread.sleep((int) (Math.random() * 100)); // 随机休眠时间，范围在0到100毫秒之间
        } catch (InterruptedException e) {
            e.printStackTrace(); // 中断异常处理
        }
        System.out.println(Thread.currentThread().getName()); // 打印当前线程的名称
    }
}
