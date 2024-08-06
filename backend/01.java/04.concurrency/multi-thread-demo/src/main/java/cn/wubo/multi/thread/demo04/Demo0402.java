package cn.wubo.multi.thread.demo04;

import java.util.concurrent.PriorityBlockingQueue;

/**
 * 实现定时器
 */
public class Demo0402 {

    /**
     * 程序的主入口函数。
     * @param args 命令行传入的参数数组，本程序未使用该参数。
     */
    public static void main(String[] args) {
        MyTimer myTimer = new MyTimer();
        // 创建一个MyTimer实例
        myTimer.schedule(() -> System.out.println("执行"),3000);
        // 计划在3秒后执行一个任务，该任务仅输出"执行"到控制台
        System.out.println("main");
        // 立即输出"main"到控制台
    }

}


//创建一个类，表示一个任务
class MyTask implements Comparable<MyTask>{ //实现Comparable接口，设定比较规则
    //任务具体要干什么
    private Runnable runnable;
    //任务具体啥时候干，保存任务要执行的毫秒级时间戳
    private long time;

    //提供一个构造方法
    public MyTask(Runnable runnable, long delay) { //delay是一个时间间隔，不是绝对的时间戳的值
        this.runnable = runnable;
        this.time = System.currentTimeMillis() + delay;
    }

    public void run(){//这里不是Runnable里面的run方法，这里只是自己定义了一个任务类，这个run指的是任务执行的方法
        runnable.run();
    }

    public long getTime() {
        return time;
    }

    @Override
    public int compareTo(MyTask o) {//这个方法的实现是在建堆的时候找最小值的比较过程中，并没有通过此处的代码进行实现
        //让时间小的在前，时间大的在后
        return (int)(this.time - o.time);
    }
}

//定时器
class MyTimer{
    private PriorityBlockingQueue<MyTask> queue = new PriorityBlockingQueue<>();
    private Object locker = new Object();

    //创建一个扫描线程
    public MyTimer(){
        Thread t = new Thread(()->{
            while (true){
                try {
                    //先取出队首元素
                    MyTask task = queue.take();
                    long curTime =  System.currentTimeMillis();
                    //判断一下时间是否到达
                    if(curTime < task.getTime()){
                        //时间没到，把任务塞回到队列中
                        queue.put(task);
                        //指定一个等待时间
                        synchronized (locker){
                            //当执行任务但没有被notify新插入任务唤醒的时候，阻塞到这里
                            locker.wait(task.getTime() - curTime);
                        }
                    }else {
                        //时间到了，执行任务
                        task.run();
                    }
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });
        t.start();
    }

    /**
     * 将指定的任务延迟指定的时间后加入到队列中进行执行。
     * @param runnable 将要执行的任务，实现了Runnable接口。
     * @param delay 任务延迟执行的时间，单位为毫秒。
     */
    public void schedule(Runnable runnable,long delay){
        // 创建一个包含任务和延迟时间的MyTask对象
        MyTask task = new MyTask(runnable,delay);
        queue.put(task);
        // 将任务成功加入队列后，通知扫描线程，以便它能检查是否有任务需要立即执行
        synchronized (locker){
            locker.notify();
        }
    }

}
