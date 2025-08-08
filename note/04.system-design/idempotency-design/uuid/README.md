# UUID

## UUID 简介

UUID (Universally Unique Identifier) 是一种用于标识信息的标准化方法，也称为 GUID (Globally Unique Identifier)。它是一个128位的数字，通常表示为32个十六进制数字，用连字符分为五组，形式为8-4-4-4-12。

### UUID 的特点

1. **唯一性**：在所有时间和空间上都是唯一的
2. **无序性**：生成的UUID之间没有顺序关系
3. **不可预测性**：不能从UUID推断出生成顺序或其他UUID
4. **标准化**：遵循RFC 4122标准

### UUID 的版本

UUID有多个版本，常见的有：

- **版本1**：基于时间戳和MAC地址
- **版本2**：基于时间戳、MAC地址和POSIX UID/GID（较少使用）
- **版本3**：基于命名空间和MD5哈希
- **版本4**：基于随机数
- **版本5**：基于命名空间和SHA-1哈希

## Java 中的 UUID 实现

Java标准库从Java 1.5开始提供了`java.util.UUID`类来处理UUID。

### 基本用法

```java
import java.util.UUID;

public class UUIDExample {
    public static void main(String[] args) {
        // 生成随机UUID (版本4)
        UUID uuid = UUID.randomUUID();
        System.out.println("随机UUID: " + uuid);
        
        // 从字符串解析UUID
        String uuidString = "550e8400-e29b-41d4-a716-446655440000";
        UUID parsedUuid = UUID.fromString(uuidString);
        System.out.println("解析的UUID: " + parsedUuid);
        
        // 获取UUID的各个部分
        System.out.println("版本: " + parsedUuid.version());
        System.out.println("变体: " + parsedUuid.variant());
        System.out.println("时间戳(仅版本1): " + getTimestampFromUUID(parsedUuid));
        System.out.println("Most Significant Bits: " + parsedUuid.getMostSignificantBits());
        System.out.println("Least Significant Bits: " + parsedUuid.getLeastSignificantBits());
    }
    
    // 仅适用于版本1的UUID获取时间戳
    private static long getTimestampFromUUID(UUID uuid) {
        if (uuid.version() != 1) {
            throw new UnsupportedOperationException("不是版本1的UUID");
        }
        return (uuid.getMostSignificantBits() & 0x0FFFL) << 48;
    }
}
```

### 生成不同版本的UUID

虽然Java的UUID类主要提供版本4的随机UUID，但你可以通过其他方式生成其他版本的UUID：

#### 版本1 UUID (基于时间戳和MAC地址)

```java
import java.net.NetworkInterface;
import java.net.SocketException;
import java.security.SecureRandom;
import java.util.Enumeration;

public class UUIDVersion1 {
    public static void main(String[] args) throws SocketException {
        // 获取MAC地址
        byte[] macAddress = getMacAddress();
        if (macAddress == null) {
            System.out.println("无法获取MAC地址，使用随机数替代");
            macAddress = new byte[6];
            new SecureRandom().nextBytes(macAddress);
        }
        
        // 获取当前时间戳
        long time = System.currentTimeMillis();
        long timeLow = time & 0xFFFFFFFFL;
        long timeMid = (time >> 32) & 0xFFFFL;
        long timeHi = (time >> 48) & 0xFFFFL;
        
        // 设置版本和变体
        long clockSeq = new SecureRandom().nextInt() & 0x3FFFL; // 14位
        
        // 组合各部分
        long msb = (timeLow << 32) | (timeMid << 16) | timeHi;
        msb &= ~0xF000L; // 清除版本位
        msb |= 0x1000L;  // 设置版本1
        
        long lsb = ((long) clockSeq & 0x3FFFL) << 48;
        lsb |= (bytesToLong(macAddress) & 0xFFFFFFFFFFFFL);
        lsb &= ~0xC000000000000000L; // 清除变体位
        lsb |= 0x8000000000000000L;  // 设置RFC 4122变体
        
        UUID uuid = new UUID(msb, lsb);
        System.out.println("版本1 UUID: " + uuid);
    }
    
    private static byte[] getMacAddress() throws SocketException {
        Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
        while (interfaces.hasMoreElements()) {
            NetworkInterface iface = interfaces.nextElement();
            if (iface.isLoopback() || !iface.isUp()) {
                continue;
            }
            byte[] mac = iface.getHardwareAddress();
            if (mac != null && mac.length == 6) {
                return mac;
            }
        }
        return null;
    }
    
    private static long bytesToLong(byte[] bytes) {
        long value = 0;
        for (byte b : bytes) {
            value = (value << 8) | (b & 0xFF);
        }
        return value;
    }
}
```

