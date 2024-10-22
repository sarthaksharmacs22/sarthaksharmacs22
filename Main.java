import java.util.Scanner;

public class P {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in)) {
            int n = sc.nextInt();
            int c = 0;
            for (int i = 2; i < n; i++) {
                if (n % i == 0) {
                    c++;

                }
            }
            if (c > 1) {
                System.out.print("not prime");

            } else {
                System.out.print("prime");
            }
        }
    }
}