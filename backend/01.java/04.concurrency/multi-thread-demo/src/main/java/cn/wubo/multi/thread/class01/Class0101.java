package cn.wubo.multi.thread.class01;

import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.AsyncResult;
import org.springframework.stereotype.Service;

import java.util.concurrent.Future;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 课堂练习额
 * Spring async + Lock实现抢票
 * 三个黄牛（张三，李四，王二麻子）抢10张车票
 * 等待所有结果一起返回
 * 并打印谁抢到第几张票
 */
@Service
public class Class0101 {

    public static int tickets = 10;
    public static Lock lock = new ReentrantLock();

    @Async("defaultThreadPoolExecutor")
    public Future<String> ticket(String name) {
        String msg = "";
        try {
            Thread.sleep((int) (Math.random() * 100));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        //判断车票是否大于0
        try {
            //加锁
            Class0101.lock.lock();
            if (Class0101.tickets > 0) {
                msg = String.format("黄牛 %s 买到第 %s 张票", name, Class0101.tickets);
                Class0101.tickets--;
                //模仿出票
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            } else {
                msg = String.format("黄牛 %s 未抢到票", name);
            }
        } finally {
            //释放锁
            Class0101.lock.unlock();
        }
        return new AsyncResult<>(msg);
    }
}
