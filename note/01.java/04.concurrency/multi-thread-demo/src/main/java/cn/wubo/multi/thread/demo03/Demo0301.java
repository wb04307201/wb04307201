package cn.wubo.multi.thread.demo03;

import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.AsyncResult;
import org.springframework.stereotype.Service;

import java.util.concurrent.Future;

/**
 * Spring Async
 */
@Service
public class Demo0301 {

    /**
     * 使用异步方式执行某个任务。
     * 该方法将任务提交给默认的线程池执行，不返回任何结果。
     *
     * @param name 任务的名称
     */
    @Async("defaultThreadPoolExecutor")
    public void doThing(String name) {
        // 模拟任务执行前的短暂延迟
        try {
            Thread.sleep((int) (Math.random() * 100));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // 打印当前线程名称和任务名称
        System.out.println(Thread.currentThread().getName() + " " + name);
    }


    /**
     * 使用异步方式执行某个操作，然后返回一个字符串结果。
     * 这个方法会随机延迟一段时间，模拟一个耗时的操作。
     *
     * @param name 要处理的字符串参数。
     * @return 一个Future对象，包含处理的字符串名称。
     */
    @Async("defaultThreadPoolExecutor")
    public Future<String> doThingThenReturn(String name) {
        // 模拟一个随机延迟，以演示异步执行
        try {
            Thread.sleep((int) (Math.random() * 100));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // 打印当前线程名称和传入的名称，以示演示
        System.out.println(Thread.currentThread().getName() + " " + name);
        // 返回异步结果
        return new AsyncResult<>(name);
    }

}
