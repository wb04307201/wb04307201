package cn.wubo.multi.thread.class01;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.stream.IntStream;

@SpringBootTest
class Class0101Test {

    @Autowired
    Class0101 class0101;


    @Test
    public void ticket(){
        List<String> names = Arrays.asList("张三","李四","王二麻子");
        List<Future> futures = new ArrayList<>();

        IntStream.range(0, 30).forEach(i -> {
            futures.add(class0101.ticket(names.get((int)(Math.random() * 3))));
        });

        while (true){
            if(futures.stream().allMatch(Future::isDone))
                break;
        }

        futures.forEach(future -> {
            try {
                System.out.println(future.get());
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            } catch (ExecutionException e) {
                throw new RuntimeException(e);
            }
        });
    }
}