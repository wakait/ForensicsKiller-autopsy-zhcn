import java.util.*;

/** 通用 bundle 加载验证：参数为完整的 bundle 基名，如 org.sleuthkit.datamodel.Bundle */
public class LoadCheck {
    public static void main(String[] args) {
        int fail = 0, totalKeys = 0, totalZhKeys = 0;
        for (String base : args) {
            try {
                ResourceBundle rb = ResourceBundle.getBundle(base, Locale.CHINA);
                int n = 0, zh = 0;
                String sample = "";
                for (String k : rb.keySet()) {
                    n++;
                    String v = rb.getString(k);
                    boolean has = false;
                    for (int i = 0; i < v.length() && !has; i++) {
                        char c = v.charAt(i);
                        if (c >= 0x4e00 && c <= 0x9fff) has = true;
                    }
                    if (has) { zh++; if (sample.isEmpty()) sample = k + "=" + v; }
                }
                totalKeys += n; totalZhKeys += zh;
                String loc = rb.getLocale().toString();
                System.out.printf("[OK] %-54s %-6s keys=%4d zh=%4d  %s%n",
                        base, loc.equals("") ? "root" : loc, n, zh,
                        sample.length() > 46 ? sample.substring(0, 46) + "..." : sample);
                if (!loc.equals("zh_CN")) { System.out.println("     WARN 未命中 zh_CN"); fail++; }
                if (zh == 0) { System.out.println("     WARN 该包无中文值"); fail++; }
            } catch (MissingResourceException e) {
                fail++;
                System.out.printf("[MISS] %s (%s)%n", base, e.getMessage());
            }
        }
        System.out.printf("%n合计 %d 包，键 %d，含中文键 %d，异常 %d%n",
                args.length, totalKeys, totalZhKeys, fail);
        if (fail > 0) System.exit(1);
    }
}