#### 版本3和版本5 UUID (基于命名空间和哈希)

```java
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.UUID;

public class UUIDVersion3And5 {
    public static void main(String[] args) throws NoSuchAlgorithmException {
        // 命名空间UUID (DNS)
        UUID namespaceDNS = UUID.fromString("6ba7b810-9dad-11d1-80b4-00c04fd430c8");
        
        // 要哈希的名称
        String name = "www.example.com";
        
        // 版本3 UUID (MD5)
        UUID uuidV3 = nameUUIDFromBytesAndAlgorithm(
            namespaceDNS.toString().getBytes(StandardCharsets.UTF_8), 
            name.getBytes(StandardCharsets.UTF_8), 
            "MD5");
        System.out.println("版本3 UUID: " + uuidV3);
        
        // 版本5 UUID (SHA-1)
        UUID uuidV5 = nameUUIDFromBytesAndAlgorithm(
            namespaceDNS.toString().getBytes(StandardCharsets.UTF_8), 
            name.getBytes(StandardCharsets.UTF_8), 
            "SHA-1");
        System.out.println("版本5 UUID: " + uuidV5);
    }
    
    private static UUID nameUUIDFromBytesAndAlgorithm(
            byte[] namespace, byte[] name, String algorithm) 
            throws NoSuchAlgorithmException {
        // 组合命名空间和名称
        byte[] hashInput = new byte[namespace.length + name.length];
        System.arraycopy(namespace, 0, hashInput, 0, namespace.length);
        System.arraycopy(name, 0, hashInput, namespace.length, name.length);
        
        // 计算哈希
        MessageDigest md = MessageDigest.getInstance(algorithm);
        byte[] hash = md.digest(hashInput);
        
        // 根据算法设置版本位
        int version = algorithm.equals("MD5") ? 3 : 5;
        
        // 设置版本和变体
        hash[6] = (byte) ((hash[6] & 0x0F) | (version << 4));
        hash[8] = (byte) ((hash[8] & 0x3F) | 0x80); // RFC 4122变体
        
        // 转换为long
        long msb = bytesToLong(hash, 0, 8);
        long lsb = bytesToLong(hash, 8, 16);
        
        return new UUID(msb, lsb);
    }
    
    private static long bytesToLong(byte[] bytes, int start, int end) {
        long value = 0;
        for (int i = start; i < end; i++) {
            value = (value << 8) | (bytes[i] & 0xFF);
        }
        return value;
    }
}
```

## UUID 的应用场景

1. **数据库主键**：作为分布式系统的主键
2. **会话标识**：Web应用中的会话ID
3. **事务标识**：分布式事务的唯一标识
4. **文件名**：生成唯一的临时文件名
5. **请求跟踪**：在微服务架构中跟踪请求链路

## 注意事项

1. **性能考虑**：版本1 UUID比版本4 UUID稍慢，因为它需要获取系统时间和MAC地址
2. **隐私问题**：版本1 UUID可能泄露MAC地址和生成时间
3. **存储空间**：UUID比自增整数占用更多存储空间
4. **索引效率**：随机UUID（如版本4）可能导致数据库索引碎片化

## 总结

Java的`java.util.UUID`类提供了简单易用的UUID生成和操作方法。对于大多数应用场景，使用`UUID.randomUUID()`生成版本4的随机UUID就足够了。如果需要基于时间或名称生成UUID，可以按照上述方法实现。