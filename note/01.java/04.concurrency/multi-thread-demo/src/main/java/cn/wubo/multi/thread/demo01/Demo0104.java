package cn.wubo.multi.thread.demo01;

import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * Callable
 * 也是一个接口，功能更强大
 * 有返回值、可以抛异常、可以加泛型
 * 可以等待全部完成
 */
public class Demo0104 {

    /**
     * 主函数，演示如何使用FutureTask进行异步计算并收集结果。
     * 该函数创建并启动了多个任务，每个任务随机等待一段时间后返回等待时间。
     * 程序会等待所有任务完成后再输出每个任务的等待时间。
     *
     * @param args 命令行参数（未使用）
     */
    public static void main(String[] args) {
        // 构造10个FutureTask任务，每个任务执行一个随机时间长度的等待
        List<FutureTask> futureTasks = IntStream.range(0, 10)
                .mapToObj(i ->
                        new FutureTask(new Callable() {
                            @Override
                            public Object call() throws Exception {
                                int time = (int) (Math.random() * 100); // 随机生成等待时间
                                System.out.println(Thread.currentThread().getName() + " 等待时间 " + time);
                                Thread.sleep(time); // 等待指定时间
                                return time; // 返回等待时间
                            }
                        })
                )
                .collect(Collectors.toList());

        // 启动所有任务
        futureTasks.forEach(futureTask -> new Thread(futureTask).start());

        // 等待所有任务完成
        while (true) {
            if (futureTasks.stream().allMatch(FutureTask::isDone))
                break;
        }

        // 输出所有任务的执行结果（等待时间）
        futureTasks.forEach(futureTask -> {
            try {
                int time = (int) futureTask.get(); // 获取任务执行结果
                System.out.println("线程" + futureTasks.indexOf(futureTask) + " 等待时间" + time);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            } catch (ExecutionException e) {
                throw new RuntimeException(e);
            }
        });

    }

}
