package cn.wubo.multi.thread.demo03;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;
import org.springframework.scheduling.support.CronTrigger;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ScheduledFuture;

/**
 * Spring Scheduled
 * 定时任务，动态调度
 */
@Service
public class Demo0302 {

    private List<ScheduledFuture<?>> futures = new ArrayList<>();

    @Qualifier("defaultThreadPoolTaskScheduler")
    @Resource
    private ThreadPoolTaskScheduler threadPoolTaskScheduler;

    /**
     * 启动一个定时任务。该任务会按照Cron表达式指定的间隔周期性执行。
     *
     * @param name 任务的名称，用于标识和输出日志。
     */
    public void startCron(String name) {
        // 使用线程池任务调度器安排一个任务，该任务将按照Cron表达式"0/5 * * * * ?"的规定周期性执行
        futures.add(
                threadPoolTaskScheduler.schedule(() -> {
                    // 打印当前线程名、任务名和开始时间
                    System.out.println(Thread.currentThread().getName() + " " + name + " " + LocalDateTime.now() + " start...");
                    // 模拟任务执行过程，随机睡眠一段时间
                    try {
                        Thread.sleep((int) (Math.random() * 1000));
                    } catch (InterruptedException e) {
                        // 打印异常栈信息
                        e.printStackTrace();
                    }
                    // 打印当前线程名、任务名和结束时间
                    System.out.println(Thread.currentThread().getName() + " " + name + " " + LocalDateTime.now() + " end...");
                }, new CronTrigger("0/5 * * * * ?"))
        );
    }


    /**
     * 停止定时任务
     * 该方法不接受任何参数，并且没有返回值。
     * 它通过遍历并取消所有未来执行的任务来停止定时任务。
     */
    public void stopCron() {
        // 遍历并取消所有定时任务的未来执行
        futures.forEach(future -> {
            future.cancel(true);
        });
    }

}