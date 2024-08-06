package cn.wubo.multi.thread.demo01;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * CompletableFuture
 * jdk1.8
 */
public class Demo0107 {

    /**
     * 主函数：创建一个工作窃取池来执行一系列异步任务。
     * 任务是随机生成的延迟后打印当前线程名，并返回延迟时间。
     * 程序会等待所有任务完成后再退出。
     *
     * @param args 命令行参数（未使用）
     * @throws InterruptedException 如果执行过程中的线程被中断
     */
    public static void main(String[] args) throws InterruptedException {
        // 创建一个工作窃取池来执行任务
        ExecutorService threadPool = Executors.newWorkStealingPool();

        // 使用IntStream生成15个随机数，每个随机数代表一个任务的延迟时间
        // 将这些任务封装成CompletableFuture，并收集到一个列表中
        List<CompletableFuture<String>> list = IntStream
                .range(0, 15)
                .mapToObj(i -> (int) (Math.random() * 100))
                .map(l -> CompletableFuture.supplyAsync(() -> {
                            // 等待一会，模拟任务执行
                            try {
                                Thread.sleep(l);
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            }
                            System.out.println(Thread.currentThread().getName());
                            return l;
                        }, threadPool)
                        .thenApply(Object::toString)) // 将任务结果转换为字符串
                .collect(Collectors.toList());

        // 等待所有任务完成
        while (list.stream().filter(e -> !e.isDone()).findAny().isPresent()) {
            Thread.sleep(100); // 每100ms检查一次
        }

        // 打印所有任务的结果
        list.forEach(cf -> {
            try {
                System.out.println(cf.get()); // 获取并打印结果
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            } catch (ExecutionException e) {
                throw new RuntimeException(e);
            }
        });
    }

}
