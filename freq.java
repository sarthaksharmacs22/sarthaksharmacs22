import java.util.*;

public class freq {
    public static void main(String[] args) {
        int count = 0;
        Scanner sc = new Scanner(System.in);
        System.out.println("enter a number");
        int n = sc.nextInt();
        System.out.println("enter frequency to find");
        int i = sc.nextInt();
        while (n > 0) {
            i = n % 10;
            // int i = n % 10;
            if (n == i) {
                count++;
            }
        }
        n /= 10;

        System.out.println(count);
    }
}
