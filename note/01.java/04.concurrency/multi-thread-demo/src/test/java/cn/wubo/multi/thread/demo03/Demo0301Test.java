package cn.wubo.multi.thread.demo03;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.stream.IntStream;

@SpringBootTest
class Demo0301Test {

    @Autowired
    Demo0301 demo0301;

    @Test
    public void testDoThing(){
        IntStream.range(0, 15).forEach(i -> demo0301.doThing("name" + i));

        try {
            Thread.sleep(1500);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testDoThingThenReturn(){
        List<Future> futures = new ArrayList<>();
        IntStream.range(0, 15).forEach(i -> futures.add(demo0301.doThingThenReturn("name" + i)));

        while (true){
            if(futures.stream().allMatch(Future::isDone))
                break;
        }

        futures.forEach(future -> {
            try {
                System.out.println("线程名:" + future.get());
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            } catch (ExecutionException e) {
                throw new RuntimeException(e);
            }
        });
    }

}