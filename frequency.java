import java.util.*;

public class frequency {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("enter a number");
        int n = sc.nextInt();
        int count = 0;
        System.out.println("enter frequency to find");
        int i = sc.nextInt();
        while (n > 0) {
            if (n % 10 == i) {
                count++;
            }
            if (count > 0) {
                System.out.println(count);
            } else {
                System.out.println("not find");
            }
            break;
        }
    }
}
